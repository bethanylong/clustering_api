#!/usr/bin/env python

# JSON API for cluster data.
# Routes should return ~immediately, regardless of whether data has been
# gathered or is being gathered.

# If you have the chance to run this with anything less flimsy than bottle
# (uwsgi, for example), you should probably enable gzip compression.

import bottle
from clustering import Clustering
from clustering_cache import ClusteringCache
from os import getuid, getcwd, chdir

# Bottle doesn't like being in a class, but it makes up for it by being awesome otherwise
app = bottle.default_app()
cl = Clustering()
cc = ClusteringCache(cl)
original_cwd = getcwd()

@app.get('/json/data/all')
def get_data_all():
    all_data = cc.get_data()
    return {'all_data': all_data}

@app.get('/json/data/<dataset_name>')
def get_data(dataset_name):
    return get_one_dataset(dataset_name, cc.get_data)

@app.get('/json/cluster/<dataset_name>')
def get_cluster(dataset_name):
    return get_one_dataset(dataset_name, cc.get_clusters)

def get_one_dataset(dataset_name, getter_fn):
    all_data = getter_fn()

    if len(all_data) == 0:
        # No data gathered yet
        return {}

    for dataset in all_data:
        if dataset['filename'] == dataset_name:
            return dataset

@app.get('/json/list/datasets')
def list_datasets():
    data = cc.get_data()
    return {'filenames': [entry['filename'] for entry in data]}

# Static Routes - http://stackoverflow.com/questions/10486224/bottle-static-files/13258941#13258941
# Look in a directory called 'frontend' for any files ending with the given regex
@app.get('/<filename:re:.*\.(js|css|html|json|png)>')
def static_resource(filename):
    chdir(original_cwd)
    return bottle.static_file(filename, root='frontend')

@app.get('/')
def index():
    return static_resource('index.html')

if __name__ == '__main__':
    port = getuid()
    if port < 1024:
        port += 60000
    bottle.run(app=app, host='0.0.0.0', port=port)
