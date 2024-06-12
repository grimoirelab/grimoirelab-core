# -*- coding: utf-8 -*-
#
# Copyright (C) GrimoireLab Contributors
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     Santiago Dueñas <sduenas@bitergia.com>
#     Jose Javier Merchante <jjmerchante@bitergia.com>
#     Eva Millán <evamillan@bitergia.com>
#

import datetime
import httpretty
import logging
import os
import pickle
import shutil
import tempfile

import rq
from django.test import TestCase

from grimoirelab.core.scheduler.errors import NotFoundError
from grimoirelab.core.scheduler.jobs import (JobLogHandler,
                                            JobResult,
                                            PercevalJob,
                                            fetch_github_owner_repos,
                                            fetch_gitlab_owner_repos)

from .base import TestBaseRQ

GITHUB_REPOS_URL = "https://api.github.com/users/chaoss_example/repos"
GITLAB_USER_URL = "https://gitlab.com/api/v4/users?username=user_example"
GITLAB_USER_REPOS_URL = "https://gitlab.com/api/v4/users/123456/projects?include_subgroups=True"


def read_file(filename, mode='r'):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename), mode) as f:
        content = f.read()
    return content


class TestJobLogHandler(TestBaseRQ):
    """Unit tests for JobLogHandler class"""

    def test_job_log_handler_init(self):
        """Tests whether the handler has initialized well"""

        job_a = rq.job.Job()
        meta_handler = JobLogHandler(job_a)
        self.assertEqual(meta_handler.job, job_a)
        self.assertListEqual(meta_handler.job.meta['log'], [])

    def test_job_log_handler_emit(self):
        """Tests whether the handler catches the messages from the logger that handles"""

        job_a = rq.job.Job()

        # Create handler
        meta_handler = JobLogHandler(job_a)

        # Get logger of this current context and add set level to INFO in order to save info and upper
        logger = logging.getLogger(__name__)
        logger.addHandler(meta_handler)
        logger.setLevel(logging.INFO)

        # Write in the logger
        logger.error("Error log to the handler")
        logger.warning("Warning log to the handler")
        logger.info("Info log to the handler")

        # Check if the logs are saved in the job meta field
        self.assertEqual(len(job_a.meta['log']), 3)
        self.assertEqual(sorted(list(job_a.meta['log'][0].keys())), ['created', 'level', 'module', 'msg'])
        self.assertRegex(job_a.meta['log'][0]['msg'], 'Error')
        self.assertRegex(job_a.meta['log'][-1]['msg'], 'Info')


class TestJobResult(TestCase):
    """Unit tests for JobResult class"""

    def test_job_result_init(self):
        result = JobResult('1234567890', 'mytask',
                           'mock_backend', 'category')

        self.assertEqual(result.job_id, '1234567890')
        self.assertEqual(result.task_id, 'mytask')
        self.assertEqual(result.backend, 'mock_backend')
        self.assertEqual(result.category, 'category')
        self.assertEqual(result.summary, None)

    def test_to_dict(self):
        """Test whether a JobResult object is converted to a dict"""

        result = JobResult('1234567890', 'mytask',
                           'mock_backend', 'category')

        expected = {
            'job_id': '1234567890',
            'task_id': 'mytask'
        }

        d = result.to_dict()
        self.assertEqual(d, expected)


