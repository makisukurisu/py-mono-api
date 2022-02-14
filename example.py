import pymono, pymono.util, pymono.types
import telebot
#file with XToken
import data

client = pymono.MonoClient(data.XToken)

bot = telebot.TeleBot(data.BotToken) #to send messages

personal = client.getPersonal() #to avoid 1 minute more wait

def sendNewStatements(statement:pymono.types.MonoStatement, account:pymono.types.MonoAccount):
    #statement should be first argument (and the only one? Or at least - the only non-positional)
    bot.send_message(data.TransactionChatID, "Got a new transaction from account: {0}\nAmount: {1} {4}\nDescription: {2}\n\nLeft on account: {3} {5}\n\nAt: {6}".format(
        account.MaksedPan,
        statement.SignedAmount,
        statement.Description,
        statement.Balance,
        account.CCYName,
        statement.CCYName,
        statement.Time
        ))
    #sending latest statement to some chat on telegram

checkList = [pymono.util.find_in(personal, "UAH:black"), pymono.util.find_in(personal, "USD:black")]

client.polling(60, checkList, sendNewStatements) #threaded pooling, nothing below will be executed untill polling is stoped