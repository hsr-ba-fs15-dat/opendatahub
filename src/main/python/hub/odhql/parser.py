from collections import Sequence

from pyparsing import nums
from pyparsing import Word, CaselessKeyword, QuotedString, Regex, Literal, Suppress
from pyparsing import Optional, ZeroOrMore, Or, Group, NotAny, Forward, StringEnd
from pyparsing import delimitedList
from enum import Enum


class OdhQLParser(object):
    """
    Parser for the OpenDataHub Query Language (OdhQL).

    Syntax borrows heavily from ANSI SQLs SELECT statement, but there are some differences.

    All keywords are case-insensitive.

    Identifiers: Everything that doesn't match r'[a-zA-Z_][a-zA-Z0-9_]*' needs to be quoted using "double quotes".
    If you need to include quote chars inside your strings, escape with a backslash ('\').

    All field references must be prefixed by the name of the data source they're coming from.

    Description in BNF (as used by the diagram generator at http://bottlecaps.de/rr/ui):

    ---------------------------------------------------------------------------
    UnionQuery ::= Query ( "union" Query )* ( OrderByList )?
    Query ::= FieldSelection DataSourceSelection ( FilterList )?

    FieldSelection ::= "select" AliasedFieldEquiv ( "," AliasedFieldEquiv )*
    AliasedFieldEquiv ::= FieldEquiv "as" Alias
    FieldEquiv ::= Function | Value | Field
    Function ::= Identifier "(" ( ListOfFunctionArguments )? ")"
    ListOfFunctionArguments ::= FieldEquiv ( ( "," FieldEquiv )* )?

    DataSourceName ::= Identifier
    FieldName ::= Identifier
    Alias ::= Identifier

    Field ::= DataSourceNameOrAlias "." FieldName

    DataSourceNameOrAlias ::= DataSourceName | Alias

    DataSourceSelection ::= "from" DataSourceName ( "as" Alias )? ( JoinDefinition )*
    JoinDefinition ::= "join" DataSourceName ( "as" Alias )? "on" JoinCondition
    JoinCondition ::= SingleJoinCondition | "(" SingleJoinCondition ( "and" SingleJoinCondition )* ")"
    SingleJoinCondition ::= Field "=" Field

    FilterList ::= "where" FilterAlternative
    FilterAlternative ::= FilterCombination ( "or" FilterCombination )*
    FilterCombination ::= FilterDefinition ( "and" FilterDefinition )*
    FilterDefinition ::= BinaryCondition | InCondition |
                       IsNullCondition | "(" FilterAlternative ")"
    BinaryCondition ::= FieldEquiv BinaryOperator FieldEquiv
    BinaryOperator ::= "=" | "!=" | "<" | "<=" | ">" | ">=" | "like"
    InCondition ::= FieldEquiv ( "not" )? "in" "(" Value ( "," Value )* ")"
    IsNullCondition ::= Field "is" ( "not" )? Null
    OrderByList ::= "order" "by" OrderByField ( "," OrderByField )*
    OrderByField ::= ( Field | Alias | Position) ( "asc" | "desc" )?
    Integer ::= ( "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" )*

    Value ::= SingleQuotedString | Number | Boolean | Null
    Number ::= Integer | Float
    Float ::= Integer "." Integer
    Boolean ::= "true" | "false"
    Null ::= "null"
    SingleQuotedString ::= "string in single quotes"
    DoubleQuotedString ::= "string in double quotes"

    Identifier ::= ( "a..z" | "A..Z" | "_" ) ( "a..z" | "A..Z" | "_" | Integer )* | DoubleQuotedString
    ---------------------------------------------------------------------------
    """

    def __init__(self):
        self.grammar = self.build_grammar()

    @classmethod
    def build_grammar(cls):
        escape_char = '\\'
        identifier = Regex(r'[a-zA-Z_][a-zA-Z0-9_]*') | QuotedString('"', escChar=escape_char)
        kw_and = CaselessKeyword('and')
        kw_or = CaselessKeyword('or')

        alias = CaselessKeyword('as') + identifier('alias')

        field = (identifier.copy()('prefix') + '.' + identifier.copy()('name') + NotAny('('))('field')
        field.setParseAction(Field.parse)

        aliased_field = field + Optional(alias)  # defaults to using name as alias
        aliased_field.setParseAction(AliasedField.parse)

        integer_value = Word(nums)
        number_value = Group(integer_value + Optional('.' + integer_value))
        number_value.setParseAction(Expression.parse_number)

        boolean_value = CaselessKeyword('true') | CaselessKeyword('false')
        boolean_value.setParseAction(Expression.parse_boolean)

        string_value = QuotedString('\'', escChar=escape_char)
        null_value = CaselessKeyword('null')
        null_value.setParseAction(Expression.parse_null)

        value = (number_value | boolean_value | string_value | null_value)('value')
        value.setParseAction(Expression.parse)

        aliased_value = (value + alias)
        aliased_value.setParseAction(AliasedExpression.parse)

        function = Forward()
        function << (identifier.copy()('name') +
                     '(' + Optional(delimitedList(field | value | function))('args') + ')')
        function.setParseAction(Function.parse)

        aliased_function = function('function') + alias
        aliased_function.setParseAction(AliasedFunction.parse)

        field_declaration = aliased_function | aliased_value | aliased_field

        field_declaration_list = Suppress(CaselessKeyword('select')) + delimitedList(field_declaration)

        data_source = identifier('name') + Optional(alias)
        data_source.setParseAction(DataSource.parse)

        join_single_condition = field('left') + '=' + field('right')
        join_single_condition.setParseAction(JoinCondition.parse)

        join_multi_condition = Literal('(') + delimitedList(join_single_condition, delim=kw_and)('conditions') + ')'
        join_multi_condition.setParseAction(JoinConditionList.parse)

        join_condition_list = join_single_condition | join_multi_condition

        join = (CaselessKeyword('join') + data_source.copy()('datasource') +
                CaselessKeyword('on') + join_condition_list.copy()('condition'))
        join.setParseAction(JoinedDataSource.parse)

        data_source_declaration = Suppress(CaselessKeyword('from')) + data_source + ZeroOrMore(join)

        condition_side = field | value | function

        operator = Literal('=') | '!=' | '<=' | '<' | '>=' | '>' | CaselessKeyword('like')
        operator.setParseAction(BinaryCondition.parse_operator)

        binary_condition = condition_side.copy()('left') + operator('operator') + condition_side.copy()('right')
        binary_condition.setParseAction(BinaryCondition.parse)

        in_condition = (condition_side.copy()('left') + Optional(CaselessKeyword('not'))('invert') +
                        CaselessKeyword('in') + '(' + Group(delimitedList(value))('in_list') + ')')
        in_condition.setParseAction(InCondition.parse)

        null_condition = (field + CaselessKeyword('is') + Optional(CaselessKeyword('not'))('invert') +
                          CaselessKeyword('null'))
        null_condition.setParseAction(IsNullCondition.parse)

        single_filter = Forward()

        filter_combination = delimitedList(single_filter, delim=kw_and)
        filter_combination.setParseAction(FilterCombination.parse)

        filter_alternative = delimitedList(filter_combination, delim=kw_or)
        filter_alternative.setParseAction(FilterAlternative.parse)

        single_filter << (null_condition | binary_condition | in_condition |
                          Suppress('(') + filter_alternative + Suppress(')'))

        filter_declaration = Suppress(CaselessKeyword('where')) + filter_alternative.copy()('conditions')

        order_by_position = Word(nums)
        order_by_position.setParseAction(OrderByPosition.parse)

        order_by_alias = identifier.copy()
        order_by_alias.setParseAction(OrderByAlias.parse)

        order_by_field_equiv = field | order_by_alias | order_by_position

        order_by_field = (order_by_field_equiv('field') + Optional(Or([
            CaselessKeyword('asc'), CaselessKeyword('desc')]))('direction'))
        order_by_field.setParseAction(OrderBy.parse)

        order_by_declaration = (Suppress(CaselessKeyword('order') + CaselessKeyword('by')) +
                                delimitedList(order_by_field, delim=',')('fields'))
        order_by_declaration.setParseAction(Query.parse_order_by)

        query = (field_declaration_list('fields') + data_source_declaration('datasources') +
                 Optional(filter_declaration('filter')))
        query.setParseAction(Query.parse)

        query.validate()

        union_query = (delimitedList(query, delim=CaselessKeyword('union'))('queries') +
                       Optional(order_by_declaration)('sort') + StringEnd())
        union_query.setParseAction(Union.parse)

        return union_query

    def parse(self, input):
        return self.grammar.parseString(input)[0]


