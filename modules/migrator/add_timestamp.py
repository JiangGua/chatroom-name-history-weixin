import os
import json
import time

def add_timestamp():
    root = os.path.dirname(os.path.abspath(__file__))
    root = os.path.join(root, '../../')
    name_history_path = os.path.join(root, 'output', 'name_history.json')
    with open(name_history_path, 'r', encoding='utf-8') as f:
        content = f.read()
        name_history = json.loads(content)

    for item in name_history:
        date = item['date']
        timeArray = time.strptime(date, "%Y-%m-%d %H:%M:%S")
        timestamp = time.mktime(timeArray)
        item['timestamp'] = timestamp

    print(name_history)

    with open(name_history_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(name_history))

if __name__ == "__main__":
    add_timestamp()