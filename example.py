import src
#file with XToken
import data

client = src.MonoClient(data.XToken)
personalData = client.getPersonal()
print(personalData)
personalData #debug stop