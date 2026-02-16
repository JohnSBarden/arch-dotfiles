"""
Pywalfox fetcher with softer color transformation and better contrast.
Transforms pywal colors: reduced saturation (softer) and improved
foreground/background contrast (darker backgrounds, brighter foregrounds
for dark themes, and vice versa for light).
"""
import json
import logging
import os
import colorsys

HOME_PATH = os.path.expanduser('~')
XDG_CACHE_DIR = os.getenv('XDG_CACHE_HOME', os.path.join(HOME_PATH, '.cache'))
PYWAL_COLORS_PATH = os.path.join(XDG_CACHE_DIR, 'wal', 'colors.json')

# Softness: 0 = original saturation, 1 = fully gray (higher = softer)
SOFTEN_SATURATION_FACTOR = 0.65
# Contrast: how much to push bg/fg (0 = none, ~0.15 = noticeable)
CONTRAST_PUSH = 0.18
# Luminance threshold to treat theme as dark
DARK_THEME_LUMINANCE = 0.4


def _hex_to_rgb(hex_str):
    """Convert #rrggbb to (r, g, b) in 0-1."""
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) / 255.0 for i in (0, 2, 4))


def _rgb_to_hex(r, g, b):
    """Convert (r,g,b) in 0-1 to #rrggbb."""
    return '#{:02x}{:02x}{:02x}'.format(
        int(round(max(0, min(1, r)) * 255)),
        int(round(max(0, min(1, g)) * 255)),
        int(round(max(0, min(1, b)) * 255)),
    )


def _relative_luminance(r, g, b):
    """Relative luminance (0 = black, 1 = white)."""
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _rgb_to_hsl(r, g, b):
    """Convert RGB 0-1 to H, S, L in 0-1."""
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return (h, s, l)


def _hsl_to_rgb(h, s, l):
    """Convert H, S, L in 0-1 to RGB 0-1."""
    return colorsys.hls_to_rgb(h, l, s)


def _soften_color(hex_str, factor=SOFTEN_SATURATION_FACTOR):
    """Reduce saturation for a softer look."""
    r, g, b = _hex_to_rgb(hex_str)
    h, s, l = _rgb_to_hsl(r, g, b)
    s = s * (1 - factor)
    r, g, b = _hsl_to_rgb(h, s, l)
    return _rgb_to_hex(r, g, b)


def _shift_luminance(hex_str, amount):
    """Shift luminance; amount > 0 lightens, < 0 darkens (typical range ±0.15)."""
    r, g, b = _hex_to_rgb(hex_str)
    h, s, l = _rgb_to_hsl(r, g, b)
    l = max(0, min(1, l + amount))
    r, g, b = _hsl_to_rgb(h, s, l)
    return _rgb_to_hex(r, g, b)


def _transform_palette(colors_dict, special_dict, is_dark):
    """Apply soften and contrast to color dict and special dict (in place)."""
    push = CONTRAST_PUSH
    if not is_dark:
        push = -push

    # Soften all
    for key in list(colors_dict.keys()):
        colors_dict[key] = _soften_color(colors_dict[key])
    if special_dict:
        for key in list(special_dict.keys()):
            special_dict[key] = _soften_color(special_dict[key])

    # Contrast: dark theme -> darker bg, brighter fg; light theme -> lighter bg, darker fg
    if is_dark:
        colors_dict['color0'] = _shift_luminance(colors_dict['color0'], -push)
        colors_dict['color8'] = _shift_luminance(colors_dict['color8'], -push * 0.7)
        colors_dict['color7'] = _shift_luminance(colors_dict['color7'], push)
        colors_dict['color15'] = _shift_luminance(colors_dict['color15'], push)
        if special_dict:
            special_dict['background'] = _shift_luminance(special_dict['background'], -push)
            special_dict['foreground'] = _shift_luminance(special_dict['foreground'], push)
    else:
        colors_dict['color0'] = _shift_luminance(colors_dict['color0'], push)
        colors_dict['color8'] = _shift_luminance(colors_dict['color8'], push * 0.7)
        colors_dict['color7'] = _shift_luminance(colors_dict['color7'], -push)
        colors_dict['color15'] = _shift_luminance(colors_dict['color15'], -push)
        if special_dict:
            special_dict['background'] = _shift_luminance(special_dict['background'], push)
            special_dict['foreground'] = _shift_luminance(special_dict['foreground'], -push)


def get_pywal_colors():
    """
    Fetches the Pywal colors from the cache file, applies softer tones and
    better contrast, then returns the transformed palette.

    :return: (success, {colors, wallpaper, special} or None, error_message)
    """
    try:
        with open(PYWAL_COLORS_PATH, 'r') as f:
            pywal_data = json.load(f)
    except (IOError, ValueError) as e:
        error_message = 'Could not read colors from: %s (%s)' % (PYWAL_COLORS_PATH, e)
        logging.error(error_message)
        return (False, None, error_message)

    if 'colors' not in pywal_data:
        error_message = '%s does not contain any color values' % PYWAL_COLORS_PATH
        logging.error(error_message)
        return (False, None, error_message)

    if 'wallpaper' not in pywal_data:
        error_message = '%s does not contain a wallpaper path' % PYWAL_COLORS_PATH
        logging.error(error_message)
        return (False, None, error_message)

    colors_dict = dict(pywal_data['colors'])
    if len(colors_dict) < 16:
        error_message = '%s containing the generated Pywal colors is invalid' % PYWAL_COLORS_PATH
        logging.error(error_message)
        return (False, None, error_message)

    special_dict = dict(pywal_data.get('special', {})) if pywal_data.get('special') else None
    if not special_dict and 'color0' in colors_dict:
        special_dict = {
            'background': colors_dict['color0'],
            'foreground': colors_dict['color7'],
            'cursor': colors_dict.get('color7', colors_dict['color15']),
        }

    bg_hex = special_dict.get('background', colors_dict['color0']) if special_dict else colors_dict['color0']
    is_dark = _relative_luminance(*_hex_to_rgb(bg_hex)) < DARK_THEME_LUMINANCE

    _transform_palette(colors_dict, special_dict, is_dark)

    colors = [colors_dict['color%i' % i] for i in range(16)]
    wallpaper = pywal_data['wallpaper']

    result = {
        'colors': colors,
        'wallpaper': wallpaper,
        'special': special_dict,
    }
    logging.debug('Successfully fetched and transformed Pywal colors')
    return (True, result, None)


def write_transformed_colors_back(pywal_data):
    """
    Write transformed colors back to pywal's colors.json so other apps
    (like Cursor/Ghostty) get the softer colors too.
    Creates a backup first.
    """
    if not pywal_data:
        return
    try:
        # Backup original
        backup_path = PYWAL_COLORS_PATH + '.bak'
        if os.path.exists(PYWAL_COLORS_PATH) and not os.path.exists(backup_path):
            import shutil
            shutil.copy2(PYWAL_COLORS_PATH, backup_path)
        
        # Read original to preserve structure (checksum, alpha, etc.)
        with open(PYWAL_COLORS_PATH, 'r') as f:
            original = json.load(f)
        
        # Update with transformed colors
        original['colors'] = {f'color{i}': pywal_data['colors'][i] for i in range(16)}
        if pywal_data.get('special'):
            original['special'] = pywal_data['special']
        
        # Write back
        with open(PYWAL_COLORS_PATH, 'w') as f:
            json.dump(original, f, indent=4)
        logging.debug('Wrote transformed colors back to pywal cache')
    except Exception as e:
        logging.warning('Could not write transformed colors back: %s', e)
