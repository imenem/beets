"""Adds Discogs album search support to the
autotagger. Requires the discogs-client library.
"""
import logging
import string

from os.path import dirname, basename
from time import strptime

from beets.plugins import BeetsPlugin
from beets.autotag import hooks

import discogs_client
from discogs_client import Artist, Release, Search, DiscogsAPIError

discogs_client.user_agent = 'curl/7.28.0'

log = logging.getLogger('beets')

# Plugin structure and autotagging logic.

class DiscogsPlugin(BeetsPlugin):
    def candidates(self, items):
        item = items[0].record

        try:
            log.debug('Discog search for: ' + item['artist'] + ' - ' + item['album'])
            results = Search(item['artist'] + ' ' + item['album']).results()[0:5]

            if not results:
                artist, album, _ = basename(dirname(item['path'])).replace('_', ' ').split('-', 2)
                log.debug('Discog search for: ' + artist + ' - ' + album)
                results = Search(artist + ' ' + album, 5).results()[0:5]

            albums = filter(lambda result: isinstance(result, Release), results)

            return map(self._album_info, albums)
        except DiscogsAPIError as e:
            message = str(e)
            if not message.startswith('404'):
                log.error('Discogs search error: ' + message)
            return []
        except Exception as e:
            log.error('Discogs search error: ' + str(e))
            return []

    def _album_info(self, album):
        return hooks.AlbumInfo(
            album.title,
            None,
            self._artists_names(album.artists),
            None,
            map(self._track_info, album.tracklist)
        )

    def _track_info(self, track):
        disk_number, position = self._position(track['position'])

        return hooks.TrackInfo(
            track['title'],
            None,
            self._artists_names(track['artists']),
            None,
            self._duration(track['duration']),
            position,
            disk_number
        )

    def _artists_names(self, artists):
        filtered = filter(lambda artist: isinstance(artist, Artist), artists)
        names =  map(lambda artist: artist.name, filtered)

        return ' and '.join(names)

    def _position(self, position):
        try:
            original = position
            """Convert track position from u'1', u'2' or u'A', u'B' to 1, 2 etc"""
            position = position.encode('ascii').lower()         # Convert from unicode to lovercase ascii

            if not len(position):
                return 0, 0

            first    = position[0]

            if string.ascii_lowercase.find(first) != -1:
                number = ord(first) - 96

                if len(position) == 1:
                    replace = '%i'  % number                    # Letter is track number
                else:
                    replace = '%i-' % number                    # Letter is vinyl side

                position = position.replace(first, replace)

            if position.find('-') == -1:
                position = '1-' + position                      # If no disk number, set to 1

            result = map(int, position.split('-'))

            if len(result) == 2:
                return result
            else:
                return 0, 0
        except ValueError:
            return 0, 0

    def _duration(self, duration):
        try:
            duration = strptime(duration.encode('ascii'), '%M:%S')
        except ValueError:
            return 0
        else:
            return duration.tm_min * 60 + duration.tm_sec