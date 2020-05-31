################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains all code related to services (as a component of RDPs)
#
################################################################################
import requests
from typing import Generator, Dict, List

from rdp.services.capacities import \
    RetrieveDataHttpHeaders, \
    RetrieveMetadata, \
    RetrieveData, \
    ServiceCapacity
from rdp.metadata.factory import MetadataFactory, Metadata
from rdp.data import FileDataFactory, Data
from rdp.exceptions import CannotCreateMetadataException
from rdp.util import Bundle, LazyFile

class Service(object):
    """ Base class + interface for Services as a component of RDPS

    Parameters
    ----------
    endpoint: str
        URL indicating the endpoint of the service

    Attributes
    ----------
    endpoint: str
    protocol: str
        Name of the protocol used by this service
    See parameters
    """
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.serviceCapacities = []
        self.credentials = {}

    @property
    def protocol(self):
        raise NotImplementedError("Protocol must be implemented by all subclasses of Services")

    def can(self, capacity: ServiceCapacity) -> bool:
        for sc in self.serviceCapacities:
            if isinstance(capacity, sc):
                return True
        return False

    def needs_credentials(self) -> str:
        """ returns a string representation of the needed
            credentials (classname). None if no credentials needed.
        """
        return None

    def inject_credentials(self, credentials) -> None:
        """ allows to inject the credentials at run time into
            the credentials dictionary
            (subclasses have to retrieve them there)
        """
        self.credentials[credentials.__name__] = credentials

class ServiceBundle(Bundle):
    """ Collection of services with methods to select a service best fit for a task
    """
    def __init__(self, credentials=[]):
        Bundle.__init__(self)
        self.credentials = credentials

    def put(self, itemType, item):
        Bundle.put(self, itemType, item)
        if item.needs_credentials():
            for given_credential in self.credentials:
                for needed_credential in item.needs_credentials():
                    if needed_credential == given_credential.__name__:
                        item.inject_credentials(credential)

    def get_metadata(self, identifier, scheme) -> Metadata:
        """ Get a metadata object for the RDP

        Parameters
        ----------
        identifier: str
            Identifier to be used in the service request
        scheme: str
            Scheme of the metadata to-be-requested

        Returns
        -------
        Metadata
            Metadata object for RDP in format specified by scheme
        """
        for key, service in self.payload.items():
            if service.can(RetrieveMetadata()):
                return service.get_metadata(identifier, scheme)
        return None

    def get_data(self, identifier) -> Generator[Data, None, None]:
        """ Get all data objects for the RDP

        Parameters
        ----------
        identifier: str
            Identifier to be used in the service request

        Yields
        ------
        Data
            Data objects for an RDP
        """
        for key, service in self.payload.items():
            if service.can(RetrieveData()):
                return service.get_data(identifier)
        return None

################################################################################
# SPECIFIC SERVICE IMPLEMENTATIONS
################################################################################
class OaipmhService(Service):
    """ OAI-PMH service for an RDP

    Parameters
    ----------
    endpoint: str
        URL indicating the endpoint of the service
    identifierPrefix: str, optional
        Prefix which will always be prepended to the identifier in OAI-PMH requests.
        Default value is the empty string.

    Methods
    -------
    get_record(identifier, metadataPrefix="datacite")
        OAI-PMH GetRecord request to retrieve metadata for the RDP in format
        specified by metadataPrefix
    """
    def __init__(self, endpoint, identifierPrefix=""):
        Service.__init__(self, endpoint)
        self.identifierPrefix = identifierPrefix
        self.serviceCapacities.append(RetrieveMetadata)

    @property
    def protocol(self):
        return "oai-pmh"

    def get_metadata(self, identifier, metadataPrefix="datacite") -> Metadata:
        """ OAI-PMH GetRecord request to retrieve metadata for the RDP in format
            specified by metadataPrefix

        Parameters
        ----------
        identifier: str
            Identifier to request the record corresponding to the RDP
        metadataPrefix: str, optional
            Format of the metadata record
        """
        params = {
            'verb': 'GetRecord',
            'metadataPrefix': metadataPrefix,
            'identifier': "{}{}".format(self.identifierPrefix, identifier)
        }
        r = requests.get(self.endpoint, params)
        if r.status_code >= 400:
            raise CannotCreateMetadataException(
                "Cannot create RDP with id {} via OAI-PMH; HTTP-Status-Code: {}".format(
                    identifier, r.status_code
                )
            )
        md_type = "oaipmh_{}".format(metadataPrefix)
        return MetadataFactory.create(md_type, r.content)

class ZenodoRestService(Service):
    """ Zenodo Rest API service for an RDP

    Parameters
    ---------
    endpoint: str
        URL indicating the endpoint of the service

    Methods
    -------
    get_files(zenodo_Id) -> Generator[Data, None, None]
        Yields all Data objects of the RDP retrievable by the zenodo API
    """
    def __init__(self, endpoint):
        Service.__init__(self, endpoint)
        self.serviceCapacities.append(RetrieveData)
        self.serviceCapacities.append(RetrieveDataHttpHeaders)

    @property
    def protocol(self):
        return "zenodo-rest"

    def download(source:str) -> bytes:
        r = requests.get(source)
        return r.content

    def _get_files_sources(self, zenodoId) -> List[str]:
        r = requests.get("{}/records/?q=recid:{}".format(self.endpoint, zenodoId))
        restJson = r.json()
        if not "hits" in restJson.keys():
            raise ValueError("{} does not seem to be a valid zenodoId".format(zenodoId))
        if restJson["hits"]["total"] != 1:
            raise ValueError("{} does not unambiguously identify a zenodo record".format(zenodoId))
        return restJson["hits"]["hits"][0]["files"]

    def get_data(self, zenodoId) -> Generator[Data, None, None]:
        """ Yields all Data objects of the RDP retrievable by the zenodo API

        Parameters
        ----------
        zenodoId: str
            Id used by zenodo to identify depositions

        Yields
        ------
        Data
            Data objects for an RDP
        """
        # TODO caching
        for data_item in self._get_files_sources(zenodoId):
            yield FileDataFactory.create(
                LazyFile(data_item["links"]["self"], ZenodoRestService.download)
            )

    def get_headers(self, zenodoId) -> Generator[Dict, None, None]:
        for data_item in self._get_files_sources(zenodoId):
            r = requests.head(data_item["links"]["self"])
            yield r.headers

