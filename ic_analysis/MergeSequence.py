#!/usr/bin/python

import re
from difflib import SequenceMatcher


class MergeSequence(object):
    """A possible sequence of token pairs of two merging clusters"""

    def __init__(self, previous, token1, token2, minwildcards, maxwildcards, weight):
        """Initializes MergeSequence object
           Add a token pair to the sequence meaning that these tokens
           would be merged together

        :param previous: previous MergeSequence that this sequence is
                         branched from; can be None
        :param token1: token from the first cluster
        :param token2: token from the second cluster
        :param minwildcards: minimum number of skipped characters in either cluster before this token pair
        :param maxwildcards: maximum number of skipped characters in either cluster before this token pair
        :param weight: similarity ratio of tokens weighted with their lengths,
                       roughly equaling the number of similar subsequent characters of the tokens
        """
        self.previous = previous
        self.token1 = token1
        self.token2 = token2
        self.minwildcards = minwildcards
        self.maxwildcards = maxwildcards
        myminlen = min(len(token1.text), len(token2.text)) + min(token1.minwildcards, token2.minwildcards)
        mymaxlen = max(len(token1.text), len(token2.text)) + max(token1.maxwildcards, token2.maxwildcards)
        if previous:
            self.weight = previous.weight + weight
            self.minlen = previous.minlen + myminlen
            self.maxlen = previous.maxlen + mymaxlen
        else:
            self.weight = weight
            self.minlen = myminlen
            self.maxlen = mymaxlen

        # Estimate the merged cluster precision, ie. number of non-wildcard characters
        # in proportion to the length of the cluster
        self.precision = float(self.weight) / ((self.minlen + self.maxlen) / 2.0)

    def to_list(self):
        """Construct an ordered list of token pairs to merge

        :returns: List of tuples containing token1, token2, minwildcards, maxwildcards
        """

        # Traverse backward the merge sequence chain and insert at the start of list
        pairs = []
        seq = self
        while seq is not None:
            pairs.insert(0, (seq.token1, seq.token2, seq.minwildcards, seq.maxwildcards))
            seq = seq.previous

        return pairs

    def __str__(self):
        text = ""
        for t1, t2, minw, maxw in self.to_list():
            if minw > 0 or maxw > 0:
                text = text + '.{' + str(minw) + ',' + str(maxw) + '}'
            text = text + "[" + str(t1) + "==" + str(t2) + "]"
        return text

        
if __name__ == "__main__":
    pass
