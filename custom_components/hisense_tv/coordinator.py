"""Data update coordinator for the Hisense TV integration."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DEFAULT_POLL_INTERVAL
from .data import NotConnected

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

    from .data import HisenseTvClient
    from .models import TvState

_LOGGER = logging.getLogger(__name__)

# Time the TV gets to push fresh values after a poll request.
_SETTLE_SECONDS = 1.0


@dataclass(slots=True)
class RuntimeData:
    """Everything the entity platforms need, stored on entry.runtime_data."""

    client: "HisenseTvClient"
    coordinator: "HisenseTvCoordinator"
    state: "TvState"


class HisenseTvCoordinator(DataUpdateCoordinator["TvState"]):
    """Poll fallback for values that are otherwise pushed by the TV.

    The protocol is push-first: volume/source/state feedback arrives
    asynchronously on /remoteapp/mobile/... The poll cycle only requests fresh
    values so a lost push heals within one interval.

    Connection loss is deliberately *not* raised as UpdateFailed: the TV's MQTT
    broker disappears while the set is powered off, which is exactly the OFF
    state -- entities translate ``state.connected`` instead of going
    unavailable.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: HisenseTvClient,
        state: TvState,
    ) -> None:
        self.client = client
        self.state = state
        try:
            poll = int(entry.options.get("poll_interval", DEFAULT_POLL_INTERVAL))
        except (TypeError, ValueError):
            poll = DEFAULT_POLL_INTERVAL
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{entry.title} ({entry.data.get('host')})",
            update_interval=timedelta(seconds=max(5, poll)),
        )

    async def _async_update_data(self) -> TvState:
        if not self.client.connected:
            return self.state
        try:
            await self.client.get_volume()
            await self.client.get_tv_state()
        except NotConnected:
            return self.state
        # Give the TV a moment to answer before listeners read the snapshot.
        await asyncio.sleep(_SETTLE_SECONDS)
        return self.state
