# New flexible attributes:
#
# - category: Primary directory override
# - subcategory: Secondary directory override
# - subtitle: disambiguating string after title, in brackets
# - prefix: string at beginning of filename, in brackets
#
# For soundtracks:
# - avmedia: Animation, TV, Video Games, Musicals, Movies
# - franchise: Final Fantasy
#
# For world music:
# - nationality: Japanese
#
# For holiday music:
# - holiday: Halloween

# Naming schemes:
#
# - A Cappella/<artist>/...
# - Anthems/<subcategory>/...
# - Artists/<artist>/...
# - Children/<subcategory>/...
# - Classical/<composer>/...
# - Comedy/<artist>/...
# - Covers/<title>/...
# - Crap/<artist>/...
# - Holidays/<holiday>/...
# - Meditation/<artist>/...
# - Soundtracks/<franchise>/...

import os

from beetsplug.romanize import text

### INLINE FIELDS ###

def topdir(args):
    category = _value('category', args)
    return _translit(category or 'Artists', args)

def subdir(args, singleton=False):
    return _translit(_subdir(args, singleton), args)

def _subdir(args, singleton):
    subcategory = _value('subcategory', args)
    if subcategory: return subcategory

    tdir = topdir(args)

    if tdir == 'Classical':
        composer = _composer(args)
        if not composer: return '[Unknown Composer]'
        if composer.lower() == '[various]': return '[Various Composers]'
        return _name(composer, args)

    if tdir == 'Soundtracks':
        franchise = _value('franchise', args)
        if not franchise: return '[Unknown Franchise]'
        if franchise.lower() == '[various]': return '[Various Franchises]'
        return franchise

    if tdir == 'Covers' or tdir == 'Holidays':
        if singleton:
            title = _latin(args, 'title', 'title_transl')
            return _simpletitle(title) or '[unknown]'
        return '[Various Songs]'

    if singleton:
        artist = _value('artist', args)
        return _name(_simpleartist(artist), args)

    comp = _value('comp', args)
    if comp: return '[Various Artists]'

    albumartist = _value('albumartist', args)
    return _name(_simpleartist(albumartist), args)

def albumdir(args):
    return _translit(_albumdir(args), args)

def _albumdir(args):
    comp = _value('comp', args)
    if comp: return _albumname(args, withartist=False)

    tdir = topdir(args)
    if tdir == 'Classical' or tdir == 'Covers' or tdir == 'Holidays' or tdir == 'Soundtracks':
        return _albumname(args, withartist=True)

    return _albumname(args, withartist=False)

def safeprefix(args):
    prefix =_value('prefix', args)
    return _translit(f'[{prefix}] ', args) if prefix else ''

def safetitle(args):
    title = _latin(args, 'title', 'title_transl') or '[Unknown Title]'
    subtitle = _value('subtitle', args)
    if subtitle:
        title += f' [{subtitle}]'
    else:
        albumtype = _value('albumtype', args)
        if albumtype == 'live':
            title += ' [live]'
    return _translit(title, args)

def safeartist(args):
    return _name(_safeartist(_value('artist', args) or ''), args)

def _safeartist(artist):
    if artist == '(həd) p.e.': return 'Hed PE'
    if artist == '*NSYNC': return 'NSYNC'
    if artist == '? and the Mysterians': return 'Q and the Mysterians'
    if len(artist) > 100:
        # Ensure safe artist string does not exceed 100 characters.
        comma = artist.find(',')
        if comma >= 0 and comma <= 93:
            return artist[:comma] + ' et al.'
        trunc = artist.find(' ')
        if trunc < 0 or trunc > 97:
            trunc = 97
        return artist[:trunc] + '...'
    return artist

