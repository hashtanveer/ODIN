from flask import Flask, request, render_template,jsonify, redirect
import flask
app = Flask(__name__)
app.config["DEBUG"] = True
import time
import base64
import json
from db_tool import *
from hook_misc import *
from odin_cmd import *
from telapi import *
import telebot

@app.route('/', methods =["GET", "POST"]) 
def home():
    return "Webhook Working"


@app.route('/bots/<botid>', methods =["GET", "POST"]) 
def wew(botid):
    #token = 'ask'
    body = request.data
    @flask.after_this_request
    def process_after_request(response):
        @response.call_on_close
        def name():
            bot_handler(botid,body)
        return response
        
    return "Hello world"

def bot_Worker(token):
    print('Botworker running :',token)

def bot_handler(botid,body): 
    #update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    
    #Decode botid from base64 encoded form
    id_hash = get_idhash(botid)
    if not id_hash:return
    update = json.loads(body)
    print(update)
    #Json decode Message object
    if "callback_query" in update:
        callback_handler(id_hash, update)
        return ""
    message = update['message']
    received_text = message["text"]
    chat = message['chat']
    from_ = message['from']
    
    c_time = str(time.time())
    print('Chat ID' , chat["id"],'Text Received', received_text)
    
    
    #Get bott object from database
    bott = O.bot_info(id_hash)
    if not bott:
        print("No Bot found for",id_hash)
        return ""
    
    #Check if user exists in bot
    
    
    
    common_cmds = ["/start", "/cmds", "/odin", "/register"]
    if any(received_text.startswith(x) for x in common_cmds):
        #Check common cmds
        
        if received_text == "/start":
            user = User.check(id_hash, chat["id"])
            if not user:
                send_message(id_hash, chat["id"], "User not found in bot, use /register ",reply_to_message_id= message['message_id'])
                
            send_start(id_hash, from_)
        elif received_text == "/register":
            if not bott['allow_register']:
                send_message(id_hash, chat["id"], "Registeration is halted by owner",reply_to_message_id= message['message_id'])
                return ""
            user  = User.check(id_hash, from_["id"])
            if user:
                send_message(id_hash, chat["id"], "You are already a user, use /start",reply_to_message_id= message['message_id'])
                return ""
            User.add(id_hash, from_["id"])
            
            send_message(id_hash, chat["id"], "Registered successfully, use /start",reply_to_message_id= message['message_id'])

        elif received_text == "/cmds": send_cmds(id_hash, message,)
        elif received_text == "/odin":
            #check if sender is owner
            user_bot = O.check_bot(from_["id"],id_hash=True)
            if user_bot != id_hash:
                send_message1(id_hash, chat["id"], "you are not owner")
                return ""
            #Extract ID for Odin
            odin_id, real , is_group = extract_id(update, received_text)
            #Find User in database
            user = User.check(id_hash, odin_id)
            if not user:
                if real: ask_add_user(id_hash, message, odin_id, is_group)
                else: send_message(id_hash, chat["id"], "No user found",reply_to_message_id= message['message_id'])
                return ""
            #send odin menu
            send_odin_menu(id_hash, chat["id"], user, from_)
        return "" 
        
    command,extracted_text = detect_command(received_text)
    
    print("Command:",command,"Text:",extracted_text)
    #if no command or no text = Stop
    if not command or not extracted_text:
        print("No command or text found in ",received_text)
        return ""

    #check if gate exists in bot
    
    gate = find_gate(bott, command)
    if not gate:
        return send_message1(id_hash, chat["id"], "Api not found")
    
    user = User.check(id_hash, chat["id"])
    if not user:
        print("User",chat["id"],"not found in bot, use /register ", bott["info"]["username"])
        send_message(id_hash, chat["id"], "User not found in bot, use /register ",reply_to_message_id= message['message_id'])
        return ""
    is_group = user["is_group"]
    
    
    #Antispam check
    
    message_time = message['date']
    last_used = user['last_used']
    
    diff = message_time - last_used
    print("Time differnce :",diff)
    
    
    if bott['anti-spam'][user['type']] > diff:
        send_message(id_hash, chat["id"], f"⚠️ANTISPAM ⚠️\nWait for {bott['anti-spam'][user['type']] - diff}s",reply_to_message_id= message['message_id'])
        return ""
    
    #check authority
    allow_use = check_access(gate, user, is_group)
    if not allow_use:
        send_message(id_hash, chat["id"], "⚠️You are not authorized for this api⚠️",reply_to_message_id= message['message_id'])
        return ""
    #send_message1(id_hash, chat["id"], "Authorized")
    #Update last used
    User.update_lastused(id_hash, user['_id'], message_time)
    
    if not gate["power_on"]:
        send_message(id_hash, chat["id"], "⚠️Gate is temporarily down⚠️",reply_to_message_id= message['message_id'])
        return ""
    
    #Send waiting message
    wait_message = send_message(id_hash, chat["id"], "Waiting for API response",reply_to_message_id= message['message_id'])
    message_id = wait_message['result']['message_id']
    #send message to gate
    
    text_list = []
    if not gate['mass']:
        text_list.append(extracted_text)
    else:
        for line in extracted_text.split("\n"):
            text_list.append(line)
            
    Total_text = ""
    for text in text_list:
        reply_from_gate = get_gate_response(gate, text)
        print("Reply from gate", text)
        #send back reply from api
        Total_text += reply_from_gate + "\n"
        
        edit_message(id_hash, chat["id"], message_id, Total_text)

def callback_handler(id_hash, update):
    #If null key pressed return
    if "null" in  update["callback_query"]["data"]: return
    
    query = update["callback_query"]
    print("Button Data:",query["data"])
    
    #Check who pressed
    if not callback_user_check(query): return ""
    
    query_data = query["data"]
    data_list = query_data.split("^")
    menu_name = data_list[1]#Menu_name = odin,cmds,adduser
    
    if menu_name == "odin":
        odin_menu_hndler(id_hash, query)
    elif menu_name == "api":
        cmd_menu_hndler(id_hash, query)
    elif menu_name == "adduser":
        adduser_hndler(id_hash, query)
    
    

app.run(host="localhost", port=80, debug=True,threaded=True)