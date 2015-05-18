"""Classes for ODHQLs Abstract Syntax Tree."""

from collections import Sequence

from enum import Enum

from hub.odhql.exceptions import TokenException


class ASTBase(object):
    """Base class for all AST classes."""

    def accept(self, visitor):
        """
        Basic support for the visitor pattern.
        """

        visitor.visit(self)


class Union(ASTBase):
    """Result for union queries."""

    def __init__(self, queries, order):
        """
        :type queries: list
        :type order: list
        """
        self.queries = queries
        self.order = order

    @classmethod
    def parse(cls, tokens):
        if len(tokens) < 1:
            raise TokenException('malformed Union (no queries)')

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
    """Result for normal queries."""

    def __init__(self, fields, data_sources, filter_definitions):
        """
        :type fields: list
        :type data_sources: list
        :type filter_definitions: list
        """
        self.fields = fields
        self.data_sources = data_sources
        self.filter_definitions = filter_definitions

    @classmethod
    def parse(cls, tokens):
        if 'fields' not in tokens:
            raise TokenException('malformed Query (no fields)')
        if 'datasources' not in tokens:
            raise TokenException('malformed Query (no data sources)')

        fields = list(tokens.get('fields'))
        data_sources = list(tokens.get('datasources'))
        filter_definitions = tokens.get('filter')[0] if 'filter' in tokens else None

        return cls(fields, data_sources, filter_definitions)

    @classmethod
    def parse_order_by(cls, tokens):
        if 'fields' not in tokens:
            raise TokenException('malformed OrderBy (no fields)')

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


class Expression(ASTBase):
    """Base class for expression types."""


class Field(Expression):
    """Reference a field in a table."""

    def __init__(self, name, prefix=None):
        self.prefix = prefix
        self.name = name

    def __repr__(self):
        return '<Field name=\'{}\' prefix=\'{}\'>'.format(self.name, self.prefix)

    @classmethod
    def parse(cls, tokens):
        if 'name' not in tokens:
            raise TokenException('malformed Field (name not found)')
        if 'prefix' not in tokens:
            raise TokenException('malformed Field (prefix not found)')

        name = tokens.get('name')
        prefix = tokens.get('prefix')

        return cls(name, prefix)


class LiteralExpression(Expression):
    """Literal values are numbers, static strings, bools, null values..."""

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '<LiteralExpression value={}>'.format(self.value)

    @classmethod
    def parse(cls, tokens):
        if 'value' not in tokens:
            raise TokenException('malformed Expression (no value)')

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
            raise TokenException('malformed boolean value (no value)')

        value = tokens[0]

        return str(value).lower() == 'true'

    @classmethod
    def parse_null(cls):
        return [None]


class CaseRule(ASTBase):
    """
    A single rule ('when <condition> then <expression>' or 'else <expression>') in a case expression.
    """

    def __init__(self, condition, expression):
        """
        :type condition: any condition or types.NoneType
        :type expression: hub.odhql.ast.Expression
        """
        self.condition = condition
        self.expression = expression

    @classmethod
    def parse_when(cls, tokens):
        if 'condition' not in tokens:
            raise TokenException('malformed CaseExpression (expected condition)')
        if 'expression' not in tokens:
            raise TokenException('malformed CaseExpression (expected expression)')

        condition = tokens.get('condition')
        expression = tokens.get('expression')

        return cls(condition, expression)

    @classmethod
    def parse_else(cls, tokens):
        if 'expression' not in tokens:
            raise TokenException('malformed CaseExpression (expected expression)')

        expression = tokens.get('expression')

        return cls(None, expression)

    def __repr__(self):
        return '<CaseRule condition={} expression={}>'.format(self.condition, self.expression)

    def accept(self, visitor):
        visitor.visit(self)

        if self.condition:
            self.condition.accept(visitor)
        self.expression.accept(visitor)