def disc_and_track(args):
    disc =_value('disc', args)
    disctotal =_value('disctotal', args) or 1
    track =_value('track', args)
    tracktotal = _album_tracktotal(args) or 2

    if disctotal <= 1:
        return _zeropad(track, tracktotal)

    # Multi-disc: always at least two track digits, e.g. 1-01.
    track_prefix = _zeropad(track, max(tracktotal, 10))
    disc_prefix = _zeropad(disc, disctotal)
    return f'{disc_prefix}-{track_prefix}'

### HELPER FUNCTIONS ###

# Romanization comes from the beets-romanize plugin
# (https://github.com/ctrueden/beets-romanize): overrides from its config,
# Latin artist names and pseudo-release titles from MusicBrainz, readable
# symbols, and Japanese romanization with cutlet.

def _name(s, obj=None):
    # Transliterate a person's or group's name.
    return text.romanize_name(s, obj)

def _translit(s, obj=None):
    return text.romanize(s, obj)

def _latin(obj, key, transl_key):
    # A title, or its Latin form from a MusicBrainz pseudo-release if it is
    # not Latin (unless the overrides make it Latin).
    return text.latin_field(obj, key, transl_key)

def _value(key, obj):
    # obj is normally the beets Item or Album (inline's `db_obj`). Item.get
    # falls back to the item's album, so album-level attributes (e.g. set via
    # `beet modify -a category=...`) are respected when computing item paths.
    # A plain dict also works here.
    return obj.get(key)

def _composer(obj):
    # Albums may carry a legacy `composer` flexible attribute; items (since
    # beets 2.9) only have the multi-valued `composers` field.
    composer = _value('composer', obj)
    if composer: return composer
    composers = _value('composers', obj) or []
    if len(composers) == 1: return composers[0]
    if len(composers) > 1: return '[Various]'
    return None

def _album_tracktotal(obj):
    # Pad track numbers consistently across all discs of an album: with
    # per_disc_numbering, tracktotal is per disc, so a short disc would
    # otherwise get less padding (1-1) than a long one (2-07).
    get_album = getattr(obj, 'get_album', None)
    album = get_album() if get_album else None
    if album:
        totals = [item.tracktotal for item in album.items() if item.tracktotal]
        if totals: return max(totals)
    return _value('tracktotal', obj)

def _zeropad(no, total):
    return str(no).zfill(len(str(total)))

# NB: The singleton field, being a computed field, is not passed to the inline
# plugin. However, it is set to True when an item's album_id is not set; see
# https://discourse.beets.io/t/duplicates-and-singletons/1142/6. Unfortunately,
# the album_id is also not set for albums imported 'as is'. Therefore, we
# cannot rely on it to differentiate between album tracks and singleton tracks.
#def singleton(args):
#    return False if value('album_id', args) else True

def _albumname(args, withartist):
    album = _latin(args, 'album', 'album_transl')
    albumartist = _value('albumartist', args)
    original_year = _value('original_year', args)
    year = original_year or _value('year', args)

    year_part = f'({year}) ' if year else ''
    artist_part = _name(albumartist, args) + ' - ' if albumartist and withartist else ''
    album_part = album if album else '[Unknown Album]'
    return year_part + artist_part + album_part

def _simpletitle(title):
    if title is None: return None
    paren = title.rfind('(')
    if paren < 0: return title
    subtitle = title[paren:].lower()
    if any(word in subtitle for word in ('mix', 'live', 'edit', 'version')):
        title = title[:paren].rstrip()
    return title

def _simpleartist(artist):
    if not artist or artist.lower() == '[unknown]':
        return '[Unknown Artist]'
    safe_artist = _safeartist(artist)
    feat = safe_artist.lower().find(' feat. ')
    if feat >= 0: return safe_artist[:feat]
    feat = safe_artist.lower().find(' featuring ')
    if feat >= 0: return safe_artist[:feat]
    return safe_artist

def _log(message):
    logfile = os.environ.get('CTRPATHS_LOGFILE', None)
    if not logfile: return
    with open(logfile, 'a') as f:
        f.write(f'{message}\n')
