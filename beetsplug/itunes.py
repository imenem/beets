"""Adds iTunes album search support to the
autotagger. Requires the python-itunes library.
"""
from __future__ import absolute_import

from beetsplug.abstract_search import AbstractSearchPlugin
from beets.autotag import hooks

from itunes import search_album

# Plugin structure and autotagging logic.

class ItunesPlugin(AbstractSearchPlugin):
    def __init__(self):
        super(ItunesPlugin, self).__init__()

    def _search(self, artist, album):
        super(ItunesPlugin, self)._search(artist, album)
        return search_album(artist + ' ' + album, 5)

    def _album_info(self, album):
        return hooks.AlbumInfo(
            album.name,
            None,
            album.artist.name,
            None,
            map(self._track_info, album.get_tracks()),
            albumtype=album.json['collectionType'].lower()
        )

    def _track_info(self, track):
        return hooks.TrackInfo(
            track.name,
            None,
            track.artist.name,
            None,
            track.duration,
            track.number,
            track.json['discNumber']
        )
