from src import util

try:
    import ujson as json
except:
    import json

class JsonDeserializable(object):

    @classmethod
    def de_json(cls, json_string):
        raise NotImplementedError

    @staticmethod
    def check_json(json_type: dict|str|list|object, dict_copy=True):
        if util.is_dict(json_type):
            return json_type.copy() if dict_copy else json_type
        elif util.is_str(json_type):
            return json.loads(json_type)
        elif util.is_list(json_type):
            return json_type      
        else:
            raise ValueError("json_type is neiter dict or str")
    
    def __str__(self) -> str:
        d = { x: y.__dict__ if hasattr(y, "__dict__") else y for x,y in self.__dict__.items() }
        return str(d)

class error(JsonDeserializable):

    @classmethod
    def de_json(cls, json_string):
        if json_string is None: return None
        obj = cls.check_json(json_string, False)
        return cls(obj["errorDescription"])

    def __init__(self, error) -> None:
        self.Error = error

class response(JsonDeserializable):

    @classmethod
    def de_json(cls, json_string):
        if json_string is None: return None
        obj = cls.check_json(json_string, False)
        return cls(obj)

    def __init__(self, obj) -> None:
        self.obj = obj