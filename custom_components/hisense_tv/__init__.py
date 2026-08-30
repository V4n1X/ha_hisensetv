"""The Hisense TV integration.

Controls Hisense Vidaa TVs through the MQTT broker built into the TV,
replicating the protocol of the official RemoteNOW app.
"""

from __future__ import annotations

import logging
from pathlib import Path
from time import monotonic as time_monotonic

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr

from .const import (
    CLIENT_CERT_FILE,
    CONF_MAC_ETHERNET,
    CONF_MAC_WIFI,
    CONF_MODEL_NAME,
    CONF_PLATFORM_VERSION,
    CONF_UUID,
    DEFAULT_NAME,
    DISPATCH_APP_VERSION,
    DISPATCH_CAPABILITY,
    DISPATCH_CONNECTION,
    DISPATCH_PAIRING_REQUIRED,
    DISPATCH_SOURCES,
    DISPATCH_STATE,
    DISPATCH_VOLUME,
    DOMAIN,
    MANUFACTURER,
)
from .coordinator import HisenseTvCoordinator, RuntimeData
from .data import CannotConnect, HisenseTvClient, default_client_cert_path
from .discovery import format_mac
from .models import CapabilityInfo, StateUpdate, TvState

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.MEDIA_PLAYER, Platform.REMOTE, Platform.SENSOR]

type HisenseConfigEntry = ConfigEntry[RuntimeData]


def bundled_client_cert() -> Path | None:
    """Bundled RemoteNOW client certificate (mutual TLS on newer models)."""
    path = Path(__file__).parent / CLIENT_CERT_FILE
    return path if path.is_file() else None


def entry_unique_id(entry: ConfigEntry) -> str:
    """Stable unique id: explicit uuid, else MAC, else host."""
    return str(
        entry.data.get(CONF_UUID)
        or entry.data.get(CONF_MAC_WIFI)
        or entry.data.get(CONF_MAC_ETHERNET)
        or f"{entry.data.get('host')}:{entry.data.get('port', 36669)}"
    )


def device_connections(entry: ConfigEntry) -> set[tuple[str, str]]:
    connections: set[tuple[str, str]] = set()
    for key in (CONF_MAC_WIFI, CONF_MAC_ETHERNET):
        mac = entry.data.get(key)
        if mac:
            connections.add((dr.CONNECTION_NETWORK_MAC, format_mac(str(mac))))
    return connections


def build_device_info(entry: ConfigEntry) -> dr.DeviceInfo:
    """Shared DeviceInfo so every entity lands on one registry device."""
    data = entry.data
    model = str(data.get(CONF_MODEL_NAME) or "").strip() or DEFAULT_NAME
    info = dr.DeviceInfo(
        identifiers={(DOMAIN, entry_unique_id(entry))},
        manufacturer=MANUFACTURER,
        model=model,
        name=entry.title or DEFAULT_NAME,
        connections=device_connections(entry),
    )
    if data.get(CONF_TV_VERSION):
        info["sw_version"] = str(data[CONF_TV_VERSION])
    if data.get(CONF_PLATFORM_VERSION):
        info["hw_version"] = f"platform {data[CONF_PLATFORM_VERSION]}"
    runtime: RuntimeData | None = getattr(entry, "runtime_data", None)
    if runtime is not None and runtime.state.capability:
        cap = runtime.state.capability
        if not info.get("hw_version") and cap.chip_platform:
            info["hw_version"] = f"chip {cap.chip_platform}"
    return info


def _register_device(hass: HomeAssistant, entry: HisenseConfigEntry) -> None:
    """Create/update the registry device immediately at setup time."""
    registry = dr.async_get(hass)
    data = entry.data
    kwargs: dict = {
        "config_entry_id": entry.entry_id,
        "identifiers": {(DOMAIN, entry_unique_id(entry))},
        "connections": device_connections(entry),
        "manufacturer": MANUFACTURER,
        "model": str(data.get(CONF_MODEL_NAME) or "").strip() or DEFAULT_NAME,
        "name": entry.title or DEFAULT_NAME,
    }
    if data.get(CONF_TV_VERSION):
        kwargs["sw_version"] = str(data[CONF_TV_VERSION])
    if data.get(CONF_PLATFORM_VERSION):
        kwargs["hw_version"] = f"platform {data[CONF_PLATFORM_VERSION]}"
    registry.async_get_or_create(**kwargs)


