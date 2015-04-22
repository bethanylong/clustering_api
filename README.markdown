clustering_api
==============

JSON API for CSCI 497E Program 1.

Calls up the assignment backend in a thread, caches the results, and returns data points and per-round clustering data to the web client.

Parses README.txt in prog1_data to find input file specifications.

Will require modifications if you need to use it with a non-Java backend or are not me.

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
{"all_clusters": [[[[point in first cluster of first round], [another point], ...],
                   [points in next cluster]],
                  [clusters for next round],
                  [clusters for another round]],
 "filename": some_filename}
```
