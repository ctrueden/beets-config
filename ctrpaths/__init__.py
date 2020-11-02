# New album flexible attributes:
#
# - category: Primary directory
# - subcategory: Secondary directory override
#
# - avmedia: Animation, TV, Video Games, Musicals, Movies (from folder name)
# - nationality: (from World)
# - franchise: Final Fantasy

# Naming schemes:
#
# - A Cappella/<artist>/...
# - Artists/<artist>/...
# - Comedy/<artist>/...
# - Crap/<artist>/...
#
# - Anthems/<subcategory>/...
# - Children/<subcategory>/...
# - Classical/<composer>/...
# - Covers/<title>/...
# - Soundtracks/<franchise>/...

def value(key, args):
    return args[key] if key in args else None

# NB: The singleton field, being a computed field, is not passed to the inline
# plugin. However, it is set to True when an item's album_id is not set; see
# https://discourse.beets.io/t/duplicates-and-singletons/1142/6. Unfortunately,
# the album_id is also not set for albums imported 'as is'. Therefore, we
# cannot rely on it to differentiate between album tracks and singleton tracks.
#def singleton(args):
#    return False if value('album_id', args) else True

def artistname(artist):
    return artist if artist and artist.lower() != '[unknown]' else '[Unknown Artist]'

def albumname(args, withartist):
    album = value('album', args)
    albumartist = value('albumartist', args)
    original_year = value('original_year', args)
    year = original_year or value('year', args)

    year_part = f'({year}) ' if year else ''
    artist_part = albumartist + ' - ' if albumartist and withartist else ''
    album_part = album if album else '[Unknown Album]'
    return year_part + artist_part + album_part

def simpletitle(title):
    if title is None: return None
    paren = title.rfind('(')
    if paren < 0:
        return title
    subtitle = title[paren:].lower()
    if 'mix' in subtitle or 'live' in subtitle or 'edit' in subtitle or 'version' in subtitle:
        return title[:paren].rstrip()
    return title

def topdir(args):
    category = value('category', args)
    return category or 'Artists'

def subdir(args, singleton=False):
    subcategory = value('subcategory', args)
    if subcategory: return subcategory

    tdir = topdir(args)

    if tdir == 'Classical':
        composer = value('composer', args)
        if not composer: return '[Unknown Composer]'
        if composer.lower() == '[various]': return '[Various Composers]'
        return composer

    if tdir == 'Soundtracks':
        franchise = value('franchise', args)
        if not franchise: return '[Unknown Franchise]'
        if franchise.lower() == '[various]': return '[Various Franchises]'
        return franchise

    if tdir == 'Covers' or tdir == 'Holidays':
        if singleton:
            title = value('title', args)
            return simpletitle(title) or '[unknown]'
        return '[Various Songs]'

    if singleton:
        artist = value('artist', args)
        return artistname(artist)

    comp = value('comp', args)
    if comp: return '[Various Artists]'

    albumartist = value('albumartist', args)
    return artistname(albumartist)

def albumdir(args):
    comp = value('comp', args)
    if comp: return albumname(args, withartist=False)

    tdir = topdir(args)
    if tdir == 'Classical' or tdir == 'Covers' or tdir == 'Holidays' or tdir == 'Soundtracks':
        return albumname(args, withartist=True)

    return albumname(args, withartist=False)

def safetitle(args):
    title = value('title', args) or '[Unknown Title]'
    subtitle = value('subtitle', args)
    if subtitle: title += f' [{subtitle}]'
    return title
