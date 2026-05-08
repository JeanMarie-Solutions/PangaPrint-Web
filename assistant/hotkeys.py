"""
Global hotkey manager for PrintFix Assistant.
Handles keyboard shortcuts.
"""

import logging
import keyboard

logger = logging.getLogger(__name__)


class HotkeyManager:
    """Manager for global hotkeys."""

    def __init__(self):
        self.hotkeys = {}

    def register_hotkey(self, hotkey, callback):
        """
        Register a global hotkey.

        Args:
            hotkey (str): Hotkey combination (e.g., 'ctrl+shift+p')
            callback (callable): Function to call when hotkey is pressed
        """
        try:
            keyboard.add_hotkey(hotkey, callback)
            self.hotkeys[hotkey] = callback
            logger.info(f"Registered hotkey: {hotkey}")
        except Exception as e:
            logger.error(f"Failed to register hotkey {hotkey}: {str(e)}")

    def unregister_hotkey(self, hotkey):
        """
        Unregister a hotkey.

        Args:
            hotkey (str): Hotkey combination to remove
        """
        try:
            if hotkey in self.hotkeys:
                keyboard.remove_hotkey(hotkey)
                del self.hotkeys[hotkey]
                logger.info(f"Unregistered hotkey: {hotkey}")
        except Exception as e:
            logger.error(f"Failed to unregister hotkey {hotkey}: {str(e)}")

    def unregister_all(self):
        """Unregister all hotkeys."""
        for hotkey in list(self.hotkeys.keys()):
            self.unregister_hotkey(hotkey)