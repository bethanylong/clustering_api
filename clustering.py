#!/usr/bin/env python

# Gather clustering data by calling prog1 backend.
# Currently only supports kmeans.

# (And you thought python was readable!)

from os import chdir
from subprocess import call, check_output

class Clustering:
    # Easy ways to get to the fields parse_readme returns
    # (TODO: Perhaps this means it would be better to store them in a dict)
    filename = lambda self, x: x[0]
    num_datapoints = lambda self, x: x[1]
    dimensionality = lambda self, x: x[2]

    def __init__(self):
        self.source_dir = '/home/longb4/code/497/svnwc/prog1'
        self.data_dir = '/home/longb4/code/497/svnwc/prog1/prog1_data'
        self.build_cmd = 'javac prog1.java'
        self.run_cmd = 'java prog1'

    def build(self):
        chdir(self.source_dir)
        call(self.build_cmd.split())

    def run(self, randomize=True, infile='./prog1_data/dataset_01.txt',
            cluster_alg='kmeans', num_clusters=10, num_datapoints=10000,
            dimensionality=2):
        # Build list of command arguments
        cmd = self.run_cmd.split()
        if randomize:
            cmd.append('-rand')
        cmd += [infile, cluster_alg, num_clusters, num_datapoints, dimensionality]
        cmd = [str(word) for word in cmd]
        # Run command and return output
        return check_output(cmd)

    def run_all(self, dim_filter=lambda x: int(x) <= 2):
        # Look for data file specifications in self.data_dir/README.txt and run
        # clustering algorithms on each of those files.
        # Capture output of command for plotting.
        # Returns a list of dicts: [ { 'filename': 'some_str', 'output': [[x1 cluster round 1, x2 cr1], [x1 cr2, x2 cr2]], 'points': [[x1, y1], [x2, y2]] } ]

        results = []
        # Iterate over dataset files specified in README.txt
        for data_spec in self.parse_readme():

            # Skip datasets which would be difficult to render (3+ dimensions)
            if not dim_filter(self.dimensionality(data_spec)):
                continue

            # Do the clustering and capture output
            output = self.run(infile=self.data_dir + '/' + self.filename(data_spec), num_datapoints=self.num_datapoints(data_spec), dimensionality=self.dimensionality(data_spec))
            # Parse output and store in dict
            result = {'filename': self.filename(data_spec), 'output': [s.strip().split() for s in output.splitlines()]}
            # Cast cluster membership for each point to int
            result['output'] = [[int(cl_num) for cl_num in cl_round] for cl_round in result['output']]

            points = []
            with open(self.data_dir + '/' + self.filename(data_spec)) as f:
                # Look in dataset file and store that in a dict too
                # (It's hard to draw a graph when you don't know the points)
                points = f.readlines()
                points = [s.strip().split() for s in points]
            # Cast coordinates for each point to float
            points = [[float(coord) for coord in point] for point in points]
            result['points'] = points

            results.append(result)

        return results

    def parse_readme(self):
        data_specs = None
        with open(self.data_dir + '/README.txt') as f:
            readme_content = f.readlines()
            # Split line on spaces (list of lists of words)
            data_specs = [line.split() for line in readme_content]
        # Remove header (only include lines where the first word ends in '.txt'
        data_specs = [line[0:3] for line in data_specs if len(line) >= 3 and line[0].endswith('.txt')]
        # Remove first two characters from words containing '=' (like 'N=10000' -> '10000')
        data_specs = [[word[2:] if '=' in word else word for word in line] for line in data_specs]
        return data_specs

if __name__ == '__main__':
    c = Clustering()
    from pprint import pprint
    pprint(c.run_all())