class ASTBase(object):
    def accept(self, visitor):
        visitor.visit(self)


class Union(ASTBase):
    def __init__(self, queries, order):
        self.queries = queries
        self.order = order

    @classmethod
    def parse(cls, tokens):
        if len(tokens) < 1:
            raise ParseException('malformed Union (no queries)')

        if len(tokens) < 2:
            return

        queries = list(tokens.get('queries'))
        order = list(tokens.get('sort')[0]) if 'sort' in tokens else []

        return cls(queries, order)

    def __repr__(self):
        return '<Union queries={} order={}>'.format(self.queries, self.order)

    def accept(self, visitor):
        visitor.visit(self)

        for q in self.queries:
            q.accept(visitor)

        if self.order:
            for o in self.order:
                o.accept(visitor)


class Query(ASTBase):
    def __init__(self, fields, data_sources, filter_definitions):
        self.fields = fields
        self.data_sources = data_sources
        self.filter_definitions = filter_definitions

    @classmethod
    def parse(cls, tokens):
        if 'fields' not in tokens:
            raise ParseException('malformed Query (no fields)')
        if 'datasources' not in tokens:
            raise ParseException('malformed Query (no data sources)')

        fields = list(tokens.get('fields'))
        data_sources = list(tokens.get('datasources'))
        filter_definitions = tokens.get('filter')[0] if 'filter' in tokens else None

        return cls(fields, data_sources, filter_definitions)

    @classmethod
    def parse_order_by(cls, tokens):
        if 'fields' not in tokens:
            raise ParseException('malformed OrderBy (no fields)')

        return [tokens.get('fields')]

    def __repr__(self):
        return '<Query fields={} data_sources={} filter_definitions={}>'.format(self.fields, self.data_sources,
                                                                                self.filter_definitions)

    def accept(self, visitor):
        visitor.visit(self)

        for f in self.fields:
            f.accept(visitor)

        for d in self.data_sources:
            d.accept(visitor)

        if self.filter_definitions:
            for f in self.filter_definitions:
                f.accept(visitor)


