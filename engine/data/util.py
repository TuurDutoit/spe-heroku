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

# Can be used to add a static value to get_groups
def static(value):
    def static_value(item):
        return (value, )
    return static_value
    
def get_groups(item, keys):
    groups = [[]]

    for key in keys:
        if callable(key):
            subgroups = key(item)
            new_groups = []

            for group in groups:
                for subgroup in subgroups:
                    new_groups.append(group + [subgroup])

            groups = new_groups
        else:
            val = getattr(item, key)
            for group in groups:
                group.append(val)

    return map(tuple, groups)

def get_all_groups(items, keys):
    groups = set()
    
    for item in items:
        groups.update(get_groups(item, keys))
    
    return groups

def group_by_flat(items, keys):
    m = {}

    for item in items:
        for group in get_groups(item, keys):
            if not group in m:
                m[group] = []

            m[group].append(m)

    return m


def map_by_flat(items, keys):
    m = {}

    for item in items:
        for group in get_groups(item, keys):
            m[group] = item

    return m

def group_by_base(items, keys, finish):
    m = {}
    
    for item in items:
        for group in get_groups(item, keys):
            nested_m = m
            
            for step in group[:-1]:
                if not step in nested_m:
                    nested_m[step] = {}
                nested_m = nested_m[step]
            
            finish(nested_m, group[-1], item)
    
    return m

def group_by_finish(m, key, item):
    if not m[key]:
        m[key] = []
    m[key].append(item)

def map_by_finish(m, key, item):
    m[key] = item

def group_by(items, keys):
    return group_by_base(items, keys, group_by_finish)

def map_by(items, keys):
    return group_by_base(items, keys, map_by_finish)

def get_deep(m, path, **kwargs):
    for step in path:
        if step in m:
            m = m[step]
        elif 'default' in kwargs:
            return kwargs['default']
        else:
            raise KeyError(str(path))
    
    return m

def find_deep(m, paths, **kwargs):
    NOT_FOUND = object()
    
    for path in paths:
        item = get_deep(m, path, default=NOT_FOUND)
        
        if item != NOT_FOUND:
            return item
    
    if 'default' in kwargs:
        return kwargs['default']
    
    raise KeyError(str(paths))

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
