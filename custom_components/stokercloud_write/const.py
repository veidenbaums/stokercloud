from __future__ import annotations


from datetime import timedelta


DOMAIN = "stokercloud_write"
PLATFORMS: list[str] = ["sensor", "number"]
DEFAULT_SCAN_INTERVAL = timedelta(seconds=30)


CONF_SERIAL = "serial"
CONF_TOKEN = "token"
CONF_SCAN_INTERVAL = "scan_interval"


API_BASE = "https://stokercloud.dk"
API_DATA_PATH = "/v2/dataout2/data.json" # читання
API_WRITE_PATH = "/v2/dataout2/updatevalue.php" # запис


DEVICE_MANUFACTURER = "NBE"
DEVICE_MODEL = "StokerCloud"


# Ключі, які краще не піднімати як сенсори (службові або дублікати)
SENSOR_EXCLUDE_PREFIXES = ("time_", "timestamp_", "history_")
SENSOR_EXCLUDE_EXACT = {"status", "ok", "error"}


# Евристики одиниць
UNIT_MAP_SUFFIX = {
"temp": "°C",
"temperature": "°C",
"pressure": "bar",
"power": "kW",
"energy": "kWh",
"pct": "%",
"%": "%",
"rpm": "rpm",
}
