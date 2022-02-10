import src, src.util
from src.types import MonoPersonalData, MonoStatements
#file with XToken
import data
#for getting statements
import datetime

client = src.MonoClient(data.XToken)
personal = client.getPersonal()
if isinstance(personal, MonoPersonalData):
    acc = src.util.find_in(personal, "7364") #Last 4 digits, card ID, CurrencyName, Account Type
else:
    print(f"Personal is {personal} ({type(personal)})")
    exit(1)
for xAcc in acc:
    statements = client.getStatements(xAcc, datetime.datetime(2022, 1, 11))
    if isinstance(statements, MonoStatements):
        foundStatements = src.util.find_in(statements, "Steam", True) #Also searches in description if last is true
        for statement in foundStatements:
            print(statement)
    else:
        print(statements)