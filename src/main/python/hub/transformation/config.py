from pyparsing import alphas, nums
from pyparsing import Word, CaselessKeyword, QuotedString
from pyparsing import Optional, ZeroOrMore, OneOrMore, Or, Suppress, Group

from pyparsing import delimitedList, unicodeString


class OQLParser(object):
    def __init__(self):
        self.grammar = self.build_grammar()

    @classmethod
    def build_grammar(cls):
        identifier = Word(alphas) ^ QuotedString('"')

        field = identifier('name')
        value = unicodeString ^ Word(nums)

        field_or_value = field ^ value("value")
        field_mapping = Or([
            Group(field),
            Group(field_or_value + Suppress(CaselessKeyword('as')) + identifier("alias"))
        ])
        field_declaration = Suppress(CaselessKeyword('select')) + delimitedList(field_mapping)

        and_or = (CaselessKeyword('and') ^ CaselessKeyword('or'))

        data_source = Group(identifier('name'))

        join_single_condition = field + '=' + field
        join_multi_condition = '(' + join_single_condition + OneOrMore(and_or + join_single_condition) + ')'
        join_condition_list = join_single_condition ^ join_multi_condition

        join = Group(Suppress(CaselessKeyword('join')) + data_source + Optional(
            Suppress(CaselessKeyword('as')) + identifier("alias")) + Suppress(CaselessKeyword(
            'on')) + join_condition_list)

        data_source_declaration = Suppress(CaselessKeyword('from')) + data_source + ZeroOrMore(join)("join")

        filter = Or([field + '=' + value,
                     field + CaselessKeyword('in') + '(' + value + ')',
                     field + CaselessKeyword('is') + CaselessKeyword('null')])

        filter_declaration = Optional(CaselessKeyword('where') + delimitedList(filter, and_or))

        order_by_field = field + Optional(Or([CaselessKeyword('asc'), CaselessKeyword('desc')]))
        order_by_declaration = Optional(CaselessKeyword('order by') + delimitedList(order_by_field))

        return field_declaration('fields') + data_source_declaration(
            'datasources') + filter_declaration + order_by_declaration

    def parse(self, input):
        return self.grammar.parseString(input)