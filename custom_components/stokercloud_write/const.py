DOMAIN = "stokercloud_write"

CONF_TOKEN = "token"
CONF_SERIAL = "serial"
CONF_NAME = "name"

ATTR_MANUFACTURER = "NBE"

# URL для запису значення (boiler.temp). За потреби підкоригуй menu/name.
UPDATE_URL = "https://stokercloud.dk/v2/dataout2/updatevalue.php"

# Межі для поля вводу
DEFAULT_MIN_TEMP = 30
DEFAULT_MAX_TEMP = 90
DEFAULT_STEP = 1.0
