#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. module:: TODO
   :platform: Unix
   :synopsis: TODO.

.. moduleauthor:: Aljosha Friemann aljosha.friemann@gmail.com

"""

import os, pip

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), encoding='utf8').read()

install_reqs = pip.req.parse_requirements('requirements.txt', session=pip.download.PipSession())

requirements = [str(ir.req) for ir in install_reqs if ir is not None]

from consul2nginx import __version__

setup(name             = 'consul2nginx',
      author           = 'Aljosha Friemann',
      author_email     = 'aljosha.friemann@gmail.com',
      description      = 'Create nginx configuration from consul',
      url              = 'https://github.com/afriemann/consul2nginx',
      keywords         = ['consul', 'proxy', 'nginx', 'configuration'],
      classifiers      = [],
      version          = __version__,
      license          = read('LICENSE.txt'),
      long_description = read('README.rst'),
      install_requires = requirements,
      packages         = [ 'consul2nginx' ],
      entry_points     = { 'console_scripts': ['consul2nginx=consul2nginx.cli:main'] },
      package_data     = { 'consul2nginx': ['consul2nginx/templates/*'] },
      platforms        = 'linux',
      include_package_data = True
)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 fenc=utf-8
