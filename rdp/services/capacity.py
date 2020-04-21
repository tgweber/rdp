################################################################################
# Copyright: Tobias Weber 2020
#
# Apache 2.0 License
#
# This file contains all code related to capacities of services
#
################################################################################

import inspect

class ServiceCapacity(object):
    """ Base class + interface for ServiceCapacities
    """
    @property
    def description(self) -> str:
        return ' '.join(inspect.getdoc(self).split("\n\n")[0].split())

class RetrieveMetadata(ServiceCapacity):
    """ Capacity to download metadata given an identifier and a metadata scheme

        Service must provide get_record(identifier: str, scheme:str) -> Metadata
    """

class RetrieveData(ServiceCapacity):
    """ Capacity to download data given an identifier

        The service must provide get_data(identifier: str) -> Generator[Data, None, None]
    """
