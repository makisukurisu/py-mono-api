import src
#file with XToken
import data
#for getting statements
import datetime

client = src.MonoClient(data.XToken)
personal = client.getPersonal()
accounts = personal.Accounts
acc = accounts[input()] #get from previous line, yes currently -- using manual input or by using keys method, or whatever you like to use
statements = client.getStatements(acc, datetime.datetime(2022, 2, 1))
statements