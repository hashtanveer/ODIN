import telebot, re
from api_tool import *
from db_tool import *
import validators

def validate_gate_name(name):
    if name in (None, ''):
        raise Exception('No name found')
        return
    if ' ' in name:
        raise Exception('Name cant include spaces')
        return
    found_name = re.findall('[a-zA-Z0-9]{1,20}', name)
    if found_name:
        return found_name[0]
    raise Exception('No valid name found')

def add_gate( message, bot, id_hash, url=None, name=None, desc=None):
    if message.text == "/cancel": return
    if url and name and desc:
        Gates.add_gate(id_hash,url,name,message.text)
        text = f"""*Gate Added*
Name : /{name}
URI  : `{url}`
Desc : {message.text}
"""
        bot.send_message(text = text,chat_id=message.chat.id ,parse_mode="Markdown")
    elif url and name:
        name = message.text
        error = False
        try:
            valid_name = validate_gate_name(name)
        except Exception as e:
            error = True
            reply = str(e)
        if error:
            msg = bot.send_message(text=reply+"\nTry again",chat_id=message.chat.id)
            bot.register_next_step_handler(msg, add_gate, bot, id_hash, url=url, name=True)
            return
        bott = O.bot_info(id_hash)
        if find_gate(bott, name):
            msg = bot.send_message(text="Same gate name already exists",chat_id=message.chat.id)
            bot.register_next_step_handler(msg, add_gate, bot, id_hash, url=url, name=True)
            return
        text = f"""Name : '{name}' used for 
=>URI : {url}
Enter description for this gate"""
        msg = bot.send_message(text=text,chat_id=message.chat.id)
        bot.register_next_step_handler(msg, add_gate, bot, id_hash, url=url, name=name, desc=True)
    elif url:
        text = message.text
        if validators.url(text):
            msg = bot.send_message(text="Got URI, Enter gate name for this URI,i.e sk,ch",chat_id=message.chat.id)
            bot.register_next_step_handler(msg, add_gate, bot, id_hash, url=text, name=True)
        else:
            msg = bot.send_message(text="Invalid URL, retry",chat_id=message.chat.id)
            bot.register_next_step_handler(msg, add_gate, bot, id_hash, url=True)
    elif url==None:
       msg = bot.send_message(text="Enter API URI :",chat_id=message.chat.id)
       bot.register_next_step_handler(msg, add_gate, bot, id_hash, url=True)


def change_name_hndlr(message, bot, gate_name, chatid):
    if not chatid == message.chat.id:
        return
    name = message.text
    try:
        x = message.text == '/cancel'
        if x:
            return
    except:
        pass

    id_hash = O.check_bot((message.from_user.id), get_bot=False, id_hash=True)
    bott = O.bot_info(id_hash)
    reply = False
    try:
        name = validate_gate_name(name)
    except Exception as e:
        try:
            reply = str(e)
        finally:
            e = None
            del e

    if find_gate(bott, name):
        reply = 'Same gate name already exists'
    print('Reply', reply)
    if reply:
        reply += '\nTry again'
        msg = bot.send_message(text=reply, chat_id=(message.from_user.id))
        bot.register_next_step_handler(msg, change_name_hndlr, gate_name, chatid=chatid)
        return
    Gates.change_name(id_hash, gate_name, name)
    bot.send_message(chat_id=(message.chat.id), text=f"Name Updated  '{name}' ")

def change_description(message,bot, gate_name, chatid):
    if not chatid == message.chat.id:
        return
    try:
        x = message.text == '/cancel'
        if x:
            return
    except:
        pass

    desc = message.text
    if desc in (None, '', ' '):
        desc = ''
    print('Description', desc)
    id_hash = O.check_bot((message.from_user.id), get_bot=False, id_hash=True)
    Gates.change_description(id_hash, gate_name, desc)
    bot.send_message(chat_id=(message.chat.id), text='Description Updated')


