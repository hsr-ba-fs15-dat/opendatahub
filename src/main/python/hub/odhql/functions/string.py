# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
OdhQL string functions
"""

import pandas as pd
from defusedxml import lxml
import types

from hub.odhql.functions.core import VectorizedFunction, OdhQLExecutionException
from hub.structures.frame import OdhType


class Concat(VectorizedFunction):
    # FIXME varargs-doku listet die variablen argumente nicht
    """
    Konkateniert eine Liste von TEXT-Spalten oder Werten.

    Parameter
        - `args`: Liste von TEXT-Spalten oder -Werten

    Beispiel
        .. code:: sql

            CONCAT(ODH5.given_name, ' ', ODH5.surname) AS name
    """
    name = 'CONCAT'

    def apply(self, a, b, *args):
        args = [self.expand(arg) for arg in [a, b] + list(args)]
        for arg in args:
            self.assert_str('string', arg)
        return args[0].str.cat(args[1:])


class Trim(VectorizedFunction):
    """
    Entfernt White Space vom Beginn und Ende der Spalte oder des Wertes.

    Parameter
        - `strings`: TEXT-Spalte oder -Wert

    Beispiel
        .. code:: sql

            TRIM(ODH7.strasse) AS strasse
    """
    name = 'TRIM'

    def apply(self, strings):
        self.assert_str('string', strings)
        return strings.str.strip()


class RTrim(VectorizedFunction):
    """
    Entfernt White Space vom Ende der Spalte oder des Wertes.

    Parameter
        - `strings`: TEXT-Spalte oder -Wert

    Beispiel
        .. code:: sql

            RTRIM(ODH7.strasse) AS strasse
    """
    name = 'RTRIM'

    def apply(self, strings):
        self.assert_str('string', strings)
        return strings.str.rstrip()


class LTrim(VectorizedFunction):
    """
    Entfernt White Space vom Beginn der Spalte oder des Wertes.

    Parameter
        - `strings`: TEXT-Spalte oder -Wert

    Beispiel
        .. code:: sql

            LTRIM(ODH7.strasse) AS strasse
    """
    name = 'LTRIM'

    def apply(self, strings):
        self.assert_str('string', strings)
        return strings.str.lstrip()


class Upper(VectorizedFunction):
    """
    Konvertiert alle Buchstaben in Grossbuchstaben.

    Parameter
        - `strings`: TEXT-Spalte oder -Wert

    Beispiel
        .. code:: sql

            UPPER(ODH7.ort) AS ort
    """
    name = 'UPPER'

    def apply(self, strings):
        self.assert_str('string', strings)
        return strings.str.upper()


class Lower(VectorizedFunction):
    """
    Konvertiert alle Buchstaben in Kleinbuchstaben.

    Parameter
        - `strings`: TEXT-Spalte oder -Wert

    Beispiel
        .. code:: sql

            LOWER(ODH7.ort) AS ort
    """
    name = 'LOWER'

    def apply(self, strings):
        self.assert_str('string', strings)
        return strings.str.lower()


class Length(VectorizedFunction):
    """
    Liefert die Länge des TEXTs.

    Parameter
        - `strings`: TEXT-Spalte oder -Wert

    Beispiel
        .. code:: sql

            LEN(ODH7.description) AS description_length
    """
    name = 'LEN'

    def apply(self, strings):
        self.assert_str('string', strings)
        return strings.str.len()


class Extract(VectorizedFunction):
    """
    Wendet einen Regulären Ausdruck (Regex) auf die angegebene Spalte oder den Wert an und liefert das Resultat
    der angegebenen Gruppe zurück.

    Parameter
        - `strings`: TEXT-Spalte oder -Wert
        - `pattern`: Regulärer Ausdruck. Siehe Regex-Dokumentation_.
        - `group`: Optional. Gruppe, welche ausgewertet werden soll. Default: 1.

        .. _Regex-Dokumentation: https://docs.python.org/2/library/re.html#regular-expression-syntax>

    Beispiel
        .. code:: sql

            EXTRACT(t.text, '\|([^|\.]+)') AS title
    """
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
                    raise OdhQLExecutionException('Error in regular expression: '
                                                  'Requested group {} > {} groups returned'
                                                  .format(group, len(res.columns)))

                res = res[group - 1]

            return res
        except ValueError as e:
            raise OdhQLExecutionException(e.message)


class StartsWith(VectorizedFunction):
    """
    Prüft ob ein Text mit einer angegebenen Zeichenkette anfängt.

    Kann als Bedingung verwendet werden.

    Parameter
        - `strings`: TEXT-Spalte oder -Wert
        - `start`: TEXT-Spalte oder -Wert

    Beispiel
        .. code:: sql

            STARTSWITH(ODH7.ort, 'Zürich') AS in_zurich
    """
    name = 'STARTSWITH'

    def apply(self, strings, start):
        self.assert_str('string', strings)
        self.assert_str('start', start)
        return strings.str.startswith(start)


class EndsWith(VectorizedFunction):
    """
    Prüft ob ein Text mit einer angegebenen Zeichenkette endet.

    Kann als Bedingung verwendet werden.

    Parameter
        - `strings`: TEXT-Spalte oder -Wert
        - `end`: TEXT-Spalte oder -Wert

    Beispiel
        .. code:: sql

            ENDSWITH(ODH9.haltestelle, 'Flughafen') AS ist_flughafen
    """
    name = 'ENDSWITH'

    def apply(self, strings, end):
        self.assert_str('string', strings)
        self.assert_str('end', end)
        return strings.str.endswith(end)


class Get(VectorizedFunction):
    """
    Liefert das Zeichen an der angegebenen Stelle im Text (0-basiert).

    Parameter
        - `strings`: Spalte oder -Wert
        - `index`: Spalte oder Wert.

    Beispiel
        .. code:: sql

            GET(ODH12.country, 1) AS c
    """
    name = 'GET'

    def apply(self, strings, index):
        self.assert_str('string', strings)
        self.assert_int('index', index)
        return strings.str.get(index)


class Contains(VectorizedFunction):
    """
    Prüft ob eine Zeichenkette in einem Text enthalten ist.

    Kann als Bedingung verwendet werden.

    Parameter
        - `strings`: Spalte oder Wert in welchem gesucht werden soll
        - `pattern`: Spalte oder Wert welcher gesucht werden soll
        - `match_case`: Optional. Gibt an ob Gross- und Kleinschreibung beachtet werden soll. Default: True.

    Beispiel
        .. code:: sql

            CONTAINS(ODH9.haltestelle, 'Hauptbahnhof') AS ist_hb
    """
    name = 'CONTAINS'

    def apply(self, strings, pattern, match_case=True):
        self.assert_str('string', strings)

        self.assert_regex('pattern', pattern)
        self.assert_value('pattern', pattern)

        self.assert_bool('match_case', match_case)
        return strings.str.contains(pattern, match_case)


class Replace(VectorizedFunction):
    """
    Ersetzt die angegebene Zeichenkette im Text.

    Parameter
        - `strings`: Spalte oder -Wert in welchem gesucht werden soll
        - `pattern`: Spalte oder -Wert welcher gesucht werden soll
        - `replace`: Ersatz-Spalte oder -Wert
        - `match_case`: Optional. Gibt an ob Gross- und Kleinschreibung beachtet werden soll. Default: True.

    Beispiel
        .. code:: sql

            REPLACE(ODH12.strasse, 'str.', 'strasse') AS strasse
    """
    name = 'REPLACE'

    def apply(self, strings, pattern, replace, match_case=True):
        self.assert_str('string', strings)

        self.assert_regex('pattern', pattern)
        self.assert_value('pattern', pattern)

        self.assert_str('replace', replace)
        self.assert_bool('match_case', match_case)
        return strings.str.replace(pattern, replace, case=match_case)


class Repeat(VectorizedFunction):
    """
    Wiederholt die Zeichenkette eine bestimme Anzahl mal.

    Parameter
        - `strings`: Spalte oder Wert welcher wiederholt werden solle
        - `times`: Anzahl Wiederholungen

    Beispiel
        .. code:: sql

            REPEAT('Lorem ipsum dolor... ', 20) AS filler
    """
    name = 'REPEAT'

    def apply(self, strings, times):
        self.assert_str('string', strings)
        self.assert_int('times', times)
        return strings.str.repeat(times)


class Pad(VectorizedFunction):
    """
    Füllt die Zeichenkette auf die angegebene Länge mit Leerzeichen auf.

    Parameter
        - `strings`: Spalte oder Wert
        - `width`: Gewünschte Länge
        - `side`: Seite. Kann 'left', 'right' oder 'both' sein.

    Beispiel
        .. code:: sql

            PAD(ODH4.name, 20, 'right') AS name
    """
    name = 'PAD'

    def apply(self, strings, width, side):
        self.assert_str('string', strings)
        self.assert_in('side', side, ['left', 'right', 'both'])
        self.assert_int('width', width)
        return strings.str.pad(width, side)


class Count(VectorizedFunction):
    """
    Zählt die Anzahl Vorkommnisse des Musters im Text.

    Parameter
        - `strings`: Spalte oder Wert
        - `pattern`: Regulárer Ausdruck. Siehe Regex-Dokumentation_.

    Beispiel
        .. code:: sql

         COUNT(ODH30.description, '\\d') AS numbers
    """
    name = 'COUNT'

    def apply(self, strings, pattern):
        self.assert_str('string', strings)
        self.assert_regex('pattern', pattern)
        self.assert_value('pattern', pattern)

        return strings.str.count(pattern)


class Substring(VectorizedFunction):
    """
    Liefert den angegebenen Teil des Texts.

    Parameter
        - `strings`: Spalte oder Wert
        - `start`: Startposition
        - `end`: Endposition

    Beispiel
        .. code:: sql

         SUBSTRING(ODH30.description, 0, 100) AS title
    """
    # FIXME 1-basiert?
    name = 'SUBSTRING'

    def apply(self, strings, start, end):
        self.assert_str('string', strings)

        self.assert_int('start', start)
        self.assert_value('start', start)

        self.assert_int('end', end)
        self.assert_value('end', end)

        return strings.str.slice(start, end)


class ToChar(VectorizedFunction):
    """
    Konvertiert eine Spalte oder einen Werte zu TEXT. Für DATETIME-Spalten/Werte kann ein Format angegeben werden.

    Parameter
        - `values`: Spalte oder Wert
        - `format`: Falls `values` vom Typ DATETIME ist: Format-Angabe für die Konversion.

    Beispiel
        .. code:: sql

         TO_CHAR(TO_DATE(ODH30.baubeginn, '%d%m%Y'), '%Y-%m-%d') AS baubeginn
    """
    # FIXME strftime-link
    name = 'TO_CHAR'

    def apply(self, values, format=None):
        with self.errorhandler('Unable to convert to string ({exception})'):
            if values.odh_type == OdhType.DATETIME:
                self.assert_str('format', format)
                return values.apply(lambda d: d.strftime(format))
            else:
                return OdhType.TEXT.convert(self.expand(values))


class XPath(VectorizedFunction):
    """
    Wendet den XPath-Ausdruck auf die Spalte oder den Wert an.

    Parameter
        - `values`: Spalte oder Wert mit gültigem XML in TEXT-Form.
        - `path`: XPath-Ausdruck. Zu beachten: Der Ausdruck darf genau ein Resultat pro Zeile in `values` liefern.

    Beispiel
        .. code:: sql

         XPATH(t.description, '//tr[1]/td[2]/text()') AS abschnitt
    """
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
