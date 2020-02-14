import os
import json
from git import Repo

root = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(root, '../../')
config_file = os.path.join(root, 'config.json')
repo_dir = os.path.join(root, 'output')

def get_repo_url():
    """
        传入 配置文件路径
        返回 远端仓库地址
    """
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
        config = json.loads(content)
        remote = str(config["repo"])
    return remote

remote = get_repo_url()

def clone_from_remote():
    repo = Repo.clone_from(url=remote, to_path=repo_dir, branch='data')
    return repo

if __name__ == "__main__":
    repo = get_repo_url()
    msg = clone_from_remote()