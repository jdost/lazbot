import unittest
from lazbot import utils


class CleanArgsTest(unittest.TestCase):
    def test_no_catch(self):
        ''' Ensure that the normal argument style is cleaned
        "Normal" argument style (a, b, c) is where there are no catch all
        parameters (i.e. *args, **kwargs).  This should filter out un expected
        args and kwargs to the function.
        '''

        @utils.clean_args
        def test(a, b, c, d=1):
            return [a, b, c, d]

        self.assertEqual([1, 2, 3, 1], test(1, 2, 3, x=4))
        self.assertEqual([1, 2, 3, 4], test(1, 2, 3, 4))

    def test_catch_args(self):
        ''' Ensure that argument catching is honored
        Argument catching is the *args style parameter.  This should still get
        all leftover arguments.
        '''

        @utils.clean_args
        def test(a, *args):
            return [a, args]

        self.assertEqual([1, (2, 3)], test(1, 2, 3))
        self.assertEqual([1, (2, 3)], test(1, 2, 3, b=4))

    def test_catch_kwargs(self):
        ''' Ensure that keyword argument catching is honored
        Keywaord argument catching is the **kwargs style parameter.  This
        should get all of the leftover arguments with a keyword.
        '''

        @utils.clean_args
        def test(a, **kwargs):
            return [a, kwargs]

        self.assertEqual([1, {"b": 2, "c": 3}], test(1, b=2, c=3))
        self.assertEqual([1, {}], test(1, 2, 3))
