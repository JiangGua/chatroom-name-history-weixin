import os
import json
from git import Repo

def deploy_json():
    root = os.path.dirname(os.path.abspath(__file__))
    root = os.path.join(root, '../../')
    config_file = os.path.join(root, 'config.json')
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
        config = json.loads(content)
        if (config["deploy_json"] != "True"):
            return -1
        remote = str(config["repo"])

    repo_dir = os.path.join(root, 'output')
    try:
        repo = Repo.init(repo_dir)
        remote = repo.create_remote(name='remote', url=remote)
    except:
        repo = Repo(repo_dir)
        remote = repo.remotes.remote

    repo.git.add('name_history.json')
    repo.git.commit(m='Update')
    remote.push(refspec='master:data', force=True)

if __name__ == "__main__":
    deploy_json()