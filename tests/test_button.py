"""Tests for Hisense TV button entities."""

from __future__ import annotations

from hisense_tv.button import BUTTON_DESCRIPTIONS, BUTTON_DESCRIPTIONS
from hisense_tv.const import KEY_COMMANDS


def test_button_descriptions_match_valid_keys():
    """All button entities map to valid KEY_* tokens or WOL."""
    for desc in BUTTON_DESCRIPTIONS:
        if desc.key_command == "WOL":
            continue
        assert desc.key_command.startswith("KEY_")
        assert desc.key_command in KEY_COMMANDS.values()
