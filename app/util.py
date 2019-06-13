import os

MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR

def env(name, default=None, decode=str):
    s = os.environ.get(name, default)
    
    if s != None:
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

def boolean(val):
    if not val:
        return False
    if type(val) == type(str()) and (val.lower() == 'n' or val.lower() == 'no' or val.lower() == 'f' or val.lower() == 'false'):
        return False
    else:
        return True

def coalesce(*values):
    for val in values:
        if val != None:
            return val

def clamp(mn, val, mx):
    return max(mn, min(mx, val))
