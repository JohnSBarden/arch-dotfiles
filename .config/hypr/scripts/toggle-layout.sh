#!/usr/bin/env bash
# Cycles through Hyprland tiling layouts.
# Usage: toggle-layout.sh [reset]
#   (no args) — advance to next layout
#   reset     — return to master

# Monocle is implemented as master layout with mfact=1 (stack windows get no space).
# All other state is read live from hyprctl, but monocle vs master requires a state file.

LAYOUTS=(master dwindle scrolling monocle)
STATE_FILE="/tmp/hypr_layout_cycle"

apply_layout() {
    local layout="$1"
    case "$layout" in
        monocle)
            hyprctl keyword general:layout master
            hyprctl keyword master:mfact 1
            ;;
        master)
            hyprctl keyword general:layout master
            hyprctl keyword master:mfact 0.5
            ;;
        *)
            hyprctl keyword general:layout "$layout"
            ;;
    esac
    echo "$layout" > "$STATE_FILE"
    notify-send -t 1500 "Layout" "$layout"
}

if [[ "$1" == "reset" ]]; then
    apply_layout "master"
    exit 0
fi

CURRENT=$(cat "$STATE_FILE" 2>/dev/null || echo "master")

for i in "${!LAYOUTS[@]}"; do
    if [[ "${LAYOUTS[$i]}" == "$CURRENT" ]]; then
        NEXT="${LAYOUTS[(($i + 1)) % ${#LAYOUTS[@]}]}"
        apply_layout "$NEXT"
        exit 0
    fi
done

# Fallback if state is stale/unknown
apply_layout "master"
