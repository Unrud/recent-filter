import unittest
from collections.abc import Iterable
from typing import Union

from recent_filter.gitignore import Pattern, escape, convert_to_re


class TestGitignore(unittest.TestCase):

    def t(self, pattern: Union[Pattern, str], positive: Iterable[str] = (),
          negative: Iterable[str] = ()) -> None:
        p = pattern if isinstance(pattern, Pattern) else convert_to_re(pattern)
        self.assertIsNotNone(p, f'{pattern!r} is not valid')
        for s in positive:
            self.assertTrue(p(s), f'{p}({s!r}) is not true')
        for s in negative:
            self.assertFalse(p(s), f'{p}({s!r}) is not false')

    def test_invalid_multiline1(self):
        with self.assertRaises(ValueError):
            convert_to_re('\n')

    def test_invalid_multiline2(self):
        with self.assertRaises(ValueError):
            convert_to_re('foo\n')

    def test_invalid_multiline3(self):
        with self.assertRaises(ValueError):
            convert_to_re('\nfoo')

    def test_invalid_multiline4(self):
        with self.assertRaises(ValueError):
            convert_to_re('foo\nfoo')

    def test_empty1(self):
        self.assertIsNone(convert_to_re(''))

    def test_empty2(self):
        self.assertIsNone(convert_to_re(' '))

    def test_empty3(self):
        self.assertIsNone(convert_to_re('#'))

    def test_empty4(self):
        self.assertIsNone(convert_to_re('#foo'))

    def test_empty5(self):
        self.assertIsNone(convert_to_re('!'))

    def test_root(self):
        self.t('/', ['/', '/foo', '/f/o/o', '/foo/'], ['', 'foo', 'foo/'])

    def test_unanchored(self):
        self.t('foo',
               ['/foo', '/foo/', '/bar/foo', '/bar/foo/', '/b/a/r/foo',
                '/b/a/r/foo/', '/foo/bar', '/foo/bar/', '/foo/b/a/r',
                '/foo/b/a/r/'],
               ['', 'foo', 'foo/', 'foobar/', '/foobar', '/foobar/',
                '/barfoo'])

    def test_unanchored_dir(self):
        self.t('foo/',
               ['/foo/', '/bar/foo/', '/b/a/r/foo/', '/foo/bar', '/foo/bar/',
                '/foo/b/a/r', '/foo/b/a/r/'],
               ['', 'foo', 'foo/', '/foo', '/bar/foo', '/b/a/r/foo', 'foobar/',
                '/foobar', '/foobar/'])

    def test_abs(self):
        self.t('/foo',
               ['/foo', '/foo/', '/foo/bar', '/foo/bar/', '/foo/b/a/r',
                '/foo/b/a/r/'],
               ['', 'foo', 'foo/', 'foobar/', '/foobar', '/foobar/',
                '/bar/foo', '/bar/foo/', '/b/a/r/foo', '/b/a/r/foo/'])

    def test_abs_dir(self):
        self.t('/foo/',
               ['/foo/', '/foo/bar', '/foo/bar/', '/foo/b/a/r', '/foo/b/a/r/'],
               ['', 'foo', 'foo/', '/foo', 'foobar/', '/foobar', '/foobar/',
                '/bar/foo', '/bar/foo/', '/b/a/r/foo', '/b/a/r/foo/'])

    def test_spaces1(self):
        self.t('/foo  ', ['/foo', '/foo/'], ['', '/foo ', '/foo  '])

    def test_spaces2(self):
        self.t('/foo \\ ', ['/foo  ', '/foo  /'], ['', '/foo', '/foo '])

    def test_spaces3(self):
        self.t(' /foo', ['/ /foo', '/ /foo/', '/ /foo/bar'],
               ['', '/ ', '/ /', '/foo', ' /foo', '/bar/ /foo'])

    def test_spaces4(self):
        self.t('\\ ', ['/ ', '/ /', '/ /foo'], ['', ' ', '/  '])

    def test_spaces5(self):
        self.t('\\  ', ['/ ', '/ /', '/ /foo'], ['', ' ', '/  '])

    def test_classes1(self):
        self.t('[[]', ['/[', '/[/', '/foo/[', '/foo/[/'],
               ['', '/', '[', '[/', '/]'])

    def test_classes2(self):
        self.t('[![]', ['/-', '/-/', '/foo/-', '/foo/-/', '/]'],
               ['', '/', '/[', '/[/', '/foo/[', '/foo/[/', '[', '[/'])

    def test_classes3(self):
        self.t('[a-d]', ['/a', '/b', '/c', '/d'], ['', '/', '/e'])

    def test_classes4(self):
        self.t('[a-bd-e]', ['/a', '/b', '/d', '/e'], ['', '/', '/c'])

    def test_classes5(self):
        self.t('[a-bd-]', ['/a', '/b', '/d', '/-'], ['', '/', '/c', '/e'])

    def test_classes6(self):
        self.t('[a-a]', ['/a'], ['', '/', '/b'])

    def test_classes7(self):
        self.t('[b-a]', ['/b'], ['', '/', '/a', '/c'])

    def test_classes8(self):
        self.t('[!a-d]', ['/e'], ['', '/', '/b', '/c', '/d'])

    def test_classes9(self):
        self.t('[[?*\\]', ['/[', '/?', '/*', '/\\'], ['', '/', '/-'])

    def test_classes10(self):
        self.t('[!]a-]', ['/[', '/b'], ['', '/', '/]', 'a', '-'])

    def test_classes11(self):
        self.t('a[b-b]c', ['/abc'],
               ['', '/', '/-b-', '/a-c', '/ac', '/b', '/ab', '/bc'])

    def test_classes12(self):
        self.assertIsNone(convert_to_re('['))

    def test_classes13(self):
        self.assertIsNone(convert_to_re('[ '))

    def test_classes14(self):
        self.assertIsNone(convert_to_re('[]'))

    def test_classes15(self):
        self.assertIsNone(convert_to_re('[] '))

    def test_wildcard_questionmark1(self):
        self.t('?', ['/?', '/?/', '/-', '/-/', '/foo/-'],
               ['', '/', '?', '?/', '/??', '/??/'])

    def test_wildcard_questionmark2(self):
        self.t('/?', ['/?', '/?/', '/-', '/-/'],
               ['', '/', '?', '?/', '/??', '/??/', '/foo/-'])

    def test_wildcard_questionmark3(self):
        self.t('/a?c', ['/a?c', '/a-c'], ['', '/', '/a??c', '/ac'])

    def test_wildcard_questionmark4(self):
        self.t('/f?o?a?', ['/foobar', '/foobar/'], ['/-oobar', '/fooba/'])

    def test_wildcard_questionmark5(self):
        self.t('/f??', ['/foo', '/foo/'], ['/f-/', '/f---'])

    def test_wildcard_star1(self):
        self.t('*', ['/', '/foo', '/foo/bar'], ['', '*'])

    def test_wildcard_star2(self):
        self.t('*/', ['/foo/', '/foo/bar', '/foo/bar/'], ['', '*', '*/', '/'])

    def test_wildcard_star3(self):
        self.t('/a*c', ['/ac', '/a-c', '/a--c'], ['', '/', '/a-', '/-c'])

    def test_wildcard_star4(self):
        self.t('/f*o*a*', ['/foobar', '/foa/', '/fooba/'], ['/-oobar'])

    def test_wildcard_star5(self):
        self.t('/f**', ['/foo', '/foo/', '/f', '/f/'], ['/-', '/-/f'])

    def test_wildcard_star6(self):
        self.t('/a**c', ['/ac', '/ac/', '/abc', '/abc/', '/abbc', '/abbc/'],
               ['/', '/ab', '/a/bc/'])

    def test_wildcard_globstar1(self):
        self.t('**', ['/', '/foo', '/foo/', '/foo/bar'], ['', '*', '**'])

    def test_wildcard_globstar2(self):
        self.t('/**', ['/', '/foo', '/foo/', '/foo/bar'], ['', '*', '**'])

    def test_wildcard_globstar3(self):
        self.t('**/', ['/foo/', '/foo/bar'], ['', '*', '**', '/', '/foo'])

    def test_wildcard_globstar4(self):
        self.t('**/foo/bar',
               ['/foo/bar', '/-/foo/bar', '/-/-/foo/bar'],
               ['/', '/bar', '/foo'])

    def test_wildcard_globstar5(self):
        self.t('/foo/bar/**',
               ['/foo/bar/', '/foo/bar/-', '/foo/bar/-/-'],
               ['/', '/bar', '/foo', '/foo/bar', '/-foo/bar/', '/-/foo/bar/'])

    def test_wildcard_globstar6(self):
        self.t('/foo/bar/**/**',
               ['/foo/bar/', '/foo/bar/-', '/foo/bar/-/-'],
               ['/', '/bar', '/foo', '/foo/bar', '/-foo/bar/', '/-/foo/bar/'])

    def test_wildcard_globstar7(self):
        self.t('/foo/bar/**/',
               ['/foo/bar/-/', '/foo/bar/-/-'],
               ['/foo/bar/', '/foo/bar/-'])

    def test_wildcard_globstar8(self):
        self.t('/foo/bar/**/**/',
               ['/foo/bar/-/', '/foo/bar/-/-'],
               ['/foo/bar/', '/foo/bar/-'])

    def test_wildcard_globstar9(self):
        self.t('/foo/**/bar',
               ['/foo/bar', '/foo/-/bar', '/foo/-/-/bar'],
               ['/', '/bar', '/foo', '/foo-/bar', '/foo/-bar'])

    def test_negate(self):
        for negate in [False, True]:
            p = convert_to_re(('!' if negate else '') + 'foo')
            self.t(p, ['/foo', '/foo/bar', '/bar/foo', '/bar/foo/bar'],
                   ['/', '/bar', '/foobar'])
            self.assertEqual(p.negate, negate)

    def test_quoted1(self):
        self.t('\\?', ['/?', '/?/'], ['', '/', '/-'])

    def test_quoted2(self):
        self.t('\\!', ['/!', '/!/'], ['', '/', '/-'])

    def test_quoted3(self):
        self.t('\\[', ['/[', '/[/'], ['', '/', '/-'])

    def test_quoted4(self):
        self.t('\\#', ['/#', '/#/'], ['', '/', '/-'])

    def test_quoted5(self):
        self.t('\\ ', ['/ ', '/ /'], ['', '/', '/-'])

    def test_quoted6(self):
        self.t('\\*', ['/*', '/*/'], ['', '/', '/-'])

    def test_quoted7(self):
        self.t('\\*\\*', ['/**', '/**/'], ['', '/', '/-', '/--'])

    def test_escape1(self):
        self.t(escape('?'), ['/?', '/?/'], ['', '/', '/-'])

    def test_escape2(self):
        self.t(escape('!'), ['/!', '/!/'], ['', '/', '/-'])

    def test_escape3(self):
        self.t(escape('['), ['/[', '/[/'], ['', '/', '/-'])

    def test_escape4(self):
        self.t(escape('#'), ['/#', '/#/'], ['', '/', '/-'])

    def test_escape5(self):
        self.t(escape(' '), ['/ ', '/ /'], ['', '/', '/-'])

    def test_escape6(self):
        self.t(escape('*'), ['/*', '/*/'], ['', '/', '/-'])

    def test_escape7(self):
        self.t(escape('**'), ['/**', '/**/'], ['', '/', '/-', '/--'])
