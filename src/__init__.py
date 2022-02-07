import src.types
import requests

class MonoClient:

    def __init__(self, api_key: str, ) -> None:
        self.XToken = api_key
        self.Endpoint = "https://api.monobank.ua/"
    
    def makeRequest(self, path):
        if path == "bank/currency":
            req = requests.get(self.Endpoint + path)
            if req.status_code == 200:
                return src.types.MonoCCYs.de_json(req.json(), req)
            else:
                return src.types.error.de_json(req.json(), req)
        else:
            req = requests.get(self.Endpoint + path, headers={"X-Token": self.XToken})
            if req.status_code == 200:
                return src.types.MonoPersonalData.de_json(req.json(), req)
            else: return src.types.error.de_json(req.json(), req)


    def getCurrency(self):
        return self.makeRequest("bank/currency")
    
    def getPersonal(self):
        return self.makeRequest("personal/client-info")