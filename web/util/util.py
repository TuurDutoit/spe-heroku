from django.core.serializers import serialize
import json
import re
import os

def get_loc(string, index, component='body'):
    lines = 0

    if type(string) == type(bytes()):
        string = string.decode('utf-8')

    if type(index) == type(str()) and type(index) == type(str()):
        match = re.search(index, string)

        if match:
            index = match.start()
        else:
            index = 0

    for line in string.split(os.linesep):
        if index <= len(line):
            return {'line': lines, 'col': index, 'component': component}
        else:
            index -= len(line) + len(os.linesep)
            lines += 1

def to_json(obj):
    return json.loads(serialize('json', [obj]))[0]

def get_doc_uri(req, suffix=''):
    return req.build_absolute_uri('/docs' + req.path + '#' + suffix)
