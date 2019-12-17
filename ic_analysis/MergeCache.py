#!/usr/bin/python

import re
from difflib import SequenceMatcher


class MergeCache(object):
    """Caches merge sequences between clusters"""

    def __init__(self):
        """Initializes MergeCache object"""

        # Dictionary key is tuple containing two cluster objects
        # Dictionary value is MergeSequence object
        # Since merge is interchangable, the order of cluster objects
        # in the tuple is swappable and does not matter
        self.cache = dict()

        # Dictionary key is cluster object
        # Dictionary value is dictionary:
        #   key: tuple of two Token objects
        #   value: SequenceMatcher object
        self.seqmatchercache = dict()

    def get_merge_sequence(self, c1, c2):
        """Gets/constructs a merge sequence between two clusters"""

        :returns: MergeSequence object
        """

        # First find if it already finds in the cache
        if (c1, c2) in self.cache:
            return self.cache.get((c1, c2))
        if (c2, c1) in self.cache:
            return self.cache.get((c2, c1))

        # Not found in cache, so generate it
        seq = c1.construct_merge_sequence(c2, minsimilarity, matchercache)
        self.cache[(c1, c1)] = seq
        return seq

    def get_sequence_matcher(self, token1, token2):
        """

    def remove_cluster(self, c):
        """Remove cluster related things from cache"""

if __name__ == "__main__":
    pass
