
import os

from redis import Redis
from rq import Queue

from jobs import handle_repository

q = Queue(connection=Redis())

for repository in os.environ.get('GITHUB_REPOSITORIES').split(' '):
    owner, repo = repository.split('/')
    q.enqueue(handle_repository, owner, repo)
