#!/usr/bin/python

import unittest
from ic_analysis import Cluster


class TestCluster(unittest.TestCase):

    def test_simple_merge(self):
        c1 = Cluster.Cluster('abc.*def')
        c2 = Cluster.Cluster('def.*ghi')
        c3 = c1.merge(c2)
        self.assertEqual(c3.pattern, '^.*def.*$', 'merge failed with ' + c3.pattern)

    def test_simple_merge_line_start(self):
        c1 = Cluster.Cluster('abc.*def')
        c2 = Cluster.Cluster('abc.*ghi')
        c3 = c1.merge(c2)
        self.assertEqual(c3.pattern, '^abc.*$', 'merge failed with ' + c3.pattern)

    def test_simple_merge_line_end(self):
        c1 = Cluster.Cluster('abc.*ghi')
        c2 = Cluster.Cluster('def.*ghi')
        c3 = c1.merge(c2)
        self.assertEqual(c3.pattern, '^.*ghi$', 'merge failed with ' + c3.pattern)

    def test_empty_merge(self):
        c1 = Cluster.Cluster('')
        c2 = Cluster.Cluster('def.*ghi')
        c3 = c1.merge(c2)
        self.assertEqual(c3.pattern, '^.*$', 'merge failed with ' + c3.pattern)

    def test_empty_merge2(self):
        c1 = Cluster.Cluster('')
        c2 = Cluster.Cluster('')
        c3 = c1.merge(c2)
        self.assertEqual(c3.pattern, '^$', 'merge failed with ' + c3.pattern)


if __name__ == '__main__':
    unittest.main()
