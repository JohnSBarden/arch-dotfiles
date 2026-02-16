# Pywalfox override (optional)

**Theme application and softening are now in your wallpaper script**  
(`~/.config/hypr/scripts/wallpaper.py` or `~/dotfiles/hypr/scripts/wallpaper.py`):

- **Desaturation**: Wallpaper is desaturated (default 50%) with ImageMagick *before* pywal runs, so pywal extracts softer colors and all apps (Cursor, wofi, waybar, dunst, etc.) get them.
- **Wofi / Waybar / Dunst**: The script writes their theme files after `wal` and reloads dunst.

Use this override only if you want the **Firefox/Zen Browser** extension to receive pywal colors (run `pywalfox update` from the script or manually). No color transformation or write-back is done here anymore.

## Usage

1. **CLI (one-off update + wofi)**  
   Run the wrapper so wofi and (if daemon is running) Firefox get the theme:
   ```bash
   ./run-pywalfox.sh update
   ```
   Or: `python3 run_pywalfox.py update`

2. **Daemon (Firefox + wofi)**  
   Point the Firefox native messaging host at the launcher so the daemon uses the override:
   - Open `~/.mozilla/native-messaging-hosts/pywalfox.json`.
   - Set `"path"` to the **absolute** path to `run-pywalfox.sh`, e.g.:
     `"/home/johnny/workspace/arch-dotfiles/pywalfox-override/run-pywalfox.sh"`.
   - Restart Firefox.

3. **Wofi**  
   Pywalfox writes **`~/.config/wofi/style.css`** with colors inlined at the top (no @import), so styling works even if the old style was a symlink into the repo. The layout is taken from `DOTFILES/wofi/style.css`; set `DOTFILES` so that template is found.

4. **Waybar**  
   Waybar style already `@import "./colors.css"`. Pywalfox writes that file. Restart waybar to apply (e.g. `killall waybar; waybar &` or restart your WM).

5. **Dunst**  
   Use the template-based setup so dunst gets pywal colors:
   - Symlink the template: `~/.config/dunst/dunstrc.template` → your dotfiles `dunst/dunstrc.template`.
   - Or set `DOTFILES` to your dotfiles root, or `DUNST_TEMPLATE` to the template path.
   - Pywalfox writes `~/.config/dunst/dunstrc` from the template and runs `dunstctl reload`. Do **not** symlink `dunstrc` itself (it is generated).

## Tunables

In `pywalfox/fetcher.py`:

- `SOFTEN_SATURATION_FACTOR` (default `0.65`): Lower = more saturated; higher = softer.
- `CONTRAST_PUSH` (default `0.18`): How much to darken/lighten bg/fg for contrast.
- `DARK_THEME_LUMINANCE` (default `0.4`): Background luminance below this is treated as dark theme.
