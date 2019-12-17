#!/usr/bin/python

import unittest
from ic_analysis import Cluster


class TestCluster(unittest.TestCase):

    def test_simple_match(self):
        c = Cluster.Cluster('abc .* def', escape=False)
        self.assertTrue(c.matches_line('abc abc def'), 'match fails with ' + str(c))

    def test_simple_merge(self):
        c1 = Cluster.Cluster('abc.*def', escape=False)
        c2 = Cluster.Cluster('def.*ghi', escape=False)
        c3 = c1.merge(c2)
        self.assertEqual(c3.pattern, '.*def.*',
                         'merge failed with ' + c3.pattern)

    def test_simple_merge_line_start(self):
        c1 = Cluster.Cluster('abc.*def', escape=False)
        c2 = Cluster.Cluster('abc.*ghi', escape=False)
        c3 = c1.merge(c2)
        self.assertEqual(c3.pattern, 'abc.*',
                         'merge failed with ' + c3.pattern)

    def test_simple_merge_line_end(self):
        c1 = Cluster.Cluster('abc.*ghi', escape=False)
        c2 = Cluster.Cluster('def.*ghi', escape=False)
        c3 = c1.merge(c2)
        self.assertEqual(c3.pattern, '.*ghi',
                         'merge failed with ' + c3.pattern)

    def test_merge_pattern_end_with_different_special_character(self):
        c1 = Cluster.Cluster('abcdef.')
        c2 = Cluster.Cluster('abcdef*')
        c3 = c1.merge(c2)
        self.assertEqual(c3.pattern, 'abcdef.*',
                         'merge failed with ' + c3.pattern)

    def test_empty_merge(self):
        c1 = Cluster.Cluster('')
        c2 = Cluster.Cluster('def.*ghi', escape=False)
        c3 = c1.merge(c2)
        self.assertEqual(c3.pattern, '.*', 'merge failed with ' + c3.pattern)

    def test_empty_merge2(self):
        c1 = Cluster.Cluster('')
        c2 = Cluster.Cluster('')
        c3 = c1.merge(c2)
        self.assertEqual(c3.pattern, '', 'merge failed with ' + c3.pattern)

    def test_nothing_in_common_merge(self):
        c1 = Cluster.Cluster('abc')
        c2 = Cluster.Cluster('def')
        c3 = c1.merge(c2)
        self.assertEqual(c3.pattern, '.*', 'merge failed with ' + c3.pattern)

    def test_complex_merge(self):
        c1 = Cluster.Cluster('a def xx defghijkl aaa testing')
        c2 = Cluster.Cluster('abc defghijkl def xx testtest')
        c3 = c1.merge(c2)
        self.assertEqual(c3.pattern, r'a.*\ defghijkl\ .*\ test.*',
                         'merge failed with ' + c3.pattern)

    def test_special_characters_merge(self):
        c1 = Cluster.Cluster(r'abc\^yy.*rret\$')
        c2 = Cluster.Cluster(r'ab\^yy.*rr xx \$')
        c3 = c1.merge(c2)
        self.assertEqual(c3.pattern, r'ab.*\\\^yy\.\*rr.*\\\$',
                         'merge failed with ' + c3.pattern)


if __name__ == '__main__':
    unittest.main()
