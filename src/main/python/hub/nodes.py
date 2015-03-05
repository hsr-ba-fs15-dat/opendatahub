
import csv
from hub import base


class FileInput(base.InputNode):
    def __init__(self, *args, **kwargs):
        super(FileInput, self).__init__(*args, **kwargs)

    def read(self):
        with open(self.filename, 'r') as file_input:
            for line in file_input:
                yield line


class CsvInput(base.TransformationNode):
    def __init__(self, *args, **kwargs):
        super(CsvInput, self).__init__(*args, **kwargs)

    def transform(self, reader):
        csv_reader = csv.DictReader(reader)
        for row in csv_reader:
            yield row


class SequentialJoin(base.JoinNode):
    def __init__(self, *args, **kwargs):
        super(SequentialJoin, self).__init__(*args, **kwargs)

    def join(self, readers):
        for reader in readers:
            for row in reader:
                yield row


class NormalizedAddressToGarbageTransform(base.TransformationNode):
    def __init__(self, *args, **kwargs):
        super(NormalizedAddressToGarbageTransform, self).__init__(*args, **kwargs)

    def transform(self, reader):
        for row in reader:
            converted = {
                'Name': '{} {}'.format(row['Name'], row['Surname']),
                'Street': '{} {}'.format(row['Street'], row['No']),
                'City': '{} {}'.format(row['Zip'], row['City'])
            }
            yield converted


class CsvOutput(base.OutputNode):
    def __init__(self, *args, **kwargs):
        super(CsvOutput, self).__init__(*args, **kwargs)

    def write(self, reader):
        with open(self.filename, 'w') as output:
            csv_writer = csv.DictWriter(output, self.field_names)
            csv_writer.writeheader()

            for row in reader:
                csv_writer.writerow(row)
