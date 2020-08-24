import unittest

from performance.utils import camelcase
from performance.utils import getattrdotted
from performance.utils import setattrdotted
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


class TestUtilsDotted(unittest.TestCase):

    class F:
        # parent = E
        def __init__(self, value):
            self.value = value

    class E:
        # parent = D
        def __init__(self, value):
            self.f = TestUtilsDotted.F(value)

    class D:
        # parent = C
        def __init__(self, value):
            self.e = TestUtilsDotted.E(value)

    class C:
        # root
        def __init__(self, value):
            self.d = TestUtilsDotted.D(value)

    def test_getattrdotted(self):
        c = self.C(10)
        self.assertIs(getattrdotted(c, 'd'), c.d)
        self.assertIs(getattrdotted(c, 'd.e'), c.d.e)
        self.assertIs(getattrdotted(c, 'd.e.f'), c.d.e.f)
        self.assertEqual(getattrdotted(c, 'd.e.f.value'), c.d.e.f.value)
        # with default
        self.assertIsNone(getattrdotted(c, 'z', None))
        self.assertEqual(getattrdotted(c, 'z', 1), 1)
        self.assertEqual(getattrdotted(c, 'z', 3.141), 3.141)
        self.assertEqual(getattrdotted(c, 'z', 'string'), 'string')
        # without default, raises like getattr
        with self.assertRaises(AttributeError):
            getattrdotted(c, 'x')
        with self.assertRaises(AttributeError):
            getattrdotted(c, 'x.y')

    def test_setattrdotted(self):
        c = self.C(10)
        setattrdotted(c, 'd.e.f.value', 12)
        self.assertEqual(c.d.e.f.value, 12)
        setattrdotted(c, 'd.e.f.value', 3.141)
        self.assertEqual(c.d.e.f.value, 3.141)
        setattrdotted(c, 'd.e.f.value', None)
        self.assertEqual(c.d.e.f.value, None)
        setattrdotted(c, 'd.e.f.value', 'string')
        self.assertEqual(c.d.e.f.value, 'string')
        # works just like setattr
        setattrdotted(c, 'someattr', 'value')
        self.assertEqual(c.someattr, 'value')
        # XXX
        # * Should this go ahead and put all attributes on each object as it
        #   works down?
        # * Maybe have a parents=True flag to do this. If it did, what objects
        #   should it use?
        # * For now, this is probably the best thing to do--raise error.
        with self.assertRaises(AttributeError):
            setattrdotted(c, 'x.y', None)


if __name__ == '__main__':
    unittest.main()
