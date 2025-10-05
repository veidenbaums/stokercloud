DOMAIN = "stokercloud_write"

CONF_TOKEN = "token"
CONF_SERIAL = "serial"
CONF_NAME = "name"

ATTR_MANUFACTURER = "NBE"

# Endpoints
UPDATE_URL = "https://stokercloud.dk/v2/dataout2/updatevalue.php"
READ_URL = "https://stokercloud.dk/v2/dataout2/getvalue.php"

# Number box limits
DEFAULT_MIN_TEMP = 30
DEFAULT_MAX_TEMP = 90
DEFAULT_STEP = 1.0

# Sensor polling
DEFAULT_SCAN_INTERVAL = 30  # seconds

# ---- Power control (misc.start / misc.stop) ----
MISC_START_NAME = "misc.start"  # ON
MISC_STOP_NAME  = "misc.stop"   # OFF
MISC_CMD_VALUE  = "1"           # і start, і stop передають 1
