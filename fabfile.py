from fabric.api import local


def pep8():
    """
    Checks PEP8 code style.

    e.g. fab pep8
    """
    exclude = ['migrations', 'example_local_settings.py', 'local_settings.py']

    local('flake8 --exclude={} .'.format(','.join(exclude)))


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
    local('open htmlcov/index.html')


def runserver():
    """
    Runs server with `local_settings`.

    e.g. fab runserver
    """
    local('./manage.py runserver --settings=rush.local_settings')


def pip(reinstall='N'):
    """
    Updates pip packages according to `requirements.pip` config file.

    e.g. fab pip
    With reinstall: fab pip:Y
    """
    extra = '-I' if reinstall.upper() == 'Y' else ''
    local('pip install {} -r requirements.pip'.format(extra))
