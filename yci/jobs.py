import os
import imp
import subprocess

from redis import Redis
from rq import Queue
import github

gh = github.GitHub(
    username=os.environ.get('GITHUB_USERNAME', None),
    access_token=os.environ.get('GITHUB_ACCESS_TOKEN', None) or None,
    password=os.environ.get('GITHUB_PASSWORD', None))
workspace = os.environ.get('workspace', '')

q = Queue(connection=Redis())


def system(cmd):
    print cmd
    return subprocess.check_output(cmd, shell=True)

def chdir(path):
    print path
    os.chdir(path)


def handle_repository(owner, repo):
    source_path = os.path.join(workspace, owner, repo, 'source')
    pulls_path = os.path.join(workspace, owner, repo, 'pulls')

    if not os.path.exists(pulls_path):
        os.makedirs(pulls_path)

    if not os.path.exists(source_path):
        system('git clone --mirror git@github.com:%s/%s.git %s' % (
            owner, repo, source_path))

    chdir(source_path)
    system('git fetch --all')

    pulls = gh.repos(owner)(repo).pulls.get()
    for pull in pulls:
        q.enqueue(handle_pull, owner, repo, pull)


def handle_pull(owner, repo, pull):
    source_path = os.path.join(workspace, owner, repo, 'source')
    pulls_path = os.path.join(workspace, owner, repo, 'pulls')

    pull_path = os.path.join(pulls_path, pull['issue_url'].split('/')[-1])
    pull_source_path = os.path.join(pull_path, 'source')

    if not os.path.exists(pull_path):
        os.makedirs(pull_path)

    if not os.path.exists(pull_source_path):
        system('git clone --recursive -b %s %s %s' % (pull.head.ref,
            source_path, pull_source_path))

    chdir(pull_source_path)
    system('git pull -f origin %s' % pull.head.ref)

    config = imp.load_source('config', os.path.join('.yci.py'))

    for test in config.test_generator('xx', pull):
        sha = system('git rev-parse HEAD').strip()
        gh.repos(owner)(repo).statuses(sha).post(
            state='pending', target_url='http://myurl',
            context=str(test), description='Enqueud')
        q.enqueue(handle_test, owner, repo, pull, test)


def handle_test(owner, repo, pull, test):
    gh.repos(owner)(repo).commits().status
    pulls_path = os.path.join(workspace, owner, repo, 'pulls')

    pull_path = os.path.join(pulls_path, pull['issue_url'].split('/')[-1])
    pull_source_path = os.path.join(pull_path, 'source')

    for key, value in test.items():
        os.environ[key] = str(value)

    chdir(pull_source_path)
    system(test['CMD'])
    sha = system('git rev-parse HEAD').strip()

    gh.repos(owner)(repo).statuses(sha).post(
        state='success', target_url='http://myurl',
        context=str(test), description='Done')

    for key in test.keys():
        os.environ.pop(key)
