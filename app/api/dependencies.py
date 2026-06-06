from app.core.config import get_settings as get_settings_config, Settings


def get_settings() -> Settings:
    return get_settings_config()
