import json
import requests
class ButtonRow:
    def __init__(self, buttons):
        self.buttons = buttons

    def to_dict(self):
        return [button.to_dict() for button in self.buttons]

class Button:
    def __init__(self, text, callback_data):
        self.text = text
        self.callback_data = callback_data

    def to_dict(self):
        return {"text": self.text, "callback_data": self.callback_data}
		
def send_message(id_hash, chat_id, text, inline_keyboard=None, reply_to_message_id=None):
    url = f"https://api.telegram.org/bot{id_hash}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }
    if inline_keyboard is not None:
        data["reply_markup"] = json.dumps({"inline_keyboard": [row.to_dict() for row in inline_keyboard]})
    if reply_to_message_id is not None:
        data["reply_to_message_id"] = reply_to_message_id
    response = requests.post(url, json=data)
    if response.status_code != 200:
        print("Error sending message: {}".format(response.text))
    return response.json()
    
def edit_message(id_hash, chat_id, message_id, text, inline_keyboard=None):
    url = f"https://api.telegram.org/bot{id_hash}/editMessageText"
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text
    }
    if inline_keyboard is not None:
        data["reply_markup"] = json.dumps({"inline_keyboard": [row.to_dict() for row in inline_keyboard]})
    response = requests.post(url, json=data)
    if response.status_code != 200:
        print("Error editing message: {}".format(response.text))
    return response.json()
    