class CaseExpression(Expression):
    """
    'case when ... then ... end' expressions.
    """

    def __init__(self, rules):
        self.rules = rules

    @classmethod
    def parse(cls, tokens):
        if 'when' not in tokens:
            raise TokenException('malformed CaseExpression (expected at least one condition)')

        rules = tokens.get('when')[:]

        if 'else' in tokens:
            rules.append(tokens.get('else')[0])

        return cls(rules)

    def accept(self, visitor):
        visitor.visit(self)

        for r in self.rules:
            r.accept(visitor)

    def __repr__(self):
        return '<CaseExpression rules={}>'.format(self.rules)


class AliasedExpression(ASTBase):
    """Expression with an alias"""
    def __init__(self, expression, alias):
        self.expression = expression
        self.alias = alias

    def __repr__(self):
        return '<AliasedExpression expression={} alias=\'{}\'>'.format(self.expression, self.alias)

    @classmethod
    def parse(cls, tokens):
        if 'expression' not in tokens and 'field' not in tokens:
            raise TokenException('malformed AliasedExpression (no expression or field)')

        if 'alias' not in tokens and 'field' not in tokens:  # fields don't need an alias
            raise TokenException('malformed AliasedExpression (no alias)')

        if 'field' in tokens:
            expression = tokens.get('field')

            assert isinstance(expression, Field)

            alias = tokens.get('alias', expression.name)
        else:
            expression = tokens.get('expression')

            if not isinstance(expression, Expression):
                raise TokenException('expected Expression, got {}'.format(type(expression)))

            alias = tokens.get('alias')

        return cls(expression, alias)

    def accept(self, visitor):
        visitor.visit(self)

        self.expression.accept(visitor)


class Function(Expression):
    """Function call. These may be nested."""
    def __init__(self, name, args):
        """
        :type name: unicode
        :type args: list
        """
        self.name = name
        self.args = args

    @classmethod
    def parse(cls, tokens):
        if 'name' not in tokens:
            raise TokenException('malformed Function (no name)')

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


class DataSource(ASTBase):
    """Reference to a data source (dataframe)"""
    def __init__(self, name, alias=None):
        """
        :type name: unicode
        :type alias: unicode
        """
        self.name = name
        self.alias = alias or name

    @classmethod
    def parse(cls, tokens):
        if len(tokens) < 1:
            raise TokenException()

        name = tokens.get('name')
        alias = tokens.get('alias', None)

        return cls(name, alias)

    def __repr__(self):
        return '<DataSource name=\'{}\' alias=\'{}\'>'.format(self.name, self.alias)


class JoinCondition(ASTBase):
    """Single join condition."""
    def __init__(self, left, right):
        """
        :type left: hub.odhql.ast.Field
        :type right: hub.odhql.ast.Field
        """
        self.left = left
        self.right = right

    @classmethod
    def parse(cls, tokens):
        if 'left' not in tokens or 'right' not in tokens:
            raise TokenException('invalid join condition')

        left = tokens.get('left')
        right = tokens.get('right')

        if not isinstance(left, Field) or not isinstance(right, Field):
            raise TokenException('expected field = field, got {} = {}'.format(type(left), type(right)))

        return cls(left, right)

    def __repr__(self):
        return '<JoinCondition left={} right={}>'.format(self.left, self.right)

    def accept(self, visitor):
        visitor.visit(self)

        self.left.accept(visitor)
        self.right.accept(visitor)


class JoinConditionList(ASTBase, Sequence):
    """List of join conditions. All of these must match for a join - 'or' is not supported."""
    def __init__(self, conditions):
        """
        :param conditions: list of hub.odhql.ast.JoinCondition
        """
        self.conditions = conditions

    def __len__(self):
        return len(self.conditions)

    def __getitem__(self, index):
        return self.conditions[index]

    @classmethod
    def parse(cls, tokens):
        if len(tokens) == 0:
            raise TokenException()

        conditions = list(tokens.get('conditions'))
        return cls(conditions)

    def __repr__(self):
        return '<JoinConditionList conditions={}>'.format(self.conditions)

    def accept(self, visitor):
        visitor.visit(self)

        for cond in self.conditions:
            cond.accept(visitor)


