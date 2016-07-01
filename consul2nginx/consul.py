#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. module:: TODO
   :platform: Unix
   :synopsis: TODO.

.. moduleauthor:: Aljosha Friemann aljosha.friemann@gmail.com

"""

import requests, simple_model, json, logging

logger = logging.getLogger(__name__)

class ConsulException(Exception):
    pass

class ConsulV1:
    def __init__(self, host, port):
        self._host = host
        self._port = port

    def _get_(self, endpoint):
        try:
            return requests.get('http://%s:%s/v1/%s' % (self._host, self._port, endpoint))
        except ValueError as e:
            logger.warning('failed to parse response data, is this really a consul server?')
            raise ConsulException(endpoint, e)
        except requests.exceptions.ConnectionError as e:
            raise ConsulException(endpoint, e)

    def get_services(self):
        for name, tags in self._get_('catalog/services').json().items():
            try:
                port = int(name.split('-')[-1])
            except ValueError:
                logger.info('ignoring service %s due to unavailable port information' % name)
                continue

            instances = [ dict(i) for i in self.get_service_instances(name) ] # necessary due to simple_model

            yield Service(name=name, port=port, tags=tags, instances=instances)

    def get_service_instances(self, name):
        for entry in self._get_('catalog/service/%s' % name).json():
            yield ServiceInstance(**entry)

class ServiceInstance(simple_model.Model):
    """
    {
        "Node": "ip-10-0-1-81.eu-west-1.compute.internal",
        "Address": "10.0.1.81",
        "ServiceID": "consul",
        "ServiceName": "consul",
        "ServiceTags": [],
        "ServiceAddress": "",
        "ServicePort": 8300,
        "ServiceEnableTagOverride": false,
        "CreateIndex": 4,
        "ModifyIndex": 5
    }
    """
    Node = simple_model.Attribute(str)
    Address = simple_model.Attribute(str)
    ServiceID = simple_model.Attribute(str)
    ServiceName = simple_model.Attribute(str)
    ServiceTags = simple_model.AttributeList(str)
    ServicePort = simple_model.Attribute(int)

class Service(simple_model.Model):
    """
    {
        "consul": [],
        "consul-loadbalancer-5601": ['udp'],
        "env-loop-1200": [
            "udp"
        ],
        "env-loop-4000": [],
        "metrics-elasticsearch": [],
        "metrics-kibana": [],
        "metrics-logstash-in": [],
        "metrics-rabbitmq": []
    }
    """
    name = simple_model.Attribute(str)
    port = simple_model.Attribute(int)
    tags = simple_model.AttributeList(str)
    instances = simple_model.AttributeList(ServiceInstance)

Consul = ConsulV1

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 fenc=utf-8
