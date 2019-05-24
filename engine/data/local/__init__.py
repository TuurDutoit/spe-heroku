from .dataset import MockDataSet


def get_data_set_for(userId):
    return MockDataSet(20)

def handle_change(change):
    pass

def remove_recommendations_for(userId):
    pass

def insert_recommendations(recs):
    pass
