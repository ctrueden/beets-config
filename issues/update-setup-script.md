The `setup.sh` script tries to set up the beets environment, but it needs updating:

* In particular, the whatlastgenre patching steps are no longer needed, since whatlastgenre has now been patched upstream and in my local `~/code/music/whatlastgenre` folder. I now have a stock working copy off the latest master branch. It is still not installable from PyPI, though, so the local working copy is (AFAIK) still necessary. Unless it would work to `pip install` it directly from a git hash?

* If I switch away from using conda/mamba to uv instead (see also switch-to-uv.md), I might want to include other steps and/or checks in the `setup.sh`, to ensure the beet CLI tool is fully functional including plugins and dependencies.
