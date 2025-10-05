DOMAIN = "stokercloud_write"

CONF_TOKEN = "token"
CONF_SERIAL = "serial"
CONF_NAME = "name"

ATTR_MANUFACTURER = "NBE"

# Endpoints
UPDATE_URL = "https://stokercloud.dk/v2/dataout2/updatevalue.php"
CONTROLLERDATA_URL = "https://stokercloud.dk/v2/dataout2/controllerdata2.php"

# Number box limits
DEFAULT_MIN_TEMP = 30
DEFAULT_MAX_TEMP = 90
DEFAULT_STEP = 1.0

# Polling
BOILER_SCAN_INTERVAL = 20  # seconds

# Power control
MISC_START_NAME = "misc.start"
MISC_STOP_NAME  = "misc.stop"
MISC_CMD_VALUE  = "1"

# Екран як у твоєму DevTools (можеш змінити на інший за потреби)
DEFAULT_SCREEN_QUERY = (
    "b1,3,b2,5,b3,4,b4,6,b5,12,b6,14,b7,15,b8,16,b9,9,b10,0,"
    "d1,3,d2,4,d3,0,d4,0,d5,0,d6,0,d7,0,d8,0,d9,0,d10,0,"
    "h1,2,h2,3,h3,4,h4,7,h5,8,h6,0,h7,0,h8,0,h9,0,h10,0,"
    "w1,2,w2,3,w3,9,w4,7,w5,4"
)
