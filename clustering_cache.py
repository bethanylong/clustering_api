from datetime import datetime, timedelta
import threading

class ClusteringCache:
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
        # Reset timestamp and generate Flot-friendly cluster data
        self.last_gather_time = datetime.now()
        self.cluster_contents = self.cl.list_clusters(self.cluster_data)

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
