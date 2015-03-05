
# todo chuesler: needs more work, these are now based on models
'''

import os

from testutils import TestBase, base_dir, temp_dir
from hub import nodes #, base

file_in = nodes.FileInput(params={'filename': TestBase.get_test_file_path('test-addresses.csv')})
csv_in = nodes.CsvInput()

file_in_2 = nodes.FileInput(params={'filename': TestBase.get_test_file_path('test-addresses2.csv')})
csv_in_2 = nodes.CsvInput()

merger = nodes.SequentialJoin()

transform = nodes.NormalizedAddressToGarbageTransform()
csv_out = nodes.CsvOutput(os.path.join(temp_dir, 'test-addresses-output.csv'), ('Name', 'Street', 'City'))

p = base.Pipeline('TestPipeline', 'Example pipeline to test the api',
                          [file_in, csv_in, file_in_2, csv_in_2, merger, transform, csv_out])
 p.run()
'''
