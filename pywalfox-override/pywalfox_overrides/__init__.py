# Override logic: patch system pywalfox with softer colors + wofi/waybar/dunst theme.
from . import fetcher
from . import wofi
from . import waybar
from . import dunst


def apply_patch(pkg):
    """Patch the given pywalfox package (system) with our fetcher and theme writers."""
    pkg.fetcher.get_pywal_colors = fetcher.get_pywal_colors

    Message = pkg.response.Message
    ACTIONS = pkg.config.ACTIONS

    def _write_themes(pywal_data):
        if pywal_data:
            # Write back to pywal cache so Cursor/Ghostty get softer colors
            fetcher.write_transformed_colors_back(pywal_data)
            wofi.write_wofi_theme(pywal_data)
            waybar.write_waybar_theme(pywal_data)
            dunst.write_dunst_theme(pywal_data)

    def send_pywal_colors(self):
        (success, pywal_data, message) = fetcher.get_pywal_colors()
        self.messenger.send_message(Message(
            ACTIONS['COLORS'],
            data=pywal_data,
            success=success,
            message=message,
        ))
        if success and pywal_data:
            _write_themes(pywal_data)

    pkg.daemon.Daemon.send_pywal_colors = send_pywal_colors
