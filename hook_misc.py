import requests
import base64
import re
from odin_cmd import *
import json
from telapi import *
def send_message1(id_hash, chat_id, text):
    print(text)

def id_regex(text):
    res = re.findall(r'[0-9]{7,15}', text)
    if res: return res[0]

def extract_id(update, text):
    text_id = id_regex(text)
    if text_id: return text_id, False , None
    try:
        if update["message"]["reply_to_message"]:
            user_id = update["message"]["reply_to_message"]["from"]["id"]
            is_group = False
    except:
        user_id = update["message"]["chat"]["id"]
        is_group = True
    return user_id , True, is_group

def get_gate_response(gate, text):
    try:
        text_without_cmd = text
        url = gate['url'] + '?message=' +text_without_cmd
        print("Request Url",url)
        print("Sent Text:", len(text_without_cmd), text_without_cmd)
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"}
        response = requests.get(url,headers=headers,timeout= 40).text
        return response
    except Exception as e:
        print("Request Error", e)
        return "Gate error"

def callback_user_check(query):
    for_user = query["data"].split("^")[0]
    print(f"For User: {for_user}  Sender : {query['from']['id']}")
    if not int(query['from']['id']) == int(for_user):
        print("This input is not for you")
        return False
    return True

def check_access(gate, user, is_group):
    if not is_group and not gate["private-allowed"]:
        return False
    if gate["type"] == "Premium":
            if user["type"] != "Premium":
                return False
                if gate["mass"] and (user["mass"] != True):
                    return False
            
    if gate["mass"] and (user["mass"] != True):
        return False
            
    return True
def get_idhash(botid):
    try:
        id_hash = base64.b64decode(botid).decode('UTF-8')
        return id_hash
    except:
        print('Cant decode botid ')
        return ""

def substr(text, start, end):
    try:
        return text.split(start)[1].split(end)[0]
    except: return

def detect_command(text):
    command = re.findall(r"/[a-zA-Z0-9]{1,20}", text)
    
    if command and text.startswith(command[0]+" "):
        rest = text[len(command[0])+1:]
        return command[0][1:],rest
        
    return None, None