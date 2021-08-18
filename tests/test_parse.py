import unittest

from performance.parse import Delay
from performance.parse import delaystring
from performance.parse import formatdelays

class TestParseDelay(unittest.TestCase):

    def check(self, text, expect):
        self.assertListEqual(delaystring(text), expect)

    def test_parse_empty(self):
        self.check('', [])
        self.check('     ', [])
        # must be three characters
        self.check('   X Y   ', [])
        self.check('   XX YY      ', [])

    def test_parse_no_minutes(self):
        self.check('AAA', [Delay('AAA', None, False)])
        self.check('AAA    ', [Delay('AAA', None, False)])
        self.check('AAA BBB', [Delay('AAA', None, False), Delay('BBB', None, False)])
        # case preserved
        self.check('AbC dEF', [Delay('AbC', None, False), Delay('dEF', None, False)])

    def test_parse_code_and_minutes(self):
        self.check('AAA1', [Delay('AAA', 1, False)])
        self.check('AAA(1)', [Delay('AAA', 1, False)])
        expected = [Delay('BBB', 123, False)]
        self.check('BBB123', expected)
        self.check('BBB(123)', expected)
        self.check('BBB(123', expected)
        self.check('BBB123)', expected)
        # two
        expected = [Delay('AAA', 123, False), Delay('BBB', 456, False)]
        self.check('AAA123BBB456', expected)
        self.check('AAA(123)BBB(456)', expected)
        self.check('AAA(123) BBB(456)', expected)
        self.check('AAA(123)    BBB(456)', expected)
        # three
        expected = [Delay('AAA', 123, False), Delay('BBB', 456, False),
                    Delay('CCC', 789, False)]
        self.check('AAA123BBB456CCC789', expected)
        self.check('AAA(123)BBB(456)CCC(789)', expected)
        self.check('AAA(123) BBB(456) CCC(789)', expected)
        self.check('    AAA(123)    BBB(456)   CCC(789)', expected)
        self.check('AAA(123)    BBB  (456)   CCC     (789)', expected)
        self.check('AAA(123) BBB ( 456  ) CCC(  789    )', expected)
        #
        self.check('AAA BBB123 CCC',
                [Delay('AAA', None, False), Delay('BBB', 123, False),
                 Delay('CCC', None, False)])
        self.check('AAA BBB(123 CCC',
                [Delay('AAA', None, False), Delay('BBB', 123, False),
                 Delay('CCC', None, False)])
        self.check('AAA BBB123) CCC',
                [Delay('AAA', None, False), Delay('BBB', 123, False),
                 Delay('CCC', None, False)])
        self.check('AAA() BBB123 CCC',
                [Delay('AAA', None, False), Delay('BBB', 123, False),
                 Delay('CCC', None, False)])

    def test_parse_cancelled(self):
        self.check('XLD AAA', [Delay('AAA', None, True)])
        self.check('XLD BBB12', [Delay('BBB', 12, True)])

    def test_formatdelays(self):
        self.assertEqual(formatdelays(delaystring('AAA1 BBB2 CCC')), 'AAA(1) BBB(2) CCC')
        self.assertEqual(formatdelays(delaystring('AAA1 XLD BBB2 CCC')), 'AAA(1) XLD BBB(2) CCC')


if __name__ == '__main__':
    unittest.main()
