#!/usr/bin/python

import re
from difflib import SequenceMatcher


class Cluster(object):
    """Analyzed cluster"""

    def __init__(self, line=None):
        """Initializes Cluster object with the given line

        :param line (optiona): line that is used per-se as a cluster
        """

        if line:
            self.tokens = [Token(line=line)]
            self.len = len(line)
            self.prog = re.compile('^' + re.escape(line) + '$')
        else:
            self.tokens = []
            self.len = 0

    def set_tokens(self, tokens):
        """Set a token list to this cluster"""

        self.tokens = tokens
        pattern = '^'

        # Note that if there can be any characters at the end of the line,
        # the last token is '' with anybefore=True
        for t in tokens:
            pattern = pattern + t.to_regex()
        pattern = pattern + '$'
        self.prog = re.compile(pattern)
        self.len = 0
        for t in self.tokens:
            self.len = self.len + t.len()

    def __str__(self):
        return self.prog.pattern

    def to_text(self, gapmarker='@@'):
        """Convert cluster to text representation, using gapmarker
           in place of .* (anything) and unescaping all else"""
        return re.sub(r'\\([^\\])', r'\1', self.prog.pattern.replace('.*', gapmarker))

    def matches_line(self, line):
        """Check if the cluster pattern matches the given line

        :returns: True if matches, False if not
        """

        if self.prog.match(line) is None:
            return False
        else:
            return True

    def matches_cluster(self, other):
        """Check if the cluster pattern matches the other cluster pattern

        :returns: True if matches (ie. this cluster replaces the other one)
        """

        # In cluster patterns, special regex characters like dot and asterix are
        # escaped by a backslash
        # To check if the cluster patterns overlap, first unescape the other one
        otherpattern = re.sub(r'\\([^\\])', r'\1', other.prog.pattern)
        return self.matches_line(otherpattern)

    def construct_merge_sequence(self, other, minsimilarity, matchercache):
        """Construct a merge sequence merging this cluster with another one

        :param other: the other cluster to merge with
        :param minsimilarity: min similarity in order to merge two tokens (0.0-1.0)
        :returns: merged cluster object or None is clusters are not similar enough
        """

        # List that contains tuple:
        #  - index reached in this cluster token list
        #  - index reached in the other cluster's token list
        #  - MergeSequence object constructed so far
        work_queue = [(0,0,None)]

        # Find a merge sequence with a maximum weight ie. similar subsequent matches
        maxweight = 0
        maxseq = None

        while len(work_queue) > 0:
            startidx, startjdx, seq = work_queue.pop()
            foundmatching = False
            for idx in range(startidx, len(self.tokens)):
                for jdx in range(startjdx, len(other.tokens)):
                    token1 = self.tokens[idx]
                    token2 = other.tokens[jdx]
                    if token1.len() == 0 or token2.len() == 0:
                        # Empty filler token (should be last token in cluster)
                        continue
                    m = matchercache.get(token1, token2)
                    if matcher.real_quick_ratio() >= minsimilarity:
                        weight = m.ratio() * (token1.len()+token2.len()) * 0.5
                        if weight >= minsimilarity:
                            # Tokens are similar enough so that we can branch
                            # into a new merge sequence path
                            seq2 = MergeSequence(seq, token1, token2,
                                                 idx>startidx or jdx>startjdx,
                                                 weight)
                            if idx+1 < len(self.tokens) or 
                               jdx+1 < len(other.tokens):
                                # Add the sequence to the working queue
                                work_queue.append((idx+1, jdx+1, seq2))
                            else:
                                # Finished to the end of both clusters
                                if seq2.weight > maxweight:
                                    maxweight = seq2.weight
                                    maxseq = seq2
            if not foundmatching:
                # Not matching token pair found after this merge sequence
                # End the merge sequence here
                if seq and seq.weight > maxweight:
                    if startidx+1 < len(self.tokens) or startjdx+1 < len(other.tokens):
                        # Not reached the end of clusters, add an end filler
                        seq.add_pair(Token(''), Token(''), True, 0)
                    maxweight = seq.weight
                    maxseq = seq

        return maxseq


if __name__ == "__main__":
    pass
