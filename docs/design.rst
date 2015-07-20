Design documentation for YourCI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Main script
===========

Given a github username and password or access token along with a list of
repositories in the form of ``owner/repo``, YourCI script should be able to:

- queue one job per repo ``handle_repo()``,
- which will update the local repo mirror and iterate over open pull requests,
  queuing one job per pull request ``handle_pull()``,
- which will import a script ``.yci.py`` from the repo and call the
  ``test_generator(build_id, pull_request)`` and queue one job ``handle_test``
  per test configuration it yields,
- that last job is supposed to run the test and update github configuration.
- test output should be written in real time in a file that is served by your
  http server of choice (which should be nginx, oh no i'm trolling again).

So that script should be run by cron with lockrun. It relies on python-rq which
relies on redis for message queuing. You may run as many workers as you want.

Start the script with any of the following environment variable::

- ``GITHUB_USERNAME``, self-descriptive,
- ``GITHUB_PASSWORD``, useful if you don't have an access token,
- ``GITHUB_ACCESS_TOKEN``, useful if you don't want to use a password,
- ``GITHUB_REPOSITORIES``, a space-separated list of repositories in the form
  of ``user/project``.
- ``HTTP_ROOT``, the root url that your http server serves the test directory
  with,

.. note:: If you have multiple users for different git repositories then just
          run the script several times with the different variables.

Example::

    GITHUB_USERNAME=foo GITHUB_ACCESS_TOKEN=bar \
        GITHUB_REPOSITORIES=jpic/test_project yourci

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
