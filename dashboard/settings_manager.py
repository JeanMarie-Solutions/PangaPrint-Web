"""
Settings manager for PrintFix application.
Provides utilities for accessing and managing system settings.
"""

import json
import logging
from functools import lru_cache
from django.core.cache import cache
from django.conf import settings as django_settings

logger = logging.getLogger(__name__)


class SettingsManager:
    """Manager for accessing system settings with caching and type conversion."""
    
    CACHE_TIMEOUT = 300  # 5 minutes
    
    @classmethod
    def get_cache_timeout(cls):
        """Get the current cache timeout from system settings."""
        try:
            from dashboard.models import SystemSettings
            setting = SystemSettings.objects.filter(key='cache_timeout_seconds').first()
            if setting:
                timeout_value = int(setting.value)
                if timeout_value > 0:
                    return timeout_value
        except Exception:
            pass
        return cls.CACHE_TIMEOUT

    @classmethod
    def get(cls, key: str, default=None, setting_type: str = None):
        """Get a setting value with type conversion and caching."""
        cache_key = f'setting_{key}'
        cached_value = cache.get(cache_key)
        
        if cached_value is not None:
            return cls._convert_type(cached_value, setting_type)
        
        try:
            from dashboard.models import SystemSettings
            setting = SystemSettings.objects.filter(key=key).first()
            
            if setting:
                value = setting.value
                cache.set(cache_key, value, cls.get_cache_timeout())
                return cls._convert_type(value, setting_type or setting.setting_type)
            else:
                return default
        except Exception as e:
            logger.warning(f"Failed to get setting {key}: {str(e)}")
            return default
    
    @classmethod
    def get_bool(cls, key: str, default: bool = False) -> bool:
        """Get a boolean setting."""
        value = cls.get(key, str(default).lower(), 'boolean')
        return str(value).lower() in ('true', '1', 'yes', 'on')
    
    @classmethod
    def get_int(cls, key: str, default: int = 0) -> int:
        """Get an integer setting."""
        try:
            return int(cls.get(key, default, 'number'))
        except (ValueError, TypeError):
            return default
    
    @classmethod
    def get_float(cls, key: str, default: float = 0.0) -> float:
        """Get a float setting."""
        try:
            return float(cls.get(key, default, 'number'))
        except (ValueError, TypeError):
            return default
    
    @classmethod
    def get_list(cls, key: str, default: list = None) -> list:
        """Get a list setting."""
        if default is None:
            default = []
        value = cls.get(key, default, 'list')
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value.split(',')
        return value
    
    @classmethod
    def set(cls, key: str, value):
        """Set a setting value and clear cache."""
        try:
            from dashboard.models import SystemSettings
            setting, _ = SystemSettings.objects.get_or_create(key=key)
            setting.value = str(value)
            setting.save()
            cache.delete(f'setting_{key}')
            logger.info(f"Setting {key} updated to {value}")
        except Exception as e:
            logger.error(f"Failed to set setting {key}: {str(e)}")
    
    @classmethod
    def _convert_type(cls, value, setting_type: str = None):
        """Convert value to appropriate type."""
        if setting_type == 'number':
            try:
                return int(value) if '.' not in str(value) else float(value)
            except (ValueError, TypeError):
                return value
        elif setting_type == 'boolean':
            return str(value).lower() in ('true', '1', 'yes', 'on')
        elif setting_type == 'list':
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value.split(',')
            return value
        return value
    
    @classmethod
    def get_by_category(cls, category: str):
        """Get all settings in a category."""
        try:
            from dashboard.models import SystemSettings
            return SystemSettings.objects.filter(category=category).order_by('key')
        except Exception as e:
            logger.error(f"Failed to get settings by category: {str(e)}")
            return []
    
    @classmethod
    def clear_cache(cls, key: str = None):
        """Clear cache for a specific setting or all settings."""
        if key:
            cache.delete(f'setting_{key}')
        else:
            # Clear all setting cache keys
            cache.clear()


# Convenience function for templates and views
def get_setting(key: str, default=None):
    """Convenience function to get a setting."""
    return SettingsManager.get(key, default)
