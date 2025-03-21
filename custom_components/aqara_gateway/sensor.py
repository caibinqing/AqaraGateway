"""Support for Xiaomi Aqara sensors."""

from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    ATTR_BATTERY_LEVEL,
    ATTR_VOLTAGE,
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_BILLION,
    CONCENTRATION_PARTS_PER_MILLION,
    EntityCategory,
    LIGHT_LUX,
    PERCENTAGE,
    STATE_PROBLEM,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfPressure,
    UnitOfTemperature,
)

from . import DOMAIN, GatewayGenericDevice
from .core.const import (
    APPROACHING_DISTANCE,
    ATTR_APPROACHING_DISTANCE,
    ATTR_CHIP_TEMPERATURE,
    ATTR_DETECTING_REGION,
    ATTR_EXITS_ENTRANCES_REGION,
    ATTR_FW_VER,
    ATTR_INTERFERENCE_REGION,
    ATTR_LATCH_STATUS,
    ATTR_LI_BATTERY,
    ATTR_LI_BATTERY_TEMP,
    ATTR_LOCK_STATUS,
    ATTR_LQI,
    ATTR_MONITORING_MODE,
    ATTR_NOTIFICATION,
    ATTR_REVERTED_MODE,
    BACK_VERSION,
    BATTERY,
    CHIP_TEMPERATURE,
    DETECTING_REGION,
    EXITS_ENTRANCES_REGION,
    INTERFERENCE_REGION,
    LATCH_STATUS,
    LATCH_STATUS_TYPE,
    LI_BATTERY,
    LI_BATTERY_TEMP,
    LOAD_POWER,
    LOCK_STATE,
    LOCK_STATUS_TYPE,
    LQI,
    MONITORING_MODE,
    POWER,
    REVERTED_MODE,
    VOLTAGE,
)
from .core.gateway import Gateway
from .core.lock_data import DEVICE_MAPPINGS, LOCK_NOTIFICATION, WITH_LI_BATTERY
from .core.utils import Utils


async def async_setup_entry(hass, entry, async_add_entities):
    """ setup config entry """
    def setup(gateway: Gateway, device: dict, attr: str):
        if attr == 'gas density':
            async_add_entities([GatewayGasSensor(gateway, device, attr)])
        elif attr == 'lock':
            async_add_entities([GatewayLockSensor(gateway, device, attr)])
        elif attr == 'key_id':
            async_add_entities([GatewayKeyIDSensor(gateway, device, attr)])
        elif attr == 'lock_event':
            async_add_entities([GatewayLockEventSensor(gateway, device, attr)])
        elif attr == 'illuminance':
            if (device['type'] == 'gateway' and
                    Utils.gateway_illuminance_supported(device['model'])):
                async_add_entities([GatewaySensor(gateway, device, attr)])
            elif device['type'] == 'zigbee':
                async_add_entities([GatewaySensor(gateway, device, attr)])
        elif attr == 'movements':
            async_add_entities([GatewayMoveSensor(gateway, device, attr)])
        elif attr == 'occupancy_region':
            async_add_entities([GatewayOccupancyRegionSensor(gateway, device, attr)])
        else:
            async_add_entities([GatewaySensor(gateway, device, attr)])

    aqara_gateway: Gateway = hass.data[DOMAIN][entry.entry_id]
    aqara_gateway.add_setup('sensor', setup)


async def async_unload_entry(hass, entry):
    # pylint: disable=unused-argument
    """ unload entry """
    return True


