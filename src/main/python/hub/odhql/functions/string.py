"""
OdhQL string functions
"""

from hub.odhql.functions.core import VectorizedFunction, OdhQLExecutionException


class Concat(VectorizedFunction):
    name = 'CONCAT'

    def apply(self, a, b, *args):
        args = [self.expand(arg) for arg in [a, b] + list(args)]
        for arg in args:
            self.assert_str('string', arg[0])
        return args[0].str.cat(args[1:])


class Trim(VectorizedFunction):
    name = 'TRIM'

    def apply(self, strings):
        self.assert_str('string', strings[0])
        return strings.str.strip()


class RTrim(VectorizedFunction):
    name = 'RTRIM'

    def apply(self, strings):
        self.assert_str('string', strings[0])
        return strings.str.rstrip()


class LTrim(VectorizedFunction):
    name = 'LTRIM'

    def apply(self, strings):
        self.assert_str('string', strings[0])
        return strings.str.lstrip()


class Upper(VectorizedFunction):
    name = 'UPPER'

    def apply(self, strings):
        self.assert_str('string', strings[0])
        return strings.str.upper()


class Lower(VectorizedFunction):
    name = 'LOWER'

    def apply(self, strings):
        self.assert_str('string', strings[0])
        return strings.str.lower()


class Length(VectorizedFunction):
    name = 'LEN'

    def apply(self, strings):
        self.assert_str('string', strings[0])
        return strings.str.len()


class Extract(VectorizedFunction):
    name = 'EXTRACT'

    def apply(self, strings, pattern):
        self.assert_str('string', strings[0])
        self.assert_regex('pattern', pattern)
        try:
            return strings.str.extract(pattern)
        except ValueError as e:
            raise OdhQLExecutionException(e.message)


class StartsWith(VectorizedFunction):
    name = 'STARTSWITH'

    def apply(self, strings, start):
        self.assert_str('string', strings[0])
        self.assert_str('start', start)
        return strings.str.startswith(start)


class EndsWith(VectorizedFunction):
    name = 'ENDSWITH'

    def apply(self, strings, end):
        self.assert_str('string', strings[0])
        self.assert_str('end', end)
        return strings.str.endswith(end)


class Get(VectorizedFunction):
    name = 'GET'

    def apply(self, strings, index):
        self.assert_str('string', strings[0])
        self.assert_int('index', index)
        return strings.str.get(index)


class Contains(VectorizedFunction):
    name = 'CONTAINS'

    def apply(self, strings, pattern, match_case):
        self.assert_str('string', strings[0])
        self.assert_regex('pattern', pattern)
        self.assert_bool('match_case', match_case)
        return strings.str.contains(pattern, match_case)


class Replace(VectorizedFunction):
    name = 'REPLACE'

    def apply(self, strings, pattern, replace, match_case):
        self.assert_str('string', strings[0])
        self.assert_regex('pattern', pattern)
        self.assert_str('replace', replace)
        self.assert_bool('match_case', match_case)
        return strings.str.replace(pattern, replace, case=match_case)


class Repeat(VectorizedFunction):
    name = 'REPEAT'

    def apply(self, strings, times):
        self.assert_str('string', strings[0])
        self.assert_int('times', times)
        return strings.str.repeat(times)


class Pad(VectorizedFunction):
    name = 'PAD'

    def apply(self, strings, width, side):
        self.assert_str('string', strings[0])
        self.assert_in('side', side, ['left', 'right', 'both'])
        self.assert_int('width', width)
        return strings.str.pad(width, side)


class Count(VectorizedFunction):
    name = 'COUNT'

    def apply(self, strings, pattern):
        self.assert_str('string', strings[0])
        self.assert_regex('pattern', pattern)
        return strings.str.count(pattern)


class Substring(VectorizedFunction):
    name = 'SUBSTRING'

    def apply(self, strings, start, end):
        self.assert_str('string', strings[0])
        self.assert_int('start', start)
        self.assert_int('end', end)
        return strings.str.slice(start, end)