def gate_menu(gate, user_id):
    menu = telebot.types.InlineKeyboardMarkup(row_width=4)

    if gate['type'] == 'Free':
        ct = 'Premium'
    else:
        ct = 'Free'
    gate_type = telebot.types.InlineKeyboardButton('Type', callback_data='null')
    gate_type_val = telebot.types.InlineKeyboardButton((gate['type']), callback_data=f"{user_id}^gate^{gate['name']}^ct^{ct}")
    menu.add(gate_type, gate_type_val)

    if gate['mass']:
        cm = 0
    else:
        cm = 1
    mass = telebot.types.InlineKeyboardButton('Mass', callback_data='null')
    mass_val = telebot.types.InlineKeyboardButton((bool_to_emoji(gate['mass'])), callback_data=f"{user_id}^gate^{gate['name']}^cm^{cm}")
    menu.add(mass, mass_val)

    if gate['private-allowed']:
        cp = 0
    else:
        cp = 1
    private = telebot.types.InlineKeyboardButton('Private', callback_data='null')
    private_val = telebot.types.InlineKeyboardButton((bool_to_emoji(gate['private-allowed'])), callback_data=f"{user_id}^gate^{gate['name']}^cp^{cp}")
    menu.add(private, private_val)

    change_name = telebot.types.InlineKeyboardButton('Edit \nName', callback_data=f"{user_id}^gate^{gate['name']}^cn^")
    change_desc = telebot.types.InlineKeyboardButton('Edit \nDesc', callback_data=f"{user_id}^gate^{gate['name']}^cd^")
    menu.add(change_name, change_desc)

    exit_ = telebot.types.InlineKeyboardButton('Exit', callback_data=f"{user_id}^exit")
    back_btn = telebot.types.InlineKeyboardButton('🔙', callback_data=f"{user_id}^gate^back^^")
    
    menu.add(back_btn, exit_)
    return menu


def gate_menu_hndl(bot, query):
    data = query.data
    print(data)
    user_id, _, gate_name, func, val = data.split('^')
    if gate_name == "back":
        send_api(bot, query, back=True)
        return
    normal_changes = False
    if func in ('ct', 'cm', 'cp', 'cr'):
        id_hash = O.check_bot((query.from_user.id), get_bot=False, id_hash=True)
        normal_changes = True
    if func in ('cm', 'cp', 'cr'):
        if val == '1':
            state = True
        elif val == '0':
            state = False
    if func == 'ct':
        Gates.change_type(id_hash, gate_name, val)
    elif func == 'cm':
        Gates.change_mass(id_hash, gate_name, state)
    elif func == 'cp':
        Gates.change_private(id_hash, gate_name, state)
    elif func == 'cr':
        Gates.change_regex(id_hash, gate_name, state)
    if normal_changes:
        bott = O.bot_info(id_hash)
        gate = find_gate(bott, gate_name)
        gate_menu_markup = gate_menu(gate, user_id)
        bot.edit_message_text(text=query.message.text, reply_markup=gate_menu_markup, chat_id= query.message.chat.id, message_id= query.message.id)

        #edit_gate((query.message), replace=True, gate_name=gate_name, id_hash=id_hash)
        return
    if func == 'cd':
        msg = bot.edit_message_text(text='Send description you want to set \nOr send /cancel to cancel update', chat_id=(query.from_user.id), message_id=(query.message.id))
        bot.register_next_step_handler(msg, change_description, bot, gate_name, chatid=(query.message.chat.id))
    if func == 'cn':
        msg = bot.edit_message_text(text='Send name you want to set \nOr send /cancel to cancel update', chat_id=(query.from_user.id), message_id=(query.message.id))
        bot.register_next_step_handler(msg, change_name_hndlr, bot, gate_name, chatid=(query.message.chat.id))


def send_api(bot, query,back = False):
    user_id = query.from_user.id
    bott = O.check_bot(user_id)
    api_menu = api_menu_builder(bott, user_id)
    if back:
        text = bot_desc(bott)
    else: text = query.message.text
    bot.edit_message_text(text=text, reply_markup=api_menu, parse_mode="html",chat_id= query.message.chat.id, message_id= query.message.id)


def api_menu_handler(bot, query):
    user_id = query.from_user.id
    
    s_data = query.data.split("^")
    command = s_data[2]
    
    if command == "back":
        my_bot(bot, query.message, replace=True, replace_id=user_id)
    elif command == "addgate":
        id_hash = O.check_bot(user_id, get_bot=False,id_hash=True)
        add_gate(query.message,bot, id_hash)
    else:
        print("Gate Name", command)
        bott = O.check_bot(user_id)
        #IF back
        gate = find_gate(bott, command)
        gate_menu_markup = gate_menu(gate, user_id)
        bot.edit_message_text(text=gate_desc(gate), reply_markup=gate_menu_markup, chat_id= query.message.chat.id, message_id= query.message.id)