async def async_setup_entry(hass: HomeAssistant, entry: HisenseConfigEntry) -> bool:
    """Set up a Hisense TV from a config entry."""
    cert_path = bundled_client_cert() or default_client_cert_path()
    _last_reauth_request = 0.0
    coordinator: HisenseTvCoordinator | None = None

    def _on_event(name: str, payload) -> None:  # noqa: ANN001 - Any payload
        """Apply push feedback to the shared TvState and refresh listeners."""
        nonlocal _last_reauth_request
        runtime: RuntimeData | None = getattr(entry, "runtime_data", None)
        if runtime is None:
            return
        changed = False

        if name == DISPATCH_STATE and isinstance(payload, StateUpdate):
            changed = runtime.state.apply_state(payload)
            _LOGGER.debug("%s: state update applied=%s (%s)", entry.title, changed, payload.statetype)
        elif name == DISPATCH_VOLUME:
            changed = runtime.state.apply_volume(payload)
            _LOGGER.debug(
                "%s: volume update applied=%s (level=%s muted=%s)",
                entry.title,
                changed,
                getattr(payload, "level", None),
                getattr(payload, "muted", None),
            )
        elif name == DISPATCH_SOURCES:
            runtime.state.apply_sources(payload)
            changed = True
            _LOGGER.debug("%s: source list updated (%d entries)", entry.title, len(payload))
        elif name == DISPATCH_CONNECTION:
            runtime.state.connected = bool(payload)
        elif name == DISPATCH_CAPABILITY and isinstance(payload, CapabilityInfo):
            runtime.state.capability = payload
            changed = True
            _refresh_device_metadata(hass, entry)
        elif name == DISPATCH_APP_VERSION and payload:
            runtime.state.app_version = str(payload)
            changed = True
        elif name == DISPATCH_PAIRING_REQUIRED:
            # The TV no longer knows us (reset/firmware update): start the
            # reauth flow so the user can re-pair with a fresh PIN.
            now = time_monotonic()
            if now - _last_reauth_request > 60:
                _last_reauth_request = now
                _LOGGER.info("%s: TV requests pairing - starting reauth flow", entry.title)
                entry.async_start_reauth(hass)
            return

        if changed and coordinator is not None:
            coordinator.async_update_listeners()

    client = HisenseTvClient(
        host=str(entry.data["host"]),
        port=int(entry.data.get("port") or 36669),
        client_id=str(entry.data["client_id"]),
        use_tls=entry.data.get("use_tls"),
        client_cert_path=cert_path,
        event_callback=_on_event,
    )
    state = TvState()
    coordinator = HisenseTvCoordinator(hass, entry, client, state)
    runtime = RuntimeData(client=client, coordinator=coordinator, state=state)
    entry.runtime_data = runtime  # before start(): early events need runtime

    try:
        await client.start()
    except CannotConnect as err:
        await client.stop()
        entry.runtime_data = None
        raise ConfigEntryNotReady(str(err)) from err

    _register_device(hass, entry)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Ask for capability/appversion once connected; responses patch metadata.
    if client.connected:
        await client.request_capability()
        await client.request_app_version()
    return True


def _refresh_device_metadata(hass: HomeAssistant, entry: HisenseConfigEntry) -> None:
    """Patch sw/hw version in the registry once capability feedback arrives."""
    runtime: RuntimeData | None = getattr(entry, "runtime_data", None)
    if runtime is None or runtime.state.capability is None:
        return
    cap = runtime.state.capability
    registry = dr.async_get(hass)
    device = registry.async_get_device(identifiers={(DOMAIN, entry_unique_id(entry))})
    if device is None:
        return
    updates: dict[str, str] = {}
    if entry.data.get("tv_version") and runtime.state.app_version:
        updates["sw_version"] = str(runtime.state.app_version)
    if cap.chip_platform:
        updates["hw_version"] = f"chip {cap.chip_platform}"
    if updates:
        registry.async_update_device(device.id, **updates)


async def async_unload_entry(hass: HomeAssistant, entry: HisenseConfigEntry) -> bool:
    """Unload platforms and close the MQTT connection cleanly."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, PLATFORMS)
    runtime: RuntimeData | None = getattr(entry, "runtime_data", None)
    if runtime is not None:
        await runtime.client.stop()
        entry.runtime_data = None
    return unload_ok
