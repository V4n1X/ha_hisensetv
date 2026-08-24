"""Remote entity: exposes all RemoteNOW keys via remote.send_command."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.remote import RemoteEntity
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_COMMAND_DELAY,
    CONF_ENABLE_WOL,
    CONF_MAC_ETHERNET,
    CONF_MAC_WIFI,
    DEFAULT_COMMAND_DELAY,
    DEFAULT_ENABLE_WOL,
    resolve_key,
)

if TYPE_CHECKING:
    from .__init__ import HisenseConfigEntry

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry: "HisenseConfigEntry", async_add_entities) -> None:  # noqa: ANN001
    """Set up the Hisense TV remote from a config entry."""
    runtime = entry.runtime_data
    async_add_entities([HisenseTvRemote(entry)])


class HisenseTvRemote(CoordinatorEntity, RemoteEntity):
    """Full key remote for a Hisense TV."""

    _attr_has_entity_name = True
    _attr_translation_key = "remote"

    def __init__(self, entry: "HisenseConfigEntry") -> None:
        runtime = entry.runtime_data
        super().__init__(runtime.coordinator)
        self._entry = entry
        self._client = runtime.client
        self._attr_unique_id = f"{entry.entry_id}-remote"

    @property
    def device_info(self):  # noqa: ANN201
        from .__init__ import build_device_info  # noqa: PLC0415

        return build_device_info(self._entry)

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def available(self) -> bool:
        return self._client.connected

    @property
    def is_on(self) -> bool | None:
        return self._client.connected

    def _wake_mac(self) -> str | None:
        for key in (CONF_MAC_WIFI, CONF_MAC_ETHERNET):
            mac = self._entry.data.get(key)
            if mac:
                return str(mac)
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        wol_enabled = self._entry.options.get(CONF_ENABLE_WOL, DEFAULT_ENABLE_WOL)
        mac = self._wake_mac()
        if wol_enabled and mac:
            await self._client.wake_on_lan(mac)
            return
        await self.async_send_command([  "power" ])

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.async_send_command(["power"])

    async def async_send_command(self, commands: list[str], **kwargs: Any) -> None:
        """Send one or more keys.

        Accepts friendly names ("power"), aliases ("back") and raw wire keys
        ("KEY_POWER"). Multiple commands may be comma separated inside a
        single string; ``delay_secs`` paces them like the APK's command queue.
        """
        delay = float(kwargs.get("delay_secs", 0))
        if delay <= 0:
            delay = int(
                self._entry.options.get(CONF_COMMAND_DELAY, DEFAULT_COMMAND_DELAY)
            ) / 1000.0

        expanded: list[str] = []
        for command in commands:
            for token in str(command).split(","):
                token = token.strip()
                if not token:
                    continue
                key = resolve_key(token)
                if key is None:
                    _LOGGER.warning("Unknown Hisense TV key: %s", token)
                    continue
                expanded.append(key)

        for index, key in enumerate(expanded):
            await self._client.send_key(key)
            if index < len(expanded) - 1 and delay > 0:
                await asyncio.sleep(delay)

    @callback
    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()
