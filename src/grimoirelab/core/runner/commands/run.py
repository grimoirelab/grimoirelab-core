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
#

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

import os
import time

import click
import django_rq
import redis
from django.conf import settings

from django.core.wsgi import get_wsgi_application
from django.core import management

if TYPE_CHECKING:
    from click import Context


@click.group()
@click.option('--config', 'cfg', envvar='GRIMOIRELAB_CONFIG',
              default='grimoirelab.core.config.settings', show_default=True,
              help="Configuration module in Python path syntax")
@click.pass_context
def run(ctx: Context, cfg: str):
    """Run a service.

    To run the tool you will need to pass a configuration file module
    using Python path syntax (e.g. grimoirelab.core.config.settings).
    Take into account the module should be accessible by your PYTHON_PATH.
    """

    env = os.environ

    if cfg:
        env['DJANGO_SETTINGS_MODULE'] = cfg
        ctx.ensure_object(dict)
        ctx.obj["cfg"] = cfg
    else:
        raise click.ClickException(
            "Configuration file not given. "
            "Set it with '--config' option "
            "or 'GRIMOIRELAB_CONFIG' env variable."
        )

    _ = get_wsgi_application()


@run.command()
@click.argument('queues', nargs=-1)
def scheduler_worker(queues: list):
    """Starts a GrimoireLab worker.

    Workers get jobs from the list of queues, executing one job at a time.
    This list of queues are passed as a list of arguments to this command,
    and they need to be defined in the configuration file. If the list is
    not given, workers will listen for jobs on all the queues defined in
    the configuration.

    The configuration is defined by a configuration file module using
    Python path syntax (e.g. grimoirelab.core.config.settings). Take into
    account the module should be accessible by your PYTHONPATH env variable.

    QUEUES: read jobs from this list; if empty, reads from all the
    defined queues in the configuration file.
    """
    try:
        management.call_command('rqworker',
                                *queues,
                                with_scheduler=True,
                                job_class='grimoirelab.core.scheduler.jobs.PercevalJob')
    except KeyError as e:
        raise click.ClickException(f"Queue '{e.args[0]}' not found")


@run.command()
@click.option('--num-workers', default=10, show_default=True,
              help="Number of workers to run in the pool.")
def workerpool(num_workers: int):
    """Starts a GrimoireLab worker pool.

    Workers get jobs from the Q_PERCEVAL_JOBS queue defined in the
    configuration file.
    """
    management.call_command('rqworker-pool',
                            settings.Q_PERCEVAL_JOBS,
                            num_workers=num_workers,
                            job_class='grimoirelab.core.scheduler.jobs.PercevalJob')


@click.option(
    "--dev",
    "devel",
    is_flag=True,
    default=False,
    help="Run the service in developer mode.",
)
@run.command()
@click.pass_context
def server(ctx: Context, devel: bool):
    """Starts the GrimoireLab core server.

    GrimoireLab allows to schedule tasks and fetch data from software
    repositories. The server provides an API to perform all the operations.

    To run the server, you will need to pass a configuration file module
    using Python path syntax (e.g. grimoirelab.core.config.settings). Take into
    account the module should be accessible by your PYTHON_PATH.

    By default, the server runs a WSGI app because in production it should
    be run with a reverse proxy. If you activate the '--dev' flag, an HTTP
    server will be run instead.
    """
    env = os.environ

    env["UWSGI_ENV"] = f"DJANGO_SETTINGS_MODULE={ctx.obj['cfg']}"

    if devel:
        env["GRIMOIRELAB_DEBUG"] = "true"

        from django.conf import settings

        env["UWSGI_HTTP"] = env.get("GRIMOIRELAB_HTTP_DEV", "127.0.0.1:8000")
        env["UWSGI_STATIC_MAP"] = settings.STATIC_URL + "=" + settings.STATIC_ROOT
    else:
        env["UWSGI_HTTP"] = ""

    env["UWSGI_MODULE"] = "grimoirelab.core.app.wsgi:application"
    env["UWSGI_SOCKET"] = "0.0.0.0:9314"

    # Run in multiple threads by default
    env["UWSGI_WORKERS"] = env.get("GRIMOIRELAB_UWSGI_WORKERS", "1")
    env["UWSGI_THREADS"] = env.get("GRIMOIRELAB_UWSGI_THREADS", "4")

    # These options shouldn't be modified
    env["UWSGI_MASTER"] = "true"
    env["UWSGI_ENABLE_THREADS"] = "true"
    env["UWSGI_LAZY_APPS"] = "true"
    env["UWSGI_SINGLE_INTERPRETER"] = "true"

    os.execvp("uwsgi", ("uwsgi",))


