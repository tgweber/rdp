################################################################################
# Copyright: Tobias Weber 2020
#
# Apache 2.0 License
#
# This file contains all code related to services (as a component of RDPs)
#
################################################################################

class CannotCreateRDPException(Exception):
    pass

class CannotCreateMetadataException(CannotCreateRDPException):
    pass
