"""Support for Xiaomi Aqara binary sensors."""

import time

from homeassistant.components.automation import ATTR_LAST_TRIGGERED
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.const import ATTR_BATTERY_LEVEL, ATTR_VOLTAGE, STATE_OFF, STATE_ON
from homeassistant.core_config import DATA_CUSTOMIZE
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util.dt import now

from . import DOMAIN, GatewayGenericDevice
from .core.const import (
    ATTR_ANGLE,
    ATTR_CHIP_TEMPERATURE,
    ATTR_ELAPSED_TIME,
    ATTR_FW_VER,
    ATTR_DENSITY,
    ATTR_LQI,
    ATTR_OPEN_SINCE,
    BATTERY,
    BUTTON,
    BUTTON_BOTH,
    CHIP_TEMPERATURE,
    CONF_INVERT_STATE,
    CONF_OCCUPANCY_TIMEOUT,
    CUBE,
    ELAPSED_TIME,
    FW_VER,
    GAS_DENSITY,
    NO_CLOSE,
    LQI,
    VOLTAGE,
    VIBRATION,
    SMOKE_DENSITY,
)
from .core.gateway import Gateway


async def async_setup_entry(hass, config_entry, async_add_entities):
    """ Perform the setup for Xiaomi/Aqara devices. """
    def setup(gateway: Gateway, device: dict, attr: str):
        if attr == 'action':
            async_add_entities([GatewayAction(gateway, device, attr)])
        elif attr == 'switch':
            async_add_entities([GatewayButtonSwitch(gateway, device, attr)])
        elif attr == 'contact':
            async_add_entities([GatewayDoorSensor(gateway, device, attr)])
        elif attr == 'gas':
            async_add_entities([GatewayNatgasSensor(gateway, device, attr)])
        elif attr == 'smoke':
            async_add_entities([GatewaySmokeSensor(gateway, device, attr)])
        elif attr == 'motion':
            async_add_entities([GatewayMotionSensor(gateway, device, attr)])
        elif attr == 'moisture':
            async_add_entities([GatewayWaterLeakSensor(gateway, device, attr)])
        elif attr == 'door_state':  # door state
            async_add_entities([GatewayLockDoorState(gateway, device, attr)])
        elif attr in ['auto locking', 'lock by handle']:  # lock state
            async_add_entities([GatewayLockLockState(gateway, device, attr)])
        elif attr == 'latch_state':  # latch state
            async_add_entities([GatewayLockLatchState(gateway, device, attr)])
        else:
            async_add_entities([GatewayCommonBinarySensor(gateway, device, attr)])

    aqara_gateway: Gateway = hass.data[DOMAIN][config_entry.entry_id]
    aqara_gateway.add_setup('binary_sensor', setup)


DESCRIPTIONS = {
    'contact': BinarySensorEntityDescription(
        key='contact',
        device_class=BinarySensorDeviceClass.DOOR,
    ),
    'door': BinarySensorEntityDescription(
        key='door',
        device_class=BinarySensorDeviceClass.DOOR,
    ),
    'door_state': BinarySensorEntityDescription(
        key='door_state',
        device_class=BinarySensorDeviceClass.DOOR,
    ),
    'gas': BinarySensorEntityDescription(
        key='gas',
        device_class=BinarySensorDeviceClass.GAS,
    ),
    'lock': BinarySensorEntityDescription(
        key='lock',
        device_class=BinarySensorDeviceClass.LOCK,
    ),
    'latch_state': BinarySensorEntityDescription(
        key='latch_state',
        device_class=BinarySensorDeviceClass.LOCK,
    ),
    'auto locking': BinarySensorEntityDescription(
        key='auto locking',
        device_class=BinarySensorDeviceClass.LOCK,
    ),
    'lock by handle': BinarySensorEntityDescription(
        key='lock by handle',
        device_class=BinarySensorDeviceClass.LOCK,
    ),
    'moisture': BinarySensorEntityDescription(
        key='moisture',
        device_class=BinarySensorDeviceClass.MOISTURE,
    ),
    'motion': BinarySensorEntityDescription(
        key='motion',
        device_class=BinarySensorDeviceClass.MOTION,
    ),
    'occupancy': BinarySensorEntityDescription(
        key='occupancy',
        device_class=BinarySensorDeviceClass.OCCUPANCY,
    ),
    'smoke': BinarySensorEntityDescription(
        key='smoke',
        device_class=BinarySensorDeviceClass.SMOKE,
    ),
    'action': BinarySensorEntityDescription(
        key='action',
        icon='hass:radiobox-blank',
    ),
    'switch': BinarySensorEntityDescription(
        key='switch',
        icon='hass:radiobox-blank',
    ),
}


