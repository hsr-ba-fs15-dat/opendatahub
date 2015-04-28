"""
OdhQL string functions
"""

import pandas as pd

from hub.odhql.functions.core import VectorizedFunction, OdhQLExecutionException
from hub.structures.frame import OdhType

from defusedxml import lxml
import types


class Concat(VectorizedFunction):
    name = 'CONCAT'

    def apply(self, a, b, *args):
        args = [self.expand(arg) for arg in [a, b] + list(args)]
        for arg in args:
            self.assert_str('string', arg)
        return args[0].str.cat(args[1:])


class Trim(VectorizedFunction):
    name = 'TRIM'

    def apply(self, strings):
        self.assert_str('string', strings)
        return strings.str.strip()


class RTrim(VectorizedFunction):
    name = 'RTRIM'

    def apply(self, strings):
        self.assert_str('string', strings)
        return strings.str.rstrip()


class LTrim(VectorizedFunction):
    name = 'LTRIM'

    def apply(self, strings):
        self.assert_str('string', strings)
        return strings.str.lstrip()


class Upper(VectorizedFunction):
    name = 'UPPER'

    def apply(self, strings):
        self.assert_str('string', strings)
        return strings.str.upper()


class Lower(VectorizedFunction):
    name = 'LOWER'

    def apply(self, strings):
        self.assert_str('string', strings)
        return strings.str.lower()


class Length(VectorizedFunction):
    name = 'LEN'

    def apply(self, strings):
        self.assert_str('string', strings)
        return strings.str.len()


class Extract(VectorizedFunction):
    name = 'EXTRACT'

    def apply(self, strings, pattern, group=1):
        self.assert_str('string', strings)

        self.assert_regex('pattern', pattern)
        self.assert_value('pattern', pattern)

        self.assert_int('group', group)
        self.assert_value('group', group)

        if group < 1:
            raise OdhQLExecutionException('Invalid parameter: group can not be smaller than 1')

        try:
            res = strings.str.extract(pattern)

            if isinstance(res, pd.Series) and group > 1:
                raise OdhQLExecutionException('Error in regular expression: Only 1 group')
            elif isinstance(res, pd.DataFrame):
                if group > len(res.columns):
                    raise OdhQLExecutionException(
                        'Error in regular expression: Requested group {} > {} groups returned'
                        .format(group, len(res.columns)))

                res = res[group - 1]

            return res
        except ValueError as e:
            raise OdhQLExecutionException(e.message)


class StartsWith(VectorizedFunction):
    name = 'STARTSWITH'

    def apply(self, strings, start):
        self.assert_str('string', strings)
        self.assert_str('start', start)
        return strings.str.startswith(start)


class EndsWith(VectorizedFunction):
    name = 'ENDSWITH'

    def apply(self, strings, end):
        self.assert_str('string', strings)
        self.assert_str('end', end)
        return strings.str.endswith(end)


class Get(VectorizedFunction):
    name = 'GET'

    def apply(self, strings, index):
        self.assert_str('string', strings)
        self.assert_int('index', index)
        return strings.str.get(index)


class Contains(VectorizedFunction):
    name = 'CONTAINS'

    def apply(self, strings, pattern, match_case=True):
        self.assert_str('string', strings)

        self.assert_regex('pattern', pattern)
        self.assert_value('pattern', pattern)

        self.assert_bool('match_case', match_case)
        return strings.str.contains(pattern, match_case)


class Replace(VectorizedFunction):
    name = 'REPLACE'

    def apply(self, strings, pattern, replace, match_case=True):
        self.assert_str('string', strings)

        self.assert_regex('pattern', pattern)
        self.assert_value('pattern', pattern)

        self.assert_str('replace', replace)
        self.assert_bool('match_case', match_case)
        return strings.str.replace(pattern, replace, case=match_case)


class Repeat(VectorizedFunction):
    name = 'REPEAT'

    def apply(self, strings, times):
        self.assert_str('string', strings)
        self.assert_int('times', times)
        return strings.str.repeat(times)


class Pad(VectorizedFunction):
    name = 'PAD'

    def apply(self, strings, width, side):
        self.assert_str('string', strings)
        self.assert_in('side', side, ['left', 'right', 'both'])
        self.assert_int('width', width)
        return strings.str.pad(width, side)


class Count(VectorizedFunction):
    name = 'COUNT'

    def apply(self, strings, pattern):
        self.assert_str('string', strings)
        self.assert_regex('pattern', pattern)
        self.assert_value('pattern', pattern)

        return strings.str.count(pattern)


class Substring(VectorizedFunction):
    name = 'SUBSTRING'

    def apply(self, strings, start, end):
        self.assert_str('string', strings)

        self.assert_int('start', start)
        self.assert_value('start', start)

        self.assert_int('end', end)
        self.assert_value('end', end)

        return strings.str.slice(start, end)


class ToChar(VectorizedFunction):
    name = 'TO_CHAR'

    def apply(self, values, format=None):
        with self.errorhandler('Unable to convert to string ({exception})'):
            if values.odh_type == OdhType.DATETIME:
                self.assert_str('format', format)
                return values.apply(lambda d: d.strftime(format))
            else:
                return OdhType.TEXT.convert(self.expand(values))


class XPath(VectorizedFunction):
    name = 'XPATH'

    def apply(self, values, path):
        self.assert_str('values', values)
        self.assert_str('path', path)
        self.assert_value('path', path)
        return values.apply(self._extract(path))

    def _extract(self, path):
        def extractor(v):
            res = lxml.fromstring(v).xpath(path)

            if isinstance(res, types.ListType):
                if len(res) == 0:
                    return None
                if len(res) > 1:
                    raise OdhQLExecutionException('Error in xpath expression: Result must be a scalar')

                res = res[0]

            if isinstance(res, basestring):
                return unicode(res)

            return res

        return extractor