import os
import json
import time

root = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(root, '../../')
json_path = os.path.join(root, 'output', 'name_history.json')

def get_stored_history():
    with open(json_path, 'r', encoding='utf-8') as f:
        history = f.read()
        history = json.loads(history)
    return history

def save_history(history):
        with open(json_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(list(history)))

def save_chatroom_name(timestamp, name):
    try:
        history = list(get_stored_history())
    except IOError:
        history = []
    date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))

    history.insert(0, {
        "date": date,
        "name": name,
        "timestamp": timestamp,
    })
    save_history(history)