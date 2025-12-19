from __future__ import annotations
from aiohttp import ClientSession
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from yarl import URL
from .const import (
    UPDATE_URL, CONTROLLERDATA_URL, CONF_TOKEN,
    MISC_START_NAME, MISC_STOP_NAME, MISC_CMD_VALUE,
    DEFAULT_SCREEN_QUERY, 
)

class StokerCloudWriteApi:
    def __init__(self, hass, entry):
        self._hass = hass
        self._entry = entry
        self._session: ClientSession = async_get_clientsession(hass)

    async def async_set_boiler_setpoint(self, value: int) -> bool:
        url = URL(UPDATE_URL).with_query({
            "menu": "boiler.temp",
            "name": "boiler.temp",
            "token": self._entry.data[CONF_TOKEN],
        })
        data = {"value": str(value)}
        try:
            async with self._session.post(str(url), data=data, timeout=15) as resp:
                return resp.status == 200
        except Exception:
            return False

    async def async_set_power(self, turn_on: bool) -> bool:
        name = MISC_START_NAME if turn_on else MISC_STOP_NAME
        url = URL(UPDATE_URL).with_query({"name": name, "token": self._entry.data[CONF_TOKEN]})
        try:
            async with self._session.post(str(url), data={"value": MISC_CMD_VALUE}, timeout=10) as resp:
                return resp.status == 200
        except Exception:
            return False

    async def _fetch_controller_json(self) -> dict | None:
        """Get JSON from controllerdata2.php."""
        url = URL(CONTROLLERDATA_URL).with_query({
            "screen": DEFAULT_SCREEN_QUERY,
            "token": self._entry.data[CONF_TOKEN],
        })
        try:
            async with self._session.get(str(url), timeout=15) as resp:
                if resp.status != 200:
                    return None
                return await resp.json(content_type=None)
        except Exception:
            return None

    async def async_get_boiler_temperature_from_controller(self) -> float | None:
        """frontdata['boilertemp'] → °C"""
        data = await self._fetch_controller_json()
        if not data:
            return None
        try:
            for item in data.get("frontdata", []):
                if str(item.get("id")) == "boilertemp":
                    return float(str(item.get("value")).replace(",", "."))
        except Exception:
            pass
        # Fallback (sometimes equal to the actual temperature):
        try:
            wc = data.get("weathercomp") or {}
            val = wc.get("zone1-actual", {}).get("val")
            if val is not None:
                return float(str(val).replace(",", "."))
        except Exception:
            pass
        return None

    async def async_get_external_temperature_from_controller(self) -> float | None:
        """weatherdata[id=='7'] → outdoor temperature, °C."""
        data = await self._fetch_controller_json()
        if not data:
            return None
        try:
            for item in data.get("weatherdata", []):
                if str(item.get("id")) == "7":  # lng_weather_7
                    return float(str(item.get("value")).replace(",", "."))
        except Exception:
            pass
        # Fallback: sometimes found in weathercomp.zone1-actualref.val
        try:
            wc = data.get("weathercomp") or {}
            val = wc.get("zone1-actualref", {}).get("val")
            if val is not None:
                return float(str(val).replace(",", "."))
        except Exception:
            pass
        return None

    async def async_get_wanted_boiler_temp_from_controller(self) -> float | None:
        """frontdata['-wantedboilertemp'] → °C."""
        data = await self._fetch_controller_json()
        if not data:
            return None
        try:
            for item in data.get("frontdata", []):
                if str(item.get("id")) == "-wantedboilertemp":
                    return float(str(item.get("value")).replace(",", "."))
        except Exception:
            pass
        return None

    async def async_get_dhw_temperature_from_controller(self) -> float | None:
        """frontdata['dhw'] → °C."""
        data = await self._fetch_controller_json()
        if not data:
            return None
        try:
            for item in data.get("frontdata", []):
                if str(item.get("id")) == "dhw":
                    return float(str(item.get("value")).replace(",", "."))
        except Exception:
            pass
        return None

    async def async_get_dhw_wanted_temperature_from_controller(self) -> float | None:
        """frontdata['dhwwanted'] → °C."""
        data = await self._fetch_controller_json()
        if not data:
            return None
        try:
            for item in data.get("frontdata", []):
                if str(item.get("id")) == "dhwwanted":
                    return float(str(item.get("value")).replace(",", "."))
        except Exception:
            pass
        return None

    async def async_get_shaft_temperature_from_controller(self) -> float | None:
        """boilerdata[id=='7'] (lng_boil_7) → °C."""
        data = await self._fetch_controller_json()
        val = None
        try:
            for item in (data or {}).get("boilerdata", []):
                if str(item.get("id")) == "7":
                    val = float(str(item.get("value")).replace(",", "."))
                    break
        except Exception:
            val = None

        if val is not None:
            return val

        # Fallback: if the main screen did not receive id=7, we fetch it separately.
        from yarl import URL
        try:
            url = URL(CONTROLLERDATA_URL).with_query({
                "screen": "b1,7",
                "token": self._entry.data[CONF_TOKEN],
            })
            async with self._session.get(str(url), timeout=10) as resp:
                if resp.status != 200:
                    return None
                data2 = await resp.json(content_type=None)
                for item in (data2 or {}).get("boilerdata", []):
                    if str(item.get("id")) == "7":
                        return float(str(item.get("value")).replace(",", "."))
        except Exception:
            return None

        return None

    async def async_get_boiler_running_from_controller(self) -> bool | None:
        """miscdata.running → True/False."""
        data = await self._fetch_controller_json()
        if not data:
            return None
        try:
            running = (data.get("miscdata") or {}).get("running")
            # We treat 1 / "1" / True as ON.
            if running is None:
                return None
            s = str(running).strip().lower()
            if s in ("1", "true", "on", "yes"):
                return True
            if s in ("0", "false", "off", "no"):
                return False
            # if it’s a number/float, we treat values > 0 as True
            try:
                return float(s) > 0
            except Exception:
                return None
        except Exception:
            return None

    async def async_get_output_kw_from_controller(self) -> float | None:
        """miscdata.output → кіловати (kW)."""
        data = await self._fetch_controller_json()
        if not data:
            return None
        try:
            val = (data.get("miscdata") or {}).get("output")
            if val is None:
                return None
            return float(str(val).replace(",", "."))
        except Exception:
            return None

    async def async_get_output_pct_from_controller(self) -> float | None:
        """miscdata.outputpct → відсотки (%)."""
        data = await self._fetch_controller_json()
        if not data:
            return None
        try:
            val = (data.get("miscdata") or {}).get("outputpct")
            if val is None:
                return None
            return float(str(val).replace(",", "."))
        except Exception:
            return None

    # ---------------------------
    # NEW: Photo sensor (lux)
    # ---------------------------

    def _find_value_by_id_and_selection(self, obj, target_id: str = "6", target_sel: str = "boiler4"):
        """Depth-first пошук value у довільній структурі (dict/list) за id і selection."""
        try:
            if isinstance(obj, dict):
                if str(obj.get("id")) == str(target_id) and str(obj.get("selection")) == str(target_sel):
                    return obj.get("value") or obj.get("val")
                for v in obj.values():
                    found = self._find_value_by_id_and_selection(v, target_id, target_sel)
                    if found is not None:
                        return found
                return None
            if isinstance(obj, list):
                for item in obj:
                    found = self._find_value_by_id_and_selection(item, target_id, target_sel)
                    if found is not None:
                        return found
                return None
            return None
        except Exception:
            return None

    async def async_get_photo_sensor_lux_from_controller(self) -> float | None:
        """
		Illuminance (lux) from controllerdata2.php — we look for an element with id="6" and selection="boiler4".
		Returns a float or None; does not raise exceptions.
        """
        data = await self._fetch_controller_json()
        if not data:
            return None
        try:
            raw = self._find_value_by_id_and_selection(data, target_id="6", target_sel="boiler4")
            if raw in (None, ""):
                return None
            return float(str(raw).replace(",", "."))
        except Exception:
            return None
    # ---------------------------
    # NEW: state code (miscdata.state.value)
    # ---------------------------
    async def async_get_state_code_from_controller(self) -> str | None:
        """Return raw state code from miscdata.state.value, e.g., 'state_5'."""
        data = await self._fetch_controller_json()
        if not data:
            return None
        try:
            misc = data.get("miscdata") or {}
            state = misc.get("state") or {}
            val = state.get("value")
            if not val:
                return None
            return str(val)
        except Exception:
            return None
    async def async_get_pump_state_from_controller(self) -> str | None:
        """Return 'ON'/'OFF' from leftoutput.output-2.val."""
        data = await self._fetch_controller_json()
        if not data:
            return None
        try:
            left = data.get("leftoutput") or {}
            out2 = left.get("output-2") or {}
            val = out2.get("val")
            if val is None:
                return None
            # Normalize to uppercase.
            return str(val).upper()
        except Exception:
            return None
    async def async_get_oxygen_from_controller(self) -> float | None:
        """
        Read oxygen level (%) from boilerdata[id=12].value.
        Returns float in percent.
        """
        data = await self._fetch_controller_json()
        if not data:
            return None
        try:
            boiler = data.get("boilerdata") or []
            item = next((x for x in boiler if str(x.get("id")) == "12"), None)
            if not item:
                return None
            raw = item.get("value")
            if raw is None or raw == "":
                return None
            return float(raw)
        except Exception:
            return None
            
    async def async_get_hopper_consumption_24h_kg(self) -> float | None:
        """
		From controllerdata2.php: hopperdata[id='3'] or selection='hopper2' → kilograms over the last 24 hours.
		Returns a float or None.
        """
        data = await self._fetch_controller_json()
        if not data:
            return None

        hopper = (data.get("hopperdata") or [])
        #1) priority by ID
        item = next((x for x in hopper if str(x.get("id")) == "3"), None)
        # 2) fallback option — by selection
        if not item:
            item = next((x for x in hopper if str(x.get("selection")) == "hopper2"), None)
        if not item:
            return None

        raw = item.get("value")
        if raw in ("", None):
            return None

        try:
            # For the case of "8,9"
            return float(str(raw).replace(",", "."))
        except Exception:
            return None
    async def async_get_hopper_content_kg(self) -> float | None:
        """
        Reads frontdata → id='hoppercontent' → value (kg) from controllerdata2.php.
        """
        try:
            from yarl import URL
            params = {"screen": DEFAULT_SCREEN_QUERY, "token": self._entry.data[CONF_TOKEN]}
            async with self._session.get(str(URL(CONTROLLERDATA_URL).with_query(params)), timeout=15) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json(content_type=None)
        except Exception:
            return None

        front = (data or {}).get("frontdata") or []
        item = next((x for x in front if str(x.get("id")) == "hoppercontent"), None)
        if not item:
            return None

        raw = item.get("value")
        if raw in ("", None):
            return None

        try:
            return float(str(raw).replace(",", "."))
        except Exception:
            return None

    async def async_set_hopper_content_kg(self, value_kg: float) -> None:
        """
		Updates hopper.content via POST form-data to updatevalue.php.
		Optimistic model: we do not parse the response and do not check the status.
        """
        token = self._entry.data.get(CONF_TOKEN)
        if not token:
            return

        payload = {
            "menu": "hopper.content",
            "name": "hopper.content",
            "token": token,
            "value": f"{float(value_kg):.1f}",
        }
        try:
            async with self._session.post(UPDATE_URL, data=payload, timeout=10):
                pass
        except Exception:
            return
