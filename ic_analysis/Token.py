#!/usr/bin/python

import re


class Token(object):
    """Token inside a cluster"""

    def __init__(self, text, minwildcards=0, maxwildcards=0):
        """Initializes Token object

        :param text: String that this token represents
        :param minwildcards (optional): Minimum number of wildcards to be matched before the token
        :param maxwildcards (optional): Maximum number of wildcards to be matched before the token
        """
        self.text = text
        self.minwildcards = minwildcards
        self.maxwildcards = maxwildcards
        self.minlen = len(text) + minwildcards
        self.maxlen = len(text) + maxwildcards

    def __str__(self):
        if self.minwildcards > 0 or self.maxwildcards > 0:
            return '+{' + str(self.minwildcards) + ',' + str(self.maxwildcards) + '}' + self.text
        return self.text

    def to_regex(self):
        """Convert this token to a regex string"""
        if self.minwildcards > 0 or self.maxwildcards > 0:
            return '.{' + str(self.minwildcards) + ',' + str(self.maxwildcards) + '}' + re.escape(self.text)
        else:
            return re.escape(self.text)

    def increase_wildcard_counts(self, minwildcardsinc, maxwildcardsinc):
        self.minwildcards += minwildcardsinc
        self.maxwildcards += maxwildcardsinc
        self.minlen = len(self.text) + self.minwildcards
        self.maxlen = len(self.text) + self.maxwildcards

    def merge(self, other, matcher):
        """Merge the tokens together

        :param other: The other token to merge with
        :param matcher: SequenceMatcher object containing both tokens
        :returns: Tokens list matching with both tokens
        """

        tokens = []
        if self.text == other.text:
            # Similar texts in the tokens
            return [Token(self.text, minwildcards=min(self.minwildcards, other.minwildcards),
                          maxwildcards=max(self.maxwildcards, other.maxwildcards))]

        # Detect similar text blocks in the tokens
        blocks = matcher.get_matching_blocks()
        latestpos1 = 0
        latestpos2 = 0
        for i, j, n in blocks:
            # Since get_matching_blocks() always returns as last an empty block
            # this automatically adds an empty filler token at the end
            if n == 0 and i == latestpos1 and j == latestpos2:
                # Last block was zero length
                continue

            # Calculate number of wildcards between this block and the preceding one
            minwildcards = min(i - latestpos1, j - latestpos2)
            maxwildcards = max(i - latestpos1, j - latestpos2)
            if len(tokens) == 0:
                # The first token generated must involve the preceding wildcards of the original token pair
                minwildcards += min(self.minwildcards, other.minwildcards)
                maxwildcards += max(self.maxwildcards, other.maxwildcards)

            tokens.append(Token(self.text[i:i+n], minwildcards=minwildcards, maxwildcards=maxwildcards))
            latestpos1 = i+n
            latestpos2 = j+n

        return tokens


if __name__ == "__main__":
    pass
