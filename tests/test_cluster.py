#!/usr/bin/python

import unittest
from ic_analysis import Cluster


class TestCluster(unittest.TestCase):

    def test_simple_match(self):
        c = Cluster.Cluster('^abc .* def$')
        self.assertTrue(c.matches('abc abc def'), 'match fails with ' + str(c))

    def test_simple_merge(self):
        c1 = Cluster.Cluster('^abc.*def$')
        c2 = Cluster.Cluster('^def.*ghi$')
        c3 = c1.merge(c2)
        self.assertEqual(c3.sequence, '.*def.*',
                         'merge failed with ' + c3.sequence)

    def test_simple_merge_line_start(self):
        c1 = Cluster.Cluster('^abc.*def$')
        c2 = Cluster.Cluster('^abc.*ghi$')
        c3 = c1.merge(c2)
        self.assertEqual(c3.sequence, 'abc.*',
                         'merge failed with ' + c3.sequence)

    def test_simple_merge_line_end(self):
        c1 = Cluster.Cluster('^abc.*ghi$')
        c2 = Cluster.Cluster('^def.*ghi$')
        c3 = c1.merge(c2)
        self.assertEqual(c3.sequence, '.*ghi',
                         'merge failed with ' + c3.sequence)

    def test_empty_merge(self):
        c1 = Cluster.Cluster('^$')
        c2 = Cluster.Cluster('^def.*ghi$')
        c3 = c1.merge(c2)
        self.assertEqual(c3.sequence, '.*', 'merge failed with ' + c3.sequence)

    def test_empty_merge2(self):
        c1 = Cluster.Cluster('^$')
        c2 = Cluster.Cluster('^$')
        c3 = c1.merge(c2)
        self.assertEqual(c3.sequence, '', 'merge failed with ' + c3.sequence)

    def test_nothing_in_common_merge(self):
        c1 = Cluster.Cluster('^abc$')
        c2 = Cluster.Cluster('^def$')
        c3 = c1.merge(c2)
        self.assertEqual(c3.sequence, '.*', 'merge failed with ' + c3.sequence)

    def test_complex_merge(self):
        c1 = Cluster.Cluster('^a def xx defghi aaa testing$')
        c2 = Cluster.Cluster('^abc defghi def xx testtest$')
        c3 = c1.merge(c2)
        self.assertEqual(c3.sequence, 'a.* defghi .* test.*',
                         'merge failed with ' + c3.sequence)

    def test_special_characters_merge(self):
        c1 = Cluster.Cluster('^abc\\^aret\\$$')
        c2 = Cluster.Cluster('^ab\\^ar xx \\$$')
        c3 = c1.merge(c2)
        self.assertEqual(c3.sequence, 'ab.*\\^ar.*\\$',
                         'merge failed with ' + c3.sequence)


if __name__ == '__main__':
    unittest.main()
