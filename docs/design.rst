Design documentation for YourCI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Global design
=============

Given a github username and password or access token along with a list of
repositories in the form of ``owner/repo``, YourCI should be able to:

- queue one job per repo ``handle_repo()``,
- which will update the local repo mirror and iterate over open pull requests,
  queuing one job per pull request ``handle_pull()``,
- which will import a script ``.yci.py`` from the repo and call the
  ``test_generator(build_id, pull_request)`` and queue one job ``handle_test``
  per test configuration it yields,
- that last job is supposed to run the test and update github configuration.
- test output should be written in real time in a file that is served by your
  http server of choice (which should be nginx, oh no i'm trolling again).

Main script
===========

So that script should be run by cron with lockrun. It relies on python-rq which
relies on redis for message queuing. You may run as many workers as you want.

Start the script with the ``GITHUB_REPOSITORIES`` environment variable, a
space-separated list of repositories in the form of ``user/project``.

Example::

    GITHUB_REPOSITORIES="jpic/test_project your/project" yourci

It doesn't matter where you run this script from, since it's just fills the
queue with ``handle_repository(owner, repo)`` calls that the workers will
handle.

Workers
=======

Run a worker in the directory you want to fill up with test data with the
``rqworker`` command provided by ``python-rq`` (installed as a dependency) with
the same environment variables:

- ``GITHUB_USERNAME``, self-descriptive,
- ``GITHUB_PASSWORD``, useful if you don't have an access token,
- ``GITHUB_ACCESS_TOKEN``, useful if you don't want to use a password,
- ``HTTP_ROOT``, the root url that your http server serves the test directory
  with,

With ``jpic/test_project``, it'll create such a directory structure which
should be served by an HTTP server::

    jpic/                                   # owner
        test_project/                       # repo
            source/                         # git clone --mirror
            pulls/                          # pull request container
                123/                        # pull request id
                    1/                      # build number
                        source/             # source code for PR
                        py34-dj18/          # artifacts for build name
                            out.txt         # output for build name py34-dj18
            123-1-py34-dj18-out.txt         # symlink to output for that build

.. danger:: The index page will take too long to load if there are too many
            symlinks. Use the find command to remove old files in a cron.

Scaling
=======

Scaling is insane: just run as many rqworkers as you want on any box you want
it just needs access to github and the redis server.

Test configuration
==================

This example causes `4 tests
<https://github.com/jpic/test_project/pull/1>`_::

    from yci.retry import IncrementalRetry
    from yci.run import Bash

    def test_generator(build_id, pull):
        ENV_VAR_1 = ['foo', 'bar']
        ENV_VAR_2 = ['x', 'y']

        for x in ENV_VAR_1:
            for y in ENV_VAR_2:
                # there i can skip or implement basic logic
                # I could even iterate over a set of files

                yield IncrementalRetry(retries=3, retry_increment=600,
                    Bash('./test.sh', env={'ENV_VAR_1': x, 'ENV_VAR_2': y}))

HTTP interface
==============

If you think this doesn't suck then go ahead and make a frontend. I'll just
right-click the "Details" for a build on github and ``curl | vim -`` it.
