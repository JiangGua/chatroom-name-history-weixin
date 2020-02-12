import os
import json
import shutil
from git import Repo

root = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(root, '../../')

def deploy_website():
    config_file = os.path.join(root, 'config.json')
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
        config = json.loads(content)
        remote = str(config["repo"])

    # 复制 CSS & JS
    try:
        repo_dir = os.path.realpath(os.path.join(root, 'static', 'html', 'src'))
        template_dir = os.path.realpath(os.path.join(root, 'static', 'template', 'src'))
        shutil.copytree(template_dir, repo_dir)
    except:
        pass
    
    repo_dir = os.path.join(root, 'static', 'html')
    try:
        repo = Repo.init(repo_dir)
        remote = repo.create_remote(name='remote', url=remote)
    except:
        repo = Repo(repo_dir)
        remote = repo.remotes.remote

    repo.git.add(all=True)
    try:
        repo.git.commit(m='Update')
    except:
        print("<Deployer> Git Repo: Failed to commit")
    remote.push(refspec='master:master', force=True)

if __name__ == "__main__":
    deploy_website()