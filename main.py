import itchat

if __name__ == "__main__":
    itchat.auto_login(hotReload=True)

    chat_rooms = str(itchat.get_chatrooms())
    if len(chat_rooms) > 0:
        with open('chatroom.json', 'w', encoding='utf-8') as file_obj:
            file_obj.write(chat_rooms)

    end = chat_rooms.find('[NSFW]') + 6
    print(end)
    start = chat_rooms.rfind('NickName', 0, end) + 12
    print(start)

    room_name = chat_rooms[start:end]
    with open('a.txt', 'w', encoding='utf-8') as file_obj:
        file_obj.write(room_name)