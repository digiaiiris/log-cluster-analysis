#!/usr/bin/python

import re
from SequenceMatcherCache import SequenceMatcherCache


class MergeSequenceCache(object):
    """Caches merge sequences between clusters"""

    def __init__(self, minsimilarity):
        """Initializes object"""

        self.minsimilarity = minsimilarity

        # Dictionary key is tuple containing two cluster objects
        # Dictionary value is MergeSequence object
        # Since merge is interchangable, the order of cluster objects
        # in the tuple is swappable and does not matter
        self.cache = dict()

        # Dictionary key is tuple containing two cluster objects
        # Dictionary value is SequenceMatcherCache object
        # Cluster object values are not interchangable because
        # merge of tokens relies on the order of tokens (a and b)
        self.seqmatchercache = dict()

    def get_merge_sequence(self, cluster1, cluster2):
        """Gets/constructs a merge sequence between two clusters

        :returns: MergeSequence object
        """

        # First find if it already finds in the cache
        for (c1, c2) in self.cache:
            if (c1 is cluster1 and c2 is cluster2) or \
               (c2 is cluster1 and c1 is cluster2):
                return self.cache.get((c1, c2))

        # Not found in cache, so generate it
        m = self.get_sequence_matcher(cluster1, cluster2)
        seq = cluster1.construct_merge_sequence(cluster2, self.minsimilarity, m)
        self.cache[(cluster1, cluster2)] = seq
        return seq

    def get_sequence_matcher(self, cluster1, cluster2):
        """Gets/constructs a sequence matcher cache for two clusters

        :returns: SequenceMatcherCache object
        """

        # First find if it already finds in the cache
        for (c1, c2) in self.seqmatchercache:
            if c1 is cluster1 and c2 is cluster2:
                return self.seqmatchercache.get((c1, c2))

        m = SequenceMatcherCache()
        self.seqmatchercache[(cluster1, cluster2)] = m
        return m

    def remove_cluster(self, cluster):
        """Remove cluster related things from cache"""

        keys_to_delete = []
        for (c1, c2) in self.cache:
            if c1 is cluster or c2 is cluster:
                keys_to_delete.append((c1, c2))
        for (c1, c2) in keys_to_delete:
            del self.cache[(c1, c2)]

        keys_to_delete = []
        for (c1, c2) in self.seqmatchercache:
            if c1 is cluster or c2 is cluster:
                keys_to_delete.append((c1, c2))
        for (c1, c2) in keys_to_delete:
            del self.seqmatchercache[(c1, c2)]


if __name__ == "__main__":
    pass
