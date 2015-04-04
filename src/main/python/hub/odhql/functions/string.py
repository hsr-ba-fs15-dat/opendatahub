"""
ANSI SQL (SQL 92) Functions
"""

from hub.odhql.functions.core import VectorizedFunction, OdhQLExecutionException


class Concat(VectorizedFunction):
    name = 'CONCAT'

    def apply(self, a, b, *args):
        for arg in [a, b] + list(args):
            self.assert_str('strings', arg[0])
        return a.str.cat([b] + list(args))


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

    def apply(self, strings, patterns):
        self.assert_str('string', strings[0])
        self.assert_regex('pattern', patterns[0])
        try:
            return strings.str.extract(patterns[0])
        except ValueError as e:
            raise OdhQLExecutionException(e.message)


class StartsWith(VectorizedFunction):
    name = 'STARTSWITH'

    def apply(self, strings, start):
        self.assert_str('string', strings[0])
        self.assert_str('start', start[0])
        return strings.str.startswith(start[0])


class EndsWith(VectorizedFunction):
    name = 'ENDSWITH'

    def apply(self, strings, end):
        self.assert_str('string', strings[0])
        self.assert_str('end', end[0])
        return strings.str.endswith(end[0])


class Get(VectorizedFunction):
    name = 'GET'

    def apply(self, strings, index):
        self.assert_str('string', strings[0])
        self.assert_int('index', index[0])
        return strings.str.get(index[0])


class Contains(VectorizedFunction):
    name = 'CONTAINS'

    def apply(self, strings, pattern, match_case):
        self.assert_str('string', strings[0])
        self.assert_regex('pattern', pattern[0])
        self.assert_bool('match_case', match_case[0])
        return strings.str.contains(pattern[0], match_case[0])


class Replace(VectorizedFunction):
    name = 'REPLACE'

    def apply(self, strings, pattern, replace, match_case):
        self.assert_str('string', strings[0])
        self.assert_regex('pattern', pattern[0])
        self.assert_str('replace', replace[0])
        self.assert_bool('match_case', match_case[0])
        return strings.str.replace(pattern[0], replace[0], case=match_case[0])


class Repeat(VectorizedFunction):
    name = 'REPEAT'

    def apply(self, strings, times):
        return strings.str.match(times[0])


class Pad(VectorizedFunction):
    name = 'PAD'

    def apply(self, strings, width, side):
        self.assert_in('side', side[0], ['left', 'right', 'both'])
        self.assert_type('width', width[0], int)
        return strings.str.pad(width[0], side[0])


class Count(VectorizedFunction):
    name = 'COUNT'

    def apply(self, strings, pattern):
        self.assert_regex('pattern', pattern[0])
        return strings.str.count(pattern[0])


class Substring(VectorizedFunction):
    name = 'SUBSTRING'

    def apply(self, strings, start, end):
        self.assert_int('start', start[0])
        self.assert_int('end', end[0])
        return strings.str.slice(start[0], end[0])
