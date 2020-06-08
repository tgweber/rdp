################################################################################
# Copyright: Tobias Weber 2020
#
# Apache 2.0 License
#
# This file contains all code related to metadata (as a component of RDPs)
#
################################################################################

from collections import OrderedDict
import re

from rdp.metadata import \
    Date, \
    Description, \
    OaiPmhMetadata, \
    Person, \
    PersonOrInstitution, \
    RelatedResource, \
    Rights, \
    Subject, \
    Title

class DataCiteMetadata(OaiPmhMetadata):
    """ DataCite Metadata Object
    """
    def __init__(self):
        self._identifier = None
        self._creators = []
        self._descriptions = []
        self._formats = []
        self._rightsList = []
        self._sizes = []
        self._subjects = []
        self._titles = []
        self._language = None
        self._version = None
        self._publicationYear = None
        self._contributors = []
        self._dates = []
        self._relatedIdentifiers = []
        self._resourceType = None

    @property
    def pid(self) -> str:
        if self.should_be_parsed("identifier"):
            identifier = self.md.get("identifier")
            if isinstance(identifier, str):
                self._identifier = identifier
            elif isinstance(identifier, OrderedDict):
                self._identifier = identifier.get("identifier", identifier.get("#text"))
        return self._identifier

    @property
    def descriptions(self):
        if self.should_be_parsed("descriptions"):
            descriptions = self.md["descriptions"].get("description")
            if isinstance(descriptions, (str, OrderedDict)):
                descriptions = [ descriptions ]
            for d in descriptions:
                if d is None:
                    continue
                if isinstance(d, OrderedDict):
                    self._descriptions.append(Description(
                        d.get("description", d.get("#text")),
                        d.get("@descriptionType"))
                    )
                else:
                    self._descriptions.append(Description(d))
        return self._descriptions

    @property
    def titles(self):
        if self.should_be_parsed("titles"):
            titles = self.md["titles"].get("title")
            if isinstance(titles, (str, OrderedDict)):
                titles = [ titles ]
            for t in titles:
                if t is None:
                    continue
                if isinstance(t, OrderedDict):
                    self._titles.append(Title(
                        t.get("title", t.get("#text")),
                        t.get("@titleType"))
                    )
                elif isinstance(t, str):
                    self._titles.append(Title(t))
        return self._titles

    @property
    def formats(self):
        if self.should_be_parsed("formats"):
            if isinstance(self.md["formats"].get("format"), list):
                self._formats = self.md["formats"]["format"]
            else:
                self._formats.append(self.md["formats"]["format"])
        return self._formats

    @property
    def rights(self):
        if self.should_be_parsed("rightsList"):
            rights = self.md["rightsList"].get("rights", None)
            if isinstance(rights, (str, OrderedDict)):
                rights = [ rights ]
            if isinstance(rights , list):
                for r in rights:
                    if r is None:
                        continue
                    if isinstance(r, str):
                        r = {"rights": r}
                    ro = Rights(
                        r.get("rights", r.get("#text")),
                        r.get("@rightsURI", None)
                    )
                    if r.get("@schemeURI", "").startswith("https://spdx.org/licenses") \
                        or r.get("@rightsIdentifierScheme", "").lower() == "spdx":
                        ro.spdx = r.get("@rightsIdentifier", None)
                    self._rightsList.append(ro)
        return self._rightsList

    @property
    def subjects(self):
        if self.should_be_parsed("subjects"):
            subjects = self.md["subjects"].get("subject")
            if isinstance(subjects, (str, OrderedDict)):
                subjects = [ subjects ]
            if isinstance(subjects, list):
                for s in subjects:
                    if s is None:
                        continue
                    if isinstance(s, str):
                        s = { "#text": s}
                    self._subjects.append(
                        Subject(
                            s.get("subject", s.get("#text")),
                            s.get("@subjectScheme"),
                            s.get("@schemeURI"),
                            s.get("@valueURI")
                        )
                    )
        return self._subjects

    @property
    def creators(self):
        if self.should_be_parsed("creators"):
            creators = self.md["creators"].get("creator")
            if isinstance(creators, (str, OrderedDict)):
                creators = [ creators ]
            for p in creators:
                self._creators.append(
                        create_personOrInstitution_object_from_OrderedDict(p)
                )
        return self._creators

    @property
    def contributors(self):
        if self.should_be_parsed("contributors"):
            contributors = self.md["contributors"].get("contributor")
            if isinstance(contributors, (str, OrderedDict)):
                contributors = [ contributors ]
            for p in contributors:
                self._contributors.append(
                        create_personOrInstitution_object_from_OrderedDict(p)
                )
        return self._contributors

    @property
    def sizes(self):
        if self.should_be_parsed("sizes"):
            sizes = self.md["sizes"].get("size")
            if isinstance(sizes, str):
                self._sizes = [sizes]
            elif isinstance(sizes, list):
                self._sizes = sizes
        return self._sizes

    @property
    def language(self):
        if self.should_be_parsed("language"):
            language = self.md.get("language")
            if isinstance(language, str):
                self._language = language
            elif isinstance(language, OrderedDict):
                self._language = language.get("language", language.get("#text"))
        return self._language

    @property
    def version(self):
        if self.should_be_parsed("version"):
            version = self.md.get("version")
            if isinstance(version, str):
                self._version = self.md.get("version")
            elif isinstance(version, OrderedDict):
                self._version = version.get("version", version.get("#version"))
        return self._version

    @property
    def publicationYear(self):
        if self.should_be_parsed("publicationYear"):
            publicationYear = self.md.get("publicationYear")
            if isinstance(publicationYear, str):
                self._publicationYear = int(publicationYear)
        return self._publicationYear

    @property
    def dates(self):
        if self.should_be_parsed("dates"):
            dates = self.md["dates"]["date"]
            if not isinstance(dates, list):
                dates = [ dates ]
            for d in dates:
                if isinstance(d, str):
                    try:
                        self._dates.append((Date(d)))
                    except ValueError as ve:
                        pass
                if isinstance(d, OrderedDict):
                    if d.get("date") is None:
                        d["date"] = d["#text"]
                    try:
                        self._dates.append(
                            Date(
                                d["date"],
                                d.get("@dateType"),
                                d.get("@dateInformation")
                            )
                        )
                    except ValueError as ve:
                        pass
        return self._dates

    @property
    def type(self):
        if self.should_be_parsed("resourceType"):
            resourceTypeGeneral = self.md["resourceType"].get("@resourceTypeGeneral")
            if resourceTypeGeneral is not None:
                self._resourceType = resourceTypeGeneral
        return self._resourceType

    @property
    def relatedResources(self):
        if self.should_be_parsed("relatedIdentifiers"):
                ris = self.md["relatedIdentifiers"].get("relatedIdentifier")
                if isinstance(ris, OrderedDict):
                    ris = [ris]
                for ri in ris:
                    self._relatedIdentifiers.append(
                        RelatedResource(
                            ri.get("relatedIdentifier", ri.get("#text")),
                            ri.get("@relatedIdentifierType"),
                            ri.get("@relationType"),
                            ri.get("@schemeURI"),
                            ri.get("@relatedMetadataScheme")
                        )
                    )
        return self._relatedIdentifiers

    def should_be_parsed(self, field):
        # check if the field has already been parsed
        if getattr(self, "_" + field):
            return False
        # check whether the field can be parsed
        if field in self.md.keys() and self.md.get(field) is not None:
            return True
        return False

