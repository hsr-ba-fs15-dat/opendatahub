__author__ = 'chuesler'

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
            csvWriter = csv.DictWriter(output, self.parameters['field_names'])
            for row in reader:
                csvWriter.writerow(row)


basedir = os.path.abspath(os.path.dirname(__file__))

fileIn = FileInput(os.path.join(basedir, 'test-addresses.csv'))
csvIn = CsvInput()

fileIn2 = FileInput(os.path.join(basedir, 'test-addresses2.csv'))
csvIn2 = CsvInput()

merger = SequentialMerger()

transform = NormalizedAddressToGarbageTransform()
csvOut = CsvOutput(os.path.join(basedir, 'test-addresses-output.csv'), ('Name', 'Street', 'City'))

p = home.models.Pipeline('TestPipeline', 'Example pipeline to test the api',
                         [fileIn, csvIn, fileIn2, csvIn2, merger, transform, csvOut])
p.run()

# Anrede, Vorname, Name, Strasse, Hausnummer, PLZ, Ort
# Name, Strasse, Ort


