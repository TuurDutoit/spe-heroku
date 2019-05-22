def init_matrix(size):
    return [[0] * size for _ in range(size)]

def map_from(items, key='pk'):
    m = {}
    
    for item in items:
        m[ getattr(item, key) ] = item
    
    return m

def select(items, key='pk'):
    l = []
    
    for item in items:
        l.append( getattr(item, key) )
    
    return l