class TestPercevalJob(TestBaseRQ):
    """Unit tests for PercevalJob class"""

    def setUp(self):
        self.tmp_path = tempfile.mkdtemp(prefix='grimoire_sched_')
        self.dir = os.path.dirname(os.path.realpath(__file__))
        super().setUp()

    def tearDown(self):
        shutil.rmtree(self.tmp_path)
        super().tearDown()

    def test_init(self):
        """Test the initialization of the object"""

        job = PercevalJob('1234567890', 'mytask', 'git',
                          'commit', self.conn, 'items')

        self.assertEqual(job.job_id, '1234567890')
        self.assertEqual(job.task_id, 'mytask')
        self.assertEqual(job.backend, 'git')
        self.assertEqual(job.category, 'commit')
        self.assertEqual(job.conn, self.conn)
        self.assertEqual(job.qitems, 'items')

        result = job.result
        self.assertIsInstance(job.result, JobResult)
        self.assertEqual(result.job_id, '1234567890')
        self.assertEqual(result.task_id, 'mytask')
        self.assertEqual(result.backend, 'git')
        self.assertEqual(job.category, 'commit')
        self.assertEqual(result.summary, None)

    def test_backend_not_found(self):
        """Test if it raises an exception when a backend is not found"""

        with self.assertRaises(NotFoundError) as e:
            _ = PercevalJob('1234567890', 'mytask',
                            'mock_backend', 'acme-category',
                            self.conn, 'items')
            self.assertEqual(e.exception.element, 'mock_backend')

    def test_run(self):
        """Test run method using the Git backend"""

        job = PercevalJob('1234567890', 'mytask',
                          'git', 'commit',
                          self.conn, 'items')
        args = {
            'uri': 'http://example.com/',
            'gitpath': os.path.join(self.dir, 'data/git_log.txt')
        }

        job.run(args)

        result = job.result
        self.assertIsInstance(job.result, JobResult)
        self.assertEqual(result.job_id, '1234567890')
        self.assertEqual(result.task_id, 'mytask')
        self.assertEqual(result.backend, 'git')
        self.assertEqual(result.category, 'commit')
        self.assertEqual(result.summary.last_uuid, '1375b60d3c23ac9b81da92523e4144abc4489d4c')
        self.assertEqual(result.summary.max_updated_on,
                         datetime.datetime(2014, 2, 12, 6, 10, 39,
                                           tzinfo=datetime.timezone.utc))
        self.assertEqual(result.summary.last_updated_on,
                         datetime.datetime(2012, 8, 14, 17, 30, 13,
                                           tzinfo=datetime.timezone.utc))
        self.assertEqual(result.summary.fetched, 9)
        self.assertEqual(result.summary.last_offset, None)

        commits = self.conn.lrange('items', 0, -1)
        commits = [pickle.loads(c) for c in commits]
        commits = [commit['data']['commit'] for commit in commits]

        expected = ['456a68ee1407a77f3e804a30dff245bb6c6b872f',
                    '51a3b654f252210572297f47597b31527c475fb8',
                    'ce8e0b86a1e9877f42fe9453ede418519115f367',
                    '589bb080f059834829a2a5955bebfd7c2baa110a',
                    'c6ba8f7a1058db3e6b4bc6f1090e932b107605fb',
                    'c0d66f92a95e31c77be08dc9d0f11a16715d1885',
                    '7debcf8a2f57f86663809c58b5c07a398be7674c',
                    '87783129c3f00d2c81a3a8e585eb86a47e39891a',
                    'bc57a9209f096a130dcc5ba7089a8663f758a703']

        self.assertEqual(commits, expected)

    def test_metadata(self):
        """Check if metadata parameters are correctly set"""

        job = PercevalJob('1234567890', 'mytask',
                          'git', 'commit',
                          self.conn, 'items')
        args = {
            'uri': 'http://example.com/',
            'gitpath': os.path.join(self.dir, 'data/git_log.txt')
        }

        job.run(args)

        items = self.conn.lrange('items', 0, -1)
        items = [pickle.loads(item) for item in items]

        for item in items:
            self.assertEqual(item['job_id'], '1234567890')

    def test_run_not_found_parameters(self):
        """Check if it fails when a required backend parameter is not found"""

        job = PercevalJob('1234567890', 'mytask',
                          'git', 'commit',
                          self.conn, 'items')
        args = {
            'uri': 'http://example.com/'
        }

        with self.assertRaises(AttributeError) as e:
            job.run(args)
            self.assertEqual(e.exception.args[1], 'gitlog')


