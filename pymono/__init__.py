import datetime
import pymono.types, pymono.util
import requests, threading, pickle

class MonoClient:

    def __init__(self, api_key: str) -> None:
        self.XToken = api_key
        self.Endpoint = "https://api.monobank.ua/"
        self.__stop_polling = threading.Event()
        self.Personal:pymono.types.MonoPersonalData = None
        self.PreferedAccount:pymono.types.MonoAccount = None
        self._last_update_time:dict[datetime.datetime] = {}
        self._callback:function = None
        self._processed_statements:list[pymono.types.MonoStatement] = []
        try:
            self._processed_statements = pickle.load(open("processed.obj", "rb"))
        except:
            print("No processed statements found")
            None
    
    def makeRequest(self, path, args:dict=None):
        if path == "bank/currency":
            req = requests.get(self.Endpoint + path)
            if req.status_code == 200:
                return pymono.types.MonoCCYs.de_json(req.json(), req)
            else:
                return pymono.types.error.de_json(req.json(), req)
        elif path == "personal/client-info":
            req = requests.get(self.Endpoint + path, headers={"X-Token": self.XToken})
            if req.status_code == 200:
                return pymono.types.MonoPersonalData.de_json(req.json(), req)
            else: return pymono.types.error.de_json(req.json(), req)
        elif path == "personal/webhook":
            req = requests.post(self.Endpoint + path, pymono.util.to_JSON(args), headers={"X-Token": self.XToken})
            if req.status_code == 200:
                return pymono.types.success(req.headers)
            else:
                return pymono.types.error.de_json(req.json(), req)
        elif path == "personal/statement":
            path += f"/{args['account']}/{args['from']}"
            if 'to' in args.keys():
                path += f"/{args['to']}"
            req = requests.get(self.Endpoint + path, headers={"X-Token": self.XToken})
            if req.status_code == 200:
                return pymono.types.MonoStatements.de_json(req.json(), req)
            else:
                return pymono.types.error.de_json(req.json(), req)

    def getCurrency(self):
        return self.makeRequest("bank/currency")
    
    def getPersonal(self):
        personal = self.makeRequest("personal/client-info")
        self.Personal = personal
        try: self.PreferedAccount = pymono.util.find_in(personal, "UAH:black")[0]
        except: None
        return personal

    def setWebhook(self, webhookLink:str):

        if not isinstance(webhookLink, str):
            raise TypeError(f"webhookLink should be str, not {type(webhookLink)}")

        if pymono.util.is_URL_Valid(webhookLink):
            return self.makeRequest("personal/webhook", {"webHookUrl": webhookLink})
        else:
            raise ValueError(f"Incorrect URL for webhook webhookLink='{webhookLink}'")
    
    def getStatements(self, account:pymono.types.MonoAccount|str|int|None, timeFrom:datetime.datetime, timeTo:datetime.datetime = None):
        
        if isinstance(account, pymono.types.MonoAccount):
            account = account.AccountID
        elif isinstance(account, str):
            None
        elif account == 0:
            None
        elif account is None:
            account = 0
        else:
            raise TypeError(f"Account should be MonoAccount, str, 0 or None, not {type(account)}", account)
        
        if isinstance(timeFrom, datetime.datetime):
            if (datetime.datetime.now() - timeFrom).seconds > 2682000:
                raise ValueError(f"Max time difference for statements is 31 days + 1 hour")
        else:
            raise TypeError(f"timeFrom should be datetime.datetime, not {type(timeFrom)}", timeFrom)
        
        if isinstance(timeTo, datetime.datetime):
            if timeTo < timeFrom:
                raise ValueError(f"timeTo is smaller then timeFrom: To={timeTo}, From={timeFrom}")
        elif timeTo is None:
            None
        else:
            raise TypeError(f"timeFrom should be datetime.datetime or None, not {type(timeTo)}", timeTo)

        args = {"account": account, "from": int(timeFrom.timestamp())}
        if timeTo is not None:
            args["to"] = int(timeTo.timestamp())

        return self.makeRequest("personal/statement", args)

    def new_statement(self, statement, account):
        self._callback(statement, account)

    def process_statements(self, updates:dict, acc):
        for x in updates.keys():
            if x in self._processed_statements:
                continue
            self.new_statement(updates[x], acc)
            self._processed_statements.append(x)
        pickle.dump(self._processed_statements, open("processed.obj", "wb"))

    def process_new_updates(self, updates, acc):

        if isinstance(updates, pymono.types.error):
            raise RuntimeError(f"Error: {updates}")
        elif isinstance(updates, pymono.types.MonoStatements):
            self.process_statements(updates.Statements, acc)
        else:
            raise TypeError("Update is not MonoStatements, somehow")

    def __retrieve_updates(self, acc_to_update:pymono.types.MonoAccount = None):
        try:
            last_update = self._last_update_time[acc_to_update._dictName]
        except:
            last_update = datetime.datetime.now() - datetime.timedelta(hours=1)
        self._last_update_time[acc_to_update._dictName] = datetime.datetime.now()
        updates = self.getStatements(acc_to_update, last_update)
        self.process_new_updates(updates, acc_to_update)

    def polling(self, interval:int = 300, accounts_to_check:list[pymono.types.MonoAccount] = None, callback = print):

        """Period is time in seconds to wait between each request"""
        self.__stop_polling.clear()
        error_interval = 0.25
        pooling_thread = pymono.types.WorkerThread("Mono_PoolingThread")
        or_event = pymono.types.OrEvent(
            pooling_thread.done_event,
            pooling_thread.exception_event,
            pooling_thread.exception_event
        )
        self._callback = callback
        if accounts_to_check is None and self.PreferedAccount is not None: accounts_to_check = [self.PreferedAccount]
        elif accounts_to_check is None and self.PreferedAccount == None:
            self.getPersonal()
            if self.PreferedAccount is not None:
                accounts_to_check = [self.PreferedAccount]
            else:
                raise RuntimeError("Could not aqquire PreferedAccount")
        while True:
            for acc in accounts_to_check:
                while not self.__stop_polling.wait(interval):
                    or_event.clear()
                    try:
                        pooling_thread.put(self.__retrieve_updates, acc[0])
                        break
                    except Exception as E:
                        print(E)
                        raise E