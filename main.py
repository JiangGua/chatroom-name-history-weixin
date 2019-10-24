import itchat

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
    #print(msg['Text'], str(msg['User']['MemberList'][0]['NickName'])) # NickName 就是微信名，DisplayName 就是群昵称
    if user_in_group(msg['User']['MemberList'], ('酱瓜')):
        print('Yes')

def user_in_group(msg_memberlist, other_users):
    """
        调用方法: user_in_group(msg['User']['MemberList'], stored_usernames_list)
        返回布尔值
    """
    for item in msg_memberlist:
        if str(item['NickName']) in other_users:
            return True
        if str(item['DisplayName']) in other_users:
            return True
        return False

if __name__ == "__main__":
    itchat.auto_login(hotReload=True)   # enableCmdQR=2
    itchat.run()
    room_name = anchor_in_chatroom_name('[NSFW]')
    with open('a.txt', 'w', encoding='utf-8') as file_obj:
        file_obj.write(room_name)