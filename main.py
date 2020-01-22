import os
import json
import time
import itchat
from jinja2 import Environment, FileSystemLoader
from git import Repo

def anchor_in_chatroom_name(mark):
    """
        通过群聊名中手动设置的锚点词对群聊进行定位.
        形参 mark 是一个字符串, 即手动设置保持不变的锚点, 
        返回一个字符串, 为提取出的群名称。
    """
    chat_rooms = str(itchat.get_chatrooms())
    end = chat_rooms.find(mark) + len(mark)
    start = chat_rooms.rfind('NickName', 0, end) + 12
    room_name = chat_rooms[start:end]
    return room_name

def get_stored_history():
        with open('output/name_history.json', 'r', encoding='utf-8') as f:
            history = f.read()
            history = json.loads(history)
        return history

def deploy_git():
    with open('config.json', 'r', encoding='utf-8') as f:
        content = f.read()
        config = json.loads(content)
        remote = str(config["repo"])

    root = os.path.dirname(os.path.abspath(__file__))
    repo_dir = os.path.join(root, 'static', 'html')

    try:
        repo = Repo.init(repo_dir)
        remote = repo.create_remote(name='remote', url=remote)
    except:
        repo = Repo(repo_dir)
        remote = repo.remotes.remote

    repo.git.add(all=True)
    repo.git.commit(m='Update')
    remote.push(refspec='master:master')

def generate_timeline_webpage():
    root = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(root, 'static', 'template')
    env = Environment(loader = FileSystemLoader(templates_dir))
    template = env.get_template('index.html')
    filename = os.path.join(root, 'static', 'html', 'index.html')
    config = os.path.join(root, 'config.json')
    with open(config, 'r',encoding='utf-8') as f:
        config = f.read()
        config = json.loads(config)
        title = str(config["title"])
    history = get_stored_history()
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
        save_chatroom_name(str(msg['Text'])[7:-1])
        print(str(msg['Text'])[7:-1])
        generate_timeline_webpage()
        deploy_git()
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

def save_chatroom_name(name):
    def save_history(history):
         with open('output/name_history.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(list(history)))
    try:
        history = list(get_stored_history())
    except IOError:
        history = []

    history.insert(0, {
        "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "name": name,
    })
    save_history(history)


if __name__ == "__main__":
    if not os.path.exists('output'):
        os.makedirs('output')
    itchat.auto_login(hotReload=True)   # enableCmdQR=2
    itchat.run()