def _create_consumer_group(connection: redis.Redis, stream_name: str, group_name: str):
    """Create a consumer group if it does not exist"""

    try:
        connection.xgroup_create(stream_name, group_name, id='0', mkstream=True)
    except redis.exceptions.ResponseError as e:
        if str(e) != 'BUSYGROUP Consumer Group name already exists':
            raise


def _recover_stream_entries(
        connection: redis.Redis,
        consumer_name: str,
        stream_name: str,
        group_name: str
) -> dict:
    """Transfers ownership of pending stream entries idle for 5m that match the specified criteria"""

    logging.info(f"Recovering events from '{stream_name}' group '{group_name}'")

    while True:
        response = connection.xautoclaim(name=stream_name,
                                         groupname=group_name,
                                         consumername=consumer_name,
                                         min_idle_time=5*60*1000,
                                         count=10)

        # The response contains an array with the following contents
        # 1) "0-0" (stream ID to be used as the start argument for the next call)
        # 2) 1) 1) "1609338752495-0" (successfully claimed messages)
        #       2) 1) "field"
        #          2) "value"
        # 3) (empty array) (message IDs that no longer exist in the stream)

        messages = response[1]
        for message in messages:
            message_id = message[0]
            message_data = message[1][b'data']

            yield json.loads(message_data)

            connection.xack(stream_name, group_name, message_id)

        if response[0] == b"0-0":
            break


def _items_consumer(
        connection: redis.Redis,
        consumer_name: str,
        stream_name: str | None = None,
        group_name: str | None = None
) -> dict:
    """Get items from a Redis stream given a group and a consumer name"""

    if not stream_name:
        stream_name = settings.REDIS_EVENTS_STREAM
    if not group_name:
        group_name = settings.REDIS_STREAM_GROUP_NAME

    _create_consumer_group(connection, stream_name, group_name)

    yield from _recover_stream_entries(connection=connection,
                                       consumer_name=consumer_name,
                                       group_name=group_name,
                                       stream_name=stream_name)

    logging.info(f"Fetching events from '{stream_name}' group '{group_name}' as '{consumer_name}'")

    total = 0
    while True:
        try:
            response = connection.xreadgroup(groupname=group_name,
                                             consumername=consumer_name,
                                             streams={stream_name: '>'},
                                             count=10,
                                             block=60000)

            # The response contains an array with the following contents
            # 1) 1) "mystream" (name of the stream)
            #    2) 1) 1) "1-0" (array of arrays containing the key and the entries)
            #          2) 1) "field"
            #             2) "value"

            if response:
                messages = response[0][1]
                for message in messages:
                    total += 1
                    message_id = message[0]
                    message_data = message[1][b'data']

                    yield json.loads(message_data)

                    connection.xack(stream_name, group_name, message_id)

                    if total % 1000 == 0:
                        logging.info(f"{total} items inserted")

            else:
                logging.info(f"No new messages for '{stream_name}:{group_name}:{consumer_name}'.")
        except Exception as e:
            logging.error(f"Error consuming messages: {e}")
            raise e


@run.command()
@click.option('--group-name', help='Name of the consumer group')
@click.option('--consumer-name', help='Name of the consumer')
def print_events_consumer(group_name, consumer_name):
    """Consume events from the Redis stream and prints them."""

    connection = django_rq.get_connection()

    if not consumer_name:
        consumer_name = f"consumer-{time.time()}"
    if not group_name:
        group_name = "test-consumer"

    items = _items_consumer(connection=connection,
                            consumer_name=consumer_name,
                            group_name=group_name)

    for i, item in enumerate(items):
        print(i, item['id'])


@run.command()
@click.argument('url')
@click.argument('index')
@click.option('--group-name', help='Name of the consumer group')
@click.option('--consumer-name', help='Name of the consumer')
def opensearch_consumer(url, index, group_name, consumer_name):
    """Consume events from the Redis stream and insert them into Opensearch."""

    from grimoire_elk.elastic import ElasticSearch

    rclient = django_rq.get_connection()
    elastic = ElasticSearch(url, index)

    if not consumer_name:
        consumer_name = f"consumer-{time.time()}"
    if not group_name:
        group_name = "opensearch-consumer"

    items = _items_consumer(connection=rclient,
                            consumer_name=consumer_name,
                            group_name=group_name)

    elastic.bulk_upload(items, field_id='id')
