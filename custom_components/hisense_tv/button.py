"""Button platform for Hisense TV remote key shortcuts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

if TYPE_CHECKING:
    from .__init__ import HisenseConfigEntry


@dataclass(frozen=True, kw_only=True)
class HisenseButtonEntityDescription(ButtonEntityDescription):
    """Describes Hisense TV button entity."""

    key_command: str


BUTTON_DESCRIPTIONS: tuple[HisenseButtonEntityDescription, ...] = (
    HisenseButtonEntityDescription(
        key="home",
        translation_key="button_home",
        icon="mdi:home",
        key_command="KEY_HOME",
    ),
    HisenseButtonEntityDescription(
        key="menu",
        translation_key="button_menu",
        icon="mdi:menu",
        key_command="KEY_MENU",
    ),
    HisenseButtonEntityDescription(
        key="back",
        translation_key="button_back",
        icon="mdi:keyboard-backspace",
        key_command="KEY_RETURNS",
    ),
    HisenseButtonEntityDescription(
        key="info",
        translation_key="button_info",
        icon="mdi:information-outline",
        key_command="KEY_INFO",
    ),
    HisenseButtonEntityDescription(
        key="guide",
        translation_key="button_guide",
        icon="mdi:television-guide",
        key_command="KEY_EPG",
    ),
    HisenseButtonEntityDescription(
        key="source",
        translation_key="button_source",
        icon="mdi:video-input-hdmi",
        key_command="KEY_SOURCES",
    ),
    HisenseButtonEntityDescription(
        key="settings",
        translation_key="button_settings",
        icon="mdi:cog",
        key_command="KEY_SETTINGS",
    ),
    HisenseButtonEntityDescription(
        key="netflix",
        translation_key="button_netflix",
        icon="mdi:netflix",
        key_command="KEY_NETFLIX",
    ),
    HisenseButtonEntityDescription(
        key="youtube",
        translation_key="button_youtube",
        icon="mdi:youtube",
        key_command="KEY_YOUTUBE",
    ),
    HisenseButtonEntityDescription(
        key="prime_video",
        translation_key="button_prime_video",
        icon="mdi:amazon",
        key_command="KEY_PRIME",
    ),
)


async def async_setup_entry(hass, entry: "HisenseConfigEntry", async_add_entities) -> None:  # noqa: ANN001
    """Set up Hisense TV button entities."""
    async_add_entities(
        [
            HisenseTvButton(entry, description)
            for description in BUTTON_DESCRIPTIONS
        ]
    )


class HisenseTvButton(CoordinatorEntity, ButtonEntity):
    """Representation of a Hisense TV remote key button."""

    entity_description: HisenseButtonEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        entry: "HisenseConfigEntry",
        description: HisenseButtonEntityDescription,
    ) -> None:
        runtime = entry.runtime_data
        super().__init__(runtime.coordinator)
        self._entry = entry
        self._client = runtime.client
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}-btn-{description.key}"

    @property
    def device_info(self):  # noqa: ANN201
        from .__init__ import build_device_info  # noqa: PLC0415

        return build_device_info(self._entry)

    @property
    def available(self) -> bool:
        return self._client.connected

    async def async_press(self) -> None:
        """Handle the button press by sending the remote key."""
        await self._client.send_key(self.entity_description.key_command)
