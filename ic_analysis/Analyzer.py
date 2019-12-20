#!/usr/bin/python

import re
from Cluster import Cluster
from MergeSequenceCache import MergeSequenceCache


class Analyzer(object):
    """Analyzer receives lines and clusters them"""

    def __init__(self, minlimit=10, maxlimit=25, minsimilarity=0.6, minprecision=0.6, clusterlist=None, debug=False):
        """Initializes Cluster object

        :param minlimit (optional): minimum number of Clusters to keep
        :param maxlimit (optional): maximum number of Clusters to keep
        :param minsimilarity (optional): how similar tokens must be in order to be
               merged together: 0.0 no similarity, 1.0 completely similar
        :param minprecision (optional): how many of the characters in a cluster must be non-wildcard (0.0-1.0)
        :param clusterlist (optional): list of Cluster objects to start with
        :param debug (optional): print debug output
        """

        if not (minsimilarity > 0 and minsimilarity < 1):
            raise ValueError('minsimilarity must be greater than 0 and less than 1')
        if not (minprecision > 0 and minprecision < 1):
            raise ValueError('minprecision must be greater than 0 and less than 1')
        self.minsimilarity = minsimilarity
        self.minprecision = minprecision
        if not (minlimit > 1 and maxlimit > 1):
            raise ValueError('Minimum and maximum number of clusters must be at least 2')
        self.minlimit = min(minlimit, maxlimit)
        self.maxlimit = maxlimit
        if clusterlist is None:
            self.clusters = []
        else:
            self.clusters = cluster_list
        self.mergeseqcache = MergeSequenceCache(minsimilarity)
        self.debug = debug
        self.linecount = 0

    def __str__(self):
        mystr = ""
        for c in self.clusters:
            mystr = mystr + str(c) + '\n'
        return mystr

    def analyze_line(self, line):
        """Analyze the given line and evolve clusters as necessary"""

        if not line:
            # Skip empty lines
            return

        # Keep an ever-increasing line count to track when clusters have been met
        self.linecount += 1

        # First check if line matches exactly to any existing cluster
        for c in self.clusters:
            if c.matches_line(line):
                c.findcount += 1
                c.lastlinecount = self.linecount
                if self.debug:
                    print(line + ": Matches cluster " + str(c))
                return

        # Append the line as a cluster per-se
        cluster = Cluster(line, lastlinecount=self.linecount)
        self.clusters.append(cluster)
        if self.debug:
            print(line + ": Add as a cluster per-se")

        if len(self.clusters) <= self.minlimit:
            # Do not merge anything, use the line per-se as a cluster
            return

        # Check if we can merge any clusters in the list
        # Find the cluster pair with highest merged precision and merge them
        maxprecision = 0
        similar_c1_idx = 0
        similar_c2_idx = 0
        listlen = len(self.clusters)
        for idx in range(listlen):
            c1 = self.clusters[idx]
            for jdx in range(idx+1, listlen):
                c2 = self.clusters[jdx]
                seq = self.mergeseqcache.get_merge_sequence(c1, c2)
                if seq is None:
                    # Clusters are not similar enough for merge
                    continue
                if seq.precision > maxprecision:
                    maxprecision = seq.precision
                    similar_c1_idx = idx
                    similar_c2_idx = jdx

        if maxprecision >= self.minprecision:
            # Found a possible cluster merge with enough precision
            similar_c1 = self.clusters[similar_c1_idx]
            similar_c2 = self.clusters[similar_c2_idx]
            mergeseq = self.mergeseqcache.get_merge_sequence(similar_c1, similar_c2)
            matcher = self.mergeseqcache.get_sequence_matcher(similar_c1, similar_c2)
            merged_cluster = Cluster.new_cluster_from_merge_sequence(mergeseq, matcher)
            merged_cluster.lastlinecount = max(similar_c1.lastlinecount, similar_c2.lastlinecount)
            merged_cluster.findcount = similar_c1.findcount + similar_c2.findcount

            self.mergeseqcache.remove_cluster(similar_c1)
            self.mergeseqcache.remove_cluster(similar_c2)
            if similar_c1_idx > similar_c2_idx:
                # Remove last first so that indices match
                del self.clusters[similar_c1_idx]
                del self.clusters[similar_c2_idx]
            else:
                del self.clusters[similar_c2_idx]
                del self.clusters[similar_c1_idx]
            self.clusters.append(merged_cluster)

            if self.debug:
                print("Merged clusters " + str(similar_c1) + " and " + str(similar_c2) +
                      " into a new cluster " + str(merged_cluster))
            return

        if len(self.clusters) > self.maxlimit:
            # Maximum number of cluster exceeded
            # Remove the cluster with the oldest emergence time

            oldestlinecount = self.clusters[0].lastlinecount
            oldestclusteridx = 0
            for idx in range(1, len(self.clusters)):
                if self.clusters[idx].lastlinecount < oldestlinecount:
                    oldestlinecount = self.clusters[idx].lastlinecount
                    oldestclusteridx = idx

            if self.debug:
                print("Remove cluster with oldest emergence time: " + str(self.clusters[oldersclusteridx]))
            self.clusters.pop(oldestclusteridx)


if __name__ == "__main__":
    pass
