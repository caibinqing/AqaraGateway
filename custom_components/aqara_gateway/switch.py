"""Support for Aqara Switches."""
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from . import DOMAIN, GatewayGenericDevice
from .core.gateway import Gateway


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """ Perform the setup for Xiaomi/Aqara devices. """
    def setup(gateway: Gateway, device: dict, attr: str):
        async_add_entities([GatewaySwitch(gateway, device, attr)])
    aqara_gateway: Gateway = hass.data[DOMAIN][config_entry.entry_id]
    aqara_gateway.add_setup('switch', setup)


class GatewaySwitch(GatewayGenericDevice, SwitchEntity, RestoreEntity):
    """Representation of a Xiaomi/Aqara Plug."""

    _attr_icon: str | None = "mdi:power-socket"

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        if last_state := await self.async_get_last_state():
            if last_state.state == STATE_ON:
                self._attr_is_on = True
            elif last_state.state == STATE_OFF:
                self._attr_is_on = False
        await super().async_added_to_hass()

    def update(self, data: dict) -> None:
        """update switch."""
        if self._attr in data:
            self._attr_is_on = bool(data[self._attr])
            self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        self.gateway.send(self.device, {self._attr: 1})

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        self.gateway.send(self.device, {self._attr: 0})
