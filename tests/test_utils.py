import unittest

from performance.utils import camelcase
from performance.utils import snakecase

class TestUtilsCase(unittest.TestCase):

    def test_camel_from_snake(self):
        self.assertEqual(camelcase('snake_case'), 'snakeCase')
        self.assertEqual(camelcase('snake_case_with_more_words'), 'snakeCaseWithMoreWords')
        self.assertEqual(camelcase('nosnake'), 'nosnake')
        self.assertEqual(camelcase('snake_case.with.dots'), 'snakeCase.With.Dots')
        self.assertEqual(camelcase('snake_case.with.dots_and_more_underscores'),
                         'snakeCase.With.DotsAndMoreUnderscores')

    def test_snake_from_camel(self):
        self.assertEqual(snakecase('camelCase'), 'camel_case')
        self.assertEqual(snakecase('CamelCase'), 'camel_case')
        self.assertEqual(snakecase('camelCaseWithMoreWords'), 'camel_case_with_more_words')
        self.assertEqual(snakecase('nocamel'), 'nocamel')
        self.assertEqual(snakecase('camelCase.With.Dots'), 'camel_case.with.dots')
        self.assertEqual(snakecase('CamelCase.WithDots.Dots.Dots'),
                         'camel_case.with_dots.dots.dots')



if __name__ == '__main__':
    unittest.main()
