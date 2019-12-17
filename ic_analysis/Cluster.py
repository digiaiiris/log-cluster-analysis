#!/usr/bin/python

import re
from Token import Token
from MergeSequence import MergeSequence


class Cluster(object):
    """Analyzed cluster"""

    def __init__(self, line=None):
        """Initializes Cluster object with the given line

        :param line (optiona): line that is used per-se as a cluster
        """

        if line:
            self.tokens = [Token(line)]
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
            self.len = self.len + t.len

    @staticmethod
    def new_cluster_from_merge_sequence(seq, matchercache):
        """Merge the token pairs and generate a cluster of them

        :params: MergeSequence to apply
        :param matchercache: SequenceMatcherCache object for this cluster merge
        :returns: Cluster object generated
        """

        tokens = []
        for token1, token2, anybefore in seq.to_list():
            mergedlist = token1.merge(token2, matchercache.get_matcher(token1, token2))
            if anybefore:
                # Mark to the first token in the merged list that there were
                # some skipped tokens ie characters before this token pair
                mergedlist[0].anybefore = True
            tokens.extend(mergedlist)

        c = Cluster()
        c.set_tokens(tokens)
        return c

    def __str__(self):
        return self.prog.pattern

    def to_text(self, gapmarker='@@'):
        """Convert cluster to text representation, using gapmarker
           in place of .* (anything) and plain unescaped text for all else"""

        text = ""
        for t in self.tokens:
            if t.anybefore:
                text = text + gapmarker
            text = text + str(t)
        return text

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

        # This cluster regex should accept larger set of texts than the other
        # and match the other cluster text representation given a random gapmarker
        return self.matches_line(other.to_text(gapmarker='@@@###@@@'))

    def construct_merge_sequence(self, other, minsimilarity, matchercache):
        """Construct a merge sequence merging this cluster with another one

        :param other: the other cluster to merge with
        :param minsimilarity: min similarity in order to merge two tokens (0.0-1.0)
        :param matchercache: SequenceMatcherCache object for this cluster merge
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
                    if token1.len == 0 or token2.len == 0:
                        # Empty filler token (should be last token in cluster)
                        continue
                    m = matchercache.get_matcher(token1, token2)
                    if m.real_quick_ratio() >= minsimilarity:
                        ratio = m.ratio()
                        if ratio >= minsimilarity:
                            # Tokens are similar enough so that we can branch
                            # into a new merge sequence path
                            weight = ratio * (token1.len+token2.len) * 0.5
                            seq2 = MergeSequence(seq, token1, token2,
                                                 idx>startidx or jdx>startjdx,
                                                 weight)
                            if idx+1 < len(self.tokens) or jdx+1 < len(other.tokens):
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
