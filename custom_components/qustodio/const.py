# Base component constants
DOMAIN = "qustodio"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.1"
PLATFORMS = ["sensor"]
REQUIRED_FILES = [
    "translations/en.json",
    "const.py",
    "config_flow.py",
    "manifest.json",
    "sensor.py",
    "qustodioapi.py",
]
ISSUE_URL = "https://github.com/custom-components/blueprint/issues"
ATTRIBUTION = "Data from this is provided by qustodio."

# Icons
ICON_IN_TIME = "mdi:timer-outline"
ICON_NO_TIME = "mdi:timer-off-outline"

# Device classes

# Configuration
CONF_SENSOR = "sensor"
CONF_ENABLED = "enabled"
CONF_NAME = "name"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

# Defaults
DEFAULT_NAME = "Qustodio"


LOGIN_RESULT_OK = "OK"
LOGIN_RESULT_UNAUTHORIZED = "UNAUTHORIZED"
LOGIN_RESULT_ERROR = "ERROR"
