import os
import json
import time
import getopt
import sys

import itchat

from modules.deploy.history_json import deploy_json
from modules.deploy.website import deploy_website
from modules.data_operator.chatroom_name import get_stored_history, save_chatroom_name
from modules.data_operator.users import save_users, get_stored_member_list, users_in_chatroom
from modules.generator.html_timeline import generate_timeline_webpage

# 处理命令行参数 --upload
def gen_and_upload():
    generate_timeline_webpage()
    deploy_website()
    print("3")
    deploy_json()
    print('Uploaded')

@itchat.msg_register(itchat.content.NOTE, isGroupChat=True)
def fetch_system_notification_name_change(msg):
    def save_and_gen(current_member_list, msg):
        save_users(current_member_list)
        save_chatroom_name(time.time(), str(msg['Text'])[7:-1])
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

if __name__ == "__main__":
    if not os.path.exists('output'):
        os.makedirs('output')

    # 命令行参数处理
    try:
        opts, args = getopt.getopt(sys.argv[1:], '-d:-n:-u', ['date=', 'name=', 'upload', 'pull'])
        for opt_name, opt_value in opts:
            if opt_name in ('-d', '--date'):
                date = opt_value
            if opt_name in ('-n', '--name'):
                name = opt_value
            if opt_name in ('-u', '--upload'):
                gen_and_upload()
                os._exit(0)

        # 如果成功接收日期和群名 则记录之        
        if ('date' in locals()) and ('name' in locals()):
            print(date, name)
            timeArray = time.strptime(date, "%Y-%m-%d %H:%M:%S")
            timestamp = time.mktime(timeArray)
            save_chatroom_name(timestamp, name)
            os._exit(0)
    except:
        pass
    
    itchat.auto_login(hotReload=True, enableCmdQR=2)   # enableCmdQR=2
    itchat.run()