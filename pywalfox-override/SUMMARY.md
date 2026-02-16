# Pywalfox Override - Complete Summary

## What Was Done

### 1. **Softer Color Transformation** ✅
- **Location**: `pywalfox_overrides/fetcher.py`
- **Changes**:
  - Saturation reduction increased from 50% to **65%** (`SOFTEN_SATURATION_FACTOR = 0.65`)
  - Contrast push increased from 12% to **18%** (`CONTRAST_PUSH = 0.18`)
  - All colors are softened (reduced saturation) before contrast adjustment
  - Dark themes: backgrounds darkened, foregrounds brightened
  - Light themes: backgrounds lightened, foregrounds darkened

### 2. **Pywal Cache Write-Back** ✅
- **Location**: `pywalfox_overrides/fetcher.py` → `write_transformed_colors_back()`
- **What it does**: Writes transformed colors back to `~/.cache/wal/colors.json`
- **Why**: So apps like Cursor/Ghostty that read directly from pywal's cache get the softer colors
- **Safety**: Creates a backup (`colors.json.bak`) before overwriting

### 3. **Wofi Theme Integration** ✅
- **Location**: `pywalfox_overrides/wofi.py`
- **What it does**: Writes `~/.config/wofi/style.css` with colors inlined (no @import)
- **Fix**: Removed duplicate color definitions; template cleaning improved
- **Template**: Reads from `DOTFILES/wofi/style.css` or fallback path

### 4. **Waybar Theme Integration** ✅
- **Location**: `pywalfox_overrides/waybar.py`
- **What it does**: Writes `~/.config/waybar/colors.css` with pywal-derived variables
- **Variables**: `background`, `on_background`, `primary`, `on_primary`, `outline_variant`, etc.

### 5. **Dunst Theme Integration** ✅
- **Location**: `pywalfox_overrides/dunst.py`
- **What it does**: Generates `~/.config/dunst/dunstrc` from template with pywal colors
- **Template**: `dunst/dunstrc.template` (with `{{PYWAL_*}}` placeholders)
- **Auto-reload**: Runs `dunstctl reload` after writing

## File Structure

```
arch-dotfiles/
├── pywalfox-override/
│   ├── pywalfox_overrides/
│   │   ├── __init__.py          # Patches system pywalfox
│   │   ├── fetcher.py           # Color transformation + write-back
│   │   ├── wofi.py              # Wofi theme writer
│   │   ├── waybar.py            # Waybar theme writer
│   │   └── dunst.py             # Dunst theme writer
│   ├── run_pywalfox.py          # Main entry point
│   ├── run-pywalfox.sh          # Shell wrapper
│   └── README.md                # Usage docs
├── dunst/
│   └── dunstrc.template         # Dunst template with placeholders
└── wofi/
    └── style.css                # Wofi style template
```

## Current Status & Verification

### ✅ Working
1. **Color transformation**: Softer (65% saturation reduction), better contrast (18% push)
2. **Pywal cache**: Transformed colors written back to `~/.cache/wal/colors.json`
3. **Wofi**: `~/.config/wofi/style.css` generated with inlined colors
4. **Waybar**: `~/.config/waybar/colors.css` generated
5. **Dunst**: `~/.config/dunst/dunstrc` generated from template

### ⚠️ Requires Manual Steps

1. **Firefox daemon** (if you want Firefox to use the override):
   - Edit `~/.mozilla/native-messaging-hosts/pywalfox.json`
   - Set `"path"` to absolute path of `run-pywalfox.sh`
   - Restart Firefox

2. **Waybar**: Restart after update (colors don't hot-reload)
   ```bash
   killall waybar; waybar &
   ```

3. **Dunst template**: Ensure `~/.config/dunst/dunstrc.template` exists
   - Either symlink from dotfiles: `ln -s ~/workspace/arch-dotfiles/dunst/dunstrc.template ~/.config/dunst/dunstrc.template`
   - Or set `DOTFILES` env var: `export DOTFILES=/home/johnny/workspace/arch-dotfiles`

4. **Cursor/Ghostty**: Should now read softer colors from `~/.cache/wal/colors.json`
   - If still too harsh, increase `SOFTEN_SATURATION_FACTOR` in `fetcher.py` (try 0.75)

## Usage

### After running `wal`:
```bash
DOTFILES=/home/johnny/workspace/arch-dotfiles \
  ~/workspace/arch-dotfiles/pywalfox-override/run-pywalfox.sh update
```

Or if `DOTFILES` is set in your shell:
```bash
~/workspace/arch-dotfiles/pywalfox-override/run-pywalfox.sh update
```

### What happens:
1. Reads `~/.cache/wal/colors.json`
2. Transforms colors (softer + contrast)
3. Writes transformed colors back to pywal cache
4. Generates wofi style
5. Generates waybar colors
6. Generates dunst config + reloads dunst

## Tunables

Edit `pywalfox_overrides/fetcher.py`:

- **`SOFTEN_SATURATION_FACTOR`** (currently `0.65`):
  - `0.0` = original saturation
  - `0.5` = moderate softening
  - `0.65` = current (softer)
  - `0.75` = very soft
  - `1.0` = fully desaturated (grayscale)

- **`CONTRAST_PUSH`** (currently `0.18`):
  - `0.0` = no contrast adjustment
  - `0.12` = subtle
  - `0.18` = current (noticeable)
  - `0.25` = strong contrast

- **`DARK_THEME_LUMINANCE`** (currently `0.4`):
  - Threshold for detecting dark vs light themes
  - Lower = more themes treated as dark

## Troubleshooting

### Wofi still transparent/white text
- Check `~/.config/wofi/style.css` exists and has `@define-color` blocks at top
- Verify no symlink: `ls -la ~/.config/wofi/style.css` (should be regular file, not symlink)
- Restart wofi/your WM

### Cursor still too harsh
- Verify transformed colors in cache: `cat ~/.cache/wal/colors.json | grep color0`
- Should see darker/softer colors than original pywal output
- Increase `SOFTEN_SATURATION_FACTOR` to `0.75` or higher
- Restart Cursor after running update

### Waybar not updating
- Colors don't hot-reload - restart waybar: `killall waybar; waybar &`
- Check `~/.config/waybar/colors.css` exists and has recent timestamp

### Dunst not updating
- Check template exists: `ls ~/.config/dunst/dunstrc.template`
- Set `DOTFILES` env var or `DUNST_TEMPLATE` path
- Verify `~/.config/dunst/dunstrc` was generated
- Check dunst logs: `dunstctl history`

## Notes

- The override patches the system pywalfox package at runtime (no system files modified)
- Transformed colors are written back to pywal's cache so all apps benefit
- Original pywal colors are backed up to `colors.json.bak` (first time only)
- All theme files are generated, not symlinked (so they can be overwritten)
