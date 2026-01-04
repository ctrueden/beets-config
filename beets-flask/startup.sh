#!/bin/sh

# This script is run by beets-flask inside the Docker container when it first starts up.
# It is used for additional tuning of the container environment before launching beets-flask.

# We install custom beets modules and plugins from the mounted code directory.
# - Runs as root during container startup via entrypoint_user_scripts.sh
# - Adapted from ~/code/music/beets-config/setup.sh

MUSIC_CODE="/home/beetle/code/music"

echo "=== Installing custom beets packages ==="

# Check that the music code directory is mounted.
if [ ! -d "$MUSIC_CODE" ]; then
    echo "✗ ERROR: Music code directory not mounted at $MUSIC_CODE"
    exit 1
fi

# Install needed packages from source in editable mode.
while IFS='|' read -r target pkg; do
  dir=$MUSIC_CODE/${target%\[*}  # Ex: ~/code/music/beets (strips [...] suffix)
  if [ -d "$dir" ]; then
      echo "Installing $pkg from $dir..."
      pip install --no-cache-dir -e "$MUSIC_CODE/$target"
      [ $? -eq 0 ] && echo "✓ $pkg installed" || { echo "✗ $pkg failed"; exit 1; }
  else
      echo "✗ ERROR: $pkg not found at $dir"
      exit 1
  fi
done << 'EOF'
beets[discogs,embedart,fetchart,lyrics,web]|beets
beets-config|ctrpaths
beets-artistcountry|beets-artistcountry
beets-ibroadcast|beets-ibroadcast
whatlastgenre|whatlastgenre
EOF

echo "=== Custom package installation complete ==="
