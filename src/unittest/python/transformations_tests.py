"""

"""

import os

from testutils import TestBase, base_dir, temp_dir
from home import models


if __name__ == '__main__':  # skip atm
    file_in = models.FileInputNode(TestBase.get_test_file_path('test-addresses.csv'))
    csv_in = models.CsvInput()

    file_in_2 = models.FileInputNode(TestBase.get_test_file_path('test-addresses2.csv'))
    csv_in_2 = models.CsvInput()

    merger = models.SequentialMerger()

    transform = models.NormalizedAddressToGarbageTransform()
    csv_out = models.CsvOutputNode(os.path.join(temp_dir, 'test-addresses-output.csv'), ('Name', 'Street', 'City'))

    p = models.Pipeline('TestPipeline', 'Example pipeline to test the api',
                        [file_in, csv_in, file_in_2, csv_in_2, merger, transform, csv_out])
    p.run()
