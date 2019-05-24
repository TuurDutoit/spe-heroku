from ..common import DataSet
from ..util import init_matrix
import random


class MockDataSet(DataSet):
    def __init__(self, size):
        self._size = size
    
    def get_record_for_location_id(self, loc_id):
        return 'Location(' + str(loc_id) + ')'

    def get_driving_times(self):
        driving_times = init_matrix(self._size + 1)

        for i in range(1, self._size + 1):
            for j in range(1, self._size + 1):
                driving_times[i][j] = 0 if i == j else random.randint(
                    0, 1.5*60*60)

        return driving_times

    def get_service_times(self):
        return [0] + [random.randint(15 * 60, 3 * 60 * 60) for _ in range(self._size)]

    def get_penalties(self):
        return [24*60*60] * self._size

    def get_locations(self):
        return list(range(1, self._size + 1))
