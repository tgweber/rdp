################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains all generic code related to metadata as a component of RDPs
#
################################################################################

from collections import OrderedDict
from datetime import datetime
import json
import re
import xmltodict

from rdp.util import Bundle

class Metadata(object):
    """ Base class and interface for Metadata as components of RDPs

    Attributes
    ----------
    descriptions: list<Description>
        Descriptions of the RDP
    pid: str
        Identifier for the RDP
    titles: list<Title>
        Titles of the RDP
    formats: list<str>
        Formats of the RDP
    rights: list<Rights>
        Legal information about the RDP
    subjects: list<Subject>
        Keywords describing the RDP
    creators: list<PersonOrInstitution>
        Creators of the RDP
    sizes: list<str>
        Size specification for the RDP
    language: str
        Language of the RDP
    version: str
        Version of the RDP
    contributors: list<PersonOrInstitution>
        Contributors to the RDP
    publicationYear: int
        Year of publication of the RDP
    dates: list<Date>
        Dates of interest for the RDP
    type: str
        Type of the RDP
    relatedResources: list<RelatedResource>
        Resources related to this RDP
    """
    @property
    def descriptions(self):
        raise NotImplementedError("Must be implemented by subclasses of Metadata.")
    @property
    def pid(self):
        raise NotImplementedError("Must be implemented by subclasses of Metadata.")
    @property
    def titles(self):
        raise NotImplementedError("Must be implemented by subclasses of Metadata.")
    @property
    def formats(self):
        raise NotImplementedError("Must be implemented by subclasses of Metadata.")
    @property
    def rights(self):
        raise NotImplementedError("Must be implemented by subclasses of Metadata.")
    @property
    def subjects(self):
        raise NotImplementedError("Must be implemented by subclasses of Metadata.")
    @property
    def creators(self):
        raise NotImplementedError("Must be implemented by subclasses of Metadata.")
    @property
    def sizes(self):
        raise NotImplementedError("Must be implemented by subclasses of Metadata.")
    @property
    def language(self):
        raise NotImplementedError("Must be implemented by subclasses of Metadata.")
    @property
    def version(self):
        raise NotImplementedError("Must be implemented by subclasses of Metadata.")
    @property
    def contributors(self):
        raise NotImplementedError("Must be implemented by subclasses of Metadata.")
    @property
    def publicationYear(self):
        raise NotImplementedError("Must be implemented by subclasses of Metadata.")
    @property
    def dates(self):
        raise NotImplementedError("Must be implemented by subclasses of Metadata.")
    @property
    def type(self):
        raise NotImplementedError("Must be implemented by subclasses of Metadata.")
    @property
    def relatedResources(self):
        raise NotImplementedError("Must be implemented by subclasses of Metadata.")

class Description(object):
    """ Base class and interface for descriptions as a metadata field of RDPs

    Attributes
    ----------
    text: str
        The text of the description
    type: str
        The type of the description, might be None
    """
    def __init__(self, text, dtype=None):
        self.text = text
        self.type = dtype

class Title(object):
    """ Base class and interface for titles as a metadata field of RDPs

    Attributes
    ----------
    text: str
        The text of the title
    type: str
        The type of the title, might be None
    """
    def __init__(self, text, ttype=None):
        self.text = text
        self.type = ttype

class Rights(object):
    """ Base class and interface of rights/licenses as part of metadata of RDPs

    Attributes
    ----------
    text: str
        The text field of the license/rights information
    uri: str
        URI poiniting to the text of the license/rights information
    spdx: str
        SPDX identifier as specified on https://spdx.org/licenses/
    """
    def __init__(self, text, uri=None, spdx=None):
        self.text = text
        self.uri = uri
        self.spdx = spdx

class Subject(object):
    """ Base class and interface for subjects as part of metadata of RDPs

    Attributes
    ----------
    text: str
        The payload of the subject
    scheme: str
        The name of the scheme of the subjects (not controlled)
    uri: str
        The uri to the scheme of the subject
    """
    def __init__(self, text, scheme=None, uri=None, valueURI=None):
        self.text = text
        self.scheme = scheme
        self.uri = uri
        self.valueURI = valueURI

