from homeassistant.const import Platform

DOMAIN = "stokercloud_write"
MANUFACTURER = "NBE"
MODEL = "StokerCloud"
PLATFORMS: list[Platform] = [Platform.NUMBER]
CONF_SERIAL = "serial"
CONF_TOKEN = "token"
BASE_URL = "https://stokercloud.dk"
