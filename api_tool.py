import requests
import re
import telebot
import base64

#x = test_api("1845390268:AAGhGupmRYeB7mFFm7aRqIoqg-poc6KNKnA")
def validate_api(api):
    x = re.findall('[0-9]{6,10}:[A-Za-z0-9_]{32,37}',api)
    if not x : raise Exception("No valid api_id:hash found")
    
    res = requests.get("https://api.telegram.org/bot"+x[0]+"/getwebhookinfo")
    if res.status_code == 200:
        return x[0]
    else:
        raise Exception("Provided api_id:hash invalid")


def get_bot_info(id_hash):
    new_bot = telebot.TeleBot(id_hash)
    return new_bot.get_me().__dict__
 
def encode(string):
    return base64.b64encode(string.encode('utf-8')).decode('utf-8')

def set_webhook(id_hash,host):
    print("=============[Hook function]================================")
    print("id_hash", id_hash)
    print("Host", host)
    x = requests.get('https://api.telegram.org/bot' + id_hash + '/setwebhook?url='+host+"/bots/"+encode(id_hash))
    print(x.status_code,x.text)
    if x.status_code == 200:
        return True
    else:
        print("Failed")

def bool_to_emoji(val):
    if val:
        return " ☑️ "
    return " ✖️ "  
