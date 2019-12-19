#!/usr/bin/python
# coding=utf-8

import unittest
from ic_analysis.Cluster import Cluster
from ic_analysis.Token import Token
from ic_analysis.SequenceMatcherCache import SequenceMatcherCache


class TestCluster(unittest.TestCase):

    def test_simple_match_line(self):
        c = Cluster('abc def')
        self.assertTrue(c.matches_line('abc def'), 'match fails with ' + str(c))
        self.assertFalse(c.matches_line('abc def ghi'), 'match fails with ' + str(c))
        self.assertFalse(c.matches_line('ghi abc def'), 'match fails with ' + str(c))
        self.assertFalse(c.matches_line('abc'), 'match fails with ' + str(c))

    def test_simple_match_tokens(self):
        c = Cluster()
        c.set_tokens([Token('abc'), Token('def', anybefore=True)])
        self.assertTrue(c.matches_line('abc XYZ def'), 'match fails with ' + str(c))
        self.assertTrue(c.matches_line('abcdef'), 'match fails with ' + str(c))
        self.assertFalse(c.matches_line('.. abc def'), 'match fails with ' + str(c))
        self.assertFalse(c.matches_line('abc XYZ def ..'), 'match fails with ' + str(c))

    def test_cluster_match(self):
        c1 = Cluster()
        c1.set_tokens([Token('abc'), Token('def', anybefore=True), Token('', anybefore=True)])
        c2 = Cluster()
        c2.set_tokens([Token('abc'), Token('def', anybefore=True)])
        self.assertTrue(c1.matches_cluster(c2), 'cluster match failed with ' + str(c1) + " and " + str(c2))
        c3 = Cluster()
        c3.set_tokens([Token('abcdef'), Token(r'\\.* ^', anybefore=True)])
        self.assertTrue(c1.matches_cluster(c3), 'cluster match failed with ' + str(c1) + " and " + str(c3))
        c4 = Cluster()
        c4.set_tokens([Token('abc'), Token('', anybefore=True)])
        self.assertFalse(c1.matches_cluster(c4), 'cluster match failed with ' + str(c1) + " and " + str(c4))

    def test_merge_sequence(self):
        c1 = Cluster('abc def')
        c2 = Cluster('foo bar def')
        seq = c1.construct_merge_sequence(c2, 0.5, SequenceMatcherCache())
        self.assertEqual(seq.weight, 5,
                         'merge failed with weight ' + str(seq.weight) + ', clusters ' + str(c1) + " and " + str(c2))

    def test_simple_merge_line_start(self):
        c1 = Cluster('abc def')
        c2 = Cluster('abc ghi')
        m = SequenceMatcherCache()
        seq = c1.construct_merge_sequence(c2, 0.5, m)
        c3 = Cluster.new_cluster_from_merge_sequence(seq, m)
        self.assertEqual(c3.to_text(), 'abc @@',
                         'merge failed with ' + c3.to_text())

    def test_merge_overlapping(self):
        c1 = Cluster()
        c1.set_tokens([Token('abc'), Token('def')])
        c2 = Cluster()
        c2.set_tokens([Token('abcd'), Token('ef')])
        m = SequenceMatcherCache()
        seq = c1.construct_merge_sequence(c2, 0.5, m)
        c3 = Cluster.new_cluster_from_merge_sequence(seq, m)
        self.assertEqual(c3.to_text(), 'abc@@ef',
                         'merge failed with ' + c3.to_text())


    def test_simple_merge_line_end(self):
        c1 = Cluster('abc ghi')
        c2 = Cluster('def yyy ghi')
        m = SequenceMatcherCache()
        seq = c1.construct_merge_sequence(c2, 0.2, m)
        c3 = Cluster.new_cluster_from_merge_sequence(seq, m)
        self.assertEqual(c3.to_text(), '@@ ghi',
                         'merge failed with ' + c3.to_text())

    def test_merge_pattern_end_with_different_special_character(self):
        c1 = Cluster('abcdef.')
        c2 = Cluster('abcdef*')
        m = SequenceMatcherCache()
        seq = c1.construct_merge_sequence(c2, 0.5, m)
        c3 = Cluster.new_cluster_from_merge_sequence(seq, m)
        self.assertEqual(c3.to_text(), 'abcdef@@',
                         'merge failed with ' + c3.to_text())

    def test_empty_merge(self):
        c1 = Cluster('')
        c2 = Cluster('def xxx ghi')
        m = SequenceMatcherCache()
        seq = c1.construct_merge_sequence(c2, 0.5, m)
        self.assertIsNone(seq, 'merge should have failed')

    def test_empty_merge2(self):
        c1 = Cluster('')
        c2 = Cluster('')
        m = SequenceMatcherCache()
        seq = c1.construct_merge_sequence(c2, 0.5, m)
        self.assertIsNone(seq, 'merge should have failed')

    def test_nothing_in_common_merge(self):
        c1 = Cluster('abc')
        c2 = Cluster('def')
        m = SequenceMatcherCache()
        seq = c1.construct_merge_sequence(c2, 0.5, m)
        self.assertIsNone(seq, 'merge should have failed')

    def test_complex_merge(self):
        c1 = Cluster('a def xx defghijkl aaa testing')
        c2 = Cluster('abc defghijkl def xx testtest')
        m = SequenceMatcherCache()
        seq = c1.construct_merge_sequence(c2, 0.5, m)
        c3 = Cluster.new_cluster_from_merge_sequence(seq, m)
        self.assertEqual(c3.to_text(), 'a@@ defghijkl @@ test@@',
                         'merge failed with ' + c3.to_text())

    def test_special_characters_merge(self):
        c1 = Cluster(r'abc\^yy.*rret\$')
        c2 = Cluster(r'ab\^yy.*rr xx \$')
        m = SequenceMatcherCache()
        seq = c1.construct_merge_sequence(c2, 0.5, m)
        c3 = Cluster.new_cluster_from_merge_sequence(seq, m)
        self.assertEqual(c3.to_text(), r'ab@@\^yy.*rr@@\$',
                         'merge failed with ' + c3.to_text())

    def test_utf8_merge(self):
        c1 = Cluster(r'ÄÄÖÖ abcde Åg')
        c2 = Cluster(r'ÄÄOO abcxxx Å')
        m = SequenceMatcherCache()
        seq = c1.construct_merge_sequence(c2, 0.5, m)
        c3 = Cluster.new_cluster_from_merge_sequence(seq, m)
        self.assertEqual(c3.to_text(), r'ÄÄ@@ abc@@ Å@@',
                         'merge failed with ' + c3.to_text())

    def test_merge_tokens_last_matching_partially(self):
        c1 = Cluster()
        c1.set_tokens([Token('abc'), Token('deftext', anybefore=True)])
        c2 = Cluster()
        c2.set_tokens([Token('abc'), Token('deftext2', anybefore=True)])
        m = SequenceMatcherCache()
        seq = c1.construct_merge_sequence(c2, 0.5, m)
        self.assertEqual(str(seq), '[abc==abc][deftext==deftext2]', 'Sequence was ' + str(seq))

    def test_merge_tokens_last_matching_first(self):
        c1 = Cluster()
        c1.set_tokens([Token('abc'), Token('def', anybefore=True)])
        c2 = Cluster()
        c2.set_tokens([Token('def'), Token('yyyyy', anybefore=True)])
        m = SequenceMatcherCache()
        seq = c1.construct_merge_sequence(c2, 0.5, m)
        self.assertEqual(str(seq), '[def==def][==]', 'Sequence was ' + str(seq))

    def test_merge_tokens_last_of_second_matching_from_first(self):
        c1 = Cluster()
        c1.set_tokens([Token('abc'), Token('def', anybefore=True)])
        c2 = Cluster()
        c2.set_tokens([Token('yyy'), Token('abc', anybefore=True)])
        m = SequenceMatcherCache()
        seq = c1.construct_merge_sequence(c2, 0.5, m)
        self.assertEqual(str(seq), '[abc==abc][==]', 'Sequence was ' + str(seq))

    def test_merge_clusters_with_one_token(self):
        c1 = Cluster()
        c1.set_tokens([Token('abc')])
        c2 = Cluster()
        c2.set_tokens([Token('abc')])
        m = SequenceMatcherCache()
        seq = c1.construct_merge_sequence(c2, 0.5, m)
        self.assertEqual(str(seq), '[abc==abc]', 'Sequence was ' + str(seq))


if __name__ == '__main__':
    unittest.main()
