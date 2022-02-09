from src import util

try:
    import ujson as json
except:
    import json

import requests, datetime

class BaseObject(object):

    def __str__(self) -> str:
        iterItems = self.__dict__.copy()
        iterItems.pop('_rawObj')
        iterItems = iterItems.items()
        #Stop showing _rawObj in console

        d = { x: y.__dict__ if hasattr(y, "__dict__") else y for x,y in iterItems}
        return str(d)

class JsonDeserializable(BaseObject):

    @classmethod
    def de_json(cls, json_string, req):
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
            raise ValueError(f"json_type is neiter dict or str type={type(json_type)}")

    @staticmethod
    def headerTimeToDatetime(headerTime:str):
        try:
            return datetime.datetime.strptime(headerTime, "%a, %d %b %Y %H:%M:%S %Z")
        except:
            return datetime.datetime.fromtimestamp(0, datetime.timezone.utc)  

class error(JsonDeserializable):

    @classmethod
    def de_json(cls, json_string, req:requests.Response):
        if json_string is None: return None
        obj = cls.check_json(json_string, False)
        return cls(obj["errorDescription"], req.headers)

    def __init__(self, error, headers:dict = None) -> None:
        self.Error = error
        self.time = self.headerTimeToDatetime(headers["Date"] or None)

class success(BaseObject):

    def __init__(self, headers:dict = None):
        self.Success = True
        self.time = JsonDeserializable.headerTimeToDatetime(headers["Date"] or None)

class CCYRatio(BaseObject):

    def __init__(self, dictionary = None, codes = None, rateBuy = None, rateSell = None, time = None, rateCross = None) -> None:
        if dictionary is not None:
            codes = [dictionary["currencyCodeA"], dictionary["currencyCodeB"]]
            try:
                rateBuy = dictionary["rateBuy"]
                rateSell = dictionary["rateSell"]
            except:
                rateCross = rateBuy = rateSell = dictionary["rateCross"]
            time = dictionary["date"]
        self.CodeA:int = codes[0]
        self.CodeB:int = codes[1]
        self.A:str = util.isoNumToName(codes[0])
        self.B:str = util.isoNumToName(codes[1])
        self._dictName = f"{self.A}:{self.B}"
        self.RateBuy:float = rateBuy
        self.RateSell:float = rateSell
        self.RateCross:float = rateCross
        self.Time = datetime.datetime.fromtimestamp(time)

class MonoCCYs(JsonDeserializable):

    @classmethod
    def de_json(cls, json_string, req:requests.Response):
        if json_string is None: return None
        obj = cls.check_json(json_string, False)
        return cls(obj, req.headers)

    def __processCCYs(self):
        ret = {}
        for x in self._rawObj:
            tmp = CCYRatio(x)
            ret[tmp._dictName] = tmp
        return ret

    def __init__(self, obj, headers:dict = None) -> None:
        self._rawObj = obj

        self.CCYDict = self.__processCCYs()
        self.Time = self.headerTimeToDatetime(headers["Date"] or None)

class MonoAccount(BaseObject):

    def __panLstOrStr(MP):
        if len(MP) == 1:
            return MP[0]
        else:
            return MP

    def __init__(self, account = None, _id = None, sendID = None, currencyCode = None, cashbackType = None, balance = None, creditLimit = None, maskedPan:list[str] = None, _type = None, iban = None) -> None:
        if account is not None:
            _id = account["id"]
            sendID = account["sendId"]
            currencyCode = account["currencyCode"]
            cashbackType = account["cashbackType"]
            balance = account["balance"]
            creditLimit = account["creditLimit"]
            maskedPan = account["maskedPan"]
            _type = account["type"]
            iban = account["iban"]
        
        self.AccountID:str = _id
        self.SendID:str = sendID
        self._CCYCode:int = currencyCode
        self.CCYName:str = util.isoNumToName(currencyCode)
        self.Cashback:str = cashbackType
        self.Balance:float = balance/100
        self.CreditLimit:float = creditLimit/100
        self.MaksedPan:str|list[str] = MonoAccount.__panLstOrStr(maskedPan)
        self.AccountType:str = _type
        self.IBAN:str = iban
        self._dictName = f"{self.AccountID}:{self.CCYName}:{self.AccountType}"
        if isinstance(self.MaksedPan, str):
            self._dictName += f":{self.MaksedPan[-4:]}"

class MonoPersonalData(JsonDeserializable):

    @classmethod
    def de_json(cls, json_string, req:requests.Response):
        if json_string is None: return None
        obj = cls.check_json(json_string, False)
        return cls(obj, req.headers)
    
    def __processAccounts(self):
        ret = {}
        for x in self._rawObj["accounts"]:
            tmp = MonoAccount(x)
            ret[tmp._dictName] = tmp
        return ret

    def __init__(self, obj, headers:dict = None) -> None:
        self._rawObj = obj

        self.Accounts = self.__processAccounts()
        self.Time = self.headerTimeToDatetime(headers["Date"] or None)

class MonoStatements(JsonDeserializable):

    @classmethod
    def de_json(cls, json_string, req:requests.Response):
        if json_string is None: return None
        obj = cls.check_json(json_string, False)
        return cls(obj, req.headers)
    
    def __processStatements(self):

        #raise NotImplementedError("Yet to be implemented")
        return None

    def __init__(self, obj, headers:dict = None) -> None:
        self._rawObj = obj

        self.Statements = self.__processStatements()
        self.Time = self.headerTimeToDatetime(headers["Date"] or None)