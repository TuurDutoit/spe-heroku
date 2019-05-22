import json

DEFAULT = object()
R_QUERYSTRING = r'(^|&){}'
R_FORMDATA = r'--{}\s*Content-Disposition\s*:\s*form-data\s*;\s*name\s*=\s*"{}"'
R_JSON = r'"{}"\s*:'
R_KEY = r''
ERR_NO_PARAM = 'Expected parameter: "{}"'
ERR_NOT_LIST = 'Expected parameter of type "list": "{}"'
ERR_NOT_DICT = 'Expected parameter of type "dict": "{}"'
ERR_NOT_JSON = 'Failed to parse parameter as JSON: "{}"'

class RequestData:
    def __init__(self, request):
        self.request = request
        self.query = request.GET

        if request.content_type == 'application/json' and request.body:
            self.body = json.loads(request.body)
        else:
            self.body = request.POST or dict()

    def __getitem__(self, key):
        return self.get(key)

    def __contains__(self, key):
        return key in self.query or key in self.body

    def get(self, key, default=DEFAULT, graceful=False):
        if key in self.query:
            return self.query[key]
        if key in self.body:
            return self.body[key]
        if default != DEFAULT:
            return default

        self._error(ERR_NO_PARAM, key, graceful)

    def getlist(self, key, strict=True, default=DEFAULT, graceful=False):
        value = DEFAULT

        # Try to get value from querystring
        if key in self.query:
            value = self.query.getlist(key)

        # Otherwise, try to get value from body
        if key in self.body:
            value = self.body[key]

        # No value found in querystring nor body
        if value == DEFAULT:
            if default != DEFAULT:
                return default
            elif strict:
                self._error(ERR_NO_PARAM, key, graceful)
            else:
                return []

        # Make sure the value is a list
        if type(value) != type(list()):
            self._error(ERR_NOT_LIST, key, graceful)

        return value

    def getdict(self, key, strict=True, default=DEFAULT, graceful=False):
        value = DEFAULT

        # Try to get value from querystring (has to be JSON-decoded)
        if key in self.query:
            str_value = self.query[key]

            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                self._error(ERR_NOT_JSON, key, graceful)

        # Otherwise, try to get from body
        if key in self.body:
            value = self.body[key]

        # No value found in querystring nor body
        if value == DEFAULT:
            if default != DEFAULT:
                return default
            elif strict:
                self._error(ERR_NO_PARAM, key, graceful)
            else:
                return {}

        # Make sure the value is a dict
        if type(value) != type(dict()):
            self._error(ERR_NOT_DICT, key, graceful)

        return value

    def get_loc(self, key):
        if key in self.query:
            return get_loc(self.request.META['QUERY_STRING'], R_QUERYSTRING.format(key), component='query')
        if key in self.body:
            if request.content_type == 'application/json':
                return get_loc(self.request.body, R_JSON.format(key))
            elif request.content_type == 'application/x-www-form-urlencoded':
                return get_loc(self.request.body, R_QUERYSTRING.format(key))
            elif request.content_type == 'multipart/form-data':
                boundary = request.content_params.get('boundary')
                return get_loc(self.request.body, R_FORMDATA.format(boundary, key))

        return {'line': 0, 'col': 0, 'component': 'request'}

    def keys(self):
        if type(self.body) == type(dict()):
            body = self.body
        else:
            body = self.body.dict()

        return list(self.query.dict().keys()) + list(self.body.keys())

    def _error(self, msg_pattern, key, graceful):
        if graceful:
            msg = msg_pattern.format(key) if graceful == True else graceful
            raise GracefulError(error(self.request, msg, 400))
        else:
            raise KeyError(msg_pattern.format(key))
