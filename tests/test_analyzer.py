#!/usr/bin/python

import unittest
from ic_analysis import Analyzer
import pprint


class TestCluster(unittest.TestCase):

    def test_simple_analysis(self):
        a = Analyzer.Analyzer(maxnum=2)
        a.analyze_line('abc def ghi')
        a.analyze_line('abc xxx 123 123 ghi')
        a.analyze_line('foo bar')

        self.assertEqual(a.clusters[0].sequence, 'foo\ bar',
                         'analyzer failed with ' + str(a))
        self.assertEqual(a.clusters[1].sequence, 'abc\ .*\ ghi',
                         'analyzer failed with ' + str(a))


if __name__ == '__main__':
    unittest.main()
