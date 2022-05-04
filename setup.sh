#!/bin/sh
python -c 'import beets' 2>/dev/null || {
  echo "Please activate the beets environment first."
  exit 1
}
dir=$(dirname "$0")
beets_code=$HOME/code/music
test -d "$beets_code/whatlastgenre" || (
  mkdir -p "$beets_code" &&
  cd "$beets_code" &&
  git clone git@github.com:YetAnotherNerd/whatlastgenre &&
  cd whatlastgenre &&
  sed -i 's/\(self.wlg.cache.save()\)/if self.wlg is not None: \1/' plugin/beets/beetsplug/wlg.py &&
  pip install -e .
) &&
beets_config=$HOME/.config/beets
test -d "$beets_config" ||
  ln -s "$dir/config" "$beets_config"
