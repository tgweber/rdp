################################################################################
# Copyright: Tobias Weber 2020
#
# Apache 2.0 License
#
# This file contains all code related to metadata factories
#
################################################################################
from rdp.metadata import Metadata, OaiPmhMetadata
from rdp.metadata.datacite import DataCiteMetadata

class MetadataFactory(object):
    """ Factory for Metadata

    Methods
    ------
    create(md_type, payload) -> Metadata
        Factory method returning a Metadata object appropriate for the given type and payload
    """
    def create(mdType, payload) -> Metadata:
        """ Creates a Metadata object appropriate for the given type and payload

        Parameters
        ----------
        md_type: str
            Type of the Metadata, supported types: oaipmh_datacite
        payload: misc
            Payload to be used to create the Metadata object

        Returns
        -------
        Metadata: The created Metadata object
        """
        if mdType in ("oaipmh_datacite"):
            md = DataCiteMetadata()
            md._initialize(payload)
            md._normalize()
            return md
        return Metadata()
