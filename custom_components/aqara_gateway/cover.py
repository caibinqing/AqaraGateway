"""Support for Xiaomi curtain."""
from typing import Any

from homeassistant.components.cover import (
    ATTR_CURRENT_POSITION,
    ATTR_CURRENT_TILT_POSITION,
    ATTR_POSITION,
    ATTR_TILT_POSITION,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from . import GatewayGenericDevice
from .core.const import DOMAIN
from .core.gateway import Gateway


ATTR_RUN_STATE = 'run_state'


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Perform the setup for Xiaomi devices."""
    def setup(gateway: Gateway, device: dict, attr: str) -> None:
        if device['model'] == 'lumi.curtain.acn002':
            async_add_entities([AqaraRollerShadeE1(gateway, device, attr)])
        elif device['model'] == 'lumi.curtain.acn011':
            async_add_entities([AqaraVerticalBlindsController(gateway, device, attr)])
        else:
            if device.get('mi_spec') or device['model'] == 'lumi.airer.acn001':
                async_add_entities([XiaomiCoverMIOT(gateway, device, attr)])
            else:
                async_add_entities([XiaomiGenericCover(gateway, device, attr)])

    aqara_gateway: Gateway = hass.data[DOMAIN][config_entry.entry_id]
    aqara_gateway.add_setup('cover', setup)


class XiaomiGenericCover(GatewayGenericDevice, CoverEntity, RestoreEntity):
    """Representation of a XiaomiGenericCover."""

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        if (last_state := await self.async_get_last_state()) is not None:
            if ATTR_CURRENT_POSITION in last_state.attributes:
                position = last_state.attributes[ATTR_CURRENT_POSITION]
                self._attr_current_cover_position = position
        await super().async_added_to_hass()

    @property
    def is_closed(self) -> bool | None:
        """Return if the cover is closed."""
        if (position := self.current_cover_position) is None:
            return None
        return position < 5

    def update(self, data: dict) -> None:
        """Update state."""
        if ATTR_POSITION in data:
            self._attr_current_cover_position = data[ATTR_POSITION]
        if ATTR_RUN_STATE in data:
            value = data[ATTR_RUN_STATE]
            self._attr_is_opening = value == 1
            self._attr_is_closing = value == 0
        self.schedule_update_ha_state()

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close cover."""
        self.gateway.send(self.device, {'position': 0})

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        self.gateway.send(self.device, {'position': 100})

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover."""
        self.gateway.send(self.device, {'motor': 2})

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Move the cover to a specific position."""
        if (position := kwargs.get(ATTR_POSITION)) is not None:
            self.gateway.send(self.device, {'position': position})


class XiaomiCoverMIOT(XiaomiGenericCover):
    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        self.gateway.send(self.device, {'motor': 2})

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close cover."""
        self.gateway.send(self.device, {'motor': 1})

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover."""
        self.gateway.send(self.device, {'motor': 0})

    async def async_open_cover_tilt(self, **kwargs: Any) -> None:
        """Open the cover tilt."""
        self.gateway.send(self.device, {'motor': 5})

    async def async_close_cover_tilt(self, **kwargs: Any) -> None:
        """Close the cover tilt."""
        self.gateway.send(self.device, {'motor': 6})


class AqaraRollerShadeE1(XiaomiGenericCover):
    """ Aqara Roller Shade E1 (lumi.curtain.acn002) """

    _attr_supported_features: CoverEntityFeature = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.SET_POSITION
        | CoverEntityFeature.STOP
        | CoverEntityFeature.OPEN_TILT
        | CoverEntityFeature.CLOSE_TILT
    )

    def __init__(self, gateway: Gateway, device: dict, attr: str) -> None:
        super().__init__(gateway, device, attr)
        self._mi_mode = True if device.get('mi_spec') else False

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover."""
        if self._mi_mode:
            self.gateway.send(self.device, {'motor': 0})
        else:
            self.gateway.send(self.device, {'motor': 2})

    async def async_open_cover_tilt(self, **kwargs: Any) -> None:
        """Open the cover tilt."""
        if self._mi_mode:
            self.gateway.send(self.device, {'motor': 4})
        else:
            self.gateway.send(self.device, {'motor': 6})

    async def async_close_cover_tilt(self, **kwargs: Any) -> None:
        """Close the cover tilt."""
        if self._mi_mode:
            self.gateway.send(self.device, {'motor': 3})
        else:
            self.gateway.send(self.device, {'motor': 5})


class AqaraVerticalBlindsController(XiaomiGenericCover):

    _attr_supported_features: CoverEntityFeature = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.STOP
        | CoverEntityFeature.SET_POSITION
        | CoverEntityFeature.OPEN_TILT
        | CoverEntityFeature.CLOSE_TILT
        | CoverEntityFeature.STOP_TILT
        | CoverEntityFeature.SET_TILT_POSITION
    )

    _tilt_angle: int | None = None  # -90~90

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        if (last_state := await self.async_get_last_state()) is not None:
            if (tilt_position := last_state.attributes.get(ATTR_CURRENT_TILT_POSITION)) is not None:  # 0~100
                self._tilt_angle = 90 - (tilt_position / 100 * 90)
        await super().async_added_to_hass()

    def update(self, data: dict) -> None:
        """Update state."""
        if ATTR_TILT_POSITION in data:
            value = data[ATTR_TILT_POSITION]  # value is -90~90
            self._tilt_angle = value
        if ATTR_POSITION in data:
            # clear `opening` or `closing` when receiving `position`
            self._attr_is_opening = False
            self._attr_is_closing = False
        super().update(data)

    @property
    def current_cover_tilt_position(self) -> int | None:
        """Return current position of cover tilt.

        None is unknown, 0 is closed, 100 is fully open.
        """
        if self._tilt_angle is None:
            return None
        return int((90 - abs(self._tilt_angle)) / 90 * 100)

    async def async_open_cover_tilt(self, **kwargs: Any) -> None:
        """Open the cover tilt."""
        self.gateway.send(self.device, {'tilt_position': 0})

    async def async_close_cover_tilt(self, **kwargs: Any) -> None:
        """Close the cover tilt."""
        self.gateway.send(self.device, {'tilt_position': -90})

    async def async_set_cover_tilt_position(self, **kwargs: Any) -> None:
        """Move the cover tilt to a specific position."""
        tilt_position = kwargs.get(ATTR_TILT_POSITION)  # 0~100
        if (self._tilt_angle or 0) >= 0:
            self.gateway.send(self.device, {'tilt_position': 90 - (tilt_position / 100 * 90)})  # 0~90
        else:
            self.gateway.send(self.device, {'tilt_position': (tilt_position / 100 * 90) - 90})  # -90~0

    async def async_stop_cover_tilt(self, **kwargs: Any) -> None:
        """Stop the cover."""
        self.gateway.send(self.device, {'tilt_motor': 2})
