from .dataset import MockDataSet


def get_data_set_for(userId):
    return MockDataSet(20)

def handle_change(change):
    return [0] # Just return a bogus userId

def remove_recommendations_for(userId):
    pass

def insert_recommendations(recs):
    pass
