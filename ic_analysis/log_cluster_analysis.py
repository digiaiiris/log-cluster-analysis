#!/usr/bin/python

from argparse import ArgumentParser
from Analyzer import Analyzer
import sys


def main(args=None):
    parser = ArgumentParser(
        description="Analyze log lines into clusters"
    )

    parser.add_argument("--debug", type=bool, const=True, default=False, nargs='?',
                        help="Debug output of cluster analysis")
    parser.add_argument("--clusterstatefile", type=str, default=None,
                        help="Path to cluster states which gets updated")
    parser.add_argument("--minlimit", type=int, default=10,
                        help="Minimum number of clusters")
    parser.add_argument("--maxlimit", type=int, default=25,
                        help="Maximum number of clusters")
    parser.add_argument("--minsimilarity", type=float, default=0.6,
                        help="Minimum similarity between token for merge (0.0-1.0, 1.0 means identical")
    parser.add_argument("--minprecision", type=float, default=0.6,
                        help="Minimum precision of clusters, 0.6 means that 60% of cluster length must \
                              be precise characters (and not wildcards)")
    parser.add_argument("--printprogress", type=bool, const=True, default=False, nargs='?',
                        help="Print dot (.) for every line processed")
    parser.add_argument("--printsummary", type=bool, const=True, default=False, nargs='?',
                        help="Print summary of analyzed lines")
    parser.add_argument("--printclustersregex", type=bool, const=True, default=False, nargs='?',
                        help="Print clusters in regex format")
    parser.add_argument("--printclusterstext", type=bool, const=True, default=False, nargs='?',
                        help="Print clusters in readable text (unescaped regex) format")
    parser.add_argument("--gapmarker", type=str, default='@@',
                        help="Text representation of cluster gaps (regex .*) when using printclusterstext")
    args = parser.parse_args(args)

    if args.clusterstatefile:
        raise NotImplementedError("--clusterstatefile is not yet implemented")
#        # Read cluster list from file, written by the previous run
#        a = open('/tmp/file.py', 'r')

    a = Analyzer(minlimit=args.minlimit, maxlimit=args.maxlimit, minsimilarity=args.minsimilarity,
                 minprecision=args.minprecision, debug=args.debug)
    for line in sys.stdin:
        a.analyze_line(line.rstrip())
        if args.printprogress:
            sys.stdout.write('.')
            sys.stdout.flush()

    if args.printclustersregex:
        for c in a.clusters:
            print(c.to_regex())

    if args.printclusterstext:
        for c in a.clusters:
            print(c.to_text(gapmarker=args.gapmarker))

    if args.printsummary:
        raise NotImplementedError("--printsummary is not yet implemented")


if __name__ == "__main__":
    main()
