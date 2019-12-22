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

* *Real-time analysis* of application log lines in a line-by-line manner, in contrast to static clustering analysis of a set of lines
* *Individual lines* are analyzed, not log sequences. The order of the lines analyzed is not relevant.
* Required *performance* of the analysis is high due to the real-time nature
* The formed clusters should be *visualizable* in an easy-to-understand manner to produce added value to the application developer
* The log lines contain *unstructured* output including human-readable text messages, information about parameters, and other values
* Application logs may contain *long IDs* and other variable fields that take most of the line even though they are not wanted to count in the clustering. A trivial clustering solution would cluster lines by session IDs or other long fields that occur frequently during a specific time interval. So, the actual log contents would be discarded in the clustering.
* Applications *develop* over time and so should the clusters. For example, software updates may alter the logging syntax completely.
* There may be totally *different type of logging* in one time period (eg. application startup) compared to others (run-time, idle time with no users, busy time etc). So, the number of meaningful clusters may vary a lot.
* Similar lines must be detected in terms of string metrics, such as similar consecutive strings. In other words, clustering must be *based on distance* between individuals rather than their vectors or centers in a n-dimensional space as in K-means clustering.
* From the point of anomaly detection, *small clusters* are the most interesting ones. However, the problem of finding relatively small clusters in the presence of one or more larger clusters is particularly hard.

## Related Articles

I have found the following articles most helpful in developing the algorithm:

* van der Laan et al. 2002. A New Partitioning Around Medoids
Algorithm. https://biostats.bepress.com/cgi/viewcontent.cgi?article=1003&context=ucbbiostat. A reworked PAM algorithm (partitioning around medoids ie. clustering of a distance matrix) that handles small clusters well with the help of maximizing a criteria called Average Silhouette.
* Landauer et al. 2018. Dynamic log file analysis: An unsupervised cluster evolution approach for anomaly detection. https://www.sciencedirect.com/science/article/pii/S0167404818306333. A cluster evolution technique that allows the use of static clustering algorithms (such as PAM) in the context of dynamic log lines with developing clusters.
* Batool and Hennig. 2019. Clustering by Optimizing the Average Silhouette Width. https://arxiv.org/pdf/1910.08644v1. A distance based clustering algorithm that estimates the number of clusters and produces the clusters by optimizing a criteria called Average Silhouette Width (ASW).
* https://en.m.wikipedia.org/wiki/Single-linkage_clustering. Single-linkage clustering, a type of hierarchical clustering that finds the closest neighbours and combines them into larger clusters.

## Algorithm Definition

TBD. describe algorithm type (hierarchical, self-linkage, partitioning etc)
TBD. describe distance measurement function
