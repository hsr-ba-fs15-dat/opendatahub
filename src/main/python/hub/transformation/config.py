from pyparsing import nums
from pyparsing import Word, CaselessKeyword, QuotedString, Regex
from pyparsing import Optional, ZeroOrMore, Or, Suppress, Group, NotAny
from pyparsing import delimitedList


class OQLParser(object):
    def __init__(self):
        self.grammar = self.build_grammar()

    @classmethod
    def build_grammar(cls):

        identifier = Regex(r'[a-zA-Z_][a-zA-Z0-9_]*') | QuotedString('"')

        alias = Suppress(CaselessKeyword('as')) + identifier('alias')

        field = Optional(identifier.copy()('prefix') + Suppress('.')) + identifier.copy()('name') + NotAny('(')
        field.setParseAction(Field.parse)

        aliased_field = field('field') + Optional(alias)  # defaults to using name as alias
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

        data_source = identifier('name') + Optional(alias)
        data_source.setParseAction(DataSource.parse)

        join_single_condition = field('left') + Suppress('=') + field('right')
        join_single_condition.setParseAction(JoinCondition.parse)

        join_multi_condition = Suppress('(') + delimitedList(join_single_condition,
                                                             delim=Suppress(CaselessKeyword('and'))) + Suppress(')')
        join_multi_condition.setParseAction(JoinConditionList.parse)

        join_condition_list = join_single_condition | join_multi_condition

        join = Suppress(CaselessKeyword('join')) + data_source.copy()('datasource') + Suppress(
            CaselessKeyword('on')) + join_condition_list.copy()('condition')
        join.setParseAction(JoinedDataSource.parse)

        data_source_declaration = Suppress(CaselessKeyword('from')) + data_source + ZeroOrMore(join)

        filter = field + '=' + value | field + CaselessKeyword('in') + '(' + value + ')' | field + CaselessKeyword(
            'is') + CaselessKeyword('null')

        and_or = (CaselessKeyword('and') | CaselessKeyword('or'))
        filter_declaration = Optional(CaselessKeyword('where') + delimitedList(filter, and_or))

        order_by_field = field + Optional(Or([CaselessKeyword('asc'), CaselessKeyword('desc')]))
        order_by_declaration = Optional(CaselessKeyword('order by') + delimitedList(order_by_field))

        return field_declaration_list('fields') + data_source_declaration(
            'datasources') + filter_declaration + order_by_declaration

    def parse(self, input):
        return self.grammar.parseString(input)


class Field(object):
    def __init__(self, name, prefix=None):
        self.prefix = prefix
        self.name = name

    def __repr__(self):
        return '<Field name=\'{}\' prefix=\'{}\'>'.format(self.name, self.prefix)

    @classmethod
    def parse(cls, tokens):
        if 'name' not in tokens:
            raise ParseException()

        name = tokens.get('name')
        prefix = tokens.get('prefix', None)

        return cls(name, prefix)


class AliasedField(Field):
    def __init__(self, name, prefix=None, alias=None):
        super(AliasedField, self).__init__(name, prefix)
        self.alias = alias or name

    def __repr__(self):
        return '<Field name=\'{}\' prefix=\'{}\' alias=\'{}\'>'.format(self.name, self.prefix, self.alias)

    @classmethod
    def parse(cls, tokens):
        if 'field' not in tokens:
            raise ParseException()

        field = tokens.get('field')

        if not isinstance(field, Field):
            raise ParseException("expected field, got %s" % type(field))

        alias = tokens.get('alias', None)

        return cls(field.name, field.prefix, alias)


class Expression(object):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '<Expr value={}>'.format(self.value)

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
        return '<Expr value={} alias=\'{}\'>'.format(self.value, self.alias)

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
        return '<Function name=\'{}\' args={}>'.format(self.name, self.args or '')


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
        return '<Function name=\'{}\' args={} alias=\'{}\'>'.format(self.name, self.args or '', self.alias)


class DataSource(object):
    def __init__(self, name, alias=None):
        self.name = name
        self.alias = alias or name

    @classmethod
    def parse(cls, tokens):
        if len(tokens) < 1:
            raise ParseException()

        name = tokens.get('name')
        alias = tokens.get('alias', None)

        return cls(name, alias)

    def __repr__(self):
        return '<DataSource name=\'{}\' alias=\'{}\'>'.format(self.name, self.alias)


class JoinCondition(object):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    @classmethod
    def parse(cls, tokens):
        if 'left' not in tokens or 'right' not in tokens:
            raise ParseException('invalid join condition')

        left = tokens.get('left')
        right = tokens.get('right')

        if not isinstance(left, Field) or not isinstance(right, Field):
            raise ParseException('expected field = field, got %s = %s' % (type(left, type(right))))

        return cls(left, right)

    def __repr__(self):
        return '<JoinCondition left={} right={}>'.format(self.left, self.right)


class JoinConditionList(object):
    def __init__(self, conditions):
        self.conditions = conditions

    def __len__(self):
        return len(self.conditions)

    def __getitem__(self, index):
        return self.conditions[index]

    @classmethod
    def parse(cls, tokens):
        if len(tokens) == 0:
            raise ParseException()

        conditions = list(tokens)
        return cls(conditions)

    def __repr__(self):
        return '<JoinConditionList conditions={}>'.format(self.conditions)


class JoinedDataSource(DataSource):
    def __init__(self, name, alias, condition):
        super(JoinedDataSource, self).__init__(name, alias)

        self.condition = condition

    @classmethod
    def parse(cls, tokens):
        if 'datasource' not in tokens:
            raise ParseException('join without datasource')
        if 'condition' not in tokens:
            raise ParseException('join without conditions')

        datasource = tokens.get('datasource')
        condition = tokens.get('condition')

        return cls(datasource.name, datasource.alias, condition)

    def __repr__(self):
        return '<JoinedDataSource name=\'{}\' alias=\'{}\' condition={}>'.format(self.name, self.alias, self.condition)


class ParseException(Exception):
    def __init__(self, message='parse error'):
        super(ParseException, self).__init__(message)
