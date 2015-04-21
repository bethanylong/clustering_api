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
from os import getuid

class ClusterCache:
    def __init__(self, clustering_obj):
        self.cl = clustering_obj # Instantiated clustering.Clustering()
        self.cluster_data = []
        self.last_gather_time = datetime.utcfromtimestamp(0) # Epoch
        self.gathering_now = threading.Lock()

    def data_is_stale(self, threshold=timedelta(minutes=5)):
        # Return True if data was gathered some threshold ago or earlier
        return self.last_gather_time < datetime.now() - threshold

    def finished_gathering_data(self):
        self.last_gather_time = datetime.now()

    def gather(self):
        self.gathering_now.acquire()
        self.cluster_data = self.cl.run_all() # Block and gather data
        self.gathering_now.release()
        self.finished_gathering_data()

    def get_data(self):
        if not self.gathering_now.locked() and self.data_is_stale():
            # Spawn a new thread, but return stale/nonexistent data for now
            # (If JS frontend gets a result indicating no data has ever been
            # gathered, it should try again, perhaps in ~5 seconds)
            th = threading.Thread(target=self.gather)
            th.daemon = True
            th.start()
        return self.cluster_data


# Bottle doesn't like being in a class, but it makes up for it by being awesome otherwise
app = bottle.default_app()
cl = Clustering()
cc = ClusterCache(cl)

@app.get('/json/data/all')
def get_data_all():
    all_data = cc.get_data()
    return {'all_data': all_data}

@app.get('/json/data/<dataset_name>')
def get_data(dataset_name):
    all_data = cc.get_data()
    this_dataset = {}
    for dataset in all_data:
        if dataset['filename'] == dataset_name:
            this_dataset = dataset
    return this_dataset

@app.get('/json/list/datasets')
def list_datasets():
    data = cc.get_data()
    return {'filenames': [entry['filename'] for entry in data]}

# Static Routes - http://stackoverflow.com/questions/10486224/bottle-static-files/13258941#13258941
# Look in a directory called 'frontend' for any files ending with the given regex
@app.get('/<filename:re:.*\.(js|css|html|json|png)>')
def static_resource(filename):
    return bottle.static_file(filename, root='frontend')

@app.get('/')
def index():
    return static_resource('index.html')

if __name__ == '__main__':
    #bottle.run(app=app, host='0.0.0.0', port='65080')
    bottle.run(app=app, host='0.0.0.0', port=getuid())
