#!/usr/bin/python

import re
from Cluster import Cluster
from MergeSequenceCache import MergeSequenceCache


class Analyzer(object):
    """Analyzer receives lines and clusters them"""

    def __init__(self, softmaxlimit=10, hardmaxlimit=25, minsimilarity=0.6, clusterlist=None):
        """Initializes Cluster object

        :param softmaxlimit (optional): soft maximum number of Clusters to form
        :param hardmaxlimit (optional): hard maximum number of Clusters to form
        :param minsimilarity (optiona): how similar lines must be in oder to be
               merged into a cluster: 0.0 no similarity, 1.0 completely similar
        :param clusterlist (optional): list of Cluster objects to start with
        """

        if not (minsimilarity > 0 and minsimilarity < 1):
            raise ValueError('minsimilarity must be greater than 0 and less than 1')
        self.minsimilarity = minsimilarity
        if not (softmaxlimit > 0 and hardmaxlimit > 0):
            raise ValueError('Maximum number of clusters must be at least 2')
        self.softmaxlimit = min(softmaxlimit, hardmaxlimit)
        self.hardmaxlimit = hardmaxlimit
        if clusterlist is None:
            self.clusters = []
        else:
            self.clusters = cluster_list
        self.mergeseqcache = MergeSequenceCache(minsimilarity)

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
            if c.matches_line(line):
                return c

        # Append the line as a cluster per-se
        c = Cluster(line)
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
                seq = mergeseqcache.get_merge_sequence(c1, c2)
                if seq is None:
                    # Clusters are not similar enough for merge
                    continue
                ratio = 2.0 * seq.weight / (c1.len + c2.len)
                if ratio > maxratio:
                    maxratio = ratio
                    similar_c1 = c1
                    similar_c2 = c2

        if maxratio < self.minsimilarity and len(self.clusters) <= self.hardmaxlimit:
            # No cluster with enough resemblance to each other
            return c

        if maxratio == 0:
            # Hard max number of clusters exceeded but no cluster resemble each other
            # Just remove the oldest one
            self.clusters.pop(0)
            return c

        mergeseq = mergeseqcache.get_merge_sequence(similar_c1, similar_c2)
        merged_cluster = Cluster.new_cluster_from_merge_sequence(mergeseq, mergeseqcache.getmatchercache(c1))

        # Next remove all clusters from the list which match the new one
        # Use unescaped version of cluster sequence in match comparison
        clusters_to_remove = [c for c in self.clusters
                              if merged_cluster.matches_cluster(c)]
        for c in clusters_to_remove:
            mergeseqcache.remove_cluster(c)
        self.clusters = [c for c in self.clusters if not c in clusters_to_remove]
        self.clusters.append(merged_cluster)

        # Return either the newly created cluster or the merged one if
        # it was already merged
        if c in self.clusters:
            return c
        else:
            return merged_cluster


if __name__ == "__main__":
    pass