def gate_desc(gate):
    return f"""Gate Name : {gate['name']}
Gate description : {gate['description']}
Api URI: `{gate["url"]}`"""

def api_menu_builder(bott, user_id):
    api_menu = telebot.types.InlineKeyboardMarkup(row_width=2)
    #callback_data=f"{user_id}^manager^casf^{inc_val}"
    add_gate_btn = telebot.types.InlineKeyboardButton('➕', callback_data=f"{user_id}^mp^addgate")
    back_btn = telebot.types.InlineKeyboardButton('🔙', callback_data=f"{user_id}^mp^back")
    if bott["gate_count"] == 0:
        api_menu.add(back_btn, add_gate_btn)
        return api_menu

    free_gates = []
    premium_gates = []
    
    #Seperate Gates
    for gate in bott["gates"]:
        name = gate["name"]
        if gate["type"] == "Premium":premium_gates.append(gate["name"])
        else: free_gates.append(gate["name"])
    #Add free gates and title
    free_gates_count = len(free_gates)
    if not free_gates_count == 0:
        free_title = telebot.types.InlineKeyboardButton('FREE', callback_data=f"null")
        api_menu.add(free_title)
        
        odd = free_gates_count % 2
        if odd:
            #seperate last gate
            last_gate = free_gates[-1]
            free_gates.pop()

        for i in range(0,len(free_gates),2):
            gate1name, gate2name = free_gates[i], free_gates[i+1]
            btn1 = telebot.types.InlineKeyboardButton(gate1name, callback_data=f"{user_id}^mp^{gate1name}")
            btn2 = telebot.types.InlineKeyboardButton(gate2name, callback_data=f"{user_id}^mp^{gate2name}")
            api_menu.add(btn1, btn2)
        if odd:
            last_gate_btn = telebot.types.InlineKeyboardButton(last_gate, callback_data=f"{user_id}^mp^{last_gate}")
            api_menu.add(last_gate_btn)
    #Add Premium gates and title
    premium_gates_count = len(premium_gates)
    if not (premium_gates_count == 0):
        premium_title = telebot.types.InlineKeyboardButton('PREMIUM', callback_data=f"null")
        api_menu.add(premium_title)
        
        odd = premium_gates_count % 2
        if odd:
            #seperate last gate
            last_gate = premium_gates[-1]
            premium_gates.pop()

        for i in range(0,len(premium_gates),2):
            gate1name, gate2name = premium_gates[i], premium_gates[i+1]
            btn1 = telebot.types.InlineKeyboardButton(gate1name, callback_data=f"{user_id}^mp^{gate1name}")
            btn2 = telebot.types.InlineKeyboardButton(gate2name, callback_data=f"{user_id}^mp^{gate2name}")
            api_menu.add(btn1,btn2)
        if odd:
            last_gate_btn = telebot.types.InlineKeyboardButton(last_gate, callback_data=f"{user_id}^mp^{last_gate}")
            api_menu.add(last_gate_btn)
    api_menu.add(back_btn, add_gate_btn)
    return api_menu

def manager_menu_hdl(bot, query):
    user_id = query.from_user.id
    data = query.data
    _, _l, func, val = data.split('^')
    print('Manager Menu Handler')
    print(func, val)
    if func == 'back':
        my_bot(bot, (query.message), replace=True, replace_id=user_id)
        return
    elif func == 'creg':
        creg = False
        if val == '1': creg = True
        id_hash = O.check_bot((query.from_user.id), get_bot=False, id_hash=True)
        O.change_register(id_hash, creg)
    elif func.startswith('cas'):
        mode = 'Free'
        if func[3] == 'p':
            mode = 'Premium'
        id_hash = O.check_bot((query.from_user.id), get_bot=False, id_hash=True)
        Gates.change_antispam(id_hash, mode, int(val))
    else:
        if func == 'cp':
            cp = False
            if val == '1':
                cp = True
            id_hash = O.check_bot((query.from_user.id), get_bot=False, id_hash=True)
            O.change_power(id_hash, cp)
    
    bott = O.bot_info(id_hash)
    manager_menu_markup = manager_menu(bott, user_id)
    bot.edit_message_text(text=query.message.text, chat_id=(query.message.chat.id), message_id=(query.message.id), reply_markup=manager_menu_markup)


