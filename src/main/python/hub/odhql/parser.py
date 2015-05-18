# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyparsing import nums
from pyparsing import Word, CaselessKeyword as CK, QuotedString, Regex, Literal, Suppress, Combine
from pyparsing import Optional, OneOrMore, ZeroOrMore, Or, Group, NotAny, Forward, StringEnd
from pyparsing import delimitedList

from hub.odhql.ast import LiteralExpression, Field, CaseRule, CaseExpression, AliasedExpression, Function
from hub.odhql.ast import BinaryCondition, InCondition, IsNullCondition, PredicateCondition, FilterCombination
from hub.odhql.ast import FilterAlternative, DataSource, JoinCondition, JoinConditionList, JoinedDataSource
from hub.odhql.ast import OrderByPosition, OrderByAlias, OrderBy, Query, Union
from opendatahub.utils.doc import DocMixin


class OdhQLParser(DocMixin):
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
    JoinDefinition ::= ("left" | "right" | "full" )? "join" DataSourceName ( "as"? Alias )? "on" JoinCondition
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

    Was ist ODHQL?
    ==============

    ODHQL ist eine an SQL angelehnte Abfrage- und Transformations-Sprache für OpenDataHub.

    Syntax
    ======

    Bestandteile einer Abfrage
    --------------------------

    Eine Abfrage besteht aus folgenden Teilen:

    * Eine Liste von Feldern oder Ausdrücken, welche im Resultat erscheinen sollen

    * Eine Liste von Datenquellen

    * Optional eine Liste von Filter-Ausdrücken

    * Optional eine Sortier-Klausel

    Gross- und Kleinschreibung wird nicht beachtet.

    Mehrere Abfragen können kombiniert werden mithilfe von Union. In diesem Fall ist nur eine Sortier-Klausel am Ende
    der kombinierten Abfrage erlaubt.

    Beispiel:

    .. code:: sql

        SELECT NULL AS userid,                                                               -- Null-Ausdruck
               SUBSTRING(NVL(EXTRACT(t.text, '\|([^|\.]+)'), 'no value'), 1, 100) AS title,  -- Funktions-Aufruf
               EXTRACT(t.text, '\|([^|]+)') AS description,
               CAST(CAST(t."df", 'bigint'), 'datetime') AS trob_start,
               CAST(CAST(t."dd", 'bigint'), 'datetime') AS trob_end,
               NULL AS trob_interval,
               'both' AS direction,                                                          -- String-Ausdruck
               NULL AS diversion_advice,
               CASE WHEN t.p = 'Switzerland' THEN 'CH'                                       -- Case-Ausdruck
                    WHEN t.p = 'France' THEN 'FR'
                    WHEN t.p = 'Austria' THEN 'AT'
               END AS country,
               t.text AS reason,                                                             -- Feld
               EXTRACT(t.text, '\|([^|,]+)') AS object_name,
               'street' AS object_type,
               CASE WHEN CONTAINS(t.text, 'closed', FALSE) THEN 'closed'
                    WHEN (CONTAINS(t.text, 'maintenance', FALSE) OR CONTAINS(t.text, 'maintenance', FALSE))
                        THEN 'obstructed'
                    ELSE 'other'
               END AS trob_type,
               ST_SETSRID(ST_GEOMFROMTEXT(CONCAT('POINT(', t.x, ' ', t.y, ')')), 3395) AS trobdb_point
          FROM ODH11 AS t                                                                    -- Datenquelle
         ORDER BY 4

    Felder und Ausdrücke
    --------------------

    In der Feld-Liste sind folgende Ausdrücke erlaubt:
        Feld
            Bezieht sich direkt auf ein Feld einer Datenquelle. Der Name des Feldes muss mit dem Namen oder Alias
            der Datenquelle prefixed werden. Optional kann ein Alias angegeben werden.
            Beispiel:

            .. code:: sql

                prefix.feld AS alias
        Wert
            Ganzzahl (Integer), Fliesskommazahl (Float, Trennzeichen ist ein Punkt), Zeichenkette (String, in einfachen
            Anführungszeichen), Boolean (true, false) oder Null. Es muss ein Alias angegeben werden.

            Einfache Anführungszeichen können innerhalb eines Strings mit "\\'" erzeugt werden, Backslashes ("\\") mit
            "\\\\".
        Funktion
            Besteht aus einem Namen und einer Liste von Argumenten. Es muss zwingend ein Alias angegeben werden.
            Beispiel:

            .. code:: sql

                SUBSTRING(NVL(EXTRACT(t.text, '\|([^|\.]+)'), 'no value'), 1, 100) AS title

        Fallunterscheidung (Case-Ausdruck)
            Kann verwendet werden, um Werte zu übersetzen. Es muss mindestens eine Bedingung angegeben werden.
            Das Format ist 'when <Bedingung> then <Ausdruck>', wobei alle unten beschriebenen Bedingungs-Arten sowie
            hier beschriebenen Ausdrücke erlaubt sind.
            Beispiel:

            .. code:: sql

                CASE WHEN CONTAINS(t.text, 'closed', FALSE) THEN 'closed'
                     WHEN (CONTAINS(t.text, 'maintenance', FALSE) OR CONTAINS(t.text, 'maintenance', FALSE))
                        THEN 'obstructed'
                     ELSE 'other'
                END

    Datenquellen
    ------------

    Es muss mindestens eine Datenquelle angegeben werden. Falls mehrere Datenquellen verwendet werden sollen, muss eine
    Verknüpfungsbedingung angegeben werden.

    Unterstützt werden folgende Join-Typen:
        Inner
            Standard. Verlangt, dass beide Seiten vorhanden sind

            .. code:: sql

                FROM ODH12 AS employees
                JOIN ODH13 AS employers ON employees.employer_id = employers.id
        Left
            Verwendet die Schlüssel der linken Seite für den Vergleich (rechte Seite kann null sein)

            .. code:: sql

                FROM ODH12 AS employees
                LEFT JOIN ODH13 AS employers ON employees.employer_id = employers.id
        Right
            Verwendet die Schlüssel der rechten Seite für den Vergleich (linke Seite kann null sein)

            .. code:: sql

                FROM ODH12 AS employees
                RIGHT JOIN ODH13 AS employers ON employees.employer_id = employers.id
        FULL
            Verwendet die Vereinigungsmenge der Schlüssel der beiden Seiten für den Vergleich (beide Seiten sind
            optional, es kann jedoch pro Zeile nur eine Seite null sein).

            .. code:: sql

                FROM ODH12 AS employees
                FULL JOIN ODH13 AS employers ON employees.employer_id = employers.id

    Filter
    ------

    Folgende Filter-Ausdrücke sind möglich:
        `is null`, `is not null`
            Prüft ob ein Feld (nicht) null ist
        `in`, `not in`
            Prüft ob ein Ausdruck (nicht) in einer Liste enthalten ist.
            Beispiel:

            .. code:: sql

                country IN ('CH', 'DE', 'AT')

        <, >, <=, >=, =, !=
            Vergleicht zwei Ausdrücke miteinander.
        `like`, `not like`
            Prüft ob ein Ausdruck einem Muster entspricht. Verwendet wird dazu ein Regulärer Ausdruck mit
            `Python Syntax <https://docs.python.org/2/library/re.html#regular-expression-syntax>`_.
        Prädikat
            Eine Funktion, welche ein boolsches Resultat liefert kann direkt als Bedingung verwendet werden.

    Mehrere Bedingungen können mit 'and' und 'or' verknüpft und mit runden Klammern gruppiert werden.

    Beispiel:

    .. code:: sql

        WHERE t.a IS NOT NULL
          AND (t.b IN (1, 2, 3) OR t.b > 20)

    Sortier-Klausel
    ---------------

    Es kann sortiert werden nach Feld-Name, Alias oder Position in der Feld-Liste.

    Beispiel:

    .. code:: sql

        ORDER BY 1, ODH4.name DESC, surname ASC

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

        expression <<= (literal_expression | case_expression | field | function)

        aliased_expression = (field('field') + Optional(alias)) | (expression('expression') + alias)
        aliased_expression.setParseAction(AliasedExpression.parse)

        function <<= (identifier('name') + '(' + Optional(delimitedList(field | expression | function))('args') + ')')
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

        single_filter <<= (null_condition | binary_condition | in_condition | predicate_condition |
                          Suppress('(') + filter_alternative + Suppress(')'))

        # 'as' is optional here in sql - let's do that too
        data_source_alias_blacklist = NotAny(
            CK('join') | CK('left') | CK('right') | CK('full') | CK('inner') | CK('outer') | CK(
                'on') | CK('where') | CK('union') | CK('order'))
        data_source = (identifier('name') + Optional(data_source_alias_blacklist + Optional(CK('as')) +
                                                     identifier('alias')))
        data_source.setParseAction(DataSource.parse)

        join_single_condition = field('left') + '=' + field('right')
        join_single_condition.setParseAction(JoinCondition.parse)

        join_multi_condition = (Optional(Literal('(')) +
                                delimitedList(join_single_condition, delim=kw_and)('conditions') + Optional(')'))
        join_multi_condition.setParseAction(JoinConditionList.parse)

        join_condition_list = join_single_condition | join_multi_condition

        join_type = Optional(CK('left') | CK('right') | CK('full')) + CK('join')
        join_type.setParseAction(JoinedDataSource.parse_join_type)

        join = (join_type('join_type') + data_source.copy()('datasource') + CK('on') +
                join_condition_list.copy()('condition'))
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
        return '\n'.join([self._strip_line_comment(l) for l in query.splitlines()])

    def parse(self, query):
        return self.build_grammar().parseString(self.strip_comments(query))[0]
