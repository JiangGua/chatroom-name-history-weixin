import os
import sys
import json
from jinja2 import Environment, FileSystemLoader

#TODO: 不太好看的相对导入，需要修改
root = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(root, '../../')
sys.path.append(root)
from modules.data_operator.chatroom_name import get_stored_history

def generate_timeline_webpage():
    templates_dir = os.path.join(root, 'static', 'template')
    env = Environment(loader = FileSystemLoader(templates_dir))
    template = env.get_template('index.html')
    html_dir = os.path.join(root, 'static', 'html')
    filename = os.path.join(html_dir, 'index.html')
    config = os.path.join(root, 'config.json')
    with open(config, 'r',encoding='utf-8') as f:
        config = f.read()
        config = json.loads(config)
        title = str(config["title"])
    history = get_stored_history()

    if not os.path.exists(html_dir):
        os.makedirs(html_dir)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(template.render(
            title = title,
            items = history,
        ))

if __name__ == "__main__":
    generate_timeline_webpage()