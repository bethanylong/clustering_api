#!/usr/bin/env python

# Read prog1 assignment output and transform it into Flot-friendly cluster data.
# This data can then be graphed in the web client if you put this script's json
# output file where the web client expects it to be.

from __future__ import print_function
from clustering import Clustering
from json import dumps
from os import path
import sys

class ClusteringDump:
    def __init__(self, cl):
        self.cl = cl # Instantiated clustering.Clustering()

    def pretend_we_just_ran(self, output_file=None):
        # Read the given output file and return what we would have gotten from
        # running it with Clustering.run().
        with open(output_file) if output_file else sys.stdin as f:
            output = f.readlines()
            return ''.join(output)

    def transform_for_flot(self, pretended_output, data_points, orig_filename):
        parsed = self.cl.parse_program_output(orig_filename, pretended_output, data_points)
        flot_friendly = self.cl.list_clusters([parsed])
        return flot_friendly[0]

if __name__ == '__main__':
    cl = Clustering()
    cd = ClusteringDump(cl)

    if len(sys.argv) > 1:
        data_points = sys.argv[1]
    else:
        print('''usage: your_prog1 [-rand] /path/to/input_data.txt options | \\
python ~/public_html/clustering_api/clustering_dump.py /path/to/input_data.txt > \\
~/public_html/clustering_api/frontend/some_filename.json''', file=sys.stderr)
        sys.exit(1)

    orig_filename = path.basename(data_points)

    pretended_output = cd.pretend_we_just_ran()
    flot_friendly = cd.transform_for_flot(pretended_output, data_points, orig_filename)
    print(dumps(flot_friendly))
