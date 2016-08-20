import os
import urlparse
import webbrowser

from fabric.api import local, env, run, cd

env.hosts = ['rush']
env.use_ssh_config = True


def pep8():
    """
    Checks PEP8 code style.

    e.g. fab pep8
    """
    exclude = ['migrations', 'example_local_settings.py', 'local_settings.py']

    local('flake8 --exclude={} --ignore=F403 .'.format(','.join(exclude)))


def test(test_path=''):
    """
    Runs unit tests using `local_settings`.

    e.g.
    [all] fab test
    [one] fab test:"contest.tests.test_views.AccountsViewTestCase.test_post"

    """
    local(
        './manage.py test {} --settings=rush.local_settings'.format(test_path)
    )


def cov():
    """
    Measures unittests coverage and prints report.

    e.g. fab cov
    """
    local(
        'coverage run --source="." manage.py test '
        '--settings=rush.local_settings'
    )
    local('coverage html')
    path = urlparse.urljoin('file:', os.path.abspath('htmlcov/index.html'))
    webbrowser.open(path, new=2)


def runserver():
    """
    Runs server with `local_settings`.

    e.g. fab runserver
    """
    local('./manage.py runserver --settings=rush.local_settings')


def rush(command=None):
    """
    Runs any Django command using `local_settings`.

    e.g. fab rush:runserver
    """
    if command:
        local('./manage.py {} --settings=rush.local_settings'.format(command))
    else:
        runserver()


def pip(reinstall='N'):
    """
    Updates pip packages according to `requirements.pip` config file.

    e.g. fab pip
    With reinstall: fab pip:Y
    """
    extra = '-I' if reinstall.upper() == 'Y' else ''
    local('pip install {} -r requirements.pip'.format(extra))


def deploy(branch='develop'):
    """
    Remote deployment command
    """
    with cd('/home/app/rush/'):
        try:
            run('pkill gunicorn')
        except SystemExit:
            pass

        run('git pull origin {}'.format(branch))
        run('python manage.py migrate')
        run('pip install -r requirements.pip')
        run('service nginx restart')
        run(
            'gunicorn --bind 127.0.0.1:8001 rush.wsgi:application '
            '--settings=rush.local_settings'
        )
