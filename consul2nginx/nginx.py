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

class NginxException(Exception):
    pass

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
    def create_config(path, services):
        config = Nginx.get_template('nginx.conf.jinja2').render(service_groups=Nginx.group_services(services))

        if config is None:
            raise NginxException('config was None after creation')

        return config

    @staticmethod
    def create_overview(services):
        overview = Nginx.get_template('index.html.jinja2').render(service_groups=Nginx.group_services(services))

        if overview is None:
            raise NginxException('overview was None after creation')

        return overview

    @staticmethod
    def update_config(config, path):
        with open(path, 'wb') as result:
            result.write(config.encode())

    @staticmethod
    def update_overview(overview, nginx_root):
        html_dir = os.path.join(nginx_root, 'html')
        if not os.path.isdir(html_dir): os.mkdir(html_dir)

        with open(os.path.join(html_dir, 'index.html'), 'wb') as result:
            result.write(overview.encode())

    @staticmethod
    def test_config(config):
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(config.encode())
            tmp.flush()
            Nginx.check_file(tmp.name)

    @staticmethod
    def group_services(services):
        grouped_services = {'stream': {}, 'http': []}

        for service in services:
            if 'http' in service.tags:
                grouped_services['http'].append(service)
            else:
                while service.port in grouped_services['stream']:
                    service.port += 1

                if service.port > 65535:
                    logging.warning('failed to find available port for service: %s' % service)
                    continue

                grouped_services['stream'][service.port] = service

        return grouped_services

    @staticmethod
    def check_file(path):
        try:
            subprocess.check_call([os.environ.get('NGINX_BINARY', '/sbin/nginx'), '-t', '-c', path])
        except subprocess.CalledProcessError:
            raise NginxException('config file did not pass test')

    @staticmethod
    def reload():
        try:
            subprocess.check_call(['service', 'nginx', 'reload'])
        except subprocess.CalledProcessError:
            raise NginxException('failed to reload nginx')

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 fenc=utf-8