def create_personOrInstitution_object_from_OrderedDict(p):
    """ creates a Person or an Instiution from a parsed p (p can be almost
        everything

    """
    nameField = p.get("creatorName", p.get("contributorName", ""))
    # None can also come from the first get call! Do not delete!
    if nameField is None:
        nameField = ""
    if isinstance(nameField, OrderedDict):
        if nameField.get("@nameType", None) == "Organizational":
            inst = PersonOrInstitution(nameField["#text"], False)
            inst.type = p.get("@contributorType")
            return inst
        # after this p is considered to be a person
        else:
            name = nameField.get("#text",
                 nameField.get("creatorName",
                     nameField.get("contributorName")
                  )
            )
    else:
        name = nameField

    po = Person(name)
    affiliations = p.get("affiliation")
    if isinstance(affiliations, str):
        affiliations = [affiliations]
    po.affiliations = affiliations
    po.type = p.get("@contributorType")

    # always override the "calculated" name parts with the "specified" ones
    po.familyName = p.get("familyName", po.familyName)
    po.givenName = p.get("givenName", po.givenName)
    if isinstance(p.get("nameIdentifier"), OrderedDict):
        p["nameIdentifier"] = [p["nameIdentifier"]]

    for ni in p.get("nameIdentifier", []):
        if isinstance(ni, OrderedDict):
            if isinstance(ni.get("nameIdentifier", None), str):
                ni["#text"] = ni["nameIdentifier"]
            if re.match("^orcid$", ni.get("@nameIdentifierScheme", ""), re.IGNORECASE) \
               or ni.get("@schemeURI", "").startswith("https://orcid.org"):
                po.orcid = ni["#text"]
    return po
