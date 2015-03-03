import home.models
import os
import csv


class FileInput(home.models.Input):
    def __init__(self, filename):
        super(FileInput, self).__init__(parameters={'filename': filename})

    def read(self):
        with open(self.parameters['filename'], 'r') as file_input:
            for line in file_input:
                yield line


class CsvInput(home.models.Transformation):
    def __init__(self):
        super(CsvInput, self).__init__()

    def transform(self, reader):
        csv_reader = csv.DictReader(reader)
        for row in csv_reader:
            yield row


class SequentialMerger(home.models.Merge):
    def __init__(self):
        super(SequentialMerger, self).__init__()

    def merge(self, readers):
        for reader in readers:
            for row in reader:
                yield row


class NormalizedAddressToGarbageTransform(home.models.Transformation):
    def __init__(self):
        super(NormalizedAddressToGarbageTransform, self).__init__()

    def transform(self, reader):
        for row in reader:
            converted = {
                'Name': '{} {}'.format(row['Name'], row['Surname']),
                'Street': '{} {}'.format(row['Street'], row['No']),
                'City': '{} {}'.format(row['Zip'], row['City'])
            }
            yield converted


class CsvOutput(home.models.Output):
    def __init__(self, filename, field_names):
        super(CsvOutput, self).__init__(parameters={'filename': filename, 'field_names': field_names})

    def write(self, reader):
        with open(self.parameters['filename'], 'w') as output:
            csv_writer = csv.DictWriter(output, self.parameters['field_names'])
            csv_writer.writeheader()

            for row in reader:
                csv_writer.writerow(row)


basedir = os.path.abspath(os.path.dirname(__file__))

file_in = FileInput(os.path.join(basedir, 'test-addresses.csv'))
csv_in = CsvInput()

file_in_2 = FileInput(os.path.join(basedir, 'test-addresses2.csv'))
csv_in_2 = CsvInput()

merger = SequentialMerger()

transform = NormalizedAddressToGarbageTransform()
csv_out = CsvOutput(os.path.join(basedir, 'test-addresses-output.csv'), ('Name', 'Street', 'City'))

p = home.models.Pipeline('TestPipeline', 'Example pipeline to test the api',
                         [file_in, csv_in, file_in_2, csv_in_2, merger, transform, csv_out])
p.run()
