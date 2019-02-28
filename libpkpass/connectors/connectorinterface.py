#!/usr/bin/env python
"""This is a base class interface for cert connectors"""
from abc import ABCMeta

class ConnectorInterface(object):
    __metaclass__ = ABCMeta
    ##############################################################################
    def __init__(self):
    ##############################################################################
        pass

    ##############################################################################
    def __getitem__(self, key):
    ##############################################################################
        return getattr(self, key)

    ##############################################################################
    def list_certificates(self):
    ##############################################################################
        raise NotImplementedError