class Field(ASTBase):
    def __init__(self, name, prefix=None):
        self.prefix = prefix
        self.name = name

    def __repr__(self):
        return '<Field name=\'{}\' prefix=\'{}\'>'.format(self.name, self.prefix)

    @classmethod
    def parse(cls, tokens):
        if 'name' not in tokens:
            raise ParseException('malformed Field (name not found)')
        if 'prefix' not in tokens:
            raise ParseException('malformed Field (prefix not found)')

        name = tokens.get('name')
        prefix = tokens.get('prefix')

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
            raise ParseException('malformed AliasedField (field not found)')

        field = tokens.get('field')

        if not isinstance(field, Field):
            raise ParseException("expected field, got {}".format(type(field)))

        alias = tokens.get('alias', None)

        return cls(field.name, field.prefix, alias)


class Expression(ASTBase):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '<Expr value={}>'.format(self.value)

    @classmethod
    def parse(cls, tokens):
        if 'value' not in tokens:
            raise ParseException('malformed Expression (no value)')

        value = tokens.get('value')

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

    @classmethod
    def parse_boolean(cls, tokens):
        if len(tokens) < 1:
            raise ParseException('malformed boolean value (no value)')

        value = tokens[0]

        return str(value).lower() == 'true'

    @classmethod
    def parse_null(cls, tokens):
        return [None]


class AliasedExpression(Expression):
    def __init__(self, value, alias):
        self.alias = alias

        super(AliasedExpression, self).__init__(value)

    def __repr__(self):
        return '<Expr value={} alias=\'{}\'>'.format(self.value, self.alias)

    @classmethod
    def parse(cls, tokens):
        if 'value' not in tokens:
            raise ParseException('malformed AliasedExpression (no value)')

        if 'alias' not in tokens:
            raise ParseException('malformed AliasedExpression (no alias)')

        value = tokens.get('value')

        if not isinstance(value, Expression):
            raise ParseException('expected Expression, got {}'.format(type(value)))

        value = value.value

        alias = tokens.get('alias')

        return cls(value, alias)


