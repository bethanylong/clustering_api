#!/usr/bin/env python

# JSON API for cluster data.
# Routes should return ~immediately, regardless of whether data has been
# gathered or is being gathered.

# If you have the chance to run this with anything less flimsy than bottle
# (uwsgi, for example), you should probably enable gzip compression.

import bottle
from clustering import Clustering
from datetime import datetime, timedelta
import threading
from os import getuid, getcwd, chdir

class ClusterCache:
    def __init__(self, clustering_obj):
        self.cl = clustering_obj # Instantiated clustering.Clustering()
        self.cluster_data = []
        self.cluster_contents = []
        self.last_gather_time = datetime.utcfromtimestamp(0) # Epoch
        self.gathering_now = threading.Lock()

    def data_is_stale(self, threshold=timedelta(minutes=5)):
        # Return True if data was gathered some threshold ago or earlier
        return self.last_gather_time < datetime.now() - threshold

    def finished_gathering_data(self):
        self.last_gather_time = datetime.now()
        self.cluster_contents = self.list_clusters()

    def gather(self):
        self.gathering_now.acquire()
        self.cluster_data = self.cl.run_all() # Block and gather data
        self.gathering_now.release()
        self.finished_gathering_data()

    def refresh_data_if_old(self):
        if not self.gathering_now.locked() and self.data_is_stale():
            # Spawn a new thread, but return stale/nonexistent data for now
            # (If JS frontend gets a result indicating no data has ever been
            # gathered, it should try again, perhaps in ~5 seconds)
            th = threading.Thread(target=self.gather)
            th.daemon = True
            th.start()

    def get_data(self):
        self.refresh_data_if_old()
        return self.cluster_data

    def get_clusters(self):
        self.refresh_data_if_old()
        return self.cluster_contents

    def list_clusters(self):
        data = self.cluster_data
        pretty_clusters = []
        p = pretty_clusters
        for file_data in data:
            pretty_file_data = {}
            pf = pretty_file_data
            pf['filename'] = file_data['filename']
            clusters = []
            max_cluster_num = max(file_data['output'][0])
            for round in file_data['output']:
                round_clusters = [[] for index in range(0, max_cluster_num + 1)]
                for ix, cluster_num in enumerate(round):
                    round_clusters[cluster_num].append(file_data['points'][ix])

                clusters.append(round_clusters)

            pf['clusters'] = clusters
            p.append(pf)
        return p


# Bottle doesn't like being in a class, but it makes up for it by being awesome otherwise
app = bottle.default_app()
cl = Clustering()
cc = ClusterCache(cl)
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
    #bottle.run(app=app, host='0.0.0.0', port='65080')
    app.debug = True
    bottle.run(app=app, host='0.0.0.0', port=getuid())