class TestExecuteJob(TestBaseRQ):
    """Unit tests for execute_perceval_job"""

    def setUp(self):
        self.tmp_path = tempfile.mkdtemp(prefix='grimoire_sched_')
        self.dir = os.path.dirname(os.path.realpath(__file__))
        super().setUp()

    def tearDown(self):
        shutil.rmtree(self.tmp_path)
        super().tearDown()

    def test_job(self):
        """Execute Git backend job"""

        backend_args = {
            'uri': 'http://example.com/',
            'gitpath': os.path.join(self.dir, 'data/git_log.txt')
        }

        q = rq.Queue('queue', is_async=False)  # noqa: W606

        job = q.enqueue(execute_perceval_job,
                        backend='git', backend_args=backend_args, category='commit',
                        qitems='items', task_id='mytask')

        result = job.return_value
        self.assertEqual(result.job_id, job.get_id())
        self.assertEqual(result.task_id, 'mytask')
        self.assertEqual(result.backend, 'git')
        self.assertEqual(result.category, 'commit')
        self.assertEqual(result.summary.last_uuid, '1375b60d3c23ac9b81da92523e4144abc4489d4c')
        self.assertEqual(result.summary.max_updated_on,
                         datetime.datetime(2014, 2, 12, 6, 10, 39,
                                           tzinfo=datetime.timezone.utc))
        self.assertEqual(result.summary.last_updated_on,
                         datetime.datetime(2012, 8, 14, 17, 30, 13,
                                           tzinfo=datetime.timezone.utc))
        self.assertEqual(result.summary.total, 9)
        self.assertEqual(result.summary.max_offset, None)

        commits = self.conn.lrange('items', 0, -1)
        commits = [pickle.loads(c) for c in commits]
        commits = [(commit['job_id'], commit['data']['commit']) for commit in commits]

        expected = ['456a68ee1407a77f3e804a30dff245bb6c6b872f',
                    '51a3b654f252210572297f47597b31527c475fb8',
                    'ce8e0b86a1e9877f42fe9453ede418519115f367',
                    '589bb080f059834829a2a5955bebfd7c2baa110a',
                    'c6ba8f7a1058db3e6b4bc6f1090e932b107605fb',
                    'c0d66f92a95e31c77be08dc9d0f11a16715d1885',
                    '7debcf8a2f57f86663809c58b5c07a398be7674c',
                    '87783129c3f00d2c81a3a8e585eb86a47e39891a',
                    'bc57a9209f096a130dcc5ba7089a8663f758a703']

        for x in range(len(expected)):
            item = commits[x]
            self.assertEqual(item[0], result.job_id)
            self.assertEqual(item[1], expected[x])

    def test_job_no_result(self):
        """Execute a Git backend job that will not produce any results"""

        backend_args = {
            'uri': 'http://example.com/',
            'gitpath': os.path.join(self.dir, 'data/git_log_empty.txt'),
            'from_date': datetime.datetime(2020, 1, 1, 1, 1, 1)
        }

        q = rq.Queue('queue', is_async=False)  # noqa: W606
        job = q.enqueue(execute_perceval_job,
                        backend='git', backend_args=backend_args,
                        category='commit', qitems='items', task_id='mytask')

        result = job.return_value
        self.assertEqual(result.job_id, job.get_id())
        self.assertEqual(result.task_id, 'mytask')
        self.assertEqual(result.backend, 'git')
        self.assertEqual(result.category, 'commit')
        self.assertEqual(result.summary.last_uuid, None)
        self.assertEqual(result.summary.max_updated_on, None)
        self.assertEqual(result.summary.last_updated_on, None)
        self.assertEqual(result.summary.total, 0)
        self.assertEqual(result.summary.max_offset, None)

        commits = self.conn.lrange('items', 0, -1)
        commits = [pickle.loads(c) for c in commits]
        self.assertListEqual(commits, [])


class TestGitHubOwnerReposJob(TestBaseRQ):
    """Unit tests for fetch_github_owner_repos"""

    @httpretty.activate
    def test_fetch_owner_repos(self):
        """Check if the job for fetching owner repositories is executed correctly."""

        repos = read_file('data/github_repos_1.json')

        httpretty.register_uri(httpretty.GET,
                               GITHUB_REPOS_URL,
                               body=repos,
                               status=200)

        expected = {
            'repositories': [{'url': 'https://github.com/chaoss_example/eagle',
                              'fork': False,
                              'has_issues': False,
                              'has_pull_requests': True,
                              'archived': True},
                             {'url': 'https://github.com/chaoss_example/echarts',
                              'fork': False,
                              'has_issues': True,
                              'has_pull_requests': True,
                              'archived': False}],
            'errors': [],
            'owner': 'chaoss_example',
            'backend': 'GitHub'
        }

        q = rq.Queue('owner', is_async=False)

        job = q.enqueue(fetch_github_owner_repos, owner='chaoss_example')

        self.assertDictEqual(job.result, expected)

    @httpretty.activate
    def test_fetch_owner_repos_token(self):
        """Check if the job for fetching owner repositories is executed when using api_token."""

        repos = read_file('data/github_repos_1.json')

        httpretty.register_uri(httpretty.GET,
                               GITHUB_REPOS_URL,
                               body=repos,
                               status=200)

        expected = {
            'repositories': [{'url': 'https://github.com/chaoss_example/eagle',
                              'fork': False,
                              'has_issues': False,
                              'has_pull_requests': True,
                              'archived': True},
                             {'url': 'https://github.com/chaoss_example/echarts',
                              'fork': False,
                              'has_issues': True,
                              'has_pull_requests': True,
                              'archived': False}],
            'errors': [],
            'owner': 'chaoss_example',
            'backend': 'GitHub'
        }

        q = rq.Queue('owner', is_async=False)
        job = q.enqueue(fetch_github_owner_repos, owner='chaoss_example', api_token='aaaa')

        self.assertDictEqual(job.result, expected)
        self.assertEqual(httpretty.last_request().headers["Authorization"], "token aaaa")

    @httpretty.activate
    def test_not_found_owner(self):
        """Check if the job for fetching owner repositories returns a not found user."""

        body = str({
            "message": "Not Found",
            "documentation_url": "https://docs.github.com/rest/reference/repos#list-repositories-for-a-user"
        })
        httpretty.register_uri(httpretty.GET,
                               GITHUB_REPOS_URL,
                               body=body,
                               status=404)
        expected = {'repositories': [],
                    'errors': ['404 Client Error: Not Found for url: '
                               'https://api.github.com/users/chaoss_example/repos'],
                    'owner': 'chaoss_example',
                    'backend': 'GitHub'}

        q = rq.Queue('owner', is_async=False)

        job = q.enqueue(fetch_github_owner_repos, owner='chaoss_example')

        self.assertDictEqual(job.result, expected)

    @httpretty.activate
    def test_server_error(self):
        """Check if the job for fetching owner repositories returns a server error."""

        httpretty.register_uri(httpretty.GET,
                               GITHUB_REPOS_URL,
                               body='',
                               status=500)
        expected = {'repositories': [],
                    'errors': ['500 Server Error: Internal Server Error for url: '
                               'https://api.github.com/users/chaoss_example/repos'],
                    'owner': 'chaoss_example',
                    'backend': 'GitHub'}
        q = rq.Queue('owner', is_async=False)

        job = q.enqueue(fetch_github_owner_repos, owner='chaoss_example')
        self.assertDictEqual(job.result, expected)


