#!/usr/bin/python

import re


class Token(object):
    """Token inside a cluster"""

    def __init__(self, text, anybefore=False):
        """Initializes Token object

        :param text: String that this token represents
        :param anybefore (optional): True if there can be anything before
                                     this token (ie. .* before token)
        """
        self.text = text
        self.anybefore = anybefore
        self.len = len(text)

    def __str__(self):
        return self.text

    def to_regex(self):
        """Convert this token to a regex string"""
        if self.anybefore:
            return '.*' + re.escape(self.text)
        else:
            return re.escape(self.text)

    def merge(self, other, matcher):
        """Merge the tokens together

        :param other: The other token to merge with
        :param matcher: SequenceMatcher object containing both tokens
        :returns: Tokens list matching with both tokens
        """

        tokens = []
        if self.text == other.text:
            # Similar texts in the tokens
            if self.anybefore == other.anybefore:
                return [self]
            return [Token(self.text, anybefore=True)]

        # Detect similar text blocks in the tokens
        blocks = matcher.get_matching_blocks()
        mergepattern = ""
        latestpos1 = 0
        latestpos2 = 0
        for i, j, n in blocks:
            if n == 0:
                # Last block
                if latestpos1 != i+n or latestpos2 != j+n:
                    # There are characters before end of tokens that
                    # could not be merged
                    tokens.append(Token('', anybefore=True))
            elif len(mergepattern) == 0 and (i > 0 or j > 0):
                # This is the first similar text block but there are
                # characters before them that could not be merged
                tokens.append(Token(self.text[i:i+n], anybefore=True))
            elif len(mergepattern) == 0:
                # This is the first similar text block and there are
                # no characters before them ie. it starts both tokens
                tokens.append(Token(self.text[i:i+n], anybefore=False))
            else:
                # This is nth text block and there are characters after
                # the previous detected text block
                tokens.append(Token(self.text[i:i+n], anybefore=True))
            latestpos1 = i+n
            latestpos2 = j+n

        return tokens


if __name__ == "__main__":
    pass