class GatewayBinarySensor(GatewayGenericDevice, BinarySensorEntity):
    """Representation of a Xiaomi/Aqara Binary Sensor."""

    _battery = None
    _chip_temperature = None
    _fw_ver = None
    _lqi = None
    _voltage = None

    is_metric = False

    def __init__(self, gateway: Gateway, device: dict, attr: str):
        """Initialize the Xiaomi/Aqara Binary Sensor."""
        super().__init__(gateway, device, attr)
        if attr in DESCRIPTIONS:
            self.entity_description = DESCRIPTIONS[attr]

    def update(self, data: dict):
        for key, value in data.items():
            if key == BATTERY:
                self._battery = value
            if key == CHIP_TEMPERATURE:
                if self.is_metric:
                    self._chip_temperature = (
                        format((int(value) - 32) * 5 / 9, '.2f')
                        if isinstance(value, (int, float))
                        else None
                    )
                else:
                    self._chip_temperature = value
            if key == FW_VER:
                self._fw_ver = value
            if key == LQI:
                self._lqi = value
            if key == VOLTAGE:
                self._voltage = (
                    format(float(value) / 1000, '.3f')
                    if isinstance(value, (int, float))
                    else None
                )
        self.schedule_update_ha_state()


class GatewayRestoredBinarySensor(GatewayBinarySensor, RestoreEntity):
    """Representation of a Xiaomi/Aqara Binary Sensor with restored data."""

    async def async_added_to_hass(self):
        """Run when entity about to be added to hass."""
        if last_state := await self.async_get_last_state():
            if last_state.state == STATE_ON:
                self._attr_is_on = True
            elif last_state.state == STATE_OFF:
                self._attr_is_on = False
        await super().async_added_to_hass()


class GatewayCommonBinarySensor(GatewayRestoredBinarySensor):
    """Representation of a Xiaomi/Aqara Common Binary Sensor."""

    def update(self, data: dict):
        """ update common binary sensor """
        super().update(data)

        if self._attr in data:
            value = data[self._attr]
            custom = self.hass.data[DATA_CUSTOMIZE].get(self.entity_id)
            if not custom.get(CONF_INVERT_STATE):
                self._attr_is_on = bool(value)
            else:
                self._attr_is_on = not value

        self.schedule_update_ha_state()


class GatewayNatgasSensor(GatewayRestoredBinarySensor):
    """Representation of a Xiaomi/Aqara Natgas Sensor."""

    _density: int | None = None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attrs = {
            ATTR_CHIP_TEMPERATURE: self._chip_temperature,
            ATTR_DENSITY: self._density,
            ATTR_FW_VER: self._fw_ver,
            ATTR_LQI: self._lqi,
        }
        return attrs

    def update(self, data: dict):
        """ update Natgas sensor """
        super().update(data)

        if self._attr in data:
            value = data[self._attr]
            custom = self.hass.data[DATA_CUSTOMIZE].get(self.entity_id)
            if not custom.get(CONF_INVERT_STATE):
                self._attr_is_on = bool(value)
            else:
                self._attr_is_on = not value

        if GAS_DENSITY in data:
            self._density = int(data[GAS_DENSITY])

        self.schedule_update_ha_state()


