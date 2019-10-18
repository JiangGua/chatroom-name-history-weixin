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

if __name__ == "__main__":
    itchat.auto_login(hotReload=True)

    room_name = anchor_in_chatroom_name('[NSFW]')
    with open('a.txt', 'w', encoding='utf-8') as file_obj:
        file_obj.write(room_name)