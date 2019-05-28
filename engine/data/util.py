import math

def init_matrix(size, default=0):
    return [[default] * size for _ in range(size)]

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

def group_by_cb(item, key):
    return [getattr(item, key)]

def group_by(items, keys):
    if len(keys) < 1:
        return items
    
    key = keys[0]
    get_group_names = key if callable(key) else group_by_cb
    m = {}
        
    for item in items:
        group_names = get_group_names(item, key)
        
        for group_name in group_names:
            if not group_name in m:
                m[group_name] = []
                
            m[group_name].append(item)
    
    keys = keys[1:]
    
    if len(keys) >= 1:
        for group_name in m:
            m[group_name] = group_by(m[group_name], keys)
    
    return m
        

def matrix_str(matrix, hheader=None, vheader=None, header=None):
    if header:
        if not vheader:
            vheader = header
        if not hheader:
            hheader = header
    if vheader:
        matrix = list(map(lambda elem, row: [elem] + row, vheader, matrix))
    if hheader:
        if vheader:
            hheader = [''] + hheader
        matrix = [hheader]+ matrix
    
    max_chars = max(map(lambda row: max(map(len, map(str, row))), matrix))
    
    return '\n'.join([
        ' '.join(map(lambda elem: str(elem).ljust(max_chars), row))
        for row in matrix
    ])
