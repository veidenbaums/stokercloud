DOMAIN = "stokercloud_write"

CONF_TOKEN = "token"
CONF_SERIAL = "serial"
CONF_NAME = "name"

ATTR_MANUFACTURER = "NBE"

# WRITE endpoint
UPDATE_URL = "https://stokercloud.dk/v2/dataout2/updatevalue.php"
# READ endpoint (за потреби заміни на той, що у материнській інтеграції)
READ_URL = "https://stokercloud.dk/v2/dataout2/getvalue.php"

DEFAULT_MIN_TEMP = 30
DEFAULT_MAX_TEMP = 90
DEFAULT_STEP = 1.0

# Інтервал опитування сенсорів, сек.
DEFAULT_SCAN_INTERVAL = 30
