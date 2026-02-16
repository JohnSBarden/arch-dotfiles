#!/usr/bin/env python3
"""
Run pywalfox with dotfiles overrides (softer colors + wofi theme).
Import system pywalfox first, then apply patches, then run main.
"""
import sys
import os

override_dir = os.path.dirname(os.path.abspath(__file__))
# So first "import pywalfox" loads system package, not our pywalfox folder
if override_dir in sys.path:
    sys.path.remove(override_dir)

import pywalfox
# Ensure submodules are loaded (system package has empty __init__)
import pywalfox.fetcher
import pywalfox.daemon
import pywalfox.config
import pywalfox.response
import pywalfox.__main__

sys.path.insert(0, override_dir)
from pywalfox_overrides import apply_patch

apply_patch(pywalfox)

if __name__ == '__main__':
    # When running "update" from CLI, write themes and transformed colors back
    if len(sys.argv) >= 2 and sys.argv[1] == 'update':
        from pywalfox_overrides.fetcher import get_pywal_colors, write_transformed_colors_back
        from pywalfox_overrides.wofi import write_wofi_theme
        from pywalfox_overrides.waybar import write_waybar_theme
        from pywalfox_overrides.dunst import write_dunst_theme
        ok, data, _ = get_pywal_colors()
        if ok and data:
            write_transformed_colors_back(data)
            write_wofi_theme(data)
            write_waybar_theme(data)
            write_dunst_theme(data)
    pywalfox.__main__.main()
