#!/usr/bin/python

import re


class IdToken(Token):
    """An identifier token ie. a token matching a configured identifier in a string"""

    def __init__(self, idname, idregexp, text, mintextlen=0, maxtextlen=0, minwildcards=0, maxwildcards=0):
        """Initializes Token object

        :param idname: Identifier name (eg. 'DATE')
        :param idRegexp: Regexp configured for the identifier
        :param text: Identifier text in the string, None if the token has been merged from strings with different identifier texts
        :param mintextlen: In case of a merged token, the minimum length of merged identifier texts
        :param maxtextlen: In case of a merged token, the maximum length of merged identifier texts
        """
        self.idname = idname
        self.idregexp = regexp
        if text:
            super().__init__(text, minwildcards, maxwildcards)
        else:
            self.mintextlen = mintextlen
            self.maxtextlen = maxtextlen
            self.minwildcards = minwildcards
            self.maxwildcards = maxwildcards
            self.minlen = mintextlen + minwildcards
            self.maxlen = maxtextlen + maxwildcards

    def __str__(self):
        if self.text:
            text = self.text
        else:
            text = '<' + self.idname + ':' + str(self.mintextlen) + '-' + str(self.maxtextlen) + '>'
        if self.minwildcards > 0 or self.maxwildcards > 0:
            return '+{' + str(self.minwildcards) + ',' + str(self.maxwildcards) + '}' + text
        return text

    def to_regex(self):
        """Convert this token to a regex string"""
        if self.minwildcards > 0 or self.maxwildcards > 0:
            return '.{' + str(self.minwildcards) + ',' + str(self.maxwildcards) + '}' + self.idregexp
        else:
            return self.idregexp

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

        raise NotImplementedError()

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
