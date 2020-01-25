import os
import json
import time
import getopt
import sys

import itchat
from jinja2 import Environment, FileSystemLoader
from git import Repo

from modules.deploy.history_json import deploy_json
from modules.deploy.website import deploy_website

def get_stored_history():
    with open('output/name_history.json', 'r', encoding='utf-8') as f:
        history = f.read()
        history = json.loads(history)
    return history

def generate_timeline_webpage():
    root = os.path.dirname(os.path.abspath(__file__))
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

@itchat.msg_register(itchat.content.NOTE, isGroupChat=True)
def fetch_system_notification_name_change(msg):
    def get_stored_member_list():
        with open('output/users.json', 'r', encoding='utf-8') as f:
            users = f.read()
            users = set(json.loads(users))
        return users

    def save_and_gen(current_member_list, msg):
        save_users(current_member_list)
        date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        save_chatroom_name(date, str(msg['Text'])[7:-1])
        print(str(msg['Text'])[7:-1])
        generate_timeline_webpage()
        deploy_website()
        deploy_json()
        print('Saved')

    # print(msg['Text'], str(msg['User']['MemberList'][0]['NickName'])) # NickName 就是微信名，DisplayName 就是群昵称
    if str(msg['Text']).find("群名") != -1:
        msg_memberlist = msg['User']['MemberList']
        current_member_list = set([str(item['NickName']) for item in msg_memberlist] + [str(item['DisplayName']) for item in msg_memberlist])
        
        try:
            stored_member_list = get_stored_member_list()
        except IOError:
            save_and_gen(current_member_list, msg)
            return 0

        if users_in_chatroom(current_member_list, stored_member_list) > (len(current_member_list) // 3):  # 允许 2/3 的用户改名（这么说其实并不严谨，毕竟有俩名）
            save_and_gen(current_member_list, msg)

def users_in_chatroom(current_member_list, stored_member_list):
    """
        调用方法: user_in_chatroom(current_member_list, stored_member_list)
        返回交集的元素个数
    """
    current_member_list = set(current_member_list)
    stored_member_list = set(stored_member_list)
    return len(current_member_list & stored_member_list)

def save_users(current_member_list):
    with open('output/users.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(list(current_member_list)))

def save_chatroom_name(date, name):
    def save_history(history):
         with open('output/name_history.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(list(history)))
    try:
        history = list(get_stored_history())
    except IOError:
        history = []

    history.insert(0, {
        "date": date,
        "name": name,
    })
    save_history(history)

if __name__ == "__main__":
    if not os.path.exists('output'):
        os.makedirs('output')

    try:
        opts, args = getopt.getopt(sys.argv[1:], '-d:-n:-u', ['date=', 'name=', 'upload'])
        for opt_name, opt_value in opts:
            if opt_name in ('-d', '--date'):
                date = opt_value
            if opt_name in ('-n', '--name'):
                name = opt_value
            if opt_name in ('-u', '--upload'):
                generate_timeline_webpage()
                deploy_website()
                deploy_json()
                print('Saved')
            
        if (date in locals()) and (name in locals()):
            save_chatroom_name(date, name)
        exit()
    except getopt.GetoptError:
        pass
    
    itchat.auto_login(hotReload=True, enableCmdQR=2)   # enableCmdQR=2
    itchat.run()