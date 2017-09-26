from fabric.api import run, cd, prefix

def deploy_everything():
    with cd('/home/httpd/let_me_play/'):
        run('git stash')
        run('git pull')
        run('git stash apply')
        run('npm install')
        with prefix('source venv/bin/activate'):
            run('pip install -r requirements.txt')
            run('python manage.py migrate')
            run('python manage.py collectstatic')
            run('python manage.py compilemessages')
        run('supervisorctl restart all')
