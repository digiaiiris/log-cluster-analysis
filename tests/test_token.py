#!/usr/bin/python
# coding=utf-8

import unittest
from difflib import SequenceMatcher
from ic_analysis.Token import Token


class TestToken(unittest.TestCase):

    def test_lengths(self):
        t = Token('abc', minwildcards=5, maxwildcards=10)
        self.assertEqual(t.minlen, 8)
        self.assertEqual(t.maxlen, 13)

    def test_similar_tokens_merge(self):
        t1 = Token('abc', minwildcards=5, maxwildcards=10)
        t2 = Token('abc', minwildcards=7, maxwildcards=13)
        m = SequenceMatcher(a=t1.text, b=t2.text)
        t = t1.merge(t2, m)
        self.assertEqual(len(t), 1)
        self.assertEqual(t[0].text, 'abc')
        self.assertEqual(t[0].minlen, 8)
        self.assertEqual(t[0].maxlen, 16)

    def test_merge_different_endings(self):
        t1 = Token('abc def', minwildcards=5, maxwildcards=10)
        t2 = Token('abc ghi', minwildcards=7, maxwildcards=13)
        m = SequenceMatcher(a=t1.text, b=t2.text)
        t = t1.merge(t2, m)
        self.assertEqual(len(t), 2)
        self.assertEqual(t[0].text, 'abc ')
        self.assertEqual(t[0].minlen, 9)
        self.assertEqual(t[0].maxlen, 17)
        self.assertEqual(t[1].text, '')
        self.assertEqual(t[1].minlen, 3)
        self.assertEqual(t[1].maxlen, 3)

    def test_merge_different_beginnings(self):
        t1 = Token('def abc', minwildcards=5, maxwildcards=10)
        t2 = Token('ghi abc', minwildcards=7, maxwildcards=13)
        m = SequenceMatcher(a=t1.text, b=t2.text)
        t = t1.merge(t2, m)
        self.assertEqual(len(t), 1)
        self.assertEqual(t[0].text, ' abc')
        self.assertEqual(t[0].minlen, 12)
        self.assertEqual(t[0].maxlen, 20)


if __name__ == '__main__':
    unittest.main()
