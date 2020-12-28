# New flexible attributes:
#
# - category: Primary directory override
# - subcategory: Secondary directory override
# - subtitle: disambiguating string after title, in brackets
#
# For soundtracks:
# - avmedia: Animation, TV, Video Games, Musicals, Movies (from folder name)
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

### INLINE FIELDS ###

def topdir(args):
    category = _value('category', args)
    return category or 'Artists'

def subdir(args, singleton=False):
    subcategory = _value('subcategory', args)
    if subcategory: return subcategory

    tdir = topdir(args)

    if tdir == 'Classical':
        composer = _value('composer', args)
        if not composer: return '[Unknown Composer]'
        if composer.lower() == '[various]': return '[Various Composers]'
        return composer

    if tdir == 'Soundtracks':
        franchise = _value('franchise', args)
        if not franchise: return '[Unknown Franchise]'
        if franchise.lower() == '[various]': return '[Various Franchises]'
        return franchise

    if tdir == 'Covers' or tdir == 'Holidays':
        if singleton:
            title = _value('title', args)
            return _simpletitle(title) or '[unknown]'
        return '[Various Songs]'

    if singleton:
        artist = _value('artist', args)
        return _simpleartist(artist)

    comp = _value('comp', args)
    if comp: return '[Various Artists]'

    albumartist = _value('albumartist', args)
    return _simpleartist(albumartist)

def albumdir(args):
    comp = _value('comp', args)
    if comp: return _albumname(args, withartist=False)

    tdir = topdir(args)
    if tdir == 'Classical' or tdir == 'Covers' or tdir == 'Holidays' or tdir == 'Soundtracks':
        return _albumname(args, withartist=True)

    return _albumname(args, withartist=False)

def safetitle(args):
    title = _value('title', args) or '[Unknown Title]'
    subtitle = _value('subtitle', args)
    if subtitle:
        title += f' [{subtitle}]'
    else:
        albumtype = _value('albumtype', args)
        if albumtype == 'live':
            title += ' [live]'
    return title

def safeartist(artist):
    if artist == '(həd) p.e.': return 'Hed PE'
    if artist == '*NSYNC': return 'NSYNC'
    if artist == '? and the Mysterians': return 'Q and the Mysterians'
    return artist

### HELPER FUNCTIONS ###

def _value(key, args):
    return args[key] if key in args else None

# NB: The singleton field, being a computed field, is not passed to the inline
# plugin. However, it is set to True when an item's album_id is not set; see
# https://discourse.beets.io/t/duplicates-and-singletons/1142/6. Unfortunately,
# the album_id is also not set for albums imported 'as is'. Therefore, we
# cannot rely on it to differentiate between album tracks and singleton tracks.
#def singleton(args):
#    return False if value('album_id', args) else True

def _albumname(args, withartist):
    album = _value('album', args)
    albumartist = _value('albumartist', args)
    original_year = _value('original_year', args)
    year = original_year or _value('year', args)

    year_part = f'({year}) ' if year else ''
    artist_part = albumartist + ' - ' if albumartist and withartist else ''
    album_part = album if album else '[Unknown Album]'
    return year_part + artist_part + album_part

def _simpletitle(title):
    if title is None: return None
    paren = title.rfind('(')
    if paren < 0:
        return title
    subtitle = title[paren:].lower()
    if 'mix' in subtitle or 'live' in subtitle or 'edit' in subtitle or 'version' in subtitle:
        return title[:paren].rstrip()
    return title

def _simpleartist(artist):
    return safeartist(artist) if artist and artist.lower() != '[unknown]' else '[Unknown Artist]'
