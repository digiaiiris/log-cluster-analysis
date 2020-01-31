#!/usr/bin/python

import re
from difflib import SequenceMatcher

# TBD: Switch to use python-Levenshtein instead of difflib


class SequenceMatcherCache(object):
    """Caches SequenceMatcher objects for cluster tokens"""

    def __init__(self):
        """Initializes object"""

        # Dictionary key is tuple containing two token objects
        # Dictionary value is SequenceMatcher object
        self.cache = dict()

    def get_matcher(self, token1, token2):
        """Gets/constructs a sequencem matcher between two tokens

        :returns: SequenceMatcher object
        """

        # First find if it already finds in the cache
        cacheobj = self.cache.get((token1, token2))
        if cacheobj:
            return cacheobj

        # Not found in cache, so generate it
        matcher = SequenceMatcher(a=token1.text, b=token2.text)
        self.cache[(token1, token2)] = matcher
        return matcher


if __name__ == "__main__":
    pass
