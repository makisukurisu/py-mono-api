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
                return src.types.response.de_json(req.json())
            else:
                return src.types.error.de_json(req.json())

    def getCurrency(self):
        return self.makeRequest("bank/currency")