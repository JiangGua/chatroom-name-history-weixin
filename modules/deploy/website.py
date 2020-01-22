import os
import json
import shutil
from git import Repo

def deploy_website():
    root = os.path.dirname(os.path.abspath(__file__))
    root = os.path.join(root, '../../')
    config_file = os.path.join(root, 'config.json')
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
        config = json.loads(content)
        remote = str(config["repo"])

    # 复制 CSS & JS
    repo_dir = os.path.realpath(os.path.join(root, 'static', 'html', 'src'))
    template_dir = os.path.realpath(os.path.join(root, 'static', 'template', 'src'))
    shutil.copytree(template_dir, repo_dir)

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

if __name__ == "__main__":
    deploy_website()