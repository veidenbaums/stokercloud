from homeassistant.const import CONF_USERNAME
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

# Не міняємо твій домен — лишаємо як є
DOMAIN = "hass_stokercloud"

# Додаємо поля під запис (token + опціонально phpsessid)
CONF_TOKEN = "token"
CONF_PHPSESSID = "phpsessid"

# Поля для low-level сервісу
ATTR_MENU = "menu"
ATTR_NAME = "name"
ATTR_VALUE = "value"
ATTR_PHPSESSID = "phpsessid"

# Ключі за замовчуванням для керування котловою температурою
DEFAULT_TEMP_MENU = "boiler.temp"
DEFAULT_TEMP_NAME = "boiler.temp"

# YAML-схема (розширена під токен)
DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_USERNAME): cv.string,   # було у тебе
    vol.Required(CONF_TOKEN): cv.string,      # обов'язково додай у YAML
    vol.Optional(CONF_PHPSESSID, default=""): cv.string,  # якщо треба cookie
})

# Додаємо 'number' до платформ (твоя water_heater лишається)
PLATFORMS = ['sensor', 'water_heater', 'number']
