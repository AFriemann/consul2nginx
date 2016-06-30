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

class ConsulV1:
    def __init__(self, host, port):
        self._host = host
        self._port = port

    def _get_(self, endpoint):
        return requests.get('http://%s:%s/v1/%s' % (self._host, self._port, endpoint))

    def check(self):
        try:
            return self._get_('agent/self').status_code == 200
        except requests.exceptions.ConnectionError:
            return False

    def get_services(self):
        for name, tags in self._get_('catalog/services').json().items():
            instances = [ dict(i) for i in self.get_service_instances(name) ] # necessary due to simple_model
            service = Service(name=name, tags=tags, instances=instances)
            yield service

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
    port = simple_model.Attribute(int, fallback=80)
    tags = simple_model.AttributeList(str)
    instances = simple_model.AttributeList(ServiceInstance)
Consul = ConsulV1

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 fenc=utf-8