class Function(ASTBase):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    @classmethod
    def parse(cls, tokens):
        if 'name' not in tokens:
            raise ParseException('malformed Function (no name)')

        name = tokens.get('name')
        # this one is weird: access by name makes it almost impossible to get a simple list of our own
        # classes (i.e. no ParseResults)
        args = list(tokens.get('args')) if 'args' in tokens else []  # get rid of ParseResult

        return cls(name, args)

    def __repr__(self):
        return '<Function name=\'{}\' args={}>'.format(self.name, self.args or '')

    def accept(self, visitor):
        visitor.visit(self)

        for arg in self.args:
            arg.accept(visitor)


class AliasedFunction(Function):
    def __init__(self, name, args, alias):
        super(AliasedFunction, self).__init__(name, args)
        self.alias = alias

    @classmethod
    def parse(cls, tokens):
        if 'function' not in tokens:
            raise ParseException('malformed AliasedFunction (no name)')
        if 'alias' not in tokens:
            raise ParseException('malformed AliasedFunction (no alias)')

        func = tokens.get('function')
        alias = tokens.get('alias')

        if not isinstance(func, Function):
            raise ParseException('expected Function, got {}'.format(type(func)))

        return cls(func.name, func.args, alias)

    def __repr__(self):
        return '<Function name=\'{}\' args={} alias=\'{}\'>'.format(self.name, self.args or '', self.alias)


class DataSource(ASTBase):
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


class JoinCondition(ASTBase):
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
            raise ParseException('expected field = field, got {} = {}'.format(type(left), type(right)))

        return cls(left, right)

    def __repr__(self):
        return '<JoinCondition left={} right={}>'.format(self.left, self.right)

    def accept(self, visitor):
        visitor.visit(self)

        self.left.accept(visitor)
        self.right.accept(visitor)


class JoinConditionList(ASTBase, Sequence):
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

        conditions = list(tokens.get('conditions'))
        return cls(conditions)

    def __repr__(self):
        return '<JoinConditionList conditions={}>'.format(self.conditions)

    def accept(self, visitor):
        visitor.visit(self)

        for cond in self.conditions:
            cond.accept(visitor)


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

    def accept(self, visitor):
        visitor.visit(self)

        self.condition.accept(visitor)


class BinaryCondition(ASTBase):
    class Operator(Enum):
        equals = 1
        not_equals = 2
        less = 3
        less_or_equal = 4
        greater = 5
        greater_or_equal = 6
        like = 7

    def __init__(self, left, operator, right, invert):
        self.left = left
        self.operator = operator
        self.right = right
        self.invert = invert

    @classmethod
    def parse(cls, tokens):
        if 'left' not in tokens:
            raise ParseException('malformed BinaryCondition (no left side)')

        if 'right' not in tokens:
            raise ParseException('malformed BinaryCondition (no right side)')

        if 'operator' not in tokens:
            raise ParseException('malformed BinaryCondition (no operator)')

        left = tokens.get('left')
        right = tokens.get('right')
        op = tokens.get('operator')
        invert = 'invert' in tokens

        v = FindClassVisitor(Field)
        left.accept(v)
        if not v.found:
            right.accept(v)
            if not v.found:
                raise ParseException('illegal BinaryCondition: at least one side needs to reference a Field')

        return cls(left, op, right, invert)

    @classmethod
    def parse_operator(cls, tokens):
        if len(tokens) < 1:
            raise ParseException('malformed operator (no operator)')

        op = tokens[0]

        if op == '=':
            return cls.Operator.equals
        if op == '!=':
            return cls.Operator.not_equals
        if op == '<':
            return cls.Operator.less
        if op == '<=':
            return cls.Operator.less_or_equal
        if op == '>':
            return cls.Operator.greater
        if op == '>=':
            return cls.Operator.greater_or_equal
        if str(op).lower() == 'like':
            return cls.Operator.like

        raise ParseException('unregistered operation: {}'.format(op))

    def __repr__(self):
        return '<BinaryCondition left={} op={} right={} invert={}>'.format(self.left, self.operator, self.right,
                                                                           self.invert)

    def accept(self, visitor):
        visitor.visit(self)

        self.left.accept(visitor)
        self.right.accept(visitor)