def manager_menu(bott, user_id):
    #Power buttons
    if bott['power_on']:
        power_state = 0
    else:
        power_state = 1
    menu = telebot.types.InlineKeyboardMarkup(row_width=4)
    bot_power = telebot.types.InlineKeyboardButton('Power', callback_data='null')
    bot_power_val = telebot.types.InlineKeyboardButton((bool_to_emoji(bott['power_on'])), callback_data=f"{user_id}^manager^cp^{power_state}")
    menu.add(bot_power, bot_power_val)
    
    #Allow Registerations
    if bott['allow_register']:
        allow_register = 0
    else:
        allow_register = 1
    register_button = telebot.types.InlineKeyboardButton('Allow Register', callback_data='null')
    register_val = telebot.types.InlineKeyboardButton((bool_to_emoji(bott['allow_register'])), callback_data=f"{user_id}^manager^creg^{allow_register}")
    menu.add(register_button, register_val)

    #FREE Gate anti-spam
    low_val = inc_val = 10
    if bott['anti-spam']['Free'] == 0:
        low_val = 0
    elif bott['anti-spam']['Free'] == 120:
            inc_val = 0

    free_antispam = telebot.types.InlineKeyboardButton('Free Antispam', callback_data='null')

    less = telebot.types.InlineKeyboardButton('◀️', callback_data=f"{user_id}^manager^casf^{-low_val}")
    more = telebot.types.InlineKeyboardButton('▶️', callback_data=f"{user_id}^manager^casf^{inc_val}")
    free_antsp_val = telebot.types.InlineKeyboardButton((f"{bott['anti-spam']['Free']}"), callback_data='null')

    menu.add(free_antispam)
    menu.add(less, free_antsp_val, more)

    #Premium Gate antispam

    low_val = inc_val = 10
    if bott['anti-spam']['Premium'] == 0:
        low_val = 0
    elif bott['anti-spam']['Premium'] == 120:
            inc_val = 0

    premium_antispam = telebot.types.InlineKeyboardButton('Premium Antispam', callback_data='null')

    less = telebot.types.InlineKeyboardButton('◀️', callback_data=f"{user_id}^manager^casp^{-low_val}")
    more = telebot.types.InlineKeyboardButton('▶️', callback_data=f"{user_id}^manager^casp^{inc_val}")
    premium_antsp_val = telebot.types.InlineKeyboardButton((f"{bott['anti-spam']['Premium']}"), callback_data='null')

    menu.add(premium_antispam)
    menu.add(less, premium_antsp_val, more)

    back = telebot.types.InlineKeyboardButton('Back', callback_data=f"{user_id}^manager^back^null")
    menu.add(back)
    return menu
        
    
def my_bot(bot, message, replace=False, replace_id=None):
    if replace: user_id = replace_id
    else: user_id = message.from_user.id
    #Check if User own a bot already
    user_s_bot = O.check_bot(user_id)
    if not replace and (not user_s_bot):
        bot.send_message(user_id,"You dont own a bot \nWatch /cmds to add one")
        return
        
    nmessage = bot_desc(user_s_bot)
    MainMenu = main_menu(user_id)
    if replace: bot.edit_message_text(text=str(nmessage),reply_markup=MainMenu,parse_mode="html",chat_id=(message.chat.id), message_id=(message.id))
    else:bot.send_message(user_id,str(nmessage),reply_markup=MainMenu,parse_mode="html")

def main_menu(user_id):
    MainMenu = telebot.types.InlineKeyboardMarkup(row_width=2)
    #static = telebot.types.InlineKeyboardButton("Statistics",callback_data=f"{message.from_user.id}^M^ST")
    manage = telebot.types.InlineKeyboardButton("Manage",callback_data=f"{user_id}^M^MN")
    my_apis = telebot.types.InlineKeyboardButton("My Apis",callback_data=f"{user_id}^M^AP")
    exit_ = telebot.types.InlineKeyboardButton("Exit",callback_data=f"{user_id}^exit")
    MainMenu.add(manage,my_apis)
    MainMenu.add(exit_)
    return MainMenu

def bot_desc(bott):
    info = bott['info']
    last_name = ""
    if info['last_name']:lastname = info['last_name']
    
    return f"""
<code>Bot Name</code> : <b>{info['first_name']} {last_name}</b>
<code>Bot Username</code> : @{info['username']}
<code>Status</code> : Running
"""