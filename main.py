import os
import json
import itchat
from jinja2 import Environment, FileSystemLoader

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

@itchat.msg_register(itchat.content.NOTE, isGroupChat=True)
def fetch_system_notification_name_change(msg):

    def get_stored_member_list():
        with open('output/users.json', 'r', encoding='utf-8') as f:
            users = f.read()
            users = set(json.loads(users))
        return users

    # print(msg['Text'], str(msg['User']['MemberList'][0]['NickName'])) # NickName 就是微信名，DisplayName 就是群昵称
    if str(msg['Text']).find("群名") != -1:
        msg_memberlist = msg['User']['MemberList']
        current_member_list = set([str(item['NickName']) for item in msg_memberlist] + [str(item['DisplayName']) for item in msg_memberlist])
        
        stored_member_list = get_stored_member_list()
        #TODO: 那我要是第一次用，还没这个文件呢
        
        if users_in_chatroom(current_member_list, stored_member_list) > (len(current_member_list) // 3):  # 允许 2/3 的用户改名（这么说其实并不严谨，毕竟有俩名）
            save_users(current_member_list)
            save_chatroom_name(str(msg['Text'])[7:-1])
            print(str(msg['Text'])[7:-1])

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
    pass
    
def generate_timeline_webpage():
    root = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(root, 'static', 'template')
    env = Environment( loader = FileSystemLoader(templates_dir) )
    template = env.get_template('index.html')
    filename = os.path.join(root, 'static', 'html', 'index.html')
    with open(filename, 'w', encoding="utf-8") as f:
        f.write(template.render(
            title = "Hello Jinja2",
            items    = [{
                "date": "2020-01-21",
                "name": "[TEST]测试名1",
            }, {
                "date": "2020-01-20",
                "name": "[TEST]测试名2",
            }],
        ))

if __name__ == "__main__":
    if not os.path.exists('output'):
        os.makedirs('output')
    generate_timeline_webpage()
    itchat.auto_login(hotReload=True)   # enableCmdQR=2
    itchat.run()