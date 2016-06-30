#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. module:: TODO
   :platform: Unix
   :synopsis: TODO.

.. moduleauthor:: Aljosha Friemann aljosha.friemann@gmail.com

"""

import tempfile, logging, subprocess, os

from jinja2 import Template
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

# Capture our current directory

class Nginx:
    @staticmethod
    def get_template(name):
        cwd = os.path.dirname(os.path.abspath(__file__))
        j2_env = Environment(loader=FileSystemLoader(os.path.join(cwd, 'templates')))
        return j2_env.get_template(name)

    @staticmethod
    def different(config, path):
        if not os.path.isfile(path):
            return True

        with open(path, 'r') as f:
            content = f.read()
        return config != content

    @staticmethod
    def create_config(path, services, test):
        config = Nginx.get_template('nginx.conf.jinja2').render(service_groups=Nginx.group_services(services))

        if config is None:
            raise Exception('config was None after creation')

        if Nginx.different(config, path):
            logger.info('config file changed')

            if test:
                logger.debug('testing created config file')
                with tempfile.NamedTemporaryFile() as tmp:
                    tmp.write(config.encode())
                    Nginx.check_file(tmp.name)

            with open(path, 'wb') as result:
                logger.debug('writing config to %s' % path)
                result.write(config.encode())

    @staticmethod
    def group_services(services):
        grouped_services = {'udp': {}, 'tcp': {}}

        for service in services:
            protocol = 'udp' if 'udp' in service.tags else 'tcp'
            service_group = grouped_services[protocol].get(service.port, [])
            grouped_services[protocol].update({ service.port: service_group + [ service ] })

        return grouped_services

    @staticmethod
    def check_file(path):
        try:
            subprocess.check_call(['/sbin/nginx', '-t', '-c', path])
        except subprocess.CalledProcessError:
            raise Exception('config file did not pass test')

    @staticmethod
    def reload():
        try:
            subprocess.check_call(['service', 'nginx', 'reload'])
        except subprocess.CalledProcessError:
            raise Exception('failed to reload nginx')

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 fenc=utf-8
