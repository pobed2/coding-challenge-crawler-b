from json import JSONEncoder


class StandardEncoder(JSONEncoder):
    def default(self, o):
        return o.to_dict()