# Beets-Flask Container

This document describes how beets-flask is made to work in tandem with this beets configuration.

## How beets-flask Works

**Container Architecture:**
- Image: `pspitzner/beets-flask:stable` (Python 3.11 on Alpine)
- Container runs as user `beetle` (UID/GID mapped to 1000)
- Mounted volumes:
  - `~/.config/beets/` → `/config/beets/` (beets library config)
  - `~/.config/beets-flask/` → `/config/beets-flask/` (flask app config)
  - Music directories

**Plugin Installation Mechanism:**
Beets-flask provides a user-extensible plugin system via startup scripts:
1. **startup.sh**: Shell script in `/config/` or `/config/beets-flask/` runs as root during container startup
2. **requirements.txt**: Python dependencies in `/config/` or `/config/beets-flask/` auto-installed via pip

Both are processed by `entrypoint_user_scripts.sh` before the main application starts.

**Beets Plugin Discovery:**
- Uses standard beets plugin loading (`load_plugins()`)
- Respects `pluginpath` in config, but those paths must be accessible inside container
- Built-in plugins come from the pre-installed `beets==2.5.1` package

**How plugins work inside the container:**
- Standard beets plugins come pre-installed with the `beets` package in the container
- Custom plugins need to be installed separately using the startup script mechanism
- To make custom modules available inside the container, use the provided extension mechanisms

## Installation Approach

**Strategy:**
1. Mount `~/code/music` into the container at the same path
   - Must mount read-write to avoid `error: [Errno 30] Read-only file system`
     during `running egg_info` step of `pip install -e`
2. Use `startup.sh` to install needed editable-from-source packages from the mounted directory
3. Use `requirements.txt` for external PyPI dependencies

**Why This Approach:**
- ✅ Single source of truth: all beets config code in one place
- ✅ Changes to source packages are immediately available (no copy/sync needed)
- ✅ Can install other local packages (plugins, utilities) from same location
- ✅ Uses built-in beets-flask extension mechanisms (startup.sh, requirements.txt)
- ✅ Self-healing: reinstalls on every container restart
- ✅ Clean separation: external deps in requirements.txt, local packages in startup.sh
- ✅ Mirrors host beets setup closely

**Why mount at the same path (`~/code/music`):**
- Keeps paths consistent between host and container
- Reduces confusion when debugging
- Makes it easy to run the same commands in both environments
- All beets-related code accessible in one place
- Note: `~` inside the container is `/home/beetle`

**Trade-offs:**
- Requires modifying `go` to add needed volume mount (minimal change)
- Container becomes dependent on this directory existing (acceptable for personal setup)

**About ~/.whatlastgenre:**
The whatlastgenre plugin hardcodes `~/.whatlastgenre` for config and cache (lines 675, 40 in whatlastgenre.py). We mount it read-write since the plugin needs to:
- Read configuration from `~/.whatlastgenre/config`
- Write cache to `~/.whatlastgenre/reqcache`
- Store discogs tokens if needed

**Why `:ro` on code mount:**
- Container doesn't need write access to source code repositories
- Prevents accidental modifications from inside container
- Beets writes to `/config/beets/library.db` etc., which is fine (separate mount)

**Note:**
- imagemagick and ffmpeg are already in the beets-flask container (Dockerfile lines 33, 39)
- Flask and other web dependencies already in beets-flask container

**What gets installed (all as editable `-e` installs):**
1. **beets[discogs,embedart,fetchart,lyrics,web]** (required) - Main beets from local source with extras
2. **ctrpaths** - Custom path formatting module
3. **beets-ibroadcast** - For uploading music to iBroadcast
4. **whatlastgenre** - For the wlg plugin
5. **beets-artistcountry** - Currently disabled, but ready if/when fixed

**Why editable installs (`-e`):**
- Changes to local code reflected immediately (just restart container)
- Matches the host setup exactly
- No need to reinstall after code changes

## How-Tos

### Restart Container

```bash
docker stop beets-flask
docker rm beets-flask
cd ~/code/music/beets-config/beets-flask
./go
```

**Note:** The command to enter a running container is `docker exec -it beets-flask sh`

### Verify Installation

```bash
# Check startup logs
docker logs beets-flask | grep -A2 "Installing ctrpaths"

# Expected output:
# Installing ctrpaths module from /config/beets-flask/ctrpaths
# ✓ ctrpaths installed successfully

# Verify ctrpaths is importable
docker exec beets-flask python -c "import ctrpaths; print('✓ ctrpaths works')"

# Verify discogs_client is installed
docker exec beets-flask python -c "import discogs_client; print('✓ discogs_client works')"

# Test beets config loads without errors
docker exec beets-flask beet config | head -20
```

## Future Maintenance

**When updating ctrpaths code:**

Since `~/code/music/beets-config` is mounted, changes are immediately visible inside the container.
However, Python modules are cached, so to reload, the container must be restarted:

```bash
# Edit ctrpaths locally
vim ~/code/music/beets-config/ctrpaths/__init__.py

# Restart container to reinstall (startup.sh runs automatically)
docker restart beets-flask

# Verify
docker exec beets-flask python -c "import ctrpaths; print('✓ Updated')"
```

## Results

**Features of this approach:**
- **Single mount point** for all music-related code (beets, plugins, beets-config)
- **Consistent paths** between host and container
- Changes to ctrpaths or plugins reflected immediately (just restart container)
- Mirrors the host beets environment as closely as possible
- Easy to add more custom packages in the future

**Benefits of this unified approach:**
- All beets code (main repo, plugins, config) is accessible at the same paths
- startup.sh closely mirrors the host system's existing setup.sh workflow
- No confusion about which directory contains what
- Container environment matches host environment structurally
