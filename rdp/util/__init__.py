import os
import tempfile
from typing import Callable


class Bundle(object):
    """ Fancy dictionary
    """
    def __init__(self):
        self.payload = {}

    def __len__(self):
        return len(self.payload.keys())

    def put(self, itemType, item):
        self.payload[itemType] = item

    def get(self, itemType):
        return self.payload.get(itemType, None)

    def has(self, itemType):
        return itemType in self.payload.keys()

class LazyFile(object):
    """ A lazy file is only downloaded if it its contents are accessed
        (i.e. if its loc property is accessed).
        The downloaded file is deleted when this wrapper class is deleted

        Attributes
        ----------
        loc: str
            Temporary path to which the file is downloaded. This automatically
            happens when loc is accessed for the first time.
    """
    def __init__(self, source: str, download: Callable[[str], bytes]):
        """
        Attributes
        ----------
            source: String identifying source to download file from
            download: Callable accepting a source information and returning bytes
        """

        self.source = source
        self._download = download
        self._loc = None

    def __del__(self):
        self.remove()

    @property
    def loc(self):
        """ Location of file - accessing this attribute lazily downloads the file
        """
        if self._loc is None:
            self.download()
        return self._loc

    def download(self) -> None:
        """ Downloads the file to loc
        """
        (fd, self._loc) = tempfile.mkstemp(suffix=self.source.split("/")[-1])
        os.write(fd, self._download(self.source))
        os.close(fd)

    def remove(self) -> None:
        """ Removes the file stored at loc
        """
        if self._loc is not None:
            os.unlink(self._loc)