class GatewayMotionSensor(GatewayBinarySensor):
    """Representation of a Xiaomi/Aqara Motion Sensor."""

    def __init__(self, gateway: Gateway, device: dict, attr: str):
        """Initialize the Xiaomi/Aqara Motion Sensor."""
        super().__init__(gateway, device, attr)

        self._attr_is_on = False

        self._default_delay = None
        self._last_on = 0
        self._last_off = 0
        self._timeout_pos = 0
        self._unsub_set_no_motion = None
        self._open_since = None

    async def async_added_to_hass(self):
        """ add to hass """
        # old version
        self._default_delay = self.device.get(CONF_OCCUPANCY_TIMEOUT, 90)

        custom: dict = self.hass.data[DATA_CUSTOMIZE].get(self.entity_id)
        custom.setdefault(CONF_OCCUPANCY_TIMEOUT, self._default_delay)

        await super().async_added_to_hass()

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        self._attrs[ATTR_BATTERY_LEVEL] = self._battery
        self._attrs[ATTR_CHIP_TEMPERATURE] = self._chip_temperature
        self._attrs[ATTR_LQI] = self._lqi
        self._attrs[ATTR_VOLTAGE] = self._voltage
        return self._attrs

    async def _start_no_motion_timer(self, delay: float):
        if self._unsub_set_no_motion:
            self._unsub_set_no_motion()

        self._unsub_set_no_motion = async_call_later(
            self.hass, abs(delay), self._set_no_motion)

    async def _set_no_motion(self, *args):
        self._last_off = time.time()
        self._timeout_pos = 0
        self._unsub_set_no_motion = None
        self._attr_is_on = False
        self.schedule_update_ha_state()

        # repeat event from Aqara integration
        self.hass.bus.fire('xiaomi_aqara.motion', {
            'entity_id': self.entity_id
        })

    def update(self, data: dict):
        """ update motion sensor """
        super().update(data)

        # https://github.com/AlexxIT/XiaomiGateway3/issues/135
        if 'illuminance' in data and ('lumi.sensor_motion.aq2' in
                                      self.device['device_model']):
            data[self._attr] = 1

        for key, value in data.items():
            if key == NO_CLOSE:  # handle push from the hub
                self._open_since = value
            if key == ELAPSED_TIME:
                self._attrs[ATTR_ELAPSED_TIME] = data[ELAPSED_TIME]

        # check only motion=1
        if data.get(self._attr) != 1:
            # handle available change
            self.schedule_update_ha_state()
            return

        # fix 1.4.7_0115 heartbeat error (has motion in heartbeat)
        if 'battery' in data:
            # handle available change
            self.schedule_update_ha_state()
            return

        # check only motion=1
        assert data[self._attr] == 1, data

        # don't trigger motion right after illumination
        time_now = time.time()
        if time_now - self._last_on < 1:
            return

        self._attr_is_on = True
        self._attrs[ATTR_LAST_TRIGGERED] = now().isoformat(timespec='seconds')
        self._last_on = time_now

        # handle available change
        self.schedule_update_ha_state()

        if self._unsub_set_no_motion:
            self._unsub_set_no_motion()

        custom = self.hass.data[DATA_CUSTOMIZE].get(self.entity_id)
        # if customize of any entity will be changed from GUI - default value
        # for all motion sensors will be erased
        timeout = custom.get(CONF_OCCUPANCY_TIMEOUT, self._default_delay)
        if timeout:
            if isinstance(timeout, list):
                pos = min(self._timeout_pos, len(timeout) - 1)
                delay = timeout[pos]
                self._timeout_pos += 1
            else:
                delay = timeout

            if delay < 0 and time_now + delay < self._last_off:
                delay *= 2

            self.hass.add_job(self._start_no_motion_timer, delay)

        # repeat event from Aqara integration
        self.hass.bus.fire('xiaomi_aqara.motion', {
            'entity_id': self.entity_id
        })


class GatewayDoorSensor(GatewayRestoredBinarySensor):
    """Representation of a Xiaomi/Aqara Door Sensor."""

    def __init__(self, gateway: Gateway, device: dict, attr: str):
        """Initialize the Xiaomi/Aqara Door Sensor."""
        super().__init__(gateway, device, attr)
        self._open_since = None
        self.is_metric = True
        self.has_since = False
        if device['model'] in (
                'lumi.sensor_magnet.aq2', 'lumi.magnet.agl02', 'lumi.magnet.ac01'):
            self.is_metric = False
            self.has_since = True

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attrs = {
            ATTR_BATTERY_LEVEL: self._battery,
            ATTR_LQI: self._lqi,
            ATTR_VOLTAGE: self._voltage,
            ATTR_CHIP_TEMPERATURE: self._chip_temperature,
        }
        if self.has_since:
            attrs[ATTR_OPEN_SINCE] = self._open_since
        return attrs

    def update(self, data: dict):
        """ update door sensor """
        super().update(data)

        if self._attr in data:
            value = data[self._attr]
            if self.device['model'] == 'lumi.magnet.acn001' and self.gateway.cloud == "miot":
                value = not value
            custom = self.hass.data[DATA_CUSTOMIZE].get(self.entity_id)
            if not custom.get(CONF_INVERT_STATE):
                self._attr_is_on = bool(value)
            else:
                self._attr_is_on = not value

        if NO_CLOSE in data:  # handle push from the hub
            self._open_since = data[NO_CLOSE]

        self.schedule_update_ha_state()


