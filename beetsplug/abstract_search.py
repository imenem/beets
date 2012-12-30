"""Abstract plugin for new search
service support for the autotagger.
"""
import logging

from os.path import dirname, basename

from beets.plugins import BeetsPlugin
from beets.autotag import match

log = logging.getLogger('beets')

# Plugin structure and autotagging logic.

class AbstractSearchPlugin(BeetsPlugin):
    def __init__(self):
        super(AbstractSearchPlugin, self).__init__()

    def candidates(self, items):
        try:
            artist, album = self._metadata_from_items(items)
            albums = self._search(artist, album)

            if not albums:
                artist, album = self._metadata_from_path(items)
                albums = self._search(artist, album)

            return map(self._album_info, albums)
        except BaseException as e:
            log.error(self.name() + ' search error: ' + str(e))
            return []

    def name(self):
        return self.__class__.__name__

    def _search(self, artist, album):
        log.debug(self.name() + ' search for: ' + artist + ' - ' + album)
        return []

    def _album_info(self, album):
        pass

    def _metadata_from_items(self, items):
        artist, album, artist_consensus = match.current_metadata(items)

        va_likely = ((not artist_consensus) or
                     (artist.lower() in match.VA_ARTISTS) or
                     any(item.comp for item in items))

        if va_likely:
            return u'', album
        else:
            return artist, album

    def _metadata_from_path(self, items):
        item = items[0].record

        artist, album, _ = basename(dirname(item['path'])).replace('_', ' ').split('-', 2)

        va_likely = artist.lower() in match.VA_ARTISTS

        if va_likely:
            return u'', album
        else:
            return artist, album