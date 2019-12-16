#!/usr/bin/python

import re
from Cluster import Cluster


class Analyzer(object):
    """Analyzer receives lines and clusters them"""

    def __init__(self, softmaxlimit=10, minsimilarity=0.5, clusterlist=None):
        """Initializes Cluster object

        :param softmaxlimit (optional): soft maximum number of Clusters to form
        :param minsimilarity (optiona): how similar lines must be in oder to be
               merged into a cluster: 0.0 no similarity, 1.0 completely similar
        :param clusterlist (optional): list of Cluster objects to start with
        """

        if not minsimilarity > 0:
            raise ValueError('minsimilarity must be greater than zero')
        self.minsimilarity = minsimilarity
        if not softmaxlimit > 0:
            raise ValueError('Maximum number of clusters must be at least 2')
        self.softmaxlimit = softmaxlimit
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

        if len(self.clusters) <= self.softmaxlimit:
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

        if maxratio < self.minsimilarity:
            # No cluster with enought resemblance to each other
            return c

        merged_cluster = similar_c1.merge(similar_c2)

        # Next remove all clusters from the list which match the new one
        # Use unescaped version of cluster sequence in match comparison
        self.clusters = [c for c in self.clusters
                         if not merged_cluster.matches(
                             re.sub(r'\\([^\\])', r'\1', c.sequence))]
        self.clusters.append(merged_cluster)

        # Return either the newly created cluster or the merged one if
        # it was already merged
        if c in self.clusters:
            return c
        else:
            return merged_cluster


if __name__ == "__main__":
    pass