class GatewayWaterLeakSensor(GatewayRestoredBinarySensor):
    """Representation of a Xiaomi/Aqara Water Leak Sensor."""

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attrs = {
            ATTR_BATTERY_LEVEL: self._battery,
            ATTR_CHIP_TEMPERATURE: self._chip_temperature,
            ATTR_LQI: self._lqi,
            ATTR_VOLTAGE: self._voltage,
        }
        return attrs

    def update(self, data: dict):
        """ update water leak sensor """
        super().update(data)

        if self._attr in data:
            value = data[self._attr]
            custom = self.hass.data[DATA_CUSTOMIZE].get(self.entity_id)
            if not custom.get(CONF_INVERT_STATE):
                self._attr_is_on = bool(value)
            else:
                self._attr_is_on = not value

        self.schedule_update_ha_state()


class GatewaySmokeSensor(GatewayRestoredBinarySensor):
    """Representation of a Xiaomi/Aqara Smoke Sensor."""

    _density: int | None = None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attrs = {
            ATTR_CHIP_TEMPERATURE: self._chip_temperature,
            ATTR_DENSITY: self._density,
            ATTR_FW_VER: self._fw_ver,
            ATTR_LQI: self._lqi,
            ATTR_VOLTAGE: self._voltage,
        }
        return attrs

    def update(self, data: dict):
        """update smoke sensor"""
        super().update(data)

        if self._attr in data:
            value = data[self._attr]
            custom = self.hass.data[DATA_CUSTOMIZE].get(self.entity_id)
            if not custom.get(CONF_INVERT_STATE):
                self._attr_is_on = bool(value)
            else:
                self._attr_is_on = not value

        if SMOKE_DENSITY in data:
            self._density = int(data[SMOKE_DENSITY])

        self.schedule_update_ha_state()


class GatewayButtonSwitch(GatewayBinarySensor):
    """Xiaomi/Aqara Button Switch"""

    def __init__(self, gateway: Gateway, device: dict, attr: str):
        """Initialize the Xiaomi/Aqara Button Switch."""
        super().__init__(gateway, device, attr)
        self._state = ''
        if device['model'] == 'lumi.sensor_switch':
            self.is_metric = True

    @property
    def state(self):
        """return state."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attrs = {
            ATTR_BATTERY_LEVEL: self._battery,
            ATTR_CHIP_TEMPERATURE: self._chip_temperature,
            ATTR_LQI: self._lqi,
            ATTR_VOLTAGE: self._voltage,
        }
        return attrs

    def update(self, data: dict):
        """update Button Switch."""
        super().update(data)

        for key, value in data.items():
            if ":" in key:
                value = int(key.split(":")[1])
                key = key.split(":")[0]

            if key == 'button':
                if 'voltage' in data:
                    return
                data[self._attr] = BUTTON.get(
                    value, 'unknown')
                break
            if key.startswith('button_both'):
                data[self._attr] = key + '_' + BUTTON_BOTH.get(
                    value, 'unknown')
                break
            if key.startswith('button'):
                data[self._attr] = key + '_' + BUTTON.get(
                    value, 'unknown')
                break

        if self._attr in data:
            self._state = data[self._attr]
            self.async_write_ha_state()

            # repeat event from Aqara integration
            self.hass.bus.async_fire('xiaomi_aqara.click', {
                'entity_id': self.entity_id, 'click_type': self._state
            })

            # time.sleep(.1)

            # self._state = ''

            # reset the state to empty after 0.1 second
            self.hass.loop.call_later(.1, self.reset_state)

        self.schedule_update_ha_state()

    def reset_state(self):
        self._state = ''
        self.async_write_ha_state()


class GatewayAction(GatewayBinarySensor):
    """ Xiaomi/Aqara Action Cube """

    def __init__(self, gateway: Gateway, device: dict, attr: str):
        """Initialize the Xiaomi/Aqara Action Cube."""
        super().__init__(gateway, device, attr)
        self._state = ''
        self._rotate_angle = None
        self.with_rotation = False
        if (device['model'] in ('lumi.remote.rkba01', 'lumi.switch.rkna01',
                'lumi.remote.cagl01', 'lumi.remote.cagl02')):
            self.with_rotation = True
        if device['model'] == 'lumi.motion.agl04':
            self.is_metric = True

    @property
    def state(self):
        """return state."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        self._attrs[ATTR_BATTERY_LEVEL] = self._battery
        self._attrs[ATTR_CHIP_TEMPERATURE] = self._chip_temperature
        self._attrs[ATTR_LQI] = self._lqi
        self._attrs[ATTR_VOLTAGE] = self._voltage

        if self.with_rotation:
            self._attrs[ATTR_ANGLE] = self._rotate_angle
        return self._attrs

    def update(self, data: dict):
        """update Button Switch."""
        super().update(data)

        if self.with_rotation:
            self._rotate_angle = None
        for key, value in data.items():
            # skip tilt and wait tilt_angle
            if key == 'vibration' and value != 2:
                data[self._attr] = VIBRATION.get(value, 'unknown')
                break
            if key == 'tilt_angle':
                data = {'vibration': 2, 'angle': value, self._attr: 'tilt'}
                break
            if key == 'rotate_angle':
                rotation = BUTTON.get(data.get('button', 0), 'unknown')
                duration = data.get('action_duration', 'unknown')
                if rotation != 'unknown':
                    data = {'duration': duration,
                            'angle': value, self._attr: rotation}
                self._rotate_angle = value
                break
            if key == 'triple_click':
                data = {'triple_click': value, self._attr: 'triple'}
                break
            if key == 'action':
                if 'voltage' in data:
                    return
                data[self._attr] = CUBE.get(value, 'unknown')
                break
            if key.startswith('action'):
                data[self._attr] = key + '_' + CUBE.get(value, 'unknown')
                break
            if key in ('mode', 'vibration_level', 'detect_interval',
                    'vibrate_intensity_level', 'report_interval_level'):
                self._attrs[key] = value
                break
            if key.startswith('scense'):
                data[self._attr] = key + '_' + str(value)
                break

        if self._attr in data:
            self._state = data[self._attr]
            self.async_write_ha_state()

            # repeat event from Aqara integration
            self.hass.bus.async_fire('xiaomi_aqara.click', {
                'entity_id': self.entity_id, 'click_type': self._state
            })

            # reset the state to empty after 0.1 second
            self.hass.loop.call_later(.1, self.reset_state)

        self.schedule_update_ha_state()

    def reset_state(self):
        self._state = ''
        self.async_write_ha_state()


