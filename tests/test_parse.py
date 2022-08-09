import unittest

from performance.parse import delaystring
from performance.parse import formatdelays

def test_parse_empty():
    assert delaystring('') == []
    assert delaystring('     ') == []
    # must be three characters
    assert delaystring('   X Y   ') == []
    assert delaystring('   XX YY      ') == []

def test_parse_no_minutes():
    assert delaystring('AAA') == [
            dict(code='AAA', minutes=None, is_cancelled=False)
        ]
    assert delaystring('AAA    ') == [
            dict(code='AAA', minutes=None, is_cancelled=False)
        ]
    assert delaystring('AAA BBB') == [
            dict(code='AAA', minutes=None, is_cancelled=False),
            dict(code='BBB', minutes=None, is_cancelled=False),
        ]

def test_parse_code_and_minutes():
    assert delaystring('AAA1') == [dict(code='AAA', minutes=1, is_cancelled=False)]
    assert delaystring('AAA(1)') == [dict(code='AAA', minutes=1, is_cancelled=False)]
    # parse handles many kinds of user input
    expected = [dict(code='BBB', minutes=123, is_cancelled=False)]
    assert delaystring('BBB123') == expected
    assert delaystring('BBB(123)') == expected
    assert delaystring('BBB(123') == expected
    assert delaystring('BBB123)') == expected
    # two delay codes and minutes
    expected = [
        dict(code='AAA', minutes=123, is_cancelled=False),
        dict(code='BBB', minutes=456, is_cancelled=False),
    ]
    assert delaystring('AAA123BBB456') == expected
    assert delaystring('AAA(123)BBB(456)') == expected
    assert delaystring('AAA(123) BBB(456)') == expected
    assert delaystring('AAA(123)    BBB(456)') == expected
    # three delay codes and minutes
    expected = [
        dict(code='AAA', minutes=123, is_cancelled=False),
        dict(code='BBB', minutes=456, is_cancelled=False),
        dict(code='CCC', minutes=789, is_cancelled=False),
    ]
    assert delaystring('AAA123BBB456CCC789') == expected
    assert delaystring('AAA(123)BBB(456)CCC(789)') == expected
    assert delaystring('AAA(123) BBB(456) CCC(789)') == expected
    assert delaystring('    AAA(123)    BBB(456)   CCC(789)') == expected
    assert delaystring('AAA(123)    BBB  (456)   CCC     (789)') == expected
    assert delaystring('AAA(123) BBB ( 456  ) CCC(  789    )') == expected
    # mixed with and without minutes
    assert delaystring('AAA BBB123 CCC') == [
            dict(code='AAA', minutes=None, is_cancelled=False),
            dict(code='BBB', minutes=123, is_cancelled=False),
            dict(code='CCC', minutes=None, is_cancelled=False)
        ]
    assert delaystring('AAA BBB(123 CCC') == [
            dict(code='AAA', minutes=None, is_cancelled=False),
            dict(code='BBB', minutes=123, is_cancelled=False),
            dict(code='CCC', minutes=None, is_cancelled=False),
        ]
    assert delaystring('AAA BBB123) CCC') == [
            dict(code='AAA', minutes=None, is_cancelled=False),
            dict(code='BBB', minutes=123, is_cancelled=False),
            dict(code='CCC', minutes=None, is_cancelled=False)
        ]
    assert delaystring('AAA() BBB123 CCC') == [
            dict(code='AAA', minutes=None, is_cancelled=False),
            dict(code='BBB', minutes=123, is_cancelled=False),
            dict(code='CCC', minutes=None, is_cancelled=False)
        ]
    #
    assert delaystring('AAA(123456)') == [
            dict(code='AAA', minutes=123456, is_cancelled=False)
        ]

def test_parse_cancelled():
    assert delaystring('XLD AAA') == [
            dict(code='AAA', minutes=None, is_cancelled=True)
        ]
    assert delaystring('XLD BBB12') == [
            dict(code='BBB', minutes=12, is_cancelled=True)
        ]
    assert delaystring('XLD') == [
            dict(code='XLD', minutes=None, is_cancelled=True)
        ]
    assert delaystring('XLD XLD') == [
            dict(code='XLD', minutes=None, is_cancelled=True)
        ]
    assert delaystring('XLD XLD AAA13 BBB23') == [
            dict(code='XLD', minutes=None, is_cancelled=True),
            dict(code='AAA', minutes=13, is_cancelled=False),
            dict(code='BBB', minutes=23, is_cancelled=False),
        ]

def format_for_test(string):
    return formatdelays(delaystring(string))

def test_formatdelays():
    assert format_for_test('AAA1 BBB2 CCC') == 'AAA(1) BBB(2) CCC'
    assert format_for_test('AAA1 XLD BBB2 CCC') == 'AAA(1) XLD BBB(2) CCC'
    assert format_for_test('XLD') == 'XLD'
    assert format_for_test('XLD14') == 'XLD(14)'
    assert format_for_test('XLD AAA') == 'XLD AAA'
    assert format_for_test('XLD13 AAA') == 'XLD(13) AAA'
    assert format_for_test('XLD AAA10') == 'XLD AAA(10)'

def test_placeholder():
    assert delaystring('AAA11 BBB22 XXX33') == [
            dict(code='AAA', minutes=11, is_cancelled=False),
            dict(code='BBB', minutes=22, is_cancelled=False),
            dict(code='XXX', minutes=33, is_cancelled=False),
        ]

if __name__ == '__main__':
    unittest.main()
