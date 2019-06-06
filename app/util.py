import os

def env(name, default=None, decode=str):
    s = os.environ.get(name, default)
    
    if default != None:
        s = decode(s)
    
    return s


def lenv(name, default=None, decode=str, sep=',', strip=True):
    s = os.environ.get(name, default)
    
    if s == None:
        return None
    else:
        parts = s.split(sep)
        
        if strip:
            parts = map(lambda s: s.strip(), parts)
            
        return list(map(decode, parts))
