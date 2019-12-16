#!/usr/bin/python

import re
from difflib import SequenceMatcher


class Cluster(object):
    """Analyzed cluster"""

    def __init__(self, line, escape=True):
        """Initializes Cluster object with the given line

        :param line: regular expression string; must match the whole line
        :param escape (optional): whether the line should be escaped,
                                  False if the line is already escaped
        """

        # We want to store the pattern as escaped so that get_matching_blocks
        # works correctly in the case where the actual line contains '.*'
        if escape:
            self.pattern = re.escape(line)
        else:
            self.pattern = line
        self.prog = re.compile('^' + self.pattern + '$')

        # From documentation: if you want to compare one sequence against
        # many sequences, use set_seq2() to set the commonly used sequence
        # once and call set_seq1() repeatedly, once for each of the other
        #  sequences
        self.seq = SequenceMatcher()
        self.seq.set_seq2(self.pattern)

    def __str__(self):
        return self.pattern

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
        otherpattern = re.sub(r'\\([^\\])', r'\1', other.pattern)
        return self.matches_line(otherpattern)

    def get_match_ratio(self, other):
        """Get matching ratio (0.0-1.0) compared to the other cluster"""

        self.seq.set_seq1(other.pattern)
        return self.seq.ratio()

    def get_matching_blocks(self, other):
        """Get non-overlapping matching sub-strings, see difflib documentation

        :param other: the other cluster to compare this cluster with
        """
        self.seq.set_seq1(other.pattern)
        return self.seq.get_matching_blocks()

    def merge(self, other):
        """Merge this cluster with another one

        :param other: the other cluster to merge with
        :returns: merged cluster object
        """
        blocks = self.get_matching_blocks(other)
        mergepattern = ""
        latestpos1 = 0
        latestpos2 = 0
        for i, j, n in blocks:
            if n == 0:
                # Last block
                if latestpos1 != i+n or latestpos2 != j+n:
                    mergepattern = mergepattern + '.*'
            elif len(mergepattern) == 0 and (i > 0 or j > 0):
                mergepattern = '.*' + self.pattern[j:j+n]
            elif len(mergepattern) == 0:
                mergepattern = mergepattern + self.pattern[j:j+n]
            else:
                mergepattern = mergepattern + '.*' + self.pattern[j:j+n]
            latestpos1 = i+n
            latestpos2 = j+n

        # Remove duplicate .* patterns that may have caused by the merging
        mergepattern = mergepattern.replace(".*.*", ".*")
        return Cluster(mergepattern, escape=False)


if __name__ == "__main__":
    pass
