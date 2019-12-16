#!/usr/bin/python

import re
from Cluster import Cluster


class Analyzer(object):
    """Analyzer receives lines and clusters them"""

    def __init__(self, maxnum=10, clusterlist=None):
        """Initializes Cluster object

        :param maxnum (optional): maximum number of Clusters to form
        :param clusterlist (optional): list of Cluster objects to start with
        """

        assert maxnum > 1, 'Maximum number of clusters must be at least 2'
        self.maxnum = maxnum
        if clusterlist is None:
            self.clusters = []
        else:
            self.clusters = cluster_list

    def __str__(self):
        mystr = ""
        for c in self.clusters:
            mystr = mystr + str(c) + '\n'
        return mystr

    def analyze_line(self, line):
        """Analyze the given line and evolve clusters as necessary

        :returns: Cluster object that matches the string
        """

        # First check if line matches exactly to any existing cluster
        for c in self.clusters:
            if c.matches(line):
                return c

        # Append the line as a cluster per-se
        c = Cluster('^' + re.escape(line) + '$')
        self.clusters.append(c)

        if len(self.clusters) <= self.maxnum:
            # Maximum number not reached, use the line per-se as a cluster
            return c

        # Maximum number exceeded, must merge two clusters in the list
        # Find the most similar clusters and merge them
        maxratio = 0
        similar_c1 = None
        similar_c2 = None
        listlen = len(self.clusters)
        for idx in range(listlen):
            c1 = self.clusters[idx]
            for jdx in range(idx+1, listlen):
                c2 = self.clusters[jdx]
                ratio = c1.get_match_ratio(c2)
                if ratio > maxratio:
                    maxratio = ratio
                    similar_c1 = c1
                    similar_c2 = c2

        if similar_c1 is None:
            # No cluster with any resemblance to each other
            similar_c1 = self.clusters[0]
            similar_c2 = self.clusters[1]

        merged_cluster = similar_c1.merge(similar_c2)

        # Next remove all clusters from the list which match the new one
        # Use unescaped version of cluster sequence in match comparison
        self.clusters = [c for c in self.clusters
                         if not merged_cluster.matches(re.sub(r'\\([^\\])',r'\1',c.sequence))]
        self.clusters.append(merged_cluster)


if __name__ == "__main__":
    pass
