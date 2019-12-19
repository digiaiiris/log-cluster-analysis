#!/usr/bin/python
# coding=utf-8

import unittest
from ic_analysis.Token import Token
from ic_analysis.SequenceMatcherCache import SequenceMatcherCache


class TestSequenceMatcherCache(unittest.TestCase):

    def test_cache(self):
        t1 = Token('abc')
        t2 = Token('def')
        t3 = Token('ghi')
        s = SequenceMatcherCache()
        t1t2 = s.get_matcher(t1, t2)
        t1t2_second = s.get_matcher(t1, t2)
        t2t1 = s.get_matcher(t2, t1)
        t1t3 = s.get_matcher(t1, t3)
        self.assertIs(t1t2, t1t2_second)
        self.assertIsNot(t1t2, t2t1)
        self.assertIsNot(t1t2, t1t3)


if __name__ == '__main__':
    unittest.main()
