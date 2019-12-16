#!/usr/bin/python

import re
from difflib import SequenceMatcher


class Cluster(object):
    """Analyzed cluster"""

    def __init__(self, pattern):
        """Initializes Cluster object

        :param pattern: regular expression string; must match the whole line
        """
        assert len(pattern) > 0, 'Pattern must not be empty'
        assert pattern[:1] == '^' and pattern[-1:] == '$', \
            'Pattern must begin with ^ and end with $'

        # Omit first ^ and last $ from sequence so they won't interfere
        # with possible ^ and $ characters inside the pattern
        self.sequence = pattern[1:-1]

        self.prog = re.compile(pattern)

        # From documentation: if you want to compare one sequence against
        # many sequences, use set_seq2() to set the commonly used sequence
        # once and call set_seq1() repeatedly, once for each of the other
        #  sequences
        self.seq = SequenceMatcher()
        self.seq.set_seq2(self.sequence)

    def __str__(self):
        return self.sequence

    def matches(self, line):
        """Check if the given line matches with the cluster pattern

        :returns: True if matches, False if not
        """

        if self.prog.match(line) is None:
            return False
        else:
            return True

    def get_match_ratio(self, other):
        """Get matching ratio (0.0-1.0) compared to the other cluster"""

        self.seq.set_seq1(other.sequence)
        return self.seq.ratio()

    def get_matching_blocks(self, other):
        """Get non-overlapping matching sub-strings, see difflib documentation

        :param other: the other cluster to compare this cluster with
        """
        self.seq.set_seq1(other.sequence)
        return self.seq.get_matching_blocks()

    def merge(self, other):
        """Merge this cluster with another one

        :param other: the other cluster to merge with
        :returns: merged cluster object
        """
        blocks = self.get_matching_blocks(other)
        mergepattern = "^"
        latestpos1 = 0
        latestpos2 = 0
        for i, j, n in blocks:
            if n == 0:
                # Last block
                if latestpos1 == i+n and latestpos2 == j+n:
                    mergepattern = mergepattern + '$'
                else:
                    mergepattern = mergepattern + '.*$'
            elif len(mergepattern) == 1 and (i > 0 or j > 0):
                mergepattern = '^.*' + self.sequence[j:j+n]
            elif len(mergepattern) == 1:
                mergepattern = mergepattern + self.sequence[j:j+n]
            else:
                mergepattern = mergepattern + '.*' + self.sequence[j:j+n]
            latestpos1 = i+n
            latestpos2 = j+n

        # Remove duplicate .* patterns that may have caused by the merging
        mergepattern = mergepattern.replace(".*.*", ".*")
        return Cluster(mergepattern)


if __name__ == "__main__":
    pass
