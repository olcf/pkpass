#!/usr/bin/env python3
"""This is a base class interface for cert connectors"""
from abc import ABCMeta

    ##############################################################################
class ConnectorInterface():
    """Simple interface for a Connector"""
    ##############################################################################
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
        """This should return a dict with the key being username and the value being
        a list of certicates """
        ##############################################################################
        raise NotImplementedError
