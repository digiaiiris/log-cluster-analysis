#!/usr/bin/python

import re


class IdentifiersConfig(object):
    """Read in identifiers configuration file"""

    def read_config(self, configfilepath):
        """Read configuration from file

        :param configfilepath: Path to confiuration file (identifiers.grok)
        """

        # Read in the configuration file into a data structure
        lines = [line.rstrip('\n') for line in open(configfilepath)]
        config = dict()
        for line in lines:
            if line.startswith('#') or line.isspace():
                continue
            m = re.match(r'^([A-Z]+) (.*)$', line)
            if not m:
                raise RuntimeError('Invalid configuration line: ' + line)
            idname = m.group(1)
            idregex = m.group(2)
            config[idname] = idregex

        self.identifiers = self.process_config(config)

    def process_config(self, config):
        """ Process the configuration list into a list of identifiers

        :param config: Dictionary containing parsed configuration lines
        """

        # This list contains all identifiers, excluding exclamation marks (intermittent flag)
        # at the beginning of identifier names
        allids = dict()
        for name, regex in config.items():
            if name.startswith('!'):
                name = name[1:]
            allids[name] = regex

        # The main list of identifiers does not contain intermittent identifiers
        identifiers = dict()        
        for name, regex in config.items():
            if not name.startswith('!'):
                identifiers[name] = regex

        # Solve recursively references to other identifiers
        namestoprocess = identifiers.keys()
        while len(namestoprocess) > 0:
            name = namestoprocess.pop()
            regex = identifiers[name]
            m = re.search(r'%\{([A-Z]+)\}', regex)
            if m:
                # After processing the identifier, take it into a new round to check
                # if the included sub-identifiers contained further references
                namestoprocess.append(name)
            while m:
                refname = m.group(1)
                if refname not in allids:
                    raise RuntimeError('Invalid identifier ' + refname + ' referenced to by ' + name)
                regex = regex.replace('%{' + refname + '}', allids[refname], 1)
                identifiers[name] = regex
                m = re.search(r'%\{([A-Z]+)\}', regex)

        return identifiers

if __name__ == "__main__":
    pass
