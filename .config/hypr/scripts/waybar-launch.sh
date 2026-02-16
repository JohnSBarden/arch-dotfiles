#!/usr/bin/env sh
killall waybar && waybar & disown
# pkill -RTMIN+1 waybar
