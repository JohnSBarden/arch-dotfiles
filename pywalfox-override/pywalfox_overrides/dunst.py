"""
Write dunst config from pywal data using a template so dunst uses the current theme.
Reads a template with placeholders and writes ~/.config/dunst/dunstrc.
Reloads dunst if dunstctl is available.
"""
import os
import logging
import subprocess

HOME = os.path.expanduser('~')
XDG_CONFIG_HOME = os.getenv('XDG_CONFIG_HOME', os.path.join(HOME, '.config'))
DUNST_CONFIG_DIR = os.path.join(XDG_CONFIG_HOME, 'dunst')
DUNSTRC_OUTPUT = os.path.join(DUNST_CONFIG_DIR, 'dunstrc')
# Template path: env DUNST_TEMPLATE, or dunstrc.template next to output, or override default
DUNSTRC_TEMPLATE_DEFAULT = os.path.join(DUNST_CONFIG_DIR, 'dunstrc.template')


def _color_list(pywal_data):
    colors = pywal_data.get('colors')
    if isinstance(colors, dict):
        return [colors.get('color%i' % i, '#000000') for i in range(16)]
    return list(colors) if colors else []


def write_dunst_theme(pywal_data, template_path=None):
    """
    Read dunstrc template (with {{PYWAL_*}} placeholders), substitute
    pywal colors, write ~/.config/dunst/dunstrc, and reload dunst.
    """
    if not pywal_data:
        return
    special = pywal_data.get('special') or {}
    color_list = _color_list(pywal_data)
    if len(color_list) < 8:
        return

    background = special.get('background') or color_list[0]
    foreground = special.get('foreground') or color_list[7]
    frame_color = color_list[4]  # accent as frame
    # Critical: keep a distinct red-ish so critical notifications stand out
    critical_bg = color_list[1] if len(color_list) > 1 else '#93000a'
    critical_fg = color_list[7] if len(color_list) > 7 else '#ffdad6'
    critical_frame = color_list[9] if len(color_list) > 9 else '#ffb4ab'

    template = (
        template_path
        or os.getenv('DUNST_TEMPLATE')
        or (os.path.join(os.getenv('DOTFILES', ''), 'dunst', 'dunstrc.template') if os.getenv('DOTFILES') else None)
        or DUNSTRC_TEMPLATE_DEFAULT
    )
    if not template or not os.path.isfile(template):
        logging.debug('Dunst template not found: %s (set DUNST_TEMPLATE or add dunstrc.template)', template)
        return

    try:
        with open(template, 'r') as f:
            content = f.read()
    except OSError as e:
        logging.warning('Could not read dunst template: %s', e)
        return

    replacements = {
        '{{PYWAL_BACKGROUND}}': background,
        '{{PYWAL_FOREGROUND}}': foreground,
        '{{PYWAL_FRAME}}': frame_color,
        '{{PYWAL_CRITICAL_BG}}': critical_bg,
        '{{PYWAL_CRITICAL_FG}}': critical_fg,
        '{{PYWAL_CRITICAL_FRAME}}': critical_frame,
    }
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)

    try:
        if not os.path.isdir(DUNST_CONFIG_DIR):
            os.makedirs(DUNST_CONFIG_DIR, mode=0o755)
        with open(DUNSTRC_OUTPUT, 'w') as f:
            f.write(content)
        logging.debug('Wrote dunst config to %s', DUNSTRC_OUTPUT)
        _reload_dunst()
    except OSError as e:
        logging.warning('Could not write dunst config: %s', e)


def _reload_dunst():
    """Reload dunst so it picks up the new config."""
    try:
        subprocess.run(['dunstctl', 'reload'], check=False, timeout=2,
                      capture_output=True)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
