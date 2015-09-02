Design document for the first feature freeze
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This document details technical specifications for this package. Requirements
are documented in a separate document.

Command line interface
======================

Commands provided by this package will:

- rely on environment variables for configuration,
- update commit statuses on github so that every job has an expected state and
  URL,
- store logs for your jobs in pending statuses in the current working directory
  and serve them via http,
- probably pickle in a file in /tmp for some caching.

Environment variables
---------------------

GITHUB_USERNAME
    Github username of the bot.

GITHUB_TOKEN
    Token for your bot's user.

GITHUB_CONTEXTS
    Configuration string, a space-separated list of ``owner/repo:context0,contextN``.

RETRY_PATTERNS
    Path to a file containing a newline-separated list of patterns to try on
    failed build logs to determine if it should be rebuilt by the retry
    command.

Commands
--------

Deprecate
`````````

This command iterates over non-success statuses of the last commit of each pull
request. If a status has a context that's not available anymore then it'll
update it to have the "success" state.

Good to clean up after jenkins.

Queue
`````

Iterate over the last commit of each pull request and mark contexts as
"pending" in github.

Build
`````

Iterate over the last commit of each pull request and build the first "pending"
context that has no running pid.

Requeue
```````

Given a file containing a pattern per line (ie. ``Network error``), iterate
over failure/error statuses of the last commit of each pull request and set
their state to "pending" if their logs contain a string in the pattern, unless
"yourci: norebuild" is found in any comment of the pull request before that
commit.

Http
````

Minimalist server to serve build logs, use nginx instead in production.

Clean
`````

Clean symlinks in the file system.

File system
===========

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