class JoinedDataSource(DataSource):
    """Data source added via join. All data source after the first are of this type."""
    class JoinType(Enum):
        """Join type."""
        inner = 1
        left = 2
        right = 3
        outer = 4

    def __init__(self, name, alias, join_type, condition):
        """

        :param name: Data source name
        :param alias: Alias (may be identical to the name)
        :param join_type: Join type.
        :param condition: hub.odhql.ast.JoinCondition
        """
        super(JoinedDataSource, self).__init__(name, alias)

        self.join_type = join_type
        self.condition = condition

    @classmethod
    def parse(cls, tokens):
        if 'datasource' not in tokens:
            raise TokenException('join without datasource')
        if 'condition' not in tokens:
            raise TokenException('join without conditions')

        datasource = tokens.get('datasource')
        join_type = tokens.get('join_type')
        condition = tokens.get('condition')

        return cls(datasource.name, datasource.alias, join_type, condition)

    @classmethod
    def parse_join_type(cls, tokens):
        lower_tokens = [token.lower() for token in tokens if isinstance(token, basestring)]
        if 'left' in lower_tokens:
            return cls.JoinType.left
        elif 'right' in lower_tokens:
            return cls.JoinType.right
        elif 'full' in lower_tokens or 'outer' in lower_tokens:
            return cls.JoinType.outer
        return cls.JoinType.inner

    def __repr__(self):
        return '<JoinedDataSource name=\'{}\' alias=\'{}\' condition={}>'.format(self.name, self.alias, self.condition)

    def accept(self, visitor):
        visitor.visit(self)

        self.condition.accept(visitor)


class BinaryCondition(ASTBase):
    """Condition with two sides (thus binary)"""
    class Operator(Enum):
        """Operators for binary conditions."""
        equals = 1
        not_equals = 2
        less = 3
        less_or_equal = 4
        greater = 5
        greater_or_equal = 6
        like = 7
        not_like = 8

    def __init__(self, left, operator, right):
        """
        :type left: hub.odhql.ast.Expression
        :type operator: hub.odhql.ast.Operator
        :type right: hub.odhql.ast.Expression
        """
        self.left = left
        self.operator = operator
        self.right = right

    @classmethod
    def parse(cls, tokens):
        if 'left' not in tokens:
            raise TokenException('malformed BinaryCondition (no left side)')

        if 'right' not in tokens:
            raise TokenException('malformed BinaryCondition (no right side)')

        if 'operator' not in tokens:
            raise TokenException('malformed BinaryCondition (no operator)')

        left = tokens.get('left')
        right = tokens.get('right')
        op = tokens.get('operator')

        return cls(left, op, right)

    @classmethod
    def parse_operator(cls, tokens):
        if len(tokens) < 1:
            raise TokenException('malformed operator (no operator)')

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
        if str(op).lower() == 'not' and str(tokens[1]).lower() == 'like':
            return cls.Operator.not_like

        raise TokenException('unregistered operation: {}'.format(op))

    def __repr__(self):
        return '<BinaryCondition left={} op={} right={}>'.format(self.left, self.operator, self.right)

    def accept(self, visitor):
        visitor.visit(self)

        self.left.accept(visitor)
        self.right.accept(visitor)


