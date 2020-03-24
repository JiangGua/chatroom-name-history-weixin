import os
import json

root = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(root, '../../')
json_path = os.path.join(root, 'output', 'users.json')

def get_stored_member_list():
    with open(json_path, 'r', encoding='utf-8') as f:
        users = f.read()
        users = set(json.loads(users))
    return users

def save_users(current_member_list):
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(list(current_member_list), ensure_ascii=False))

def users_in_chatroom(current_member_list, stored_member_list):
    """
        调用方法: user_in_chatroom(current_member_list, stored_member_list)
        返回交集的元素个数
    """
    current_member_list = set(current_member_list)
    stored_member_list = set(stored_member_list)
    return len(current_member_list & stored_member_list)