#!/usr/bin/python
# coding=utf-8

import unittest
from ic_analysis.Cluster import Cluster
from ic_analysis.SequenceMatcherCache import SequenceMatcherCache
from ic_analysis.MergeSequenceCache import MergeSequenceCache


class TestMergeSequenceCache(unittest.TestCase):

    def test_seq_cache(self):
        c1 = Cluster('abcdef')
        c2 = Cluster('abcdef1')
        c3 = Cluster('abcdef2')
        m = MergeSequenceCache(minsimilarity = 0.5)

        # Test that caching works and clusters are interchangable in cache
        seq_c1_c2 = m.get_merge_sequence(c1, c2)
        seq_c1_c2_second = m.get_merge_sequence(c1, c2)
        seq_c2_c1 = m.get_merge_sequence(c2, c1)
        seq_c1_c3 = m.get_merge_sequence(c1, c3)
        self.assertIs(seq_c1_c2, seq_c1_c2_second)
        self.assertIs(seq_c1_c2, seq_c2_c1)
        self.assertIsNot(seq_c1_c2, seq_c1_c3)

        # Test that cache is cleared for a cluster when it's removed
        m.remove_cluster(c2)
        seq_new_c1_c2 = m.get_merge_sequence(c1, c2)
        seq_new_c1_c3 = m.get_merge_sequence(c1, c3)
        self.assertIsNot(seq_c1_c2, seq_new_c1_c2)
        self.assertIs(seq_c1_c3, seq_new_c1_c3)

    def test_matcher_cache(self):
        c1 = Cluster('abcdef')
        c2 = Cluster('abcdef1')
        c3 = Cluster('abcdef2')
        m = MergeSequenceCache(minsimilarity = 0.5)

        # Test that caching works and clusters are not interchangable in cache
        m_c1_c2 = m.get_sequence_matcher(c1, c2)
        m_c1_c2_second = m.get_sequence_matcher(c1, c2)
        m_c2_c1 = m.get_sequence_matcher(c2, c1)
        m_c1_c3 = m.get_sequence_matcher(c1, c3)
        self.assertIs(m_c1_c2, m_c1_c2_second)
        self.assertIsNot(m_c1_c2, m_c2_c1)
        self.assertIsNot(m_c1_c2, m_c1_c3)

        # Test that cache is cleared for a cluster when it's removed
        m.remove_cluster(c2)
        m_new_c1_c2 = m.get_sequence_matcher(c1, c2)
        m_new_c1_c3 = m.get_sequence_matcher(c1, c3)
        self.assertIsNot(m_c1_c2, m_new_c1_c2)
        self.assertIs(m_c1_c3, m_new_c1_c3)

if __name__ == '__main__':
    unittest.main()
