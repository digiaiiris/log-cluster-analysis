#!/usr/bin/python

import re
from difflib import SequenceMatcher


class MergeSequence(object):
    """A possible sequence of token pairs of two merging clusters"""

    def __init__(self, previous, token1, token2, anybefore, weight):
        """Initializes MergeSequence object
           Add a token pair to the sequence meaning that these tokens
           would be merged together

        :param previous: previous MergeSequence that this sequence is
                         branched from; can be None
        :param token1: token from the first cluster
        :param token2: token from the second cluster
        :param anybefore: there were skipped token(s) in either cluster before
                          these tokens
        :param weight: similarity of tokens weighted with their lengths,
                       roughly the number of similar subsequent characters
        """
        self.previous = previous
        self.token1 = token1
        self.token2 = token2
        self.anybefore = anybefore
        if previous:
            self.weight = weight + previous.weight
        else:
            self.weight = weight

    def generate_cluster(self, matchercache):
        """Merge the token pairs and generate a cluster of them

        :returns: Cluster object generated
        """

        # First construct an ordered list of token pairs to merge
        pairs = []
        seq = self
        while seq is not None:
            pairs.insert(0, (seq.token1, seq.token2, seq.anybefore))
            seq = seq.previous

        for token1, token2, anybefore in pairs:
            mergedlist = token1.merge(token2, matchercache.get(token1, token2))
            if anybefore:
                # Mark to the first token in the merged list that there were
                # some skipped tokens ie characters before this token pair
                mergedlist[0].anybefore = True
            tokens.extend(mergedlist)

        c = Cluster()
        c.set_tokens(tokens)
        return c


if __name__ == "__main__":
    pass
