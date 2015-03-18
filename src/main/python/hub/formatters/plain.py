from hub.formatter import Formatter, FormatterDescription


class PlainOutput(Formatter):
    description = FormatterDescription('plain', 'Returns the document as-is', 'text/plain', 'txt')

    def format(self, document, writer, parameters):
        writer.write(document.content)
