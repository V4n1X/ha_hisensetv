"""Tests for the MQTT feedback dispatcher (no broker required)."""

from hisense_tv.data import HisenseTvClient
from hisense_tv.models import AuthenResult, StateUpdate, VolumeUpdate

CID = "ha-hisense-test1234"


def make_client() -> tuple[HisenseTvClient, list]:
    events: list[tuple[str, object]] = []
    client = HisenseTvClient("127.0.0.1", 36669, CID)
    client.on_event = lambda name, data: events.append((name, data))
    return client, events


def test_state_dispatch_from_broadcast():
    client, events = make_client()
    client._handle_message(
        "/remoteapp/mobile/broadcast/ui_service/state",
        b'{"statetype":"sourceswitch","sourceid":"4","sourcename":"HDMI 2"}',
    )
    assert len(events) == 1
    name, data = events[0]
    assert name == "state"
    assert isinstance(data, StateUpdate)
    assert data.statetype == "sourceswitch"


def test_volume_alias_dispatch_for_own_client():
    # Firmware variants use either /volume or /volumechange.
    client, events = make_client()
    client._handle_message(
        f"/remoteapp/mobile/{CID}/platform_service/volume",
        b'{"volume_type":0,"volume_value":25}',
    )
    client._handle_message(
        "/remoteapp/mobile/broadcast/ui_service/volumechange",
        b'{"volume_type":2,"volume_value":1}',
    )
    kinds = [name for name, _ in events]
    assert kinds == ["volume", "volume"]
    assert isinstance(events[0][1], VolumeUpdate) and events[0][1].level == 25
    assert isinstance(events[1][1], VolumeUpdate) and events[1][1].muted is True


def test_pairing_and_auth_result_flow():
    client, events = make_client()
    client._handle_message("/remoteapp/mobile/broadcast/ui_service/authentication", b"{}")
    client._handle_message(
        f"/remoteapp/mobile/{CID}/ui_service/authenticationcode",
        b'{"result":1,"info":"ok"}',
    )
    names = [name for name, _ in events]
    assert names == ["pairing_required", "authentication_result"]
    assert isinstance(events[1][1], AuthenResult) and events[1][1].ok


def test_auth_toast_counts_as_success():
    """Some firmwares only send /authenticationcodetoast after a valid PIN."""
    client, events = make_client()
    client._handle_message(
        f"/remoteapp/mobile/{CID}/ui_service/authenticationcodetoast",
        b"",
    )
    assert len(events) == 1
    name, result = events[0]
    assert name == "authentication_result"
    assert result.ok is True


def test_foreign_client_ids_are_ignored():
    client, events = make_client()
    client._handle_message(
        "/remoteapp/mobile/someoneelse/ui_service/state",
        b'{"statetype":"app"}',
    )
    assert events == []


def test_irrelevant_topics_are_ignored():
    client, events = make_client()
    client._handle_message("/remoteapp/tv/remote_service/x/actions/sendkey", b"KEY_POWER")
    client._handle_message("garbage", b"x")
    assert events == []


def test_pop_event_returns_newest_match():
    client, _events = make_client()
    client._handle_message(
        "/remoteapp/mobile/broadcast/ui_service/state", b'{"statetype":"app"}'
    )
    found = client.pop_event("state")
    assert found is not None
    data, index = found
    assert data.statetype == "app"

    marker = index
    client._handle_message(
        "/remoteapp/mobile/broadcast/ui_service/state", b'{"statetype":"livetv"}'
    )
    newer = client.pop_event("state", after_index=marker + 1)
    assert newer is not None
    assert newer[0].statetype == "livetv"
    # Nothing new after the latest marker:
    assert client.pop_event("state", after_index=len(client.recent_events())) is None
