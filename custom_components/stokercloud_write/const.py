from __future__ import annotations

DOMAIN = "stokercloud_write"

# поля конфігу
CONF_SERIAL_NUMBER = "serial_number"
CONF_TOKEN = "token"
CONF_PHPSESSID = "phpsessid"

# сервіс (низькорівневий)
ATTR_MENU = "menu"
ATTR_NAME = "name"
ATTR_VALUE = "value"
ATTR_PHPSESSID = "phpsessid"
ATTR_ENTRY_ID = "entry_id"  # якщо треба вказати конкретний пристрій/енрі

# дефолтні ключі для керування котловою температурою
DEFAULT_TEMP_MENU = "boiler.temp"
DEFAULT_TEMP_NAME = "boiler.temp"

PLATFORMS: list[str] = ["number"]
