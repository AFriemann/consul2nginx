#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. module:: TODO
   :platform: Unix
   :synopsis: TODO.

.. moduleauthor:: Aljosha Friemann aljosha.friemann@gmail.com

"""

import click, logging, time

from .consul import Consul, Service
from .nginx import Nginx, NginxException

logger = logging.getLogger(__name__)

def setup_logging(verbose, debug):
    if verbose or debug:
        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
        logging.getLogger('simple_model').setLevel(logging.INFO)
        logging.getLogger('requests').setLevel(logging.INFO if debug else logging.WARNING)
    else:
        logging.basicConfig(level=logging.WARNING)

@click.command()
@click.option('--test/--no-test', default=True, help='test the generated file before reloading nginx')
@click.option('--reload/--no-reload', default=True, help='reload nginx after file generation')
@click.option('-v', '--verbose/--no-verbose', default=False, help='print verbose log output')
@click.option('--debug/--no-debug', default=False, help='print debug log output')
@click.option('-d', '--daemonize/--no-daemonize', default=False, help='run forever')
@click.option('-o', '--output', default='/etc/nginx/nginx.conf')
@click.option('-h', '--host', default='127.0.0.1', help='consul host')
@click.option('-p', '--port', default=8500, type=int, help='consul port')
@click.option('-t', '--timeout', default=5, type=int, help='timeout for polling (only used when running as daemon)')
def main(test, reload, verbose, debug, daemonize, output, host, port, timeout):
    try:
        setup_logging(verbose, debug)

        logger.debug('creating consul client')

        consul = Consul(host, port)

        logger.debug('checking consul connection')

        if not consul.check():
            logger.error('failed to connect to consul API via %s:%s', host, port)
            return 1

        if daemonize:
            logger.info('checking %s:%s every %ss' % (host, port, timeout))

        while (True):
            logger.debug('creating nginx config from consul')

            config = Nginx.create_config(output, consul.get_services(), test)

            if Nginx.different(config, output):
                logger.info('config file changed')
                Nginx.update_config(config, output, test)

                if reload:
                    logger.info('reloading nginx')
                    Nginx.reload()

            if daemonize:
                time.sleep(timeout)
            else:
                break

        return 0
    except NginxException as e:
        logger.error(e)
        return 1
    except Exception as e:
        logger.exception(e)
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 fenc=utf-8
