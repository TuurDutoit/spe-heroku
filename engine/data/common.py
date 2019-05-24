from .util import map_from, select

class RecordSet:
    def __init__(self, records, key='pk'):
        self.all = records
        self.map = map_from(records)
        self.ids = select(records)
        self.total = len(records)

class DataSet:
    def get_driving_times(self):
        raise NotImplementedError

    def get_service_times(self):
        raise NotImplementedError

    def get_penalties(self):
        raise NotImplementedError

    def get_locations(self):
        raise NotImplementedError
