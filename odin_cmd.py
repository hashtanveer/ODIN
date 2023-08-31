from api_tool import bool_to_emoji
from telapi import *
from db_tool import *

def send_start(id_hash, from_):
    print("Start message\n check /cmds")

def send_cmds(id_hash, message):
    text = "ϟ 𝐌𝐲 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬"
    menu = cmd_menu(message["from"]["id"])
    chat_id = message["chat"]["id"]
    reply_to = message["message_id"]
    send_message(id_hash, chat_id, text, inline_keyboard=menu, reply_to_message_id=reply_to)

def cmd_menu_hndler(id_hash, query):
    query_data = query["data"]
    chat_id = query["message"]["chat"]["id"]
    message_id = query["message"]["message_id"]
    menu_for, menu, gate_type = query_data.split("^")
    
    #If pressed back
    if gate_type == "back":
        text = "ϟ 𝐌𝐲 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬"
        menu = cmd_menu(menu_for)
        edit_message(id_hash, chat_id, message_id, text, inline_keyboard=menu)
    
    bott = O.bot_info(id_hash)
    Text = Gates_details(bott, gate_type)
    #If no gate  stop
    if not Text :return
    
    new_menu = [ButtonRow([Button("🔙",f"{menu_for}^api^back"), Button("Exit", f"{menu_for}^exit^")] )]
    
    edit_message(id_hash, chat_id, message_id, Text, new_menu)
    

def cmd_menu(menu_for):
    Gates_title = Button("Gates", f"{menu_for}^null")
    premium = Button("Premium", f"{menu_for}^api^Premium")
    mass = Button("Mass", f"{menu_for}^api^Mass")
    free = Button("Free", f"{menu_for}^api^Free")
    exit_ = Button("Exit",f"{menu_for}^exit")
    row1 = ButtonRow([Gates_title])
    row2 = ButtonRow([free,premium,mass])
    row3 = ButtonRow([exit_])
    return [row1, row2, row3]
    
def send_odin_menu(id_hash, chat_id ,user, from_):
    reply = create_odin_menu(user, meun_for = from_['id'])
    send_message(id_hash, chat_id, "This is menu", inline_keyboard=reply)

def odin_menu_hndler(id_hash, query):
    query_data = query["data"]
    owner_id, menu, func, user_id, val = query_data.split("^")
    user_id = int(user_id)
    if func in ('cm', 'cp'):
        if val == '1':state = True
        elif val == '0':state = False
        
    if func == "ct":
        User.change_type(id_hash, user_id, val)
    elif func == "cp":
        User.change_private(id_hash, user_id, state)
    elif func == "cm":
        User.change_mass(id_hash, user_id, state)
    elif func == "du":
        User.delete(id_hash, user_id)
        Text = "User Deleted"
        new_menu = None
        
    if func != "du":
        user = User.check(id_hash, user_id )
        #Create new menu after changes
        new_menu = create_odin_menu(user, meun_for=owner_id)
        Text = "This is menu"
    
    chat_id = query["message"]["chat"]["id"]
    message_id = query["message"]["message_id"]
    
    edit_message(id_hash, chat_id, message_id, Text, inline_keyboard=new_menu)
    
    
def create_odin_menu(user, meun_for):
    #Type Button
    if user['type'] == 'Free': ct = 'Premium'
    else: ct = 'Free'
    user_type = Button("Type", "null")
    user_type_val = Button(user["type"],
                    f"{meun_for}^odin^ct^{user['_id']}^{ct}")
    type_row = ButtonRow([user_type, user_type_val])
    
    #Mass Button
    if user['mass']:cm = 0
    else: cm = 1
    
    mass = Button("Mass","null")
    mass_val = Button(bool_to_emoji(user["mass"]),
                f"{meun_for}^odin^cm^{user['_id']}^{cm}")
    
    mass_row = ButtonRow([mass, mass_val])
    #Private-allowed
    if user['private-allowed']: cp = 0
    else: cp = 1
    priv_title = Button("Private","null")
    priv_val = Button(bool_to_emoji(user["private-allowed"]),
                        f"{meun_for}^odin^cp^{user['_id']}^{cp}")
    
    priv_row = ButtonRow([priv_title, priv_val])
    
    #Exit
    exit_ = Button("Exit", f"{meun_for}^exit")
    del_user = Button("Delete", f"{meun_for}^odin^du^{user['_id']}^")
    last_row = ButtonRow([del_user, exit_])
    menu = [type_row,mass_row,priv_row,last_row]
    return menu

def ask_add_user(id_hash, message, to_add_id, is_group):
    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    user_type = "User"
    if is_group: user_type = "Group"
    Text = f"{user_type} not found in DB"
    
    menu = add_user_menu(message["from"]["id"], to_add_id, is_group)
    send_message(id_hash, chat_id, Text, inline_keyboard=menu, reply_to_message_id= message_id)

def adduser_hndler(id_hash, query):
    query_data = query["data"]
    owner_id, menu, user_id, is_group = query_data.split("^")
    
    user_id = int(user_id)
    if is_group == '1': is_group = True
    else: is_group = False
    
    User.add(id_hash, user_id, is_group)
    
    Text = "User added, now you can use /odin again"
    
    chat_id = query["message"]["chat"]["id"]
    message_id = query["message"]["message_id"]
    
    edit_message(id_hash, chat_id, message_id, Text)

def add_user_menu(menu_for, to_add_id, is_group):
    val = 0
    if is_group: val = 1
    add = Button("Add User", f"{menu_for}^adduser^{to_add_id}^{val}")
    exit_ = Button("Exit",f"{menu_for}^exit")
    return [ButtonRow([add, exit_])]