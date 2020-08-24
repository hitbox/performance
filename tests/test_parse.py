import unittest

from performance import parse

class TestParseDelay(unittest.TestCase):

    def check(self, text, expect):
        self.assertListEqual(parse.delaystring(text), expect)

    def test_parse_empty(self):
        self.check('', [])
        self.check('     ', [])
        # must be three characters
        self.check('   X Y   ', [])
        self.check('   XX YY      ', [])

    def test_parse_no_minutes(self):
        self.check('AAA', [('AAA', None)])
        self.check('AAA    ', [('AAA', None)])
        self.check('AAA BBB', [('AAA', None), ('BBB', None)])
        # case preserved
        self.check('AbC dEF', [('AbC', None), ('dEF', None)])

    def test_parse_code_and_minutes(self):
        self.check('AAA1', [('AAA', 1)])
        self.check('AAA(1)', [('AAA', 1)])
        expected = [('BBB', 123)]
        self.check('BBB123', expected)
        self.check('BBB(123)', expected)
        self.check('BBB(123', expected)
        self.check('BBB123)', expected)
        # two
        expected = [('AAA', 123), ('BBB', 456)]
        self.check('AAA123BBB456', expected)
        self.check('AAA(123)BBB(456)', expected)
        self.check('AAA(123) BBB(456)', expected)
        self.check('AAA(123)    BBB(456)', expected)
        # three
        expected = [('AAA', 123), ('BBB', 456), ('CCC', 789)]
        self.check('AAA123BBB456CCC789', expected)
        self.check('AAA(123)BBB(456)CCC(789)', expected)
        self.check('AAA(123) BBB(456) CCC(789)', expected)
        self.check('    AAA(123)    BBB(456)   CCC(789)', expected)
        self.check('AAA(123)    BBB  (456)   CCC     (789)', expected)
        self.check('AAA(123) BBB ( 456  ) CCC(  789    )', expected)
        #
        self.check('AAA BBB123 CCC', [('AAA', None), ('BBB', 123), ('CCC', None)])
        self.check('AAA BBB(123 CCC', [('AAA', None), ('BBB', 123), ('CCC', None)])
        self.check('AAA BBB123) CCC', [('AAA', None), ('BBB', 123), ('CCC', None)])
        self.check('AAA() BBB123 CCC', [('AAA', None), ('BBB', 123), ('CCC', None)])


if __name__ == '__main__':
    unittest.main()
