"""Latin-script album and track titles from MusicBrainz pseudo-releases.

Many releases with non-Latin titles have pseudo-releases on MusicBrainz that
give the tracklist in Latin script: either a translation (e.g. English,
"Dream of Glass") or a transliteration (romaji, "Glass no Yume"). These are
far better than automatic romanization, which cannot know how a title is
meant to be read.

The `romaji` plugin (beetsplug/romaji.py) looks them up and stores the chosen
titles in the beets database, as the flexible attributes `album_transl`
(albums) and `title_transl` (items), the same names the mbpseudo plugin uses.
ctrpaths uses them in place of non-Latin titles.

Which pseudo-release wins is configurable:

    romaji:
      languages: [eng]       # translation languages, most preferred first
      prefer: translation    # or: transliteration

A pseudo-release counts as a transliteration when its language is that of the
original release (or unknown), and as a translation when its language is one
of `languages`. Pseudo-releases in other languages are ignored. Each title is
taken from the most preferred pseudo-release that has a Latin form of it.
"""

from .aliases import is_latin, mb_get

TRANSLATION = 'translation'
TRANSLITERATION = 'transliteration'


def candidates(release, languages, prefer=TRANSLATION):
    """List a release's Latin-script pseudo-releases, most preferred first.

    `release` is MusicBrainz release data including release relations.
    Returns (kind, language, mbid) tuples.
    """
    original = (release.get('text-representation') or {}).get('language')
    found = []
    for rel in release.get('relations', []):
        if (rel.get('type') != 'transl-tracklisting'
                or rel.get('direction') != 'forward'
                or 'release' not in rel):
            continue
        pseudo = rel['release']
        rep = pseudo.get('text-representation') or {}
        if rep.get('script') != 'Latn':
            continue
        language = rep.get('language')
        if language in languages:
            kind, rank = TRANSLATION, languages.index(language)
        elif language is None or original is None or language == original:
            kind, rank = TRANSLITERATION, 0
        else:
            continue
        found.append((kind != prefer, rank, kind, language, pseudo['id']))
    found.sort()
    return [(kind, language, mbid) for _, _, kind, language, mbid in found]


def _tracks(release):
    """Map each track of a release to its title, by ID and by position."""
    by_id, by_position = {}, {}
    for medium in release.get('media', []):
        for track in medium.get('tracks', []):
            by_id[track['id']] = track['title']
            by_position[(medium.get('position'), track.get('position'))] = (
                track['title'])
    return by_id, by_position


def lookup(mbid, languages, prefer=TRANSLATION):
    """Find Latin titles for a release from its pseudo-releases.

    Returns None if the release has no suitable pseudo-release, or a dict:

    - `release`, `kind`, `language`: the most preferred pseudo-release.
    - `album`: the Latin album title, or None.
    - `tracks`: Latin titles keyed by the original release's track IDs.
    - `positions`: the same, keyed by (disc, track) number.
    """
    release = mb_get('release', mbid, inc='release-rels recordings')
    choices = candidates(release, languages, prefer)
    if not choices:
        return None

    official_ids = {
        (medium.get('position'), track.get('position')): track['id']
        for medium in release.get('media', [])
        for track in medium.get('tracks', [])
    }
    album = None
    positions = {}
    for _, _, pseudo_id in choices:
        pseudo = mb_get('release', pseudo_id, inc='recordings')
        if album is None and is_latin(pseudo.get('title') or ''):
            album = pseudo['title']
        _, titles = _tracks(pseudo)
        for position, title in titles.items():
            if position not in positions and title and is_latin(title):
                positions[position] = title
        if album and len(positions) >= len(official_ids):
            break  # Everything found; skip less preferred pseudo-releases.

    kind, language, pseudo_id = choices[0]
    return {
        'release': pseudo_id,
        'kind': kind,
        'language': language,
        'album': album,
        'tracks': {official_ids[pos]: title for pos, title in positions.items()
                   if pos in official_ids},
        'positions': positions,
    }


def track_title(result, item):
    """The Latin title for an item from a lookup() result, or None."""
    trackid = item.get('mb_releasetrackid')
    if trackid and trackid in result['tracks']:
        return result['tracks'][trackid]
    return result['positions'].get((item.get('disc') or 1, item.get('track')))
