################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains all code related to data (as a component of RDPs)
#
################################################################################
import csv
import re
import requests
import tempfile
from mimetypes import guess_type
from textract import process
from textract.exceptions import ExtensionNotSupported

from rdp.util import LazyFile

class Data(object):
    """ Base class and interface for Data as components of RDPs

    Methods
    -------
    download() -> None
        Downloads the data item (will be removed on object deletion)
    """
    def __init__(self):
        self.static = True

    @property
    def text(self):
        """ Returns the data as text
        """
        raise NotImplementedError("Must be implemented by subclass")

################################################################################
# FILE-BASED DATA (INTERFACE + FACTORY)
################################################################################
class FileData(Data):
    """ Base class and fall back for Data based on files
    """
    def __init__(self, lazyFile):
        Data.__init__(self)
        self.file = lazyFile
        (self.type, self.encoding) = guess_type(self.file.source)

    @property
    def text(self):
        try:
            return re.sub(r"([A-Z]{1})\s+([A-Z]{5,})",
                               r"\1\2",
                               process(self.file.loc).decode("utf-8")
                              )
        except ExtensionNotSupported:
            # textextract does not support this ending, so we consider it a textfile
            try:
                with open(self.file.loc, "r") as f:
                    return f.read()
            except Exception:
                return None

class FileDataFactory(object):
    """ Factory for FileData

    Methods
    -------
    create(lazyFile: LazyFile) -> FileData
        Factory method returning a FileData object appropriate for the source
    """
    def create(lazyFile: LazyFile) -> FileData:
        """ Creats a Data object appropriate for the specified source

        Parameters
        ----------
        source: str
            URI indicating where to find the data item

        Returns
        -------
        Data: The created Data object
        """

        (ftype, encoding) = guess_type(lazyFile.source)
        if ftype == "text/csv":
            return CSVData(lazyFile)
        return FileData(lazyFile)

################################################################################
# SPECIFIC FILE-BASED DATA IMPLEMENTATIONS
################################################################################
class CSVData(FileData):
    """ Comma-separated Data object

    Attributes
    ----------
    header: dict
        List of column names of the csv (first row)
    rows: list of dicts
        List of key-value pairs for each row, keys are column headers
    """
    def __init__(self, lazyFile):
        FileData.__init__(self, lazyFile)
        self._header = []
        self._rows = []

    def _read_csv(self):
        if len(self._header) == 0:
            with open(self.file.loc, "r") as f:
                reader = csv.reader(f, skipinitialspace=True)
                self._header = next(reader)
                self._rows = [dict(zip(self.header, row)) for row in reader]

    @property
    def header(self):
        self._read_csv()
        return self._header

    @property
    def rows(self):
        self._read_csv()
        return self._rows
