import threading
from src import util

try:
    import ujson as json
except:
    import json

import requests, datetime, queue as Queue

class BaseObject(object):

    def __str__(self) -> str:
        iterItems = self.__dict__.copy()
        try:iterItems.pop('_rawObj')
        except:None
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

class MonoStatement(BaseObject):

    def __init__(self, statement:dict = None, id_:str = None, time:int = None, desc:str = None, mcc:int = None, mcc_:int = None, amount:int = None, op_amount:int = None, ccy_code:int = None, commission:int = None, cashback:int = None, balance:int = None, hold:bool = None) -> None:

        if statement is not None:
            id_ = statement["id"]
            time = statement["time"]
            desc = statement["description"]
            mcc = statement["mcc"]
            mcc_ = statement["originalMcc"]
            amount = statement["amount"]
            op_amount = statement["operationAmount"]
            ccy_code = statement["currencyCode"]
            commission = statement["commissionRate"]
            cashback = statement["cashbackAmount"]
            balance = statement["balance"]
            hold = statement["hold"]

        self.StatementID = id_
        self.Time = datetime.datetime.fromtimestamp(time)
        self.Description = desc
        self.MCC = mcc
        self.MCCOriginal = mcc_
        self.Amount:float = amount/100
        self.SignedAmount = f"+{self.Amount}" if self.Amount >0 else f"-{self.Amount.__abs__()}"
        self.OperationAmount = op_amount/100
        self.CCYCode = ccy_code
        self.CCYName = util.isoNumToName(ccy_code)
        self.Commission = commission
        self.Cashback = cashback
        self.Balance = balance/100
        self.OnHold = hold
        self._dictName = f"{time}:{id_}"

class MonoStatements(JsonDeserializable):

    @classmethod
    def de_json(cls, json_string, req:requests.Response):
        if json_string is None: return None
        obj = cls.check_json(json_string, False)
        return cls(obj, req.headers)
    
    def __processStatements(self):

        ret = {}
        for x in self._rawObj:
            statement = MonoStatement(x)
            ret[statement._dictName] = statement
        return ret

    def __init__(self, obj, headers:dict = None) -> None:
        self._rawObj = obj

        self.Statements = self.__processStatements()
        self.Time = self.headerTimeToDatetime(headers["Date"] or None)

def or_set(self):
    self._set()
    self.changed()


def or_clear(self):
    self._clear()
    self.changed()

def orify(e, changed_callback):
    if not hasattr(e, "_set"):
        e._set = e.set
    if not hasattr(e, "_clear"):
        e._clear = e.clear
    e.changed = changed_callback
    e.set = lambda: or_set(e)
    e.clear = lambda: or_clear(e)

def OrEvent(*events):
    or_event = threading.Event()

    def changed():
        bools = [ev.is_set() for ev in events]
        if any(bools):
            or_event.set()
        else:
            or_event.clear()

    def busy_wait():
        while not or_event.is_set():
            # noinspection PyProtectedMember
            or_event._wait(3)

    for e in events:
        orify(e, changed)
    or_event._wait = or_event.wait
    or_event.wait = busy_wait
    changed()
    return or_event

class WorkerThread(threading.Thread):
    count = 0

    def __init__(self, name = None):
        name = name or f"Mono_WorkerThread{self.__class__.count+1}"
        self.__class__.count+=1
        threading.Thread.__init__(self, name=name)
        self.queue = Queue.Queue()
        self.daemon = True
        self._running = True
        self.received_task_event = threading.Event()
        self.done_event = threading.Event()
        self.exception_event = threading.Event()
        self.continue_event = threading.Event()

        self.exception_info = None
        self.start()
    
    def run(self):
        while self._running:
            try:
                task, args, kwargs = self.queue.get(True, 0.5)
                self.continue_event.clear()
                self.received_task_event.clear()
                self.done_event.clear()
                self.exception_event.clear()
                self.received_task_event.set()

                task(*args, **kwargs)
                self.done_event.set()
            except Queue.Empty:
                pass
            except Exception as E:
                self.exception_info = E
                self.exception_event.set()
                self.continue_event.wait()
    
    def put(self, task, *args, **kwargs):
        self.queue.put((task, args, kwargs))
    
    def raise_exception(self):
        if self.exception_event.is_set():
            raise self.exception_info
    
    def clear_exception(self):
        self.exception_event.clear()
        self.continue_event.set()
    
    def stop(self):
        self._running = False



