#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import re
import time
import json
import random
import platform
from shutil import copy2 as copyfile
from shutil import copytree as copytree

import yaml
import itchat
from git import Repo
from jinja2 import Environment, FileSystemLoader

def initialize():
    # 创建输出文件夹
    if not os.path.exists('output'):
        os.makedirs('output')
    # 创建全局输出文件夹
    if not os.path.exists('output/global'):
        os.makedirs('output/global')
    # 创建空白的data.json文件
    if not os.path.exists('output/global/data.json'):
        with open('output/global/data.json', 'w', encoding='utf-8') as f:
            f.write('[]')
    # 将全局配置文件拷贝入通用输出文件夹
    if not os.path.exists('output/global/config.yml'):
        copyfile('config.yml.example', 'output/global/config.yml')
    
class ChatroomDataOperator():
    def __init__(self, chatroom_id):
        self.id = chatroom_id
        self.path = 'output/global/{}.json'.format(chatroom_id)

    def generate_chatroom_item(self):
        obj = {
            'roomName': [],
            'deploy': {
                'enable': False,
                'repo': '',
                'branch': 'gh-pages',
                'siteTitle': '站点标题',
                'theme': 'default',
            },
        }
        return obj

    def dump(self, obj):
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False)

    def fullData(self):
        with open(self.path, 'r', encoding='utf-8') as f:
            obj = json.load(f)
        return obj
    def deployConfig(self):
        return self.fullData()['deploy']
    def enable(self):
        return self.deployConfig()['enable']
    def theme(self):
        return self.deployConfig()['theme']
    def siteTitle(self):
        return self.deployConfig()['siteTitle']
    def repo(self):
        return self.deployConfig()['repo']
    def branch(self):
        return self.deployConfig()['branch']
    def roomName(self):
        return self.fullData()['roomName']

    def append_name(self, name_item: dict):
        obj = self.fullData()
        obj['roomName'].append(name_item)
        self.dump(obj)

