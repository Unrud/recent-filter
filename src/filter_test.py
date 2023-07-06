import os
import unittest
from collections.abc import Iterable

from recent_filter.filter import Filter, expand_path, path_to_pattern


class TestGitignore(unittest.TestCase):

    def t(self, ignore_pattern: str, positive: Iterable[str] = (),
          negative: Iterable[str] = ()) -> None:
        f = Filter(ignore_pattern)
        for s in positive:
            self.assertTrue(f(s), f'{f}({s!r}) is not true')
        for s in negative:
            self.assertFalse(f(s), f'{f}({s!r}) is not false')

    def test_simple(self):
        self.t('/', ['/'], [])

    def test_negate(self):
        self.t('!/', [], ['/', '/-'])

    def test_include_negate(self):
        self.t('/\n!/bar', ['/', '/foo'], ['/bar'])

    def test_include_negate_include(self):
        self.t('/\n!/bar\n/bar/foo', ['/', '/foo', '/bar/foo'], ['/bar'])

    def test_empty(self):
        self.t('', [], ['', '/'])

    def test_expand_home1(self):
        self.assertEqual(os.path.expanduser('~'), expand_path('~'))

    def test_expand_home2(self):
        self.assertEqual(os.expanduser('~/foo'), expand_path('~/foo'))

    def test_path_to_pattern1(self):
        self.assertEqual(path_to_pattern(os.expanduser('~')), '~')

    def test_path_to_pattern2(self):
        self.assertEqual(path_to_pattern(os.expanduser('~/foo')), '~/foo')

    def test_path_to_pattern3(self):
        self.assertEqual(path_to_pattern('/['), '/\\[')
