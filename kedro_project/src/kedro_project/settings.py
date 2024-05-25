# src/kedro_project/settings.py

from kedro.config import TemplatedConfigLoader, ConfigLoader

CONF_SOURCE = "conf"
CONFIG_LOADER_CLASS = ConfigLoader
CONFIG_LOADER_ARGS = {
    "config_patterns": {
        "catalog": ["catalog*", "catalog*/**"],
        "credentials": ["credentials*", "credentials*/**"],
        "parameters": ["parameters*", "parameters*/**"],
        "logging": ["logging*", "logging*/**"],
    }
}
HOOKS = ()
