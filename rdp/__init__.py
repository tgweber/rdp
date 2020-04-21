################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains all code related to Research Data Product objects
#
################################################################################

from rdp.services import ServiceBundle, OaipmhService, ZenodoRestService
from rdp.util import Bundle

class Rdp(object):
    """ Base class + interface for Research Data Products (RDP)

    Parameters
    ----------
    pid : str
        Persistent Identifier of the RDP

    Attributes
    ----------
    data: Bundle
        All files which constitute the payload of the RDP
    metadata: Bundle
        All metadata describing the payload for the RDP
    services: ServiceBundle
        All services offering access to the data or metadata of the RDP
    """
    def __init__(self, pid):
        self.pid = pid
        self._data = []
        self._metadata = Bundle()
        self._services = ServiceBundle()

    @property
    def data(self) -> Bundle:
        """ Getter for the data bundle (lazy loading)

        Returns
        -------
        Bundle
            Bundle of Data objects
        """
        if len(self._data) < 1:
            for f in self._services.get_data(self.pid):
                self._data.append(f)
        return self._data

    @property
    def metadata(self) -> Bundle:
        """ Getter for the metadata bundle (lazy loading via services)

        Returns
        -------
        Bundle
            Bundle of metadata objects.
        """
        if len(self._metadata) < 1:
           self._metadata.put("metadata", self._services.get_metadata(self.pid, "metadata"))
        return self._metadata

class RdpFactory(object):
    """ Factory for RDPs (research data products)

    Methods
    -------
    create(pid, rdpType=None) -> Rdp
        Factory method returning an RDP appropriate for the given rdpType or a default RDP.
    """
    def create(pid, rdpType=None, **kwargs) -> Rdp:
        """Returns a fitting RDP given a type, a default otherwise

        Parameters
        ----------
        pid: str
            Persistent Identifier of the RDP
        rdpType: str, optional
            A key indicating which RDP should be instantiated (supported: zenodo)
        kwargs: dict
            Further optional arguments
        """
        if rdpType == "zenodo":
            return ZenodoRdp(pid)
        else:
            return Rdp(pid)

################################################################################
# SPECIFIC RDP IMPLEMENTATIONS
################################################################################
class ZenodoRdp(Rdp):
    """ RDP for RDPs stored in Zenodo (https://zenodo.org)

    Summary
    -------
    The ZenodoRDP is initiated with an OAI-PMH and an Zenodo REST-API service.

    """
    def __init__(self, pid):
       super(ZenodoRdp, self).__init__(pid)
       self.zenodo_id = self.pid.split(".")[-1]
       self._services.put(
           "oai-pmh",
           OaipmhService("https://zenodo.org/oai2d", "oai:zenodo.org:"))
       self._services.put(
           "zenodo-rest-api",
           ZenodoRestService("https://zenodo.org/api")
       )

    @property
    def data(self):
        if len(self._data) < 1:
            for f in self._services.get_data(self.zenodo_id):
                self._data.append(f)
        return self._data

    @property
    def metadata(self) -> Bundle:
        if not self._metadata.has("datacite"):
           self._metadata.put("datacite", self._services.get_metadata(self.zenodo_id, "datacite"))
        return self._metadata.get("datacite")
