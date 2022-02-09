import datetime
import src.types, src.util
import requests

class MonoClient:

    def __init__(self, api_key: str, ) -> None:
        self.XToken = api_key
        self.Endpoint = "https://api.monobank.ua/"
    
    def makeRequest(self, path, args:dict=None):
        if path == "bank/currency":
            req = requests.get(self.Endpoint + path)
            if req.status_code == 200:
                return src.types.MonoCCYs.de_json(req.json(), req)
            else:
                return src.types.error.de_json(req.json(), req)
        elif path == "personal/client-info":
            req = requests.get(self.Endpoint + path, headers={"X-Token": self.XToken})
            if req.status_code == 200:
                return src.types.MonoPersonalData.de_json(req.json(), req)
            else: return src.types.error.de_json(req.json(), req)
        elif path == "personal/webhook":
            req = requests.post(self.Endpoint + path, src.util.to_JSON(args), headers={"X-Token": self.XToken})
            if req.status_code == 200:
                return src.types.success(req.headers)
            else:
                return src.types.error.de_json(req.json(), req)
        elif path == "personal/statement":
            path += f"/{args['account']}/{args['from']}"
            if 'to' in args.keys():
                path += f"/{args['to']}"
            req = requests.get(self.Endpoint + path, headers={"X-Token": self.XToken})
            if req.status_code == 200:
                return src.types.MonoStatements.de_json(req.json(), req)
            else:
                return src.types.error.de_json(req.json(), req)

    def getCurrency(self):
        return self.makeRequest("bank/currency")
    
    def getPersonal(self):
        return self.makeRequest("personal/client-info")

    def setWebhook(self, webhookLink:str):

        if not isinstance(webhookLink, str):
            raise TypeError(f"webhookLink should be str, not {type(webhookLink)}")

        if src.util.is_URL_Valid(webhookLink):
            return self.makeRequest("personal/webhook", {"webHookUrl": webhookLink})
        else:
            raise ValueError(f"Incorrect URL for webhook webhookLink='{webhookLink}'")
    
    def getStatements(self, account:src.types.MonoAccount|str|int|None, timeFrom:datetime.datetime, timeTo:datetime.datetime = None):
        
        if isinstance(account, src.types.MonoAccount):
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