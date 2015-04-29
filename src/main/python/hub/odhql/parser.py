# encoding: utf-8
from collections import Sequence

from pyparsing import nums
from pyparsing import Word, CaselessKeyword as CK, QuotedString, Regex, Literal, Suppress, Combine
from pyparsing import Optional, OneOrMore, ZeroOrMore, Or, Group, NotAny, Forward, StringEnd
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

    FieldDeclarationList ::= "select" FieldDeclaration ( "," FieldDeclaration )*
    FieldDeclaration ::= FieldEquiv "as" Alias

    CaseExpression ::= "case" ( "when" Condition "then" Expression )+  ( "else" Expression )? "end"

    Expression ::= Function | LiteralExpression | Field | CaseExpression

    Function ::= Identifier "(" ( FunctionArgumentList )? ")"
    FunctionArgumentList ::= Expression ( ( "," Expression )* )?

    DataSourceName ::= Identifier
    FieldName ::= Identifier
    Alias ::= Identifier

    Field ::= DataSourceNameOrAlias "." FieldName

    DataSourceNameOrAlias ::= DataSourceName | Alias

    DataSourceSelection ::= "from" DataSourceName ( "as"? Alias )? ( JoinDefinition )*
    JoinDefinition ::= "join" DataSourceName ( "as"? Alias )? "on" JoinCondition
    JoinCondition ::= SingleJoinCondition | "(" SingleJoinCondition ( "and" SingleJoinCondition )* ")"
    SingleJoinCondition ::= Field "=" Field

    FilterList ::= "where" FilterAlternative
    FilterAlternative ::= FilterCombination ( "or" FilterCombination )*
    FilterCombination ::= Condition ( "and" Condition )*

    Condition ::= BinaryCondition | InCondition | IsNullCondition | PredicateCondition | "(" FilterAlternative ")"

    BinaryCondition ::= Expression BinaryOperator Expression
    BinaryOperator ::= "=" | "!=" | "<=" | "<"| ">=" | ">" | ( "not" )? "like"
    InCondition ::= Expression ( "not" )? "in" "(" Expression ( "," Expression )* ")"
    IsNullCondition ::= Field "is" ( "not" )? Null
    PredicateCondition ::= ( "not" )? Function

    OrderByList ::= "order" "by" OrderByField ( "," OrderByField )*
    OrderByField ::= ( Field | Alias | Position) ( "asc" | "desc" )?
    Integer ::= ( "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" )+

    LiteralExpression ::= SingleQuotedString | Number | Boolean | Null
    Number ::= Integer | Float
    Float ::= Integer "." Integer
    Boolean ::= "true" | "false"
    Null ::= "null"
    SingleQuotedString ::= "string in single quotes"
    DoubleQuotedString ::= "string in double quotes"

    Identifier ::= ( "a..z" | "A..Z" | "_" ) ( "a..z" | "A..Z" | "_" | Integer )* | DoubleQuotedString
    ---------------------------------------------------------------------------
    """

    UI_HELP = """
    .. class:: language

    Hilfe zu ODHQL
    ==============

    ODHQL ist eine an SQL angelehnte Abfrage- und Transformations-Sprache für OpenDataHub.

    Bestandteile einer Abfrage
    --------------------------

    Eine Abfrage besteht aus folgenden Teilen:
    - Eine Liste von Feldern oder Ausdrücken, welche im Resultat erscheinen sollen
    - Eine Liste von Datenquellen
    - Optional eine Liste von Filter-Ausdrücken
    - Optional eine Sortier-Klausel

    Gross- und Kleinschreibung wird nicht beachtet.

    Mehrere Abfragen können kombiniert werden mithilfe von Union. In diesem Fall ist nur eine Sortier-Klausel am Ende
    der kombinierten Abfrage erlaubt.

    Beispiel:

    .. code:: sql

        select null as userid,                                                               -- Null-Ausdruck
               substring(nvl(extract(t.text, '\|([^|\.]+)'), 'no value'), 0, 100) as title,  -- Funktions-Aufruf
               extract(t.text, '\|([^|]+)') as description,
               cast(cast(t."df", 'bigint'), 'datetime') as trob_start,
               cast(cast(t."dd", 'bigint'), 'datetime') as trob_end,
               null as trob_interval,
               'both' as direction,                                                          -- String-Ausdruck
               null as diversion_advice,
               case when t.p = 'Switzerland' then 'CH'                                       -- Case-Ausdruck
                    when t.p = 'France' then 'FR'
                    when t.p = 'Austria' then 'AT'
               end as country,
               t.text as reason,                                                             -- Feld
               extract(t.text, '\|([^|,]+)') as object_name,
               'street' as object_type,
               case when contains(t.text, 'closed', false) then 'closed'
                    when (contains(t.text, 'maintenance', false) or contains(t.text, 'maintenance', false))
                        then 'obstructed'
                    else 'other'
               end as trob_type,
               st_setsrid(st_geomfromtext(concat('POINT(', t.x, ' ', t.y, ')')), 3395) as trobdb_point
          from ODH11 as t                                                                    -- Datenquelle
         order by 4

    Felder und Ausdrücke
    --------------------

    In der Feld-Liste sind folgende Ausdrücke erlaubt:
        Feld
            Bezieht sich direkt auf ein Feld einer Datenquelle. Der Name des Feldes muss mit dem Namen oder Alias
            der Datenquelle prefixed werden. Optional kann ein Alias angegeben werden.
            Beispiel:

            .. code:: sql

                prefix.feld as alias
        Wert
            Ganzzahl (Integer), Fliesskommazahl (Float, Trennzeichen ist ein Punkt), Zeichenkette (String, in einfachen
            Anführungszeichen), Boolean (true, false) oder Null. Es muss ein Alias angegeben werden.

            Einfache Anführungszeichen können innerhalb eines Strings mit "\\'" erzeugt werden, Backslashes ("\\") mit
            "\\\\".
        Funktion
            Besteht aus einem Namen und einer Liste von Argumenten. Es muss zwingend ein Alias angegeben werden.
            Beispiel:

            .. code:: sql

                substring(nvl(extract(t.text, '\|([^|\.]+)'), 'no value'), 0, 100) as title

        Fallunterscheidung (Case-Ausdruck)
            Kann verwendet werden, um Werte zu übersetzen. Es muss mindestens eine Bedingung angegeben werden.
            Das Format ist 'when <Bedingung> then <Ausdruck>', wobei alle unten beschriebenen Bedingungs-Arten sowie
            hier beschriebenen Ausdrücke erlaubt sind.
            Beispiel:

            .. code:: sql

                case when contains(t.text, 'closed', false) then 'closed'
                     when (contains(t.text, 'maintenance', false) or contains(t.text, 'maintenance', false))
                        then 'obstructed'
                     else 'other'
                end as trob_type

    Datenquellen
    ------------

    Es muss mindestens eine Datenquelle angegeben werden. Falls mehrere Datenquellen verwendet werden sollen, muss eine
    Verknüpfungsbedingung angegeben werden.

    Beispiel:

    .. code:: sql

        from ODH12 as employees
        join ODH13 as employers on employees.employer_id = employers.id

    Filter
    ------

    Folgende Filter-Ausdrücke sind möglich:
        is null, is not null
            Prüft ob ein Feld (nicht) null ist
        in, not in
            Prüft ob ein Ausdruck (nicht) in einer Liste enthalten ist.
            Beispiel:

            .. code:: sql

                country in ('CH', 'DE', 'AT')

        <, >, <=, >=, =, !=
            Vergleicht zwei Ausdrücke miteinander.
        like, not like
            Prüft ob ein Ausdruck einem Muster entspricht. Verwendet wird dazu ein Regulärer Ausdruck mit
            `Python Syntax <https://docs.python.org/2/library/re.html#regular-expression-syntax>`_.
        Prädikat
            Eine Funktion, welche ein boolsches Resultat liefert kann direkt als Bedingung verwendet werden.

    Mehrere Bedingungen können mit 'and' und 'or' verknüpft und mit runden Klammern gruppiert werden.

    Beispiel:

    .. code:: sql

        where t.a is not null
          and (t.b in (1, 2, 3) or t.b > 20)

    Sortier-Klausel
    ---------------

    Es kann sortiert werden nach Feld-Name, Alias oder Position in der Feld-Liste.

    Beispiel:

    .. code:: sql

        order by 1, 2 desc

    Union
    -----

    Die Resultate mehrerer Abfragen können mithilfe von Union kombiniert werden. Zu beachten sind folgende Punkte:
    - Union verhält sich wie UNION ALL in SQL, d.h. es wird keine Deduplizierung der Einträge vorgenommen
    - Die einzelnen Abfragen müssen kompatible Feldlisten liefern, d.h. gleiche Feld-Zahl und Feld-Typen.

    Als Feld-Namen werden im Resultat die Feld-Namen der ersten Abfrage verwendet.
    """

    grammar = None

    @classmethod
    def build_grammar(cls):
        if cls.grammar:
            return cls.grammar

        escape_char = '\\'
        identifier = Regex(r'[a-zA-Z_][a-zA-Z0-9_]*') | QuotedString('"', escChar=escape_char)
        kw_and = CK('and')
        kw_or = CK('or')

        alias = CK('as') + identifier('alias')

        field = (identifier('prefix') + '.' + identifier('name') + NotAny('('))('field')
        field.setParseAction(Field.parse)

        integer_value = Combine(Optional('-') + Word(nums))
        number_value = Group(integer_value + Optional('.' + Word(nums)))
        number_value.setParseAction(LiteralExpression.parse_number)

        boolean_value = CK('true') | CK('false')
        boolean_value.setParseAction(LiteralExpression.parse_boolean)

        string_value = QuotedString('\'', escChar=escape_char)
        null_value = CK('null')
        null_value.setParseAction(LiteralExpression.parse_null)

        single_filter = Forward()

        expression = Forward()

        when_expression = (CK('when') + single_filter('condition') + CK('then') + expression('expression'))
        when_expression.setParseAction(CaseRule.parse_when)
        else_expression = CK('else') + expression('expression')
        else_expression.setParseAction(CaseRule.parse_else)
        case_expression = ((CK('case') + Group(OneOrMore(when_expression))('when') + Optional(else_expression)('else'))
                           + CK('end'))
        case_expression.setParseAction(CaseExpression.parse)

        literal_expression = (number_value | boolean_value | string_value | null_value)('value')
        literal_expression.setParseAction(LiteralExpression.parse)

        function = Forward()

        expression << (literal_expression | case_expression | field | function)

        aliased_expression = (field('field') + Optional(alias)) | (expression('expression') + alias)
        aliased_expression.setParseAction(AliasedExpression.parse)

        function << (identifier('name') + '(' + Optional(delimitedList(field | expression | function))('args') + ')')
        function.setParseAction(Function.parse)

        operator = (Literal('=') | '!=' | '<=' | '<' | '>=' | '>' | Optional(CK('not'))('invert') + CK('like'))
        operator.setParseAction(BinaryCondition.parse_operator)

        binary_condition = expression.copy()('left') + operator('operator') + expression.copy()('right')
        binary_condition.setParseAction(BinaryCondition.parse)

        in_condition = (expression.copy()('left') + Optional(CK('not'))('invert') + CK('in') + '(' +
                        Group(delimitedList(expression))('in_list') + ')')
        in_condition.setParseAction(InCondition.parse)

        null_condition = (field + CK('is') + Optional(CK('not'))('invert') + CK('null'))
        null_condition.setParseAction(IsNullCondition.parse)

        predicate_condition = Optional(CK('not'))('invert') + function('predicate')
        predicate_condition.setParseAction(PredicateCondition.parse)

        filter_combination = delimitedList(single_filter, delim=kw_and)
        filter_combination.setParseAction(FilterCombination.parse)

        filter_alternative = delimitedList(filter_combination, delim=kw_or)
        filter_alternative.setParseAction(FilterAlternative.parse)

        single_filter << (null_condition | binary_condition | in_condition | predicate_condition |
                          Suppress('(') + filter_alternative + Suppress(')'))

        # 'as' is optional here in sql - let's do that too
        data_source = (identifier('name') +
                       Optional(NotAny(CK('join') | CK('on') | CK('where') | CK('union') | CK('order')) +
                                Optional(CK('as')) + identifier('alias')))
        data_source.setParseAction(DataSource.parse)

        join_single_condition = field('left') + '=' + field('right')
        join_single_condition.setParseAction(JoinCondition.parse)

        join_multi_condition = (Optional(Literal('(')) +
                                delimitedList(join_single_condition, delim=kw_and)('conditions') + Optional(')'))
        join_multi_condition.setParseAction(JoinConditionList.parse)

        join_condition_list = join_single_condition | join_multi_condition

        join = (CK('join') + data_source.copy()('datasource') +
                CK('on') + join_condition_list.copy()('condition'))
        join.setParseAction(JoinedDataSource.parse)

        order_by_position = Word(nums)
        order_by_position.setParseAction(OrderByPosition.parse)

        order_by_alias = identifier.copy()
        order_by_alias.setParseAction(OrderByAlias.parse)

        order_by_field_equiv = field | order_by_alias | order_by_position
        order_by_field = (order_by_field_equiv('field') + Optional(Or([CK('asc'), CK('desc')]))('direction'))
        order_by_field.setParseAction(OrderBy.parse)

        field_declaration_list = Suppress(CK('select')) + delimitedList(aliased_expression)
        data_source_declaration = Suppress(CK('from')) + data_source + ZeroOrMore(join)
        filter_declaration = Suppress(CK('where')) + filter_alternative.copy()('conditions')
        order_by_declaration = (Suppress(CK('order') + CK('by')) + delimitedList(order_by_field, delim=',')('fields'))
        order_by_declaration.setParseAction(Query.parse_order_by)

        query = (field_declaration_list('fields') + data_source_declaration('datasources') +
                 Optional(filter_declaration('filter')))
        query.setParseAction(Query.parse)

        union_query = (delimitedList(query, delim=CK('union'))('queries') + Optional(order_by_declaration)('sort') +
                       StringEnd())
        union_query.setParseAction(Union.parse)

        cls.grammar = union_query

        return cls.grammar

    @staticmethod
    def _strip_line_comment(line):
        comment_chars = '--'
        comment_start = line.find(comment_chars)
        if comment_start >= 0:
            # ignore comments inside strings
            while (comment_start < len(line)
                   and (line.count('\'', 0, comment_start) % 2 == 1 or line.count('"', 0, comment_start) % 2 == 1)):
                comment_start = line.find(comment_chars, comment_start + 1)

            return line[0:comment_start]
        return line

    def strip_comments(self, query):
        return '\n'.join(map(self._strip_line_comment, query.splitlines()))

    def parse(self, query):
        return self.build_grammar().parseString(self.strip_comments(query))[0]


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
    def __init__(self, fields, data_sources, filter_definitions):
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
    pass


class Field(Expression):
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
    def __init__(self, condition, expression):
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
    def __init__(self, name, args):
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
    def __init__(self, name, alias=None):
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
    def __init__(self, left, right):
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
    def __init__(self, conditions):
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
    def __init__(self, name, alias, condition):
        super(JoinedDataSource, self).__init__(name, alias)

        self.condition = condition

    @classmethod
    def parse(cls, tokens):
        if 'datasource' not in tokens:
            raise TokenException('join without datasource')
        if 'condition' not in tokens:
            raise TokenException('join without conditions')

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
        not_like = 8

    def __init__(self, left, operator, right):
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

        v = FindClassVisitor(Field)
        left.accept(v)
        if not v.found:
            right.accept(v)
            if not v.found:
                raise TokenException('illegal BinaryCondition: at least one side needs to reference a Field')

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
    def __init__(self, left, in_list, invert):
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
    def __init__(self, field, invert):
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
    def __init__(self, predicate, invert):
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
    def __init__(self, conditions):
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
    def __init__(self, position):
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
    class Direction(Enum):
        ascending = 1
        descending = 2

    def __init__(self, field, direction):
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


class FindClassVisitor(object):
    def __init__(self, target_class):
        self.target = target_class
        self.found = False

    def visit(self, obj):
        if isinstance(obj, self.target):
            self.found = True


class TokenException(Exception):
    def __init__(self, message='parse error'):
        super(TokenException, self).__init__(message)
