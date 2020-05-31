################################################################################
# Copyright: Tobias Weber 2020
#
# Apache 2.0 License
#
# This file contains all capacity-related tests
#
###############################################################################
from unittest import mock
import pytest
from util import mocked_requests_get
from rdp.exceptions import \
        CannotCreateRDPException, \
        CannotCreateMetadataException
from rdp.services import OaipmhService

def test_cannot_create_exceptions():
    oaipmh = OaipmhService("https://zenodo.org/oai2d", "oai:zenodo.org:")
    with pytest.raises(CannotCreateRDPException) as e:
        md = oaipmh.get_metadata("exception1", "datacite")
        assert e.endswith("404")
        assert isinstance(e, CannotCreateMetadataException)

