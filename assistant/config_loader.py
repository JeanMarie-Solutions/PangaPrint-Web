"""
Configuration loader for PangaPrint Assistant.
Loads and manages configuration settings.
"""

import os
import json
import logging
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


def get_system_setting(key, default=None):
    """Get a system setting from the database with caching."""
    cache_key = f'system_setting_{key}'
    value = cache.get(cache_key)
    if value is None:
        try:
            from dashboard.models import SystemSettings
            setting = SystemSettings.objects.filter(key=key).first()
            value = setting.value if setting else default
            cache.set(cache_key, value, 300)  # Cache for 5 minutes
        except Exception as e:
            logger.warning(f"Failed to get system setting {key}: {str(e)}")
            value = default
    return value


class ConfigLoader:
    """Configuration loader and manager."""

    def __init__(self, config_file=None):
        self.config_file = config_file or os.path.join(settings.CONFIG_FOLDER, 'settings.json')
        self.config = self.load_config()

    def load_config(self):
        """Load configuration from file."""
        default_config = {
            'watch_folder': settings.WATCH_FOLDER,
            'temp_folder': settings.TEMP_FOLDER,
            'output_folder': settings.OUTPUT_FOLDER,
            'logs_folder': settings.LOGS_FOLDER,
            'default_printer': settings.DEFAULT_PRINTER,
            'hotkey': settings.HOTKEY,
            'auto_start': False,
            'notification_enabled': True,
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                default_config.update(loaded_config)
                logger.info(f"Loaded config from {self.config_file}")
            except Exception as e:
                logger.error(f"Failed to load config: {str(e)}")

        return default_config

    def save_config(self):
        """Save current configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Saved config to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save config: {str(e)}")

    def get(self, key, default=None):
        """Get a configuration value, checking system settings first."""
        # First check system settings (database)
        system_value = get_system_setting(key)
        if system_value is not None:
            return system_value

        # Then check JSON config file
        file_value = self.config.get(key)
        if file_value is not None:
            return file_value

        # Finally return default
        return default

    def set(self, key, value):
        """Set a configuration value."""
        self.config[key] = value
        self.save_config()
        # Clear cache for this setting
        cache.delete(f'system_setting_{key}')

    def get_watch_folder(self):
        """Get the watch folder path."""
        return self.get('watch_folder', settings.WATCH_FOLDER)

    def get_temp_folder(self):
        """Get the temp folder path."""
        return self.get('temp_folder', settings.TEMP_FOLDER)

    def get_output_folder(self):
        """Get the output folder path."""
        return self.get('output_folder', settings.OUTPUT_FOLDER)

    def get_logs_folder(self):
        """Get the logs folder path."""
        return self.get('logs_folder', settings.LOGS_FOLDER)