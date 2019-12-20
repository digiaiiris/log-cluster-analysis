#!/usr/bin/python

import unittest
from ic_analysis import Analyzer
import pprint


class TestCluster(unittest.TestCase):

    def test_simple_analysis(self):
        a = Analyzer.Analyzer(maxlimit=2, minsimilarity=0.3, minprecision=0.3)
        a.analyze_line('abc def ghi')
        self.assertEqual(a.clusters[0].to_text(), 'abc def ghi', str(a))

        a.analyze_line('abc xxx 123 123 ghi')
        self.assertEqual(a.clusters[1].to_text(), 'abc xxx 123 123 ghi', str(a))

        a.analyze_line('foo bar')

        self.assertEqual(len(a.clusters), 2, 'merge failed ' + str(a))
        self.assertEqual(a.clusters[0].to_text(), r'foo bar', 'analyzer failed with ' + str(a))
        self.assertEqual(a.clusters[1].to_text(), r'abc @@3,11@@ ghi', 'analyzer failed with ' + str(a))

    def test_high_similarity_max_limit(self):
        a = Analyzer.Analyzer(maxlimit=2, minsimilarity=0.99)
        a.analyze_line('foo bar')
        a.analyze_line('foo ghi xxx')
        a.analyze_line('bar xxx')

        # Because of the high minsimilarity it should not merge them but remove the oldest
        self.assertEqual(len(a.clusters), 2, str(a))
        self.assertEqual(a.clusters[0].to_text(), r'foo ghi xxx')
        self.assertEqual(a.clusters[1].to_text(), r'bar xxx')


if __name__ == '__main__':
    unittest.main()
