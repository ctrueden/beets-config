#!/bin/sh

# Check prerequisites.
command -v uv >/dev/null 2>&1 || {
  echo "This script requires uv to be installed."
  exit 1
}

command -v convert >/dev/null 2>&1 || {
  echo "ImageMagick not installed. Installing now..."
  sudo apt install imagemagick || exit 2
}

# Clone needed sources.
dir=$(cd "$(dirname "$0")" && pwd)
beets_code="$HOME/code/music"
mkdir -p "$beets_code"
test -d "$beets_code/beets" ||
  git clone git@github.com:beetbox/beets "$beets_code/beets"
test -d "$beets_code/whatlastgenre" ||
  git clone git@github.com:YetAnotherNerd/whatlastgenre "$beets_code/whatlastgenre"
test -d "$beets_code/beets-artistcountry" ||
  git clone git@github.com:agrausem/beets-artistcountry "$beets_code/beets-artistcountry"
test -d "$beets_code/beets-ibroadcast" ||
  git clone git@github.com:ctrueden/beets-ibroadcast "$beets_code/beets-ibroadcast"
test -d "$beets_code/beetle" ||
  git clone https://gitlab.com/maxburon/beetle.git "$beets_code/beetle"

beet --version >/dev/null 2>&1 || {
  uv tool install beets \
    --with beets-usertag \
    --with mutagen \
    --with requests \
    --with packaging \
    --with rauth \
    --with-editable "$beets_code/beets[discogs,embedart,fetchart,lyrics,web]" \
    --with-editable "$beets_code/beets-config" \
    --with-editable "$beets_code/beets-artistcountry" \
    --with-editable "$beets_code/beets-ibroadcast" \
    --with-editable "$beets_code/whatlastgenre" \
    --reinstall
}

# Set up beets config directory.
beets_config=$HOME/.config/beets
test -d "$beets_config" ||
  ln -sv "$dir/config" "$beets_config"

# Set up whatlastgenre config directory.
if [ ! -f ~/.whatlastgenre/config ]; then
  mkdir -p ~/.whatlastgenre
  cat > ~/.whatlastgenre/config <<EOF
[wlg]
sources = discogs, lastfm
whitelist = 
tagsfile = 
id3v23sep = 

[genres]
love = 
hate = alternative, electronic, indie, pop, rock

[scores]
artist = 1.33
various = 0.66
splitup = 0.33
minimum = 0.10
src_discogs = 1.00
src_lastfm = 0.66
src_mbrainz = 0.66
src_redacted = 1.50

[discogs]
token = 
secret = 

[redacted]
username = 
password = 
session = 
EOF
fi

# Verify that everything is working.
# Note: beet returns exit code 0 even when plugins fail to load, so we check explicitly.
beets_info=$(beet --version 2>&1)
echo "$beets_info" | grep -q 'beets version' || {
  echo "Beets installation failed!"
  exit 3
}
echo "$beets_info" | grep -q Traceback && {
  echo "Beets configuration is broken:"
  echo "$beets_info"
  exit 4
} || true

echo "Beets setup appears successful!"
beet --version
