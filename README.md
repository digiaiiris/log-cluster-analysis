# log-cluster-analysis
Python package to analyze a set of log lines and detect clusters ie. repeated patterns with similar lines; fit for continuous analysis and cluster evolution

# Usage

## Pre-filtering of the Log Lines

Log lines should be pre-filtered before analysis as follows:

* Multi-line logging should be detected and only the first lines feeded into the analysis (excluding, for example, stack traces).
* Timestamps should preferably be removed from the lines to be analyzed
* Different log sources should be not combined but analyzed independently of each other


# About the Algorithm

## Goals and Challenges

This log clustering solution focuses mainly on arbitrary application logs, even though it can be applied
to other logs as well. Application logs present numerous distinct challenges that have been addressed
in this solution. The following lists both the goals set and the challenges met:

* The solution incorporates a *real-time analysis* of application log lines in a line-by-line manner, in contrast to static clustering analysis of a given set of lines
* *Individual lines* are analyzed, not log sequences or correlation between lines. In other words, the order of the lines analyzed is not relevant.
* Required *performance* of the analysis is high due to the real-time nature.
* The formed clusters should be *visualizable* in an easy-to-understand manner to produce added value to the application developer. To achieve that, clusters are represented by regexp patterns where wildcard portions of the lines are visualized differently from the ones that are the same for all the lines in the cluster.
* The log lines may contain *unstructured* or raw text that includes human-readable paragraphs, timestamps, and values.
* Application logs may contain *long identifiers* and other fields that take most of the line even though they should not matter in the clustering. A trivial clustering solution (that we want to avoid) would cluster lines by session identifiers or other long fields that occur frequently during a specific time interval.
* Applications *develop* over time and so should the clusters. For example, software updates may alter the logging format completely.
* There may be totally *different types of logging* in one time period (eg. application startup) compared to others (run-time, idle time with no users, busy time etc). So, the number of meaningful clusters may vary a lot.
* Similar lines must be detected in terms of string metrics, such as similar consecutive strings. In other words, clustering must be *based on distance* between individual lines rather than their vectors or centers in a n-dimensional space as per K-means clustering.
* From the point of anomaly detection, *small clusters* are the most interesting ones. However, the problem of finding relatively small clusters in the presence of one or more larger clusters is particularly hard.
* Since we want to represent the clusters as regexp patterns, the order of strings within lines means a lot. In other words, `cat has brown hair` should not belong to the same cluster as `brown horses and a cat`.
* The *development of clusters* is important to detect anomalies from the log.

## Related Articles

I have found the following articles most helpful in developing the algorithm:

* van der Laan et al. 2002. A New Partitioning Around Medoids
  Algorithm. https://biostats.bepress.com/cgi/viewcontent.cgi?article=1003&context=ucbbiostat. A reworked PAM algorithm (partitioning around medoids ie. clustering of a distance matrix)
  that handles small clusters well with the help of maximizing a criteria called Average Silhouette.
* Landauer et al. 2018. Dynamic log file analysis: An unsupervised cluster evolution approach for anomaly detection. https://www.sciencedirect.com/science/article/pii/S0167404818306333.
  A cluster evolution technique that allows the use of static clustering algorithms (such as PAM) in the context of dynamic log lines with developing clusters.
* Batool and Hennig. 2019. Clustering by Optimizing the Average Silhouette Width. https://arxiv.org/pdf/1910.08644v1. A distance based clustering algorithm that
  estimates the number of clusters and produces the clusters by optimizing a criteria called Average Silhouette Width (ASW).
* https://en.m.wikipedia.org/wiki/Single-linkage_clustering. Single-linkage clustering, a type of hierarchical clustering that finds the closest neighbours and combines them into larger clusters.

## Algorithm 

### Primitive Clustering

Primitive clustering goes basically along the lines of Lauander et al. method.

For each line l, the following steps are performed:

1. Preprocessing: Tokenize identifiers of l that match the known identifier patterns (eg. timestamps, numerical values)
2. Check if l matches regexp pattern of any existing cluster. If it does, it belongs to that cluster (end of processing).
3. Find a set of cluster candidates C for l by comparing the lenght of l, |l|, with the length of each cluster c, |c|. A cluster c is added to C if |c| within 10% range of |l|. See below for the definition of cluster length.
4. Filter out the cluster candidates further by 2-mers algorithm. Find out the number of matching 2-mers in each cluster c and l. The minimum amount of matching 2-mers, M, that is required for c to remain in C is defined as M=(L-1)*p where L=min(|c|,|l|) and p=similarity ratio between 0.0 and 1.0; 1.0 means that all 2-mers possible must be matching.
5. Find out the closest (ie. most similar) cluster c1 in C by calculating the similarity between each c in C and l. See below for the calculation of similarity between a cluster and a line. The similarity metrics roughly corresponds to the number of similar characters in ordered sequence.
6. Assign l to cluster c1 if the similarity between c1 and l is greater than (|c1|+|l|)/2*s where s=minimum similarity ratio between 0.01 and 1.0; 1.0 means that lines in a cluster must be identical.

TBD: A similarity is  calculated by comparing each sequency of tokens in c and l ...

TBD. describe algorithm type (hierarchical, self-linkage, partitioning etc)
TBD. describe distance measurement function

TBD define: Cluster length
TBD describe how 2-mers are calculated from a cluster?


### Super-Clustering

The primitive clustering above presents a problem from an analytics point of view.
With a low s (minimum similarity ratio) value, there would be a high number of primitive clusters which is impractical and does not add any real value for analytics.
With a high s, there would be less clusters but they are all large so that small clusters or "outliers" are not detected from the log data.
To overcome the limitations of primitive clustering, a low s value is used and the primitive clusters are next clustered into "super clusters".

Two alternative super-clustering algorithms are provided:

1. Closest-neighbour clustering that targets at a defined number of clusters
2. Partitioning around memoids / optimizing Average Silhouette Width ??

Super-Clustering adds one more value to the outcome, namely the ability to detect the development of (super-)clusters.
A super-cluster retains its identity while primitive clusters are added to it or removed because of out-dating. 
So, we can reliably report the number of log lines per each permanent super-cluster even though the nature of logging
varies accross time.

Closest-neighbour clustering involves the following steps for each line l assigned to cluster c1:

1. If c1 already belongs to a super-cluster q1, do nothing. Report q1 as the cluster of l.
2. Create a new super-cluster and add c1 to it.
3. Check the number of super-clusters. If it does not exceed the configured target value, stop here.
4. Find the two closest super-clusters and merge them.

