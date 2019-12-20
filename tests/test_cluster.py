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
        c.set_tokens([Token('abc'), Token('def', maxwildcards=5)])
        self.assertTrue(c.matches_line('abc XYZ def'), 'match fails with ' + str(c))
        self.assertTrue(c.matches_line('abcdef'), 'match fails with ' + str(c))
        self.assertFalse(c.matches_line('.. abc def'), 'match fails with ' + str(c))
        self.assertFalse(c.matches_line('abc XYZ def ..'), 'match fails with ' + str(c))

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
        self.assertEqual(c3.to_text(), 'abc @@3,3@@', 'merge failed with ' + c3.to_text())

    def test_merge_overlapping(self):
        c1 = Cluster()
        c1.set_tokens([Token('abc'), Token('def')])
        c2 = Cluster()
        c2.set_tokens([Token('abcd'), Token('ef')])
        m = SequenceMatcherCache()
        seq = c1.construct_merge_sequence(c2, 0.5, m)
        c3 = Cluster.new_cluster_from_merge_sequence(seq, m)
        self.assertEqual(c3.to_text(), 'abc@@0,2@@ef', 'merge failed with ' + c3.to_text())

    def test_simple_merge_line_end(self):
        c1 = Cluster('abc ghi')
        c2 = Cluster('def yyy ghi')
        m = SequenceMatcherCache()
        seq = c1.construct_merge_sequence(c2, 0.2, m)
        c3 = Cluster.new_cluster_from_merge_sequence(seq, m)
        self.assertEqual(c3.to_text(), '@@3,7@@ ghi', 'merge failed with ' + c3.to_text())

    def test_merge_pattern_end_with_different_special_character(self):
        c1 = Cluster('abcdef.')
        c2 = Cluster('abcdef*')
        m = SequenceMatcherCache()
        seq = c1.construct_merge_sequence(c2, 0.5, m)
        c3 = Cluster.new_cluster_from_merge_sequence(seq, m)
        self.assertEqual(c3.to_text(), 'abcdef@@1,1@@', 'merge failed with ' + c3.to_text())

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
        self.assertEqual(c3.to_text(), 'a@@2,7@@ defghijkl @@3,6@@ test@@3,4@@', 'merge failed with ' + c3.to_text())

    def test_special_characters_merge(self):
        c1 = Cluster(r'abc\^yy.*rret\$')
        c2 = Cluster(r'ab\^yy.*rr xx \$')
        m = SequenceMatcherCache()
        seq = c1.construct_merge_sequence(c2, 0.5, m)
        c3 = Cluster.new_cluster_from_merge_sequence(seq, m)
        self.assertEqual(c3.to_text(), r'ab@@0,1@@\^yy.*rr@@2,4@@\$', 'merge failed with ' + c3.to_text())

    def test_utf8_merge(self):
        c1 = Cluster(r'ÄÄÖÖ abcde Åg')
        c2 = Cluster(r'ÄÄOO abcxxx Å')
        m = SequenceMatcherCache()
        seq = c1.construct_merge_sequence(c2, 0.5, m)
        c3 = Cluster.new_cluster_from_merge_sequence(seq, m)

        # Merge handles utf-8 characters as having a length of 2
        # That's why between ÄÄ and ' abc' there are 4 characters ('ÖÖ')
        self.assertEqual(c3.to_text(), r'ÄÄ@@2,4@@ abc@@2,3@@ Å@@0,1@@', 'merge failed with ' + c3.to_text())

    def test_merge_tokens_last_matching_partially(self):
        c1 = Cluster()
        c1.set_tokens([Token('abc'), Token('deftext', maxwildcards=5)])
        c2 = Cluster()
        c2.set_tokens([Token('abc'), Token('deftext2', maxwildcards=5)])
        m = SequenceMatcherCache()
        seq = c1.construct_merge_sequence(c2, 0.5, m)
        self.assertEqual(str(seq), '[abc==abc][+{0,5}deftext==+{0,5}deftext2]', 'Sequence was ' + str(seq))

    def test_merge_tokens_last_matching_first(self):
        c1 = Cluster()
        c1.set_tokens([Token('abc'), Token('def', maxwildcards=5)])
        c2 = Cluster()
        c2.set_tokens([Token('def'), Token('yyyyy', maxwildcards=5)])
        m = SequenceMatcherCache()
        seq = c1.construct_merge_sequence(c2, 0.5, m)
        self.assertEqual(str(seq), '.{0,3}[+{0,5}def==def].{0,10}[==]', 'Sequence was ' + str(seq))

    def test_merge_tokens_last_of_second_matching_from_first(self):
        c1 = Cluster()
        c1.set_tokens([Token('abc'), Token('def', maxwildcards=5)])
        c2 = Cluster()
        c2.set_tokens([Token('yyy'), Token('abc', maxwildcards=5)])
        m = SequenceMatcherCache()
        seq = c1.construct_merge_sequence(c2, 0.5, m)
        self.assertEqual(str(seq), '.{0,3}[abc==+{0,5}abc].{0,8}[==]', 'Sequence was ' + str(seq))

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
