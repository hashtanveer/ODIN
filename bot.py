
from api_tool import *
from db_tool import *
from hndler import *
from hndler import main_menu
from config import BOT_TOKEN, HOST
import telebot
bot = telebot.TeleBot(BOT_TOKEN)


cmds = """/addbot apiid:hash 
/deletebot  : to delete current bot
/mybot : manage bot
/gate gateName : manage gate settings"""
welcome = """You awakend ODIN!

Press /req  and get requests menu"""
@bot.message_handler(commands=['start'])
def send_welcome(message):
    print(message)
    id_ = message.chat.id
    username1 = message.chat.first_name
    bot.send_message(id_,welcome,parse_mode='Markdown')
    
@bot.message_handler(commands=['req'])
def send_cmds(message):
    username1 = message.chat.first_name
    bot.send_message(message.chat.id,cmds ,parse_mode='Markdown')

def check_auth(query):
    for_user = query.data.split("^")[0]
    #print(f"For User: {for_user}  Sender : {query.from_user.id}")
    if not int(query.from_user.id) == int(for_user):
        bot.answer_callback_query(query.id, "This input is not for you", show_alert=True)
        return False
    return True

def delete_msg(message):
    bot.delete_message(message.chat.id,message.id)

@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
    #Callback data format
    #user_id:menu_code:

    if query.data == "null":return #For dummy buttons
    #Check who pressed button
    if not check_auth(query): return
    #check exit
    if query.data.endswith("exit"): delete_msg(query.message)
    
    data = query.data
    #For main menu
    s_data = data.split("^")
    user_id = s_data[0]#From user
    menu = s_data[1]#M or gate
    
    if menu == "M":
        if s_data[2] == 'MN':
            send_manager(query)
        elif s_data[2] == 'AP':
            send_api(bot, query)
    
    #Manager menu query
    if menu == "manager":
        manager_menu_hdl(bot, query)#Manager Menu
    elif menu == "mp":
        api_menu_handler(bot, query)#MYapi menu callback
    elif menu == "gate":
        gate_menu_hndl(bot, query)
        
def send_manager(query, replace=False,replace_id=None):
    if replace : user_id = replace_id
    else : user_id = query.from_user.id
    
    bott = O.check_bot(user_id)
    manager_menu_markup = manager_menu(bott, user_id)
    bot.edit_message_text(text=query.message.text, chat_id=(query.message.chat.id), message_id=(query.message.id), reply_markup=manager_menu_markup)

@bot.message_handler(commands=['addbot'])
def add_bot(message):
    #Check if User own a bot already
    if(O.check_bot(message.from_user.id)):
        bot.send_message(message.from_user.id,"You already own a bot")
        return
    try:
        id_hash =validate_api(message.text[6:])
    #Check if creds are valid
    except Exception as error:
        print("Error:",error,"  using creds: ",message.text[6:])
        bot.send_message(message.chat.id,str(error))
        return
    
    #Get additional bot info
    info = get_bot_info(id_hash)#from api_tool
    #Add bot to database
    O.add_bot(message.from_user.id,id_hash,info)
    #set webhook
    set_webhook(id_hash,HOST)
    bot.send_message(message.from_user.id,f"Bot **@{info['username']}** added successfully",parse_mode='Markdown')

@bot.message_handler(commands=['mybot'])
def my_bot_manager(message, replace=False, replace_id=None):
    my_bot(bot, message)

@bot.message_handler(commands=['deletebot'])
def del_bot(message):
    #Check if User own a bot already
    if(not O.check_bot(message.from_user.id)):
        bot.send_message(message.from_user.id,"You dont own a bot")
        return
    
    #delete bot from database
    O.delete_bot(message.from_user.id)
    bot.send_message(message.from_user.id,"Bot removed successfully",parse_mode='Markdown')


if __name__ == "__main__":
    bot.polling(none_stop=True, interval=1, timeout=1)