class PersonOrInstitution(object):
    """ Base class and interface for objects that could be listed as either
        persons or institutions

    Attributes
    ----------
    name: str
        Name of the person/institution
    """
    def __init__(self, name, person=True):
        self.name = name
        self.person = person
        self.type = None

    def __getattr__(self, name):
        return None

class Person(PersonOrInstitution):
    """ Base class and interface for persons as part of metadata of RDPs

    Attributes
    ----------
    name: str
        Name of the person
    givenName: str
        Given name of the person
    familiyName: str
        Familiy name of the person
    affiliation: str
        Affiliation of the person
    orcid: str
        ORCiD of the person
    type: str
        Type of the person (only set for contributors)
    """
    def __init__(self, name, affiliation=None, orcid=None):
        PersonOrInstitution.__init__(self, name, True)
        self.name = name
        if ", " in self.name:
            self.givenName = self.name.split(", ")[1]
            self.familyName = self.name.split(", ")[0]
        else:
            self.givenName = None
            self.familyName = None
        self.affiliations = [affiliation]
        self.orcid = orcid
        self.type = None

class Date(object):
    """ Base class and interface for dates as part of metadata of RDPs

    Attributes
    ----------
    date: datetime
        Datetime value of the date
    type: str
        Type of the date
    """
    def __init__(self, dateString, dateType=None, information=None):
        if "/" in dateString:
            self.date = parseDateString(dateString.split("/")[0])
            self.end = parseDateString(dateString.split("/")[1])
            self.duration = True
        else:
            self.date = parseDateString(dateString)
            self.end = self.date
            self.duration = False
        self.type = dateType
        self.information = information

def parseDateString(dateString):
    """ Function to parse a dateString compliant to ISO 8601 profile specified
        by W3CDTF (https://www.w3.org/TR/NOTE-datetime, retrieved 2020-03-09)
        or None otherwise

    Argument
    --------
    dateString: str
        String representing a valid date format

    Returns
    -------
    Datetime object
    """
    # Remedy for "+/-%H:%S" time zone formatting
    # adapted version from https://stackoverflow.com/a/45300534
    # Should become superfluous if Python version is >= 3.7
    if re.match(r".*(\+|-)\d{1,2}:\d\d$", dateString):
        # drop the colon
        dateString = dateString[:-3] + dateString[-2:]
    formats = ("%Y", "%Y-%m", "%Y-%m-%d", "%Y-%m-%dT%H:%M%z", "%Y-%m-%dT%H:%M:%S%z")
    for f in formats:
        try:
            return datetime.strptime(dateString, f)
        except ValueError:
            continue
    raise ValueError("'{}' is not in a supported format".format(dateString))

class RelatedResource(object):
    """ Base class and interface for related resources of an RDP

    Attributes
    ----------
    pid: str
        Persistant identifier of the related resource
    pidType: str
        Type of the identifier of the related resource
    relationType: str
        Type of the relation of the RDP to the resource
    schemeURI: str
        URI of the scheme describing the related resource
    schemeType: str
        Type of the scheme describing the related resource
    """
    def __init__(self, pid, pidType=None, relationType=None, schemeURI=None, schemeType=None):
        self.pid = pid
        self.pidType = pidType
        self.relationType = relationType
        self.schemeURI = schemeURI
        self.schemeType = schemeType

class OaiPmhMetadata(Metadata):
    """ Base class and interface et or all OAI-PMH-based Metadata objects
    """

    def _initialize(self, oaipmh):
        """ Initializes the md attribute from an XML-encoded OAI-PMH response

        Parameters
        ----------
        oaipmh: str
            XML-encoded OAI-PMH response
        """
        oaipmh = xmltodict.parse(oaipmh)
        self.md = oaipmh["OAI-PMH"]["GetRecord"]["record"]["metadata"]["resource"]

    def _normalize(self, md=None) -> None:
        """ Normalizes the metadata (recursively)

        Parameters
        ----------
        md: dict, optional
            Metadata to be normalized. If empty, the md attribute of the object will be used.
        """
        if not md:
            md = self.md
        for key in md.keys():
            if type(md[key]) == OrderedDict:
                if '#text'in md[key].keys():
                    md[key][key] = md[key]['#text']
                    del md[key]['#text']
                self._normalize(md[key])
