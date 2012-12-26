"""Adds iTunes album search support to the
autotagger. Requires the pyitunes library.
"""
from __future__ import absolute_import

from os.path import dirname, basename
import logging

from beets.plugins import BeetsPlugin
from beets.autotag import hooks

from itunes import search_album

log = logging.getLogger('beets')

# Plugin structure and autotagging logic.

class ItunesPlugin(BeetsPlugin):
    def candidates(self, items):
        item = items[0].record

        albums = search_album(item['artist'] + ' ' + item['album'], 5)

        if not albums:
            artist, album, _ = basename(dirname(item['path'])).replace('_', ' ').split('-', 2)
            albums = search_album(artist + ' ' + album, 5)

        return map(self._album_info, albums)

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