class DataJsonOperator():
    def __init__(self, path = 'output/global/data.json'):
        self.path = path

    def _ranstr(self, num):
        """
            生成长度为 num 的随机字符串
        """
        seed = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        salt = ''
        for i in range(num):
            salt += random.choice(seed)
        return salt

    def chatrooms(self):
        path = self.path
        with open(path, 'r', encoding='utf-8') as f:
            chatrooms = json.load(f)
        return chatrooms

    def dump(self, chatrooms):
        path = self.path
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(chatrooms, f, ensure_ascii=False)

    def _generate_chatroom_item(self):
        """
            返回一个字典
        """
        chatrooms = self.chatrooms()
        # 生成唯一ID
        while (uuid:=self._ranstr(8)) in [i['id'] for i in chatrooms]:
            pass
        obj = {
            'id': uuid,
            'members': [],
        }
        return obj

    def _recompose_memberlist(self, memberlist):
        """
            读入 memberlist
            输出一个包含若干 dict 的 list
        """
        result = []
        for member in memberlist:
            obj = {
                'wxName': member['NickName'],
                'nickInGroup': member['DisplayName'] or member['NickName'],
            }
            result.append(obj)
        return result

    def find_chatroom_by_member(self, chatrooms, memberlist):
        """
            根据成员列表找到群id.
            如果找不到, 应该自动在data.json创建一个新的群item, 并返回其id.
            用新获取到的成员列表覆盖原来记录的.
            返回值：id
        """
        current_members = self._recompose_memberlist(memberlist)
        current_member_set = set([str(item['wxName']) for item in current_members])

        flag = False    # 匹配成功则设为 True

        #TODO: 怎么匹配饭团特色「黑学讨论群」?
        for chatroom in chatrooms:
            recorded_member_set = set([item['wxName'] for item in chatroom['members']])  # 记录中的成员名单
            intersection = recorded_member_set & current_member_set     # 交集
            if len(intersection) > (max(len(recorded_member_set)//2, len(recorded_member_set)-3)):       # 允许1/2或3个(取较大者)人改名
                flag = True
                chatroom['members'] = current_members
                self.dump(chatrooms)
                return chatroom['id']
    
        # 没有找到，则创建一个群item
        if not flag:
            chatroom = self._generate_chatroom_item()
            chatroom['members'] = current_members
            chatrooms.append(chatroom)
            self.dump(chatrooms)
            i = ChatroomDataOperator(chatroom['id'])
            i.dump(i.generate_chatroom_item())
            return chatroom['id']

class WebsiteGenerator():
    def __init__(self, chatroom_id):
        self.id = chatroom_id
        self.path = 'output/{}/'.format(chatroom_id)
        o = ChatroomDataOperator(chatroom_id)
        self.config = o.deployConfig()
        self.title = o.siteTitle()
        self.roomName = o.roomName()
        self.theme_path = 'themes/{}/'.format(o.theme())

    def generate(self):
        path = self.path
        theme_path = self.theme_path
        if not os.path.exists(path):
            # 复制模板的静态文件到仓库文件夹
            copytree(theme_path, path)

        env = Environment(loader = FileSystemLoader(path))
        template = env.get_template('index.html')

        html = template.render(
            title = self.title,
            items = self.roomName,
        )

        with open(path+'index.html', 'w', encoding='utf-8') as f:
            f.write(html)

class DeployerGit():
    def __init__(self, chatroom_id, repo=None, branch="backup"):
        self.id = chatroom_id
        self.path = 'output/{}/'.format(chatroom_id)
        if not repo:
            c = ChatroomDataOperator(chatroom_id)
            self.repo = c.repo()
            self.branch = c.branch()
        else:
            self.repo = repo
            self.branch = branch

    def deploy(self):
        try:
            repo = Repo.init(self.path)
            remote = repo.create_remote(name='kotonoha', url=self.repo)
        except:
            repo = Repo(self.path)
            remote = repo.remotes.kotonoha

        try:
            repo.index.add('*')
            repo.index.commit(message='Update')
        except:
            print("<Deployer> Git Repo: Failed to commit")

        try:
            remote.push(refspec='master:{}'.format(self.branch), force=True)
        except:
            print("<Deployer> Git Repo: Failed to push")
class GlobalConfig():
    def __init__(self):
        self.path = 'output/global/config.yml'
    def allData(self):
        with open(self.path, encoding='utf-8') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        return data
    def deployConfig(self):
        return self.allData()['deploy']
    def theme(self):
        return self.allData()['deploy']['theme']
    def backupConfig(self):
        return self.allData()['backup']
    def backupEnable(self):
        return self.allData()['backup']['enable']
    def backupRepo(self):
        return self.allData()['backup']['repo']
    def backupBranch(self):
        return self.allData()['backup']['branch']
    def backup(self):
        d = DeployerGit("global", self.backupRepo(), self.backupBranch())
        d.deploy()

def msg_handler(msg):
    # 仅处理与修改群名有关的系统消息
    if str(msg['Text']).find("群名") != -1:
        current_memberlist = msg['User']['MemberList']

        o = DataJsonOperator()
        chatrooms = o.chatrooms()
        # 根据成员列表找到群id, 如果找不到, 应该自动在data.json创建一个新的群item, 并返回其id
        chatroom_id = o.find_chatroom_by_member(chatrooms, current_memberlist)
        chatroom = ChatroomDataOperator(chatroom_id)

        name_re = re.compile(r'(?<=修改群名为“)[\s\S]*(?=”)')
        name = re.search(name_re, str(msg['Text'])).group()
        print('Modification Detected: {}'.format(name))
        item = {
            'timestamp': time.time(),
            'date': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
            'name': name,
        }
        chatroom.append_name(item)

        if chatroom.enable():
            # 生成网页
            w = WebsiteGenerator(chatroom_id)
            w.generate()
            # Git 操作
            print('Started: Deploying to remote repo...')
            g = DeployerGit(chatroom_id)
            g.deploy()
            print('Deploy Success: {}'.format(chatroom_id))

            # 全局数据及配置文件备份
            gl = GlobalConfig()
            if gl.backupEnable():
                print('Started: Global Data Backup')
                gl.backup()
                print('Success: Global Data Backup')

@itchat.msg_register(itchat.content.NOTE, isGroupChat=True)
def received_msg(msg):
    msg_handler(msg)

if __name__ == "__main__":
    # 初始化
    initialize()

    # 如果不是 Windows 系统,则把二维码打在命令行界面; 如果是 Windows 系统，则用图片浏览器打开二维码
    if platform.platform().lower().find('windows') == -1:
        itchat.auto_login(hotReload=True, enableCmdQR=2)
    else:
        itchat.auto_login(hotReload=True)
    
    # 运行 itchat
    itchat.run()