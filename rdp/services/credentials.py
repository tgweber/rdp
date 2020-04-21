################################################################################
# Copyright: Tobias Weber 2020
#
# Apache 2.0 License
#
# This file contains all code related to credentials for services
#
################################################################################

class ServiceCredential(object):
    """  Base class + interface for credentials to use sevices
    """

class UsernamePasswordCredential(ServiceCredential):
    """ Simple username/password credential
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password
