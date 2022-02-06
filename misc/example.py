import src

client = src.MonoClient("")
currency = client.getCurrency()
print(currency)
print(type(currency))