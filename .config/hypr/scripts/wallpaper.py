import os
import sys
import re
import argparse
import fcntl
import subprocess
import asyncio
import random as _random
import colorsys
import json
import tempfile

lock_file_path = '/tmp/wallpaper.lock'
settings_file_path = os.path.expanduser('~/dotfiles/.settings/settings.json')

# Desaturate wallpaper before pywal so extracted colors are softer (0=grayscale, 1=no change)
WAL_DESATURATION = 0.5
DOTFILES = os.environ.get("DOTFILES") or os.path.expanduser("~/dotfiles")
XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))


def acquire_lock():
    global lock_file
    lock_file = open(lock_file_path, 'w')
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock_file.write(str(os.getpid()))
        lock_file.flush()
    except IOError:
        print("Another instance of the script is already running.")
        sys.exit(1)


def release_lock():
    fcntl.flock(lock_file, fcntl.LOCK_UN)
    lock_file.close()
    os.remove(lock_file_path)


HYPR_DYNAMIC_COLORS = os.path.expanduser("~/.config/hypr/conf/colors/dynamic.conf")
WAL_DIR = os.path.join(os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache")), "wal")


def _hex_no_hash(hex_str):
    return hex_str.lstrip("#").lower()


def _hex_to_rgb_dec(hex_str):
    h = _hex_no_hash(hex_str)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _load_wal_colors():
    """Load colors from pywal cache: colors.json first, else plain 'colors' file."""
    json_path = os.path.join(WAL_DIR, "colors.json")
    try:
        with open(json_path) as f:
            data = json.load(f)
        special = data.get("special", {})
        colors = data.get("colors", {})
        return special.get("background", colors.get("color0")), special.get("foreground", colors.get("color7")), colors
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    plain_path = os.path.join(WAL_DIR, "colors")
    try:
        with open(plain_path) as f:
            lines = [l.strip().lstrip("#") for l in f if l.strip()]
        if len(lines) >= 8:
            return "#" + lines[0], "#" + lines[7], {f"color{i}": "#" + c for i, c in enumerate(lines[:16])}
    except FileNotFoundError:
        pass
    return None


def _load_wal_data():
    """Load full pywal cache (for theme writers). Returns dict with colors + special or None."""
    json_path = os.path.join(WAL_DIR, "colors.json")
    try:
        with open(json_path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _apply_wofi():
    """Write ~/.config/wofi/style.css from pywal colors."""
    data = _load_wal_data()
    if not data:
        return
    colors = data.get("colors", {})
    if not colors or len(colors) < 9:
        return
    special = data.get("special", {})
    color_list = [colors.get(f"color{i}", "#000000") for i in range(16)]
    bg = special.get("background") or color_list[0]
    fg = special.get("foreground") or color_list[7]
    primary = color_list[4]
    surface = color_list[8]
    # Load template (strip @import and color blocks)
    template_paths = [
        os.path.join(DOTFILES, "wofi", "style.css"),
        os.path.join(os.path.expanduser("~"), "workspace", "arch-dotfiles", "wofi", "style.css"),
    ]
    template = None
    for p in template_paths:
        if os.path.isfile(p):
            try:
                with open(p) as f:
                    t = f.read()
                t = re.sub(r'@import\s+url\s*\([^)]+\)\s*;\s*\n?', '', t)
                t = re.sub(r'/\*[^*]*(?:Generated|Pywal)[^*]*\*/\s*\n?', '', t, flags=re.I)
                t = re.sub(r'@define-color\s+\w+\s+[^;]+;\s*\n+', '', t)
                template = t.strip()
                break
            except OSError:
                continue
    if not template:
        template = "* { font-family: sans-serif; font-size: 14px; }\nwindow { background-color: @background; padding: 10px; }\n#input { color: @primary; background-color: @surface_container; }\n#text { color: @on_background; }\n#entry:selected { background-color: @primary; }\n#entry:selected #text { color: @background; }"
    wofi_dir = os.path.join(XDG_CONFIG_HOME, "wofi")
    os.makedirs(wofi_dir, exist_ok=True)
    style_path = os.path.join(wofi_dir, "style.css")
    block = f"/* Generated from pywal */\n@define-color background {bg};\n@define-color on_background {fg};\n@define-color primary {primary};\n@define-color surface_container {surface};\n\n"
    with open(style_path, "w") as f:
        f.write(block + template)
    print(f":: Wrote {style_path}")


def _apply_waybar():
    """Write ~/.config/waybar/colors.css from pywal colors."""
    data = _load_wal_data()
    if not data:
        return
    colors = data.get("colors", {})
    if len(colors) < 9:
        return
    special = data.get("special", {})
    color_list = [colors.get(f"color{i}", "#000000") for i in range(16)]
    bg = special.get("background") or color_list[0]
    fg = special.get("foreground") or color_list[7]
    primary = color_list[4]
    out_path = os.path.join(XDG_CONFIG_HOME, "waybar", "colors.css")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    lines = [
        "/* Generated from pywal */",
        f"@define-color background {bg};",
        f"@define-color on_background {fg};",
        f"@define-color primary {primary};",
        f"@define-color on_primary {color_list[0]};",
        f"@define-color outline_variant {color_list[8]};",
        f"@define-color surface {bg};",
        f"@define-color surface_container {color_list[8]};",
        f"@define-color waybar_accent {primary};",
        f"@define-color waybar_accent_fg {fg};",
    ]
    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f":: Wrote {out_path}")


def _apply_dunst():
    """Write ~/.config/dunst/dunstrc from template + pywal colors; reload dunst."""
    data = _load_wal_data()
    if not data:
        return
    colors = data.get("colors", {})
    if len(colors) < 8:
        return
    special = data.get("special", {})
    color_list = [colors.get(f"color{i}", "#000000") for i in range(16)]
    bg = special.get("background") or color_list[0]
    fg = special.get("foreground") or color_list[7]
    frame = color_list[4]
    crit_bg = color_list[1] if len(color_list) > 1 else "#93000a"
    crit_fg = color_list[7]
    crit_frame = color_list[9] if len(color_list) > 9 else "#ffb4ab"
    template_paths = [
        os.getenv("DUNST_TEMPLATE"),
        os.path.join(DOTFILES, "dunst", "dunstrc.template"),
        os.path.join(XDG_CONFIG_HOME, "dunst", "dunstrc.template"),
        os.path.join(os.path.expanduser("~"), "workspace", "arch-dotfiles", "dunst", "dunstrc.template"),
    ]
    template_path = next((p for p in template_paths if p and os.path.isfile(p)), None)
    if not template_path:
        print(":: Dunst template not found (dunstrc.template in dotfiles or ~/.config/dunst)")
        return
    with open(template_path) as f:
        content = f.read()
    for k, v in [
        ("{{PYWAL_BACKGROUND}}", bg),
        ("{{PYWAL_FOREGROUND}}", fg),
        ("{{PYWAL_FRAME}}", frame),
        ("{{PYWAL_CRITICAL_BG}}", crit_bg),
        ("{{PYWAL_CRITICAL_FG}}", crit_fg),
        ("{{PYWAL_CRITICAL_FRAME}}", crit_frame),
    ]:
        content = content.replace(k, v)
    dunst_dir = os.path.join(XDG_CONFIG_HOME, "dunst")
    os.makedirs(dunst_dir, exist_ok=True)
    out_path = os.path.join(dunst_dir, "dunstrc")
    with open(out_path, "w") as f:
        f.write(content)
    print(f":: Wrote {out_path}")
    subprocess.run(["dunstctl", "reload"], check=False, capture_output=True)


def write_hypr_dynamic_conf():
    """Read pywal cache and write ~/.config/hypr/conf/colors/dynamic.conf."""
    loaded = _load_wal_colors()
    if loaded is None:
        print(f":: Skipping dynamic.conf (no pywal cache in {WAL_DIR}; run wal or ensure GENERATOR writes there)")
        return
    bg, fg, colors = loaded
    if not isinstance(colors, dict):
        colors = {}
    bg = bg or colors.get("color0", "#000000")
    fg = fg or colors.get("color7", "#ffffff")
    accent = colors.get("color2", colors.get("color4", fg))
    inactive = colors.get("color8", "#666666")
    err = colors.get("color1", "#ff0000")
    bg_dec = _hex_to_rgb_dec(bg)
    fg_dec = _hex_to_rgb_dec(fg)
    accent_dec = _hex_to_rgb_dec(accent)
    inactive_dec = _hex_to_rgb_dec(inactive)
    err_dec = _hex_to_rgb_dec(err)
    lines = [
        f"# {bg}, {inactive}, {fg}, {accent}, {err}",
        f"$background = rgb({_hex_no_hash(bg)})",
        f"$foreground = rgb({_hex_no_hash(fg)})",
        f"$border_color_active = rgb({_hex_no_hash(accent)})",
        f"$accent_inactive = rgba({_hex_no_hash(accent)}40)",
        f"$border_color_inactive = rgb({_hex_no_hash(inactive)})",
        "",
        "# rgba versions for hyprlock compatibility",
        f"$background_rgba = rgba({bg_dec[0]}, {bg_dec[1]}, {bg_dec[2]}, 1.0)",
        f"$background_rgba_transparent = rgba({bg_dec[0]}, {bg_dec[1]}, {bg_dec[2]}, 0)",
        f"$foreground_rgba = rgba({fg_dec[0]}, {fg_dec[1]}, {fg_dec[2]}, 1.0)",
        f"$foreground_rgba_75 = rgba({fg_dec[0]}, {fg_dec[1]}, {fg_dec[2]}, 0.75)",
        f"$border_color_active_rgba = rgba({accent_dec[0]}, {accent_dec[1]}, {accent_dec[2]}, 1.0)",
        f"$border_color_inactive_rgba = rgba({inactive_dec[0]}, {inactive_dec[1]}, {inactive_dec[2]}, 0)",
        f"$border_color_active_hex = 0xff{_hex_no_hash(accent)}",
        "",
        f"$accent_primary = rgba({accent_dec[0]}, {accent_dec[1]}, {accent_dec[2]}, 1.0)",
        f"$accent_error = rgba({err_dec[0]}, {err_dec[1]}, {err_dec[2]}, 1.0)",
    ]
    os.makedirs(os.path.dirname(HYPR_DYNAMIC_COLORS), exist_ok=True)
    with open(HYPR_DYNAMIC_COLORS, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f":: Wrote {HYPR_DYNAMIC_COLORS}")
    subprocess.run(["hyprctl", "reload"], check=False)


def hue_to_numeric_hex(hue):
    hue = hue / 360.0
    rgb = colorsys.hls_to_rgb(hue, 0.5, 1.0)
    hex_color_str = '#{:02x}{:02x}{:02x}'.format(
        int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
    )
    numeric_hex_color = int(hex_color_str.lstrip('#'), 16)
    return numeric_hex_color


def load_settings():
    with open(settings_file_path, 'r') as file:
        return json.load(file)


parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-I', '--image', type=str, help="Image")
group.add_argument('-P', '--prev', help="Use last used wallpaper for color generation", action='store_true')
group.add_argument('-R', '--random', help="Random image from folder", action='store_true')
parser.add_argument('-n', '--notify', help="Send notifications", action='store_true')
parser.add_argument('--status', type=str, help="Status file", default="/tmp/wallpaper.status")

args = parser.parse_args()

random = args.random
prev = args.prev
image = args.image
notify = args.notify
status = args.status

HOME = os.path.expanduser("~")

cache_file = f"{HOME}/.cache/current_wallpaper"
square = f"{HOME}/.cache/square_wallpaper.png"
png = f"{HOME}/.cache/current_wallpaper.png"


def current_state(state_str: str):
    with open(status, 'w') as f:
        f.write(state_str)


def send_notify(label: str, desc: str):
    if not notify:
        return
    subprocess.run(["notify-send", label, desc])


def state(name: str | None, label: str | None, desc: str | None):
    if name is not None:
        current_state(name)
    if label is not None:
        send_notify(label, desc or "")


def join(*args):
    return os.path.join(*args)


async def main():
    global color_scheme, custom_color, generation_scheme, swww_animation, wallpaper_engine, hyprpaper_tpl

    state("init", None, None)

    settings = load_settings()
    color_scheme = settings['color-scheme']
    custom_color = settings['custom-color']
    generation_scheme = settings['generation-scheme']
    swww_animation = settings['swww-anim']
    wallpaper_engine = settings['wallpaper-engine']
    hyprpaper_tpl = settings['hyprpaper-tpl']

    new_wallpaper = f"{HOME}/dotfiles/wallpapers/default.png"
    wallpaper_dir = f"{HOME}/wallpaper/active"

    if random:
        files = [f for f in os.listdir(wallpaper_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
        current = None
        try:
            with open(cache_file) as f:
                current = os.path.basename(f.read().strip())
        except FileNotFoundError:
            pass
        if current and current in files:
            files = [f for f in files if f != current]
        if not files:
            files = [f for f in os.listdir(wallpaper_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
        if files:
            new_wallpaper = join(wallpaper_dir, _random.choice(files))
    elif prev:
        try:
            with open(cache_file) as f:
                new_wallpaper = f.read().strip()
        except FileNotFoundError:
            ...
    elif image is not None:
        new_wallpaper = os.path.abspath(image)

    print(f":: Wallpaper {new_wallpaper}")

    with open(cache_file, 'w') as f:
        f.write(new_wallpaper)

    with_image = f"with image {new_wallpaper}"

    # -----------------------------------------------------
    # Set the new wallpaper
    # -----------------------------------------------------

    transition_type = swww_animation

    state("changing", "Changing wallpaper...", with_image)
    print(":: Changing wallpaper...")

    if wallpaper_engine == "swww":
        print(":: Using swww")
        
        subprocess.run(['killall', 'swww'])

        cursor_pos = subprocess.getoutput('hyprctl cursorpos').replace(", ", ",")

        subprocess.run([
            'swww', 'img', new_wallpaper,
            '--transition-bezier', '.43,1.19,1,.4',
            '--transition-fps', '60',
            '--transition-type', transition_type,
            '--transition-duration', '0.7',
            '--transition-pos', cursor_pos
        ])

    elif wallpaper_engine == "hyprpaper":
        print(":: Using hyprpaper")

        subprocess.run(['killall', 'hyprpaper'])

        output = hyprpaper_tpl.replace('WALLPAPER', new_wallpaper)
        hyprpaper_conf_file = os.path.expanduser('~/dotfiles/hypr/hyprpaper.conf')

        with open(hyprpaper_conf_file, 'w') as file:
            file.write(output)

        subprocess.Popen(["hyprpaper"])

    else:
        print(":: Wallpaper Engine disabled")

    # -----------------------------------------------------
    # Generate colors (optional desaturate -> wal -> dynamic.conf -> themes)
    # -----------------------------------------------------
    state("colors", "Generating colors...", with_image)
    print(":: Generate colors")
    wal_cmd = os.path.expanduser("~/.local/bin/wal")
    if not os.path.isfile(wal_cmd):
        wal_cmd = "wal"
    # Optionally desaturate image before pywal so extracted colors are softer
    wal_input = new_wallpaper
    if WAL_DESATURATION < 1.0:
        sat_pct = int(round(WAL_DESATURATION * 100))
        fd, wal_input = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        try:
            subprocess.run(
                ["magick", new_wallpaper + "[0]", "-modulate", "100", str(sat_pct), "100", wal_input],
                check=True,
                capture_output=True,
            )
            print(f":: Desaturated wallpaper for pywal (saturation {sat_pct}%)")
        except (subprocess.CalledProcessError, FileNotFoundError):
            wal_input = new_wallpaper
    try:
        subprocess.run([wal_cmd, "-i", wal_input, "-n"], check=False)  # -n: don't set wallpaper
    finally:
        if wal_input != new_wallpaper and os.path.isfile(wal_input):
            os.remove(wal_input)
    write_hypr_dynamic_conf()
    _apply_wofi()
    _apply_waybar()
    _apply_dunst()
    subprocess.run(["pywalfox", "update"], check=False)  # push colors to Zen Browser

    # -----------------------------------------------------
    # Square image
    # -----------------------------------------------------
    square_task = asyncio.create_task(square_image(new_wallpaper))

    # -----------------------------------------------------
    # Png image
    # -----------------------------------------------------
    png_task = asyncio.create_task(png_image(new_wallpaper))

    state("tasks", None, None)
    await asyncio.gather(square_task, png_task)
    state("finish", "Wallpaper procedure complete!", with_image)


async def png_image(wallpaper: str):
    _from = (".jpg", "jpeg")
    if not wallpaper.endswith(_from):
        cmd = f"cp -f {wallpaper} {png}"
    else:
        with_image = f"with image {wallpaper}"
        state(None, "Converting jpg to png...", with_image)
        print(":: Converting jpg to png...")
        cmd = f"magick {wallpaper}[0] {png}"
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        print(f":: Error while processing image: {stderr.decode()}")
    else:
        print(":: JPG successfully converted to PNG!")


async def square_image(wallpaper):
    with_image = f"with image {wallpaper}"
    state(None, "Creating square version...", with_image)
    print(":: Creating square version")
    cmd = f"magick {wallpaper}[0] -gravity Center -extent 1:1 {square}"
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        print(f":: Error while processing image: {stderr.decode()}")
    else:
        print(":: Square image created!")


if __name__ == "__main__":
    acquire_lock()
    try:
        asyncio.run(main())
    finally:
        release_lock()
