from pyparsing import nums
from pyparsing import Word, CaselessKeyword, QuotedString
from pyparsing import Optional, ZeroOrMore, OneOrMore, Or, Suppress, Group, NotAny

from pyparsing import delimitedList, srange


class OQLParser(object):
    def __init__(self):
        self.grammar = self.build_grammar()

    @classmethod
    def build_grammar(cls):
        identifier_chars = srange('[a-zA-Z_]')

        identifier = Word(identifier_chars) | QuotedString('"')

        alias = Suppress(CaselessKeyword('as')) + identifier

        field = identifier.copy() + NotAny('(')
        field.setParseAction(Field.parse)

        aliased_field = field + Optional(alias)  # defaults to using name as alias
        aliased_field.setParseAction(AliasedField.parse)

        integer_value = Word(nums)
        number_value = Group(integer_value + Optional('.' + integer_value))
        number_value.setParseAction(Expression.parse_number)

        string_value = QuotedString('\'')

        value = (number_value | string_value)
        value.setParseAction(Expression.parse)

        aliased_value = (value + alias)
        aliased_value.setParseAction(AliasedExpression.parse)

        function = identifier + Suppress('(') + Optional(Group(delimitedList(field | value))) + Suppress(')')
        function.setParseAction(Function.parse)

        aliased_function = function + alias
        aliased_function.setParseAction(AliasedFunction.parse)

        field_declaration = aliased_function | aliased_value | aliased_field

        field_declaration_list = Suppress(CaselessKeyword('select')) + delimitedList(field_declaration)

        and_or = (CaselessKeyword('and') | CaselessKeyword('or'))

        data_source = Group(identifier('name'))

        join_single_condition = field + '=' + field
        join_multi_condition = '(' + join_single_condition + OneOrMore(and_or + join_single_condition) + ')'
        join_condition_list = join_single_condition ^ join_multi_condition

        data_source_with_alias = data_source + Optional(Suppress(CaselessKeyword('as')) + identifier("alias"))

        join = Group(Suppress(CaselessKeyword('join')) + data_source_with_alias + Suppress(
            CaselessKeyword('on')) + join_condition_list)

        data_source_declaration = Optional(
            Suppress(CaselessKeyword('from')) + data_source_with_alias + ZeroOrMore(join)("join")
        )

        filter = field + '=' + value | field + CaselessKeyword('in') + '(' + value + ')' | field + CaselessKeyword(
            'is') + CaselessKeyword('null')

        filter_declaration = Optional(CaselessKeyword('where') + delimitedList(filter, and_or))

        order_by_field = field + Optional(Or([CaselessKeyword('asc'), CaselessKeyword('desc')]))
        order_by_declaration = Optional(CaselessKeyword('order by') + delimitedList(order_by_field))

        return field_declaration_list('fields') + data_source_declaration(
            'datasources') + filter_declaration + order_by_declaration

    def parse(self, input):
        return self.grammar.parseString(input)


class Field(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '[Field name=\'{}\']'.format(self.name)

    @classmethod
    def parse(cls, tokens):
        if len(tokens) < 1:
            raise ParseException()

        name = tokens[0]

        return cls(name)


class AliasedField(Field):
    def __init__(self, name, alias=None):
        super(AliasedField, self).__init__(name)
        self.alias = alias or name

    def __repr__(self):
        return '[Field name=\'{}\' alias=\'{}\']'.format(self.name, self.alias)

    @classmethod
    def parse(cls, tokens):
        if len(tokens) < 1:
            raise ParseException()

        field = tokens[0]

        if not isinstance(field, Field):
            raise ParseException("expected field, got %s" % type(field))

        alias = tokens[1] if len(tokens) > 1 else None

        return cls(field.name, alias)


class Expression(object):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '[Expr value=\'{}\']'.format(self.value)

    @classmethod
    def parse(cls, tokens):
        if len(tokens) < 1:
            raise ParseException()

        value = tokens[0]

        return cls(value)

    @classmethod
    def parse_number(cls, tokens):
        try:
            num = tokens.pop()

            if len(num) > 1:
                joined = ''.join(num)
                return [float(joined)]
            else:
                return [int(num.pop())]
        except:
            pass


class AliasedExpression(Expression):
    def __init__(self, value, alias):
        self.alias = alias

        super(AliasedExpression, self).__init__(value)

    def __repr__(self):
        return '[Expr value=\'{}\' alias=\'{}\']'.format(self.value, self.alias)

    @classmethod
    def parse(cls, tokens):
        if len(tokens) < 2:
            raise ParseException('missing alias')

        value = tokens[0]

        if isinstance(value, Expression):
            value = value.value

        alias = tokens[1]

        return cls(value, alias)


class Function(object):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    @classmethod
    def parse(cls, tokens):
        if len(tokens) < 1:
            raise ParseException()

        name = tokens[0]
        args = list(tokens[1]) if len(tokens) > 1 else []  # get rid of ParseResult

        return cls(name, args)

    def __repr__(self):
        return '[Function name=\'{}\' args=\'{}\']'.format(self.name, self.args or '')


class AliasedFunction(Function):
    def __init__(self, name, args, alias):
        super(AliasedFunction, self).__init__(name, args)
        self.alias = alias

    @classmethod
    def parse(cls, tokens):
        if len(tokens) < 2:
            raise ParseException()

        func = tokens[0]
        alias = tokens[1]

        if not isinstance(func, Function):
            raise ParseException('function expected, got %s' % type(func))

        return cls(func.name, func.args, alias)

    def __repr__(self):
        return '[Function name=\'{}\' args=\'{}\' alias=\'{}\']'.format(self.name, self.args or '', self.alias)


class ParseException(Exception):
    def __init__(self, message='parse error'):
        super(ParseException, self).__init__(message)