# guess door/lock/latch state from 'door' attr
# True means open or unlocked
# False means closed or locked
STATES_FROM_DOOR = {
    2: {"door": True, "lock": True, "latch": True},  # The door is not closed
    3: {"door": False, "lock": True, "latch": True},  # The door is not locked
    4: {"door": False, "lock": False, "latch": True},  # The door is locked
    5: {"door": False, "lock": True, "latch": False},  # The door is auti-locked
    6: {"door": False, "lock": True, "latch": True},  # The door is unlocked
    7: {"door": False, "lock": False, "latch": False},  # The door is locked and auti-locked
}


class GatewayLockDoorState(GatewayRestoredBinarySensor):
    """
    Door state of an Aqara Door Lock.
    _attr: 'door_state'
    """

    # Get door state from 'door_state' attr
    # True means open, False means closed
    DOOR_STATE_MAP = {
        0: True,  # Door is open
        1: False,  # Door is closed
        2: True,  # Door is not close
        4: True,  # Lock is damaged
        5: True,  # Door is concealed
    }

    def update(self, data: dict):
        super().update(data)
        if "lock" in data:
            value = data["lock"]
            if value in GatewayLockDoorState.DOOR_STATE_MAP:
                self._attr_is_on = GatewayLockDoorState.DOOR_STATE_MAP[value]
                self.async_write_ha_state()
        elif "door" in data:
            value = data["door"]
            if value in STATES_FROM_DOOR:
                self._attr_is_on = STATES_FROM_DOOR[value]["door"]
                self.async_write_ha_state()


class GatewayLockLockState(GatewayRestoredBinarySensor):
    """
    Lock state of an Aqara Door Lock.
    _attr: 'auto locking' or 'lock by handle'
    """

    def update(self, data: dict):
        super().update(data)
        if self._attr in data:  # _attr: 'auto locking' or 'lock by handle'
            self._attr_is_on = not data[self._attr]  # 1: Locked
            self.async_write_ha_state()
        elif "door" in data:
            value = data["door"]
            if value in STATES_FROM_DOOR:
                self._attr_is_on = STATES_FROM_DOOR[value]["lock"]
                self.async_write_ha_state()


class GatewayLockLatchState(GatewayRestoredBinarySensor):
    """
    Latch state of an Aqara Door Lock.
    _attr: 'latch_state'
    """

    def update(self, data: dict):
        super().update(data)
        if self._attr in data:  # _attr: 'latch_state'
            self._attr_is_on = not data[self._attr]  # 0: Unlocked 1: Locked
            self.async_write_ha_state()
        elif "door" in data:
            value = data["door"]
            if value in STATES_FROM_DOOR:
                self._attr_is_on = STATES_FROM_DOOR[value]["latch"]
                self.async_write_ha_state()