class InCondition(ASTBase):
    """'<left> [not] in <list>' condition."""
    def __init__(self, left, in_list, invert):
        """
        :param left: hub.odhql.ast.Expression
        :param in_list: list of hub.odhql.ast.Expression
        :param invert: bool
        """
        self.left = left
        self.in_list = in_list
        self.invert = invert

    @classmethod
    def parse(cls, tokens):
        if 'left' not in tokens:
            raise TokenException('malformed InCondition (no left side)')

        if 'in_list' not in tokens:
            raise TokenException('malformed InCondition (no in_list)')

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
    """'<field> is [not] null' condition."""
    def __init__(self, field, invert):
        """
        :param field: hub.odhql.ast.Field
        :param invert: bool
        """
        self.field = field
        self.invert = invert

    @classmethod
    def parse(cls, tokens):
        if 'field' not in tokens:
            raise TokenException('malformed IsNullCondition')

        field = tokens.get('field')
        invert = 'invert' in tokens

        if not isinstance(field, Field):
            raise TokenException('expected Field, got {}'.format(type(field)))

        return cls(field, invert)

    def accept(self, visitor):
        visitor.visit(self)

        self.field.accept(visitor)

    def __repr__(self):
        return '<IsNullCondition field={} invert={}>'.format(self.field, self.invert)


class PredicateCondition(ASTBase):
    """'[not] <predicate()>' condition."""
    def __init__(self, predicate, invert):
        """
        :type predicate: hub.odhql.ast.Function
        :type invert: bool
        """
        self.predicate = predicate
        self.invert = invert

    @classmethod
    def parse(cls, tokens):
        if 'predicate' not in tokens:
            raise TokenException('malformed PredicateCondition (no predicate)')

        invert = 'invert' in tokens
        predicate = tokens.get('predicate')

        return cls(predicate, invert)

    def accept(self, visitor):
        visitor.visit(self)

        self.predicate.accept(visitor)

    def __repr__(self):
        return '<PredicateCondition predicate={}>'.format(self.predicate)


class FilterListBase(ASTBase, Sequence):
    """Base class for lists of filter conditions."""
    def __init__(self, conditions):
        """
        :type conditions: list
        """
        self.conditions = conditions

    @classmethod
    def parse(cls, tokens):
        if len(tokens) < 1:
            raise TokenException('malformed {} (no conditions)'.format(cls.__name__))

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
    """Order by index in the field list."""
    def __init__(self, position):
        """
        :type position: int > 1
        """
        self.position = position

    @classmethod
    def parse(cls, tokens):
        if len(tokens) < 1:
            raise TokenException('malformed OrderByPosition (no position)')

        try:
            position = int(tokens[0])

            if position < 1:
                raise TokenException('invalid OrderByPosition: Needs to be at least 1')

            return cls(position)
        except ValueError:
            pass

    def __repr__(self):
        return '<OrderByPosition position={}>'.format(self.position)


class OrderByAlias(ASTBase):
    """Order by alias (alias == field name if no alias was specified)."""
    def __init__(self, alias):
        self.alias = alias

    @classmethod
    def parse(cls, tokens):
        if len(tokens) < 1:
            raise TokenException('malformed OrderByAlias (no alias)')

        return cls(tokens[0])

    def __repr__(self):
        return '<OrderByAlias alias={}>'.format(self.alias)


class OrderBy(ASTBase):
    """Order by expression."""
    class Direction(Enum):
        ascending = 1
        descending = 2

    def __init__(self, field, direction):
        """
        :type field: hub.odhql.ast.OrderByPosition, hub.odhql.ast.OrderByAlias or hub.odhql.ast.Field
        :type direction: hub.odhql.ast.Direction
        """
        self.field = field
        self.direction = direction

    @classmethod
    def parse(cls, tokens):
        if 'field' not in tokens:
            raise TokenException('malformed OrderByField (no field)')

        field = tokens.get('field')
        direction = str(tokens.get('direction', 'asc')).lower()

        if direction == 'desc':
            direction = OrderBy.Direction.descending
        else:
            direction = OrderBy.Direction.ascending

        return cls(field, direction)

    def __repr__(self):
        return '<OrderBy field={} direction={}>'.format(self.field, self.direction)
