"""Latin-script artist names from MusicBrainz aliases.

Romanizing a name mechanically often goes wrong: name readings are
irregular (小池令 is Ryo Koike, not "Koike Rei"), and segmentation can fail
(矢井田瞳 is Hitomi Yaida, not "Ya Ida Hitomi"). MusicBrainz knows better:
most artists have an English alias or a Latin-script sort name.

Path computation cannot query MusicBrainz on the fly, so the `romaji` plugin
(beetsplug/romaji.py) fetches Latin names ahead of time into a JSON cache in
the beets config directory, keyed by the original artist credit, and
ctrpaths looks names up there.
"""

import json
import os
import time
import unicodedata

CACHE_FILENAME = 'romaji-names.json'

_MB_URL = 'https://musicbrainz.org/ws/2'
_USER_AGENT = 'beets-config-romaji/1.0 ( https://github.com/ctrueden/beets-config )'
_MB_INTERVAL = 1.1  # seconds between requests; MusicBrainz allows 1/s

_names = None  # credit or name -> Latin name, or None if none is known
_last_request = 0.0


def is_latin(s):
    """Whether every letter of s is Latin script (so needs no romanizing)."""
    # Modifier letters (e.g. the Hawaiian ʻokina in Hoʻaikāne) are fine too.
    return all(
        not ch.isalpha()
        or unicodedata.name(ch, '').startswith('LATIN')
        or unicodedata.category(ch) == 'Lm'
        for ch in s
    )


def _cache_path():
    from beets import config
    return os.path.join(config.config_dir(), CACHE_FILENAME)


def names():
    global _names
    if _names is None:
        try:
            with open(_cache_path(), encoding='utf-8') as f:
                _names = json.load(f).get('names', {})
        except (OSError, ValueError):
            _names = {}
    return _names


def save():
    path = _cache_path()
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump({'names': names()}, f, ensure_ascii=False, indent=1,
                  sort_keys=True)
    os.replace(tmp, path)


def lookup(name):
    """Return the known Latin form of an artist credit or name, or None."""
    return names().get(name) if name else None


def known(name):
    """Whether name has been looked up already (even if nothing was found)."""
    return name in names()


### Fetching ###

def mb_get(entity, mbid, inc='artist-credits aliases', retries=4):
    """Fetch an entity from the MusicBrainz API, respecting its rate limit."""
    import requests
    global _last_request
    for attempt in range(retries + 1):
        wait = _last_request + _MB_INTERVAL - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        _last_request = time.monotonic()
        response = requests.get(
            f'{_MB_URL}/{entity}/{mbid}',
            params={'inc': inc, 'fmt': 'json'},
            headers={'User-Agent': _USER_AGENT},
            timeout=30,
        )
        # MusicBrainz answers 503 when it is overloaded or we are too fast.
        if response.status_code == 503 and attempt < retries:
            time.sleep(2 ** attempt * 5)
            continue
        response.raise_for_status()
        return response.json()


def latin_name(artist):
    """Choose a Latin-script name for a MusicBrainz artist, or None."""
    if is_latin(artist['name']):
        return artist['name']

    aliases = [a for a in artist.get('aliases', []) if is_latin(a['name'])]

    def rank(alias):
        locale = alias.get('locale') or ''
        return (
            locale != 'en',
            not locale.endswith('-Latn'),
            alias.get('type') == 'Search hint',
            not alias.get('primary'),
        )

    if aliases:
        return min(aliases, key=rank)['name']

    # Fall back to the sort name, if Latin: "Yaida, Hitomi" -> "Hitomi Yaida".
    sort_name = artist.get('sort-name') or ''
    if sort_name and is_latin(sort_name):
        last, sep, first = sort_name.partition(', ')
        return f'{first} {last}' if sep else sort_name

    return None


def _known_names(artist):
    return {artist['name'], artist.get('sort-name')} | {
        alias['name'] for alias in artist.get('aliases', [])
    }


def learn(entity, mbid, *credits):
    """Fetch a recording or release, and record Latin names for its artists.

    Returns the number of names learned. Each of `credits` (the artist
    credit strings beets stored, e.g. item.artist) is recorded too, so that
    it is not fetched again even if MusicBrainz knows no Latin form.
    """
    table = names()
    data = mb_get(entity, mbid)
    credit = data.get('artist-credit') or []

    learned = 0
    original, credited, latin = '', '', ''
    for part in credit:
        artist = part['artist']
        join = part.get('joinphrase', '')
        name = latin_name(artist)
        if name and not is_latin(artist['name']):
            table[artist['name']] = name
            learned += 1
        original += artist['name'] + join
        credited += part.get('name', artist['name']) + join
        latin += (name or artist['name']) + join

    # If only some of the artists have Latin names, keep the partly Latin
    # credit; ctrpaths romanizes the rest.
    for key in (original, credited):
        if key and not is_latin(key):
            table[key] = latin if latin != key else None
    # A credit stored by beets may match neither form exactly (e.g. if it was
    # edited, or mixes scripts); substitute the individual artist names.
    for key in credits:
        if key and key not in table:
            if len(credit) == 1 and key in _known_names(credit[0]['artist']):
                # A lone artist, credited under another of its names.
                latin = latin_name(credit[0]['artist']) or key
            else:
                latin = key
                for part in credit:
                    name = latin_name(part['artist'])
                    if name:
                        latin = latin.replace(part['artist']['name'], name)
            table[key] = latin if latin != key else None
    return learned
