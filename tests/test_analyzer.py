#!/usr/bin/python

import unittest
from ic_analysis import Analyzer
import pprint


class TestCluster(unittest.TestCase):

    def test_simple_analysis(self):
        a = Analyzer.Analyzer(softmaxlimit=2)
        c1 = a.analyze_line('abc def ghi')
        self.assertEqual(c1.pattern, r'abc\ def\ ghi', str(a))

        c2 = a.analyze_line('abc xxx 123 123 ghi')
        self.assertEqual(c2.pattern, r'abc\ xxx\ 123\ 123\ ghi', str(a))

        c3 = a.analyze_line('foo bar')
        self.assertEqual(c3.pattern, r'foo\ bar', str(a))

        self.assertEqual(len(a.clusters), 2, 'merge failed ' + str(a))
        self.assertEqual(a.clusters[0].pattern, r'foo\ bar',
                         'analyzer failed with ' + str(a))
        self.assertEqual(a.clusters[1].pattern, r'abc\ .*\ ghi',
                         'analyzer failed with ' + str(a))

    def test_merged_return_value(self):
        a = Analyzer.Analyzer(softmaxlimit=2)
        a.analyze_line('foo bar gee')
        a.analyze_line('ghi')
        c = a.analyze_line(r'foo bar')
        self.assertEqual(c.pattern, r'foo\ bar.*', str(a))

    def test_high_similarity(self):
        a = Analyzer.Analyzer(softmaxlimit=2, minsimilarity=0.99)
        a.analyze_line('foo bar')
        a.analyze_line('foo ghi xxx')
        a.analyze_line('bar xxx')

        # Because of the high minsimilarity it should not merge them
        self.assertEqual(len(a.clusters), 3, str(a))


if __name__ == '__main__':
    unittest.main()
