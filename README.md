# 🔥 StokerCloud Write — Home Assistant custom integration

**StokerCloud Write** is a Home Assistant integration for **NBE / StokerCloud** pellet boilers, providing both **read and write** access to your boiler via the official StokerCloud API.  
It extends the original [homeassistant-stokercloud](https://github.com/KristianOellegaard/homeassistant-stokercloud) project with **temperature and power control** support.

---

## ✨ Features

- ✅ Full data readout from your NBE boiler via StokerCloud  
- ✍️ Control functions: change boiler temperature setpoint, toggle power  
- 🔐 Authentication via **serial** and **token** from [stokercloud.dk](https://stokercloud.dk)  
- 🧩 Native Home Assistant Config Flow  
- 🎛️ Lovelace-ready controls (switches, number inputs)  
- ⚙️ Works in automations, scripts, dashboards  

---

## 📦 Installation

### Option A — via HACS (recommended)

1. Open **HACS → Integrations → ⋯ → Custom repositories**
2. Add repository URL:
   ```
   https://github.com/chaichuk/stokercloud_write
   ```
   Category: **Integration**
3. Install and **Restart Home Assistant**
4. Go to **Settings → Devices & Services → Add Integration → StokerCloud Control**

### Option B — manual installation

1. Copy the folder:
   ```
   custom_components/stokercloud_write/
   ```
   into:
   ```
   <config>/custom_components/stokercloud_write/
   ```
2. Restart Home Assistant.
3. Add the integration manually from **Settings → Devices & Services**.

---

## 🔑 Getting Your Serial and Token

1. Log in to [https://stokercloud.dk](https://stokercloud.dk)
2. Open your boiler page. The URL looks like:
   ```
   https://stokercloud.dk/v3/#/user/main-page
   ```
   → Settings → User account
   → The number in "Serial number on the controller" is the **serial** (e.g. `23862`).

4. Open **Developer Tools → Network tab**, refresh the page, and find a request such as `ajaxdata.js` or `data.json`.  
   In the **Headers**, look for:
   ```
   Request URL:  <https://stokercloud.dk/v2/dataout2/getstatus.php?token=8ff57581385cb15c3689fd2416........>
   ```
5. Copy the entire token string (all symbols after "token=").

In the HA configuration form, paste:
- **serial** → your boiler serial (e.g. `23862`)
- **token** → the copied token (e.g. `8ff57581385cb15c3689fd2416......`)
- **name** → optional display name (e.g. “My Boiler”)

⚠️ Tokens can expire — if data stops updating, repeat the steps to refresh your token.

---

## 🧠 Entities

Once connected, a device (e.g. **NBE 23862 (My Boiler)**) is created with all sensors and controls.

### 🧾 Sensors

| Entity | Description |
|--------|-------------|
| `sensor.boiler_temperature` | Boiler temperature |
| `sensor.boiler_temperature_setpoint` | Boiler setpoint |
| `sensor.external_temperature` | Outside temperature |
| `sensor.hot_water_temperature` | Current DHW temperature |
| `sensor.hot_water_wanted_temperature` | Target DHW temperature |
| `sensor.return_temperature` | Return line temperature |
| `sensor.shaft_temperature` | Shaft temperature |
| `sensor.flue_temperature` | Flue gas temperature |
| `sensor.oxygen` | O₂ level (%) |
| `sensor.power_percent` | Boiler power (%) |
| `sensor.power_kw` | Boiler power (kW) |
| `sensor.pellet_consumption_last_24h` | Pellet usage (last 24h) |
| `sensor.photo_sensor` | Photodiode reading |
| `sensor.state` | Operational status |
| `sensor.pump_state` | Circulation pump status |
| `sensor.hopper_content` | Hopper content (kg) |

### 🎛️ Controls

| Entity | Type | Description |
|--------|------|-------------|
| `switch.boiler_power` | Switch | Turn boiler on/off |
| `number.boiler_temperature` | Number | Adjust boiler setpoint |
| `number.hopper_content` | Number | Manually update hopper pellet weight |


## 👨‍💻 Author

- GitHub: [@chaichuk](https://github.com/chaichuk)  
- Telegram: [@serhii_chaichuk](https://t.me/serhii_chaichuk)

Custom integration for **NBE / StokerCloud** pellet boilers with full control from Home Assistant.

---

## 📜 License

MIT License — see [LICENSE](LICENSE)
