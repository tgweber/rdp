################################################################################
# Copyright: Tobias Weber 2020
#
# Apache 2.0 License
#
# This file contains all RDP-related tests
#
################################################################################

from rdp.services.capacity import RetrieveData, RetrieveMetadata

def test_capacity_description():
    cap = RetrieveData()
    assert cap.description == "Capacity to download data given an identifier"
    cap = RetrieveMetadata()
    assert cap.description == "Capacity to download metadata given an identifier and a metadata scheme"
