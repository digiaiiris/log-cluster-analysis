#!/usr/bin/python

import re
from Token import Token
from MergeSequence import MergeSequence


class Cluster(object):
    """Analyzed cluster"""

    def __init__(self, line=None, lastlinecount=0):
        """Initializes Cluster object with the given line

        :param line (optional): line that is used per-se as a cluster
        :param lastlinecount (optional): line count number when the cluster was encountered
        """

        if line:
            self.tokens = [Token(line)]
            self.minlen = len(line)
            self.maxlen = len(line)
            self.prog = re.compile('^' + re.escape(line) + '$')
        else:
            self.tokens = []
            self.minlen = 0
            self.maxlen = 0
        self.lastlinecount = lastlinecount
        self.findcount = 1

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
        self.minlen = 0
        self.maxlen = 0
        for t in self.tokens:
            self.minlen = self.minlen + t.minlen
            self.maxlen = self.maxlen + t.maxlen

    @staticmethod
    def new_cluster_from_merge_sequence(seq, matchercache):
        """Merge the token pairs and generate a cluster of them

        :params: MergeSequence to apply
        :param matchercache: SequenceMatcherCache object for this cluster merge
        :returns: Cluster object generated
        """

        tokens = []
        for token1, token2, minwildcards, maxwildcards in seq.to_list():
            mergedlist = token1.merge(token2, matchercache.get_matcher(token1, token2))

            # Add the number of wildcards ie. characters that were skipped before this token pair
            mergedlist[0].increase_wildcard_counts(minwildcards, maxwildcards)

            tokens.extend(mergedlist)

        # Token merge may end up with an end filler (empty token with preceding wildcards)
        # that is in the midst of the cluster.
        # Replace them by adding the number of wildcards to the next token in the cluster
        tokens_to_remove = []
        for idx in range(len(tokens) - 1):
            if len(tokens[idx].text) == 0:
                tokens[idx + 1].increase_wildcard_counts(tokens[idx].minwildcards, tokens[idx].maxwildcards)

                # Insert at the beginning so the removing will be done from end to beginning
                tokens_to_remove.insert(0, idx)
        for idx in tokens_to_remove:
            del tokens[idx]

        c = Cluster()
        c.set_tokens(tokens)
        return c

    def __str__(self):
        return self.prog.pattern

    def to_text(self, gapmarker='@@'):
        """Convert cluster to text representation, using gapmarker
           in place of wildcards and using plain unescaped text for all else"""

        text = ""
        for t in self.tokens:
            if t.minwildcards > 0 or t.maxwildcards > 0:
                text = text + gapmarker + str(t.minwildcards) + ',' + str(t.maxwildcards) + gapmarker
            text = text + t.text
        return text

    def matches_line(self, line):
        """Check if the cluster pattern matches the given line

        :returns: True if matches, False if not
        """

        if self.prog.match(line) is None:
            return False
        else:
            return True

    # TBD: Move to a separate MergeSequenceConstructor class??
    #    Rationale: too long for Cluster class, it should be separated into sub-functions and can be done
    #               well outside of Cluster class
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
        work_queue = [(0, 0, None)]

        # Find a merge sequence with a maximum precision ie. similar subsequent matches
        maxprecision = 0
        maxseq = None

        while len(work_queue) > 0:
            startidx, startjdx, seq = work_queue.pop()
            foundmatching = False
            for idx in range(startidx, len(self.tokens)):
                for jdx in range(startjdx, len(other.tokens)):
                    token1 = self.tokens[idx]
                    token2 = other.tokens[jdx]
                    if len(token1.text) == 0 or len(token2.text) == 0:
                        # Empty filler token (should be last token in cluster)
                        continue
                    m = matchercache.get_matcher(token1, token2)
                    if m.real_quick_ratio() >= minsimilarity:
                        ratio = m.ratio()
                        if ratio >= minsimilarity:
                            # Calculate min and max number of wildcards since the last token
                            # in the merge sequence, ie. the length of the tokens skipped
                            minwildcards1 = 0
                            maxwildcards1 = 0
                            minwildcards2 = 0
                            maxwildcards2 = 0
                            for kdx in range(startidx, idx):
                                minwildcards1 += self.tokens[kdx].minlen
                                maxwildcards1 += self.tokens[kdx].maxlen
                            for kdx in range(startjdx, jdx):
                                minwildcards2 += other.tokens[kdx].minlen
                                maxwildcards2 += other.tokens[kdx].maxlen

                            # Extend the merge sequence to this token pair
                            seq2 = MergeSequence(seq, token1, token2,
                                                 min(minwildcards1, minwildcards2),
                                                 max(maxwildcards1, maxwildcards2),
                                                 ratio)
                            if idx+1 < len(self.tokens) or jdx+1 < len(other.tokens):
                                # Add the sequence to the working queue
                                work_queue.append((idx+1, jdx+1, seq2))
                            else:
                                # Finished to the end of both clusters
                                # Take only the merge sequence with the maximum precision and forget all others
                                if seq2.precision > maxprecision:
                                    maxprecision = seq2.precision
                                    maxseq = seq2
                            foundmatching = True
            if not foundmatching:
                # Not matching token pair found after this merge sequence
                # End the merge sequence here
                if seq and seq.precision > maxprecision:
                    if startidx < len(self.tokens) or startjdx < len(other.tokens):
                        # No matching at the end of clusters, add an end filler

                        # Calculate min and max number of wildcards until the last token
                        # in the merge sequence, ie. the length of the tokens skipped
                        minwildcards1 = 0
                        maxwildcards1 = 0
                        minwildcards2 = 0
                        maxwildcards2 = 0
                        for kdx in range(startidx, len(self.tokens)):
                            minwildcards1 += self.tokens[kdx].minlen
                            maxwildcards1 += self.tokens[kdx].maxlen
                        for kdx in range(startjdx, len(other.tokens)):
                            minwildcards2 += other.tokens[kdx].minlen
                            maxwildcards2 += other.tokens[kdx].maxlen

                        seq = MergeSequence(seq, Token(''), Token(''),
                                            min(minwildcards1, minwildcards2),
                                            max(maxwildcards1, maxwildcards2), 0)

                    maxprecision = seq.precision
                    maxseq = seq

        return maxseq


if __name__ == "__main__":
    pass