class TestGitLabOwnerReposJob(TestBaseRQ):
    """Unit tests for fetch_gitlab_owner_repos"""

    @httpretty.activate
    def test_fetch_owner_repos(self):
        """Check if the job for fetching owner repositories is executed correctly."""

        body_user = read_file('data/gitlab_user.json')
        body_repos = read_file('data/gitlab_user_repos_1.json')

        httpretty.register_uri(httpretty.GET,
                               GITLAB_USER_URL,
                               body=body_user,
                               status=200)
        httpretty.register_uri(httpretty.GET,
                               GITLAB_USER_REPOS_URL,
                               body=body_repos,
                               status=200)

        expected = {
            'repositories': [
                {'url': 'https://gitlab.com/user_example/project-1',
                 'archived': False,
                 'fork': True,
                 'has_issues': True,
                 'has_pull_requests': False},
                {'url': 'https://gitlab.com/user_example/project-2',
                 'archived': False,
                 'fork': False,
                 'has_issues': False,
                 'has_pull_requests': True},
                {'url': 'https://gitlab.com/user_example/project-3',
                 'archived': True,
                 'fork': False,
                 'has_issues': True,
                 'has_pull_requests': True}
            ],
            'errors': [],
            'owner': 'user_example',
            'backend': 'GitLab'
        }

        q = rq.Queue('owner', is_async=False)
        job = q.enqueue(fetch_gitlab_owner_repos, owner='user_example')

        self.assertDictEqual(job.result, expected)

    @httpretty.activate
    def test_fetch_owner_repos_token(self):
        """Check if the job for fetching owner repositories is executed when using api_token."""

        body_user = read_file('data/gitlab_user.json')
        body_repos = read_file('data/gitlab_user_repos_1.json')

        httpretty.register_uri(httpretty.GET,
                               GITLAB_USER_URL,
                               body=body_user,
                               status=200)
        httpretty.register_uri(httpretty.GET,
                               GITLAB_USER_REPOS_URL,
                               body=body_repos,
                               status=200)

        expected = {
            'repositories': [
                {'url': 'https://gitlab.com/user_example/project-1',
                 'archived': False,
                 'fork': True,
                 'has_issues': True,
                 'has_pull_requests': False},
                {'url': 'https://gitlab.com/user_example/project-2',
                 'archived': False,
                 'fork': False,
                 'has_issues': False,
                 'has_pull_requests': True},
                {'url': 'https://gitlab.com/user_example/project-3',
                 'archived': True,
                 'fork': False,
                 'has_issues': True,
                 'has_pull_requests': True}
            ],
            'errors': [],
            'owner': 'user_example',
            'backend': 'GitLab'
        }

        q = rq.Queue('owner', is_async=False)
        job = q.enqueue(fetch_gitlab_owner_repos, owner='user_example', api_token='aaaa')

        self.assertDictEqual(job.result, expected)
        self.assertEqual(httpretty.last_request().headers["Authorization"], "Bearer aaaa")

    @httpretty.activate
    def test_not_found_owner(self):
        """Check if the job for fetching owner repositories returns a not found error."""

        user_unknown_url = 'https://gitlab.com/api/v4/users?username=user_unknown'
        group_unknown_url = 'https://gitlab.com/api/v4/groups/user_unknown'

        httpretty.register_uri(httpretty.GET,
                               user_unknown_url,
                               body="[]",
                               status=200)

        httpretty.register_uri(httpretty.GET,
                               group_unknown_url,
                               body=str({"message": "404 Group Not Found"}),
                               status=404)
        expected = {'repositories': [],
                    'errors': ['GitLab owner "user_unknown" not found'],
                    'owner': 'user_unknown',
                    'backend': 'GitLab'}

        q = rq.Queue('owner', is_async=False)
        job = q.enqueue(fetch_gitlab_owner_repos, owner='user_unknown')

        self.assertDictEqual(job.result, expected)
