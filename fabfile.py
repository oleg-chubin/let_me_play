from fabric.api import run, cd, prefix 

def deploy_everything():
    with cd('/home/httpd/let_me_play/'):
        run('git stash')
        run('git pull')
        run('git stash apply')
        with prefix('source venv/bin/activate'):
            run('python manage.py migrate')
            run('python manage.py collectstatic')
            run('python manage.py compilemessages')
        run('supervisorctl restart all')