DESCRIPTIONS = {
    'temperature': SensorEntityDescription(
        key='temperature',
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    'humidity': SensorEntityDescription(
        key='humidity',
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    'illuminance': SensorEntityDescription(
        key='illuminance',
        device_class=SensorDeviceClass.ILLUMINANCE,
        native_unit_of_measurement=LIGHT_LUX,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    'pressure': SensorEntityDescription(
        key='pressure',
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.HPA,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    'battery': SensorEntityDescription(
        key='battery',
        device_class=SensorDeviceClass.BATTERY,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    'li battery': SensorEntityDescription(
        key='li_battery',
        device_class=SensorDeviceClass.BATTERY,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    'power': SensorEntityDescription(
        key='power',
        device_class=SensorDeviceClass.POWER,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    'consumption': SensorEntityDescription(
        key='energy',
        device_class=SensorDeviceClass.ENERGY,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    'carbon_dioxide': SensorEntityDescription(
        key='co2',
        device_class=SensorDeviceClass.CO2,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    'pm25': SensorEntityDescription(
        key='pm25',
        device_class=SensorDeviceClass.PM25,
        icon='mdi:air-filter',
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    'pm10': SensorEntityDescription(
        key='pm10',
        device_class=SensorDeviceClass.PM10,
        icon='mdi:air-filter',
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    'pm1': SensorEntityDescription(
        key='pm1',
        device_class=SensorDeviceClass.PM1,
        icon='mdi:air-filter',
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    'tvoc': SensorEntityDescription(
        key='tvoc',
        device_class=SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS,
        icon='mdi:cloud',
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_BILLION,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    'gas density': SensorEntityDescription(
        key='gas_density',
        icon='mdi:google-circles-communities',
        native_unit_of_measurement='% LEL',
        state_class=SensorStateClass.MEASUREMENT,
    ),
    'smoke density': SensorEntityDescription(
        key='smoke_density',
        icon='mdi:google-circles-communities',
        native_unit_of_measurement='% obs/ft',
        state_class=SensorStateClass.MEASUREMENT,
    ),
    'gateway': SensorEntityDescription(
        key='gateway',
        device_class=SensorDeviceClass.TIMESTAMP,
        icon='mdi:router-wireless',
    ),
    'zigbee': SensorEntityDescription(
        key='zigbee',
        device_class=SensorDeviceClass.TIMESTAMP,
        icon='mdi:zigbee',
    ),
    'key_id': SensorEntityDescription(
        key='key_id',
        icon='mdi:key',
    ),
    'lock': SensorEntityDescription(
        key='lock',
        icon='mdi:lock',
    ),
    'lock_event': SensorEntityDescription(
        key='lock_event',
        icon='mdi:lock',
    ),
    'movements': SensorEntityDescription(
        key='movements',
        icon='mdi:page-layout-body',
    ),
    'occupancy_region': SensorEntityDescription(
        key='occupancy_region',
        icon='mdi:square-opacity',
    ),
}


class GatewaySensor(GatewayGenericDevice, RestoreSensor):
    """ Xiaomi/Aqara Sensors """

    def __init__(self, gateway: Gateway, device: dict, attr: str):
        """Initialize the Xiaomi/Aqara Sensors."""
        super().__init__(gateway, device, attr)
        if attr in DESCRIPTIONS:
            self.entity_description = DESCRIPTIONS[attr]

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        if last_state := await self.async_get_last_sensor_data():
            self._attr_native_value = last_state.native_value
        await super().async_added_to_hass()

    def update(self, data: dict) -> None:
        """update sensor."""
        for key, value in data.items():
            if self._attr == POWER and LOAD_POWER in data:
                self._attr_native_value = data[LOAD_POWER]
            if self._attr == key:
                self._attr_native_value = data[key]
        self.async_write_ha_state()


class GatewayGasSensor(GatewaySensor):
    """ Xiaomi/Aqara Gas sensor """

    def update(self, data: dict) -> None:
        """update sensor."""
        if 'gas' in data:
            self._attr_native_value = data['gas']
        self.async_write_ha_state()


class GatewayLockSensor(GatewaySensor):
    """Representation of a Aqara Lock."""

    def __init__(self, gateway: Gateway, device: dict, attr: str):
        """Initialize the Aqara lock device."""
        super().__init__(gateway, device, attr)
        self._features = DEVICE_MAPPINGS[self.device['model']]
        self._battery = None
        self._fw_ver = None
        self._li_battery = None
        self._li_battery_temperature = None
        self._lqi = None
        self._voltage = None
        self._notification = "Unknown"
        self._lock_status = None
        self._latch_status = None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attrs = {
            ATTR_BATTERY_LEVEL: self._battery,
            ATTR_FW_VER: self._fw_ver,
            ATTR_LQI: self._lqi,
            ATTR_VOLTAGE: self._voltage,
            ATTR_LOCK_STATUS: self._lock_status,
            ATTR_LATCH_STATUS: self._latch_status,
            ATTR_NOTIFICATION: self._notification,
        }
        if self._features & WITH_LI_BATTERY:
            attrs[ATTR_LI_BATTERY] = self._li_battery
            attrs[ATTR_LI_BATTERY_TEMP] = self._li_battery_temperature
        return attrs

    def update(self, data: dict) -> None:
        """ update lock state """
        # handle available change
        for key, value in data.items():
            if key == BATTERY:
                self._battery = value
            if key == BACK_VERSION:
                self._fw_ver = value
            if key == LI_BATTERY:
                self._li_battery = value
            if key == LI_BATTERY_TEMP:
                self._li_battery_temperature = value / 10
            if key == LQI:
                self._lqi = value
            if key == VOLTAGE:
                self._voltage = format(
                    float(value) / 1000, '.3f') if isinstance(
                    value, (int, float)) else None
            if key == LATCH_STATUS:
                self._latch_status = LATCH_STATUS_TYPE.get(
                    str(value), str(value))
            if key in LOCK_NOTIFICATION:
                notify = LOCK_NOTIFICATION[key]
                self._notification = notify.get(
                    str(value), None) if notify.get(
                    str(value), None) else notify.get("default")
            if key == self._attr:
                self._attr_native_value = LOCK_STATE.get(str(value), STATE_PROBLEM)
                self._lock_status = LOCK_STATUS_TYPE.get(
                    str(value), str(value))
        self.async_write_ha_state()


class GatewayKeyIDSensor(GatewaySensor):
    """Representation of a Aqara Lock Key ID."""

    def update(self, data: dict) -> None:
        """ update lock state """
        # handle available change
        for key, value in data.items():
            if (key == self._attr or "unlock by" in key):
                self._attr_native_value = value
        self.async_write_ha_state()


class GatewayLockEventSensor(GatewaySensor):
    """Representation of a Aqara Lock Event."""

    def update(self, data: dict) -> None:
        """ update lock state """
        # handle available change
        for key, value in data.items():
            if key in LOCK_NOTIFICATION:
                notify = LOCK_NOTIFICATION[key]
                self._attr_native_value = notify.get(str(value), None) if notify.get(
                    str(value), None) else notify.get("default")

        self.async_write_ha_state()


class GatewayMoveSensor(GatewaySensor):
    """Representation of a Aqara Moving Sensor."""

    def update(self, data: dict) -> None:
        """ update move state """
        # handle available change
        for key, value in data.items():
            if key == self._attr:
                self._attr_native_value = value

        if self._attr in data:
            self._attr_native_value = data[self._attr]
            self.async_write_ha_state()

            # repeat event from Aqara integration
            self.hass.bus.async_fire('xiaomi_aqara.click', {
                'entity_id': self.entity_id, 'click_type': self._state
            })

        self.schedule_update_ha_state()


class GatewayOccupancyRegionSensor(GatewaySensor):
    """Representation of a Aqara Occupancy Region Sensor."""

    def __init__(self, gateway: Gateway, device: dict, attr: str) -> None:
        """Initialize the Aqara lock device."""
        super().__init__(gateway, device, attr)
        self._chip_temperature = None
        self._lqi = None
        self._approaching_distance = None
        self._detecting_region = None
        self._exits_entrances_region = None
        self._interference_region = None
        self._monitoring_mode = None
        self._reverted_mode = None

    def update(self, data: dict) -> None:
        """ update move state """
        # handle available change
        for key, value in data.items():
            if key == APPROACHING_DISTANCE:
                self._approaching_distance = value
            if key == DETECTING_REGION:
                self._detecting_region = value
            if key == EXITS_ENTRANCES_REGION:
                self._exits_entrances_region = value
            if key == INTERFERENCE_REGION:
                self._interference_region = value
            if key == MONITORING_MODE:
                self._monitoring_mode = value
            if key == REVERTED_MODE:
                self._reverted_mode = value
            if key == CHIP_TEMPERATURE:
                self._chip_temperature = value
            if key == LQI:
                self._lqi = value

        if self._attr in data:
            self._attr_native_value = data[self._attr]
            self.async_write_ha_state()

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attrs = {
            ATTR_LQI: self._lqi,
            ATTR_CHIP_TEMPERATURE: self._chip_temperature,
            ATTR_APPROACHING_DISTANCE: self._approaching_distance,
            ATTR_DETECTING_REGION: self._detecting_region,
            ATTR_EXITS_ENTRANCES_REGION: self._exits_entrances_region,
            ATTR_INTERFERENCE_REGION: self._interference_region,
            ATTR_MONITORING_MODE: self._monitoring_mode,
            ATTR_REVERTED_MODE: self._reverted_mode
        }
        return attrs
