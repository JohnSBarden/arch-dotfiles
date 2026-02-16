#!/usr/bin/env bash
# Run pywalfox with dotfiles override (softer colors + wofi theme).
# Use this as the native messaging host path in ~/.mozilla/native-messaging-hosts/pywalfox.json
# so Firefox and wofi both get the transformed theme.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${SCRIPT_DIR}/run_pywalfox.py" "$@"
