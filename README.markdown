clustering_api
==============

JSON API for CSCI 497E Program 1.

Calls up the assignment backend in a thread, caches the results, and returns data points and per-round clustering data to the web client.

Parses README.txt in prog1_data to find input file specifications.

Usage
-----

1. Modify `clustering_options.py` with the paths to your source directory and dataset directory
2. Install the `bottle` module in a virtualenv
    - Read the instructions in `/usr/local/bin/virtualenvwrapper.sh` to create a virtualenv
    - Once you're in your virtualenv, do `pip install bottle`
3. Run `python clustering_bottle.py`
4. In a web browser, navigate to the machine you're using at whatever port Bottle tells you it's using (example: linux-09.cs.wwu.edu:10960)

Routes
------

`host:port/json/list/datasets`: Object containing list of dataset filenames

```
{"filenames": ["dataset_01.txt", ...]}
```

`host:port/json/data/some_filename`: Data points and per-round clustering data for some_filename (which should be in /json/list/datasets)

```
{"filename": some_filename,
 "output": [[first-round clustering for each point], [next-round clustering], ...],
 "points": [[coords of first point], [second point], ...]}
```

`host:port/json/data/all`: Object containing list of all files' data points and per-round clustering data

```
{"all_data": [{"filename": first_filename,
               "output": [[], [], ...],
               "points": [[], [], ...]},
              { same thing for the next filename },
              ...]}
```

`host:port/json/cluster/some_filename`: Object containing data points in clusters in rounds of clustering. This is explicit membership (the actual points are in each cluster), rather than having to sift through indices at each round of clustering (as with the routes above).

```
{"clusters": [[[[point in first cluster of first round], [another point], ...],
               [points in next cluster]],
              [clusters for next round],
              [clusters for another round]],
 "filename": some_filename}
```

Static graph data
-----------------

In case setting up the API to dynamically retrieve graph data from your program seems intimidating, you can transform prog1 output into plottable graph data with `clustering_dump.py`.

This script can be run in a pipeline with your program output. Assuming you've checked this repository out into `~/public_html/clustering_api`:

```
$ java prog1 -rand your_dataset.txt algorithm clusters num_datapoints num_dimensions | \
python ~/public_html/clustering_api/clustering_dump.py your_dataset.txt > \
~/public_html/clustering_api/frontend/your_dataset.json
```

(Obviously, if you used C/C++ to implement prog1, change the command accordingly.)

Then, once your json file has been written, you can view the graph at `http://sw.cs.wwu.edu/~your_username/clustering_api/frontend/plot_from_file.html?filename=your_dataset.json`.
