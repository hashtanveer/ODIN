import pymongo
import telebot
import time
from config import MONGODB_CLIENT
cluster = pymongo.MongoClient(MONGODB_CLIENT)

bot_owners = cluster['Host_bot']['bot_owners']
bots_db = cluster['Host_bot']

class O:
    def check_bot(owner,get_bot=True,id_hash=False):
        post = {"_id": owner }
        result = bot_owners.find_one(post)
        if result:
            print(f"Bot found for user {owner}")
            if id_hash:
                return result['id_hash']
            #print("Bot of provided Owner:",result)
            if get_bot: 
                return bots_db[result['id_hash']].find_one({"_id":1})
            return True
        print(f"no Bot found for user {owner}")
        return False

    def bot_info(id_hash):
        x = bots_db[id_hash].find_one({"_id":1})
        return x

    def add_bot(owner,id_hash,info):
        id_ ,hash_ = id_hash.split(":")
        post = {"_id": 1,
            "owner_id": owner ,
            "info" : info, 
            "power_on": True ,
            "gate_count" : 0,
            "gates":[],
            "anti-spam":{
                "Free":40,
                "Premium":10
                },
            "allow_register": True
            }
        bots_db[id_hash].insert_one(post)
        bot_owners.insert_one({"_id":owner,"id_hash":id_hash})
    
    #Change Power: ON/OFF
    def change_power(id_hash,state):
        bots_db[id_hash].update_one({"_id": 1},{"$set" : {"power_on": state }},False,True)
        #change_gate_field(id_hash,gate_name,field="power_on",val=statre)
    
    def change_register(id_hash, state):
        bots_db[id_hash].update_one({"_id": 1},{"$set" : {"allow_register": state }},False,True)
    
    def delete_bot(owner,id_hash=None):
        if not id_hash:
            id_hash = bot_owners.find_one({"_id":owner})['id_hash']
        bots_db[id_hash].drop()
        #Bot owner DB
        bot_owners.delete_one({"_id":owner})
        print('User Deleted! successfully')

class Gates:


    def add_gate(id_hash,url,name,desc=''):
        gate_dict = {
            "name" : name,
            "url" : url,
            "power_on": True,
            "type": "Free",
            "regex" : True,
            "private-allowed" : False,
            "mass" : False,
            "description" : desc
        }
        slice_len = 50
        bots_db[id_hash].update_one({"_id": 1}, {"$push": { "gates": { "$each": [gate_dict], "$slice": slice_len }},"$inc": { "gate_count": 1 }})
    
    #Remove Gate
    def remove_gate(id_hash,name):
        post = {"name" : name}
        bots_db[id_hash].update_one({"_id": 1},{"$pull" : {"gates" : { "name" : name}},"$inc": { "gate_count": -1 }},False,False)


    #Change Gate : free/premium
    def change_antispam(id_hash,gate,val):
        if val == 0:
            return
        if val > 0:
             bots_db[id_hash].update_one({"_id": 1},{"$inc" : {"anti-spam."+gate: val }})
             return
        bots_db[id_hash].update_one({"_id": 1,f"anti-spam."+gate : {"$gte": 9}},{"$inc" : {"anti-spam."+gate: val }})
    
    def change_type(id_hash,gate_name,type_):
        change_gate_field(id_hash,gate_name,field="type",val=type_)

    def change_regex(id_hash,gate_name,state):
        change_gate_field(id_hash,gate_name,field="regex",val=state)
    
    def change_private(id_hash,gate_name,state):
        change_gate_field(id_hash,gate_name,field="private-allowed",val=state)
    
    def change_mass(id_hash,gate_name,state):
        change_gate_field(id_hash,gate_name,field="mass",val=state)       

    def change_description(id_hash,gate_name,desc):
        change_gate_field(id_hash,gate_name,field="description",val=desc)

    def change_name(id_hash,gate_name,new_name):
        change_gate_field(id_hash,gate_name,field="name",val=new_name)
    
    
    def change_power(id_hash,gate_name,state):
        change_gate_field(id_hash,gate_name,field="power_on",val=state)
    
    
def change_gate_field(id_hash,gate_name,field,val):
    bots_db[id_hash].update_one({"_id": 1, "gates.name" : gate_name},{"$set" : {"gates.$."+field: val }},False,True)
    
#O.add_bot(848484848,"5469253781:AAHiGNDG0hhAmkE7B0HRClMwuHwiQOeremo",{"name":"Bot name","other":"info"})
#x = time.time()
#O.check_bot(848484848)
#print(time.time() - x)
#O.delete_bot(848484848)
#O.change_power("5469253781:AAHiGNDG0hhAmkE7B0HRClMwuHwiQOeremo",False)

#Gates.add_gate("5071344820:AAH3RyoGQdyJ1nwcxsdH11bbWVLr2F7WgOc","sk.com","sk")
#O.change_power("5469253781:AAHiGNDG0hhAmkE7B0HRClMwuHwiQOeremo","sk",True)
#Gates.change_antispam("5469253781:AAHiGNDG0hhAmkE7B0HRClMwuHwiQOeremo","free",-10)

class User:
    def check(id_hash, user_id):
        post = {"_id": user_id }
        result = bots_db[id_hash].find_one(post)
        if result:
            print(f"User found {user_id}")
            return result
    
    def add(id_hash, user_id,is_group=False):
        if User.check(id_hash, user_id):
            print("User already Exists")
            return
        user_dict = {
            "_id" : user_id,
            "is_group": is_group,
            "type": "Free",
            "private-allowed" : False,
            "mass" : False,
            "register_time": int(time.time()),
            "last_used": int(time.time())
        }
        bots_db[id_hash].insert_one(user_dict)
        
    def delete(id_hash, user_id):
        print("user",user_id, "deleted")
        bots_db[id_hash].delete_one({"_id":user_id})
    
    def change_type(id_hash, user_id, val):
        bots_db[id_hash].update_one({"_id": user_id},{"$set" : {"type": val }},False,True)
        print("User",user_id,"Type changed to",val)
    
    def change_private(id_hash, user_id, val):
        bots_db[id_hash].update_one({"_id": user_id},{"$set" : {"private-allowed": val }},False,True)
        print("User",user_id,"private-allowed changed to",val)
    
    def change_mass(id_hash, user_id, val):
        bots_db[id_hash].update_one({"_id": user_id},{"$set" : {"mass": val }},False,True)
        print("User",user_id,"mass changed to",val)
    
    def update_lastused(id_hash, user_id, new_time):
        bots_db[id_hash].update_one({"_id": user_id},{"$set" : {"last_used": new_time }},False,True)

def find_gate(bott, gate_name):
    for gate in bott['gates']:
        if gate['name'] == gate_name:
            return gate

def Gates_details(bott, gate_type):
    Gates = bott["gates"]
    
    filter_gates = []
    if gate_type == "Mass":
        parameter, val = "mass" , True
    else: 
        parameter, val = "type", gate_type
    for gate in Gates:
        if gate[parameter] == val:
            filter_gates.append(gate)
    
    if not filter_gates : return None
    Text = f"    {gate_type} Gates\n"
    for gate in filter_gates:
        Text +=f"""━━━━━━━━━━━━━━━━━━━━
ϟ Format: /{gate['name']} cc|mm|yy|cvv
ϟ Status: {gate_status(gate["power_on"])}
ϟ Comment: {gate['description']}
"""
    return Text
    
def gate_status(val):
    if val: return "ON ✅"
    return "OFF ✖️"
gate_type = "Mass"  
