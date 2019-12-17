#!/usr/bin/python

import re


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

    def get_merge_sequence(self, c1, c2):
        """Gets/constructs a merge sequence between two clusters

        :returns: MergeSequence object
        """

        # First find if it already finds in the cache
        if (c1, c2) in self.cache:
            return self.cache.get((c1, c2))
        if (c2, c1) in self.cache:
            return self.cache.get((c2, c1))

        # Not found in cache, so generate it
        seq = c1.construct_merge_sequence(c2, self.minsimilarity, matchercache)
        self.cache[(c1, c1)] = seq
        return seq

    def get_sequence_matcher(self, token1, token2):
        """Gets/constructs a sequence matcher cache for two clusters

        :returns: SequenceMatcherCache object
        """

        cacheobj = self.matchercache.get((c1, c2))
        if cacheobj:
            return cacheobj

        m = SequenceMatcherCache()
        matchercache[(token1, token2)] = m
        return m

    def remove_cluster(self, c):
        """Remove cluster related things from cache"""

        keys_to_delete = []
        for (c1, c2) in self.cache:
            if c1 == c or c2 == c:
                keys_to_delete.append((c1, c2))
        for (c1, c2) in keys_to_delete:
            del self.cache[(c1, c2)]

        keys_to_delete = []
        for (c1, c2) in self.matchercache:
            if c1 == c or c2 == r:
                keys_to_delete.append((c1, c2))
        for (c1, c2) in keys_to_delete:
            del self.matchercache[(c1, c2)]


if __name__ == "__main__":
    pass
