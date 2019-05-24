import math

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
