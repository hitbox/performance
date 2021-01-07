import sys
import unittest

from pathlib import Path

from performance.mdbreader import mdbreader

class TestMDBReader(unittest.TestCase):

    @unittest.skipUnless(sys.platform == 'win32', 'Test requires windows.')
    def test_mdbreader_windows(self):
        reader = mdbreader(Path('tests/Database1.accdb').resolve().absolute())
        print(reader.read_table('table1'))


if __name__ == '__main__':
    unittest.main()
