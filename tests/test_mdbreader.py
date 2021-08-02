import sys
import unittest

from pathlib import Path

from performance.mdbreader import mdbreader

class TestMDBReader(unittest.TestCase):

    @unittest.skipUnless(sys.platform == 'win32', 'Test requires windows.')
    def test_mdbreader_windows(self):
        # XXX
        # Wow. The hardest system to read a MICROSOFT Access database is
        # MICROSOFT Windows!
        # Nothing is working here.
        #  import pyodbc

        #  path = Path('tests/Database1.accdb')
        #  constr = ( 'DRIVER={Microsoft Access Driver (*.mdb)};'
        #            f'DBQ={path.absolute()}')
        #  print(constr)

        #  pyodbc.connect(constr)
        #  #reader = mdbreader(coj)
        #  #print(reader.read_table('table1'))
        pass


if __name__ == '__main__':
    unittest.main()
