################################################################################
# Copyright: Tobias Weber 2020
#
# Apache 2.0 License
#
# This file contains all credential-related tests
#
################################################################################

from rdp.services.credentials import UsernamePasswordCredential

def test_capacity_description():
    cred = UsernamePasswordCredential("username", "password")
    assert cred.username == "username"
    assert cred.password == "password"