class InCondition(ASTBase):
    def __init__(self, left, in_list, invert):
        self.left = left
        self.in_list = in_list
        self.invert = invert

    @classmethod
    def parse(cls, tokens):
        if 'left' not in tokens:
            raise ParseException('malformed InCondition (no left side)')

        if 'in_list' not in tokens:
            raise ParseException('malformed InCondition (no in_list)')

        left = tokens.get('left')
        in_list = tokens.get('in_list')
        invert = 'invert' in tokens

        return cls(left, in_list, invert)

    def __repr__(self):
        return '<InCondition left={} in_list={}>'.format(self.left, self.in_list)

    def accept(self, visitor):
        visitor.visit(self)

        self.left.accept(visitor)

        for item in self.in_list:
            item.accept(visitor)


class IsNullCondition(ASTBase):
    def __init__(self, field, invert):
        self.field = field
        self.invert = invert

    @classmethod
    def parse(cls, tokens):
        if 'field' not in tokens:
            raise ParseException('malformed IsNullCondition')

        field = tokens.get('field')
        invert = 'invert' in tokens

        if not isinstance(field, Field):
            raise ParseException('expected Field, got {}'.format(type(field)))

        return cls(field, invert)

    def accept(self, visitor):
        visitor.visit(self)

        self.field.accept(visitor)

    def __repr__(self):
        return '<IsNullCondition field={} invert={}>'.format(self.field, self.invert)


class FilterListBase(ASTBase, Sequence):
    def __init__(self, conditions):
        self.conditions = conditions

    @classmethod
    def parse(cls, tokens):
        if len(tokens) < 1:
            raise ParseException('malformed {} (no conditions)'.format(cls.__name__))

        conditions = list(tokens[:])

        return [cls(conditions)]

    def accept(self, visitor):
        visitor.visit(self)

        for cond in self.conditions:
            cond.accept(visitor)

    def __len__(self):
        return len(self.conditions)

    def __getitem__(self, item):
        return self.conditions[item]

    def __repr__(self):
        return '<{} conditions={}>'.format(self.__class__.__name__, self.conditions)


class FilterCombination(FilterListBase):
    """list of filters joined by AND"""


class FilterAlternative(FilterListBase):
    """list of filters joined by OR"""


class OrderByPosition(ASTBase):
    def __init__(self, position):
        self.position = position

    @classmethod
    def parse(cls, tokens):
        if len(tokens) < 1:
            raise ParseException('malformed OrderByPosition (no position)')

        try:
            position = int(tokens[0])
            return cls(position)
        except ValueError:
            pass

    def __repr__(self):
        return '<OrderByPosition position={}>'.format(self.position)


class OrderByAlias(ASTBase):
    def __init__(self, alias):
        self.alias = alias

    @classmethod
    def parse(cls, tokens):
        if len(tokens) < 1:
            raise ParseException('malformed OrderByAlias (no alias)')

        return cls(tokens[0])

    def __repr__(self):
        return '<OrderByAlias alias={}>'.format(self.alias)


class OrderBy(ASTBase):
    class Direction(Enum):
        ascending = 1
        descending = 2

    def __init__(self, field, direction):
        self.field = field
        self.direction = direction

    @classmethod
    def parse(cls, tokens):
        if 'field' not in tokens:
            raise ParseException('malformed OrderByField (no field)')

        field = tokens.get('field')
        dir = str(tokens.get('direction', 'asc')).lower()

        if dir == 'desc':
            direction = OrderBy.Direction.descending
        else:
            direction = OrderBy.Direction.ascending

        return cls(field, direction)

    def __repr__(self):
        return '<OrderBy field={} direction={}>'.format(self.field, self.direction)


class FindClassVisitor(object):
    def __init__(self, target_class):
        self.target = target_class
        self.found = False

    def visit(self, obj):
        if isinstance(obj, self.target):
            self.found = True


class ParseException(Exception):
    def __init__(self, message='parse error'):
        super(ParseException, self).__init__(message)
