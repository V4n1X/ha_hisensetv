# Remote Control Commands & Keys

The `hisense_tv` integration provides a full remote entity (`remote.hisense_tv`) as well as quick-action button entities. You can send any key command to your TV using the `remote.send_command` service.

---

## Service Call Example

In Home Assistant automations or scripts:

```yaml
service: remote.send_command
target:
  entity_id: remote.hisense_tv
data:
  command: home
```

Sending multiple keys with delay:

```yaml
service: remote.send_command
target:
  entity_id: remote.hisense_tv
data:
  command:
    - "1"
    - "2"
  delay_secs: 0.5
```

---

## Available Remote Keys

You can pass either the friendly name (e.g. `home`, `volume_up`) or the raw wire token (e.g. `KEY_HOME`, `KEY_VOLUMEUP`).

### Navigation & Core Controls
| Friendly Name / Alias | Raw Token | Description |
|---|---|---|
| `power` | `KEY_POWER` | Toggle TV power state |
| `home` | `KEY_HOME` | Open Home screen / Launcher |
| `menu` | `KEY_MENU` | Open Quick Menu |
| `back`, `return`, `returns` | `KEY_RETURNS` | Back / Return |
| `exit` | `KEY_EXIT` | Exit current app / menu |
| `ok`, `enter`, `select` | `KEY_OK` | OK / Select |
| `up` | `KEY_UP` | Direction Up |
| `down` | `KEY_DOWN` | Direction Down |
| `left` | `KEY_LEFT` | Direction Left |
| `right` | `KEY_RIGHT` | Direction Right |
| `info` | `KEY_INFO` | Information overlay |
| `settings` | `KEY_SETTINGS` | TV Settings menu |
| `tools` | `KEY_TOOLS` | Tools / Options |

### Input & Live TV
| Friendly Name / Alias | Raw Token | Description |
|---|---|---|
| `source`, `sources`, `input` | `KEY_SOURCES` | Source input selector |
| `guide`, `epg` | `KEY_EPG` | Electronic Program Guide (EPG) |
| `livetv`, `tvs` | `KEY_LIVETV` / `KEY_TVS` | Switch to Live TV |
| `channel_up`, `ch_up` | `KEY_CHANNELUP` | Next channel |
| `channel_down`, `ch_down` | `KEY_CHANNELDOWN` | Previous channel |
| `last` | `KEY_LAST` | Last tuned channel |
| `favorite` | `KEY_FAVORITE` | Favorite channel list |
| `teletext`, `text` | `KEY_TEXT` | Teletext toggle |
| `subtitle` | `KEY_SUBTITLE` | Subtitle track toggle |
| `audio` | `KEY_AUDIO` | Audio track / language toggle |

### Volume & Audio
| Friendly Name / Alias | Raw Token | Description |
|---|---|---|
| `volume_up`, `vol_up` | `KEY_VOLUMEUP` | Increase volume |
| `volume_down`, `vol_down` | `KEY_VOLUMEDOWN` | Decrease volume |
| `mute` | `KEY_MUTE` | Toggle audio mute |
| `sound` | `KEY_SOUND` | Sound mode settings |

### Media Playback
| Friendly Name / Alias | Raw Token | Description |
|---|---|---|
| `play` | `KEY_PLAY` | Play |
| `pause` | `KEY_PAUSE` | Pause |
| `stop` | `KEY_STOP` | Stop |
| `rewind`, `fr` | `KEY_BACKS` | Fast rewind |
| `forward`, `ff` | `KEY_FORWARDS` | Fast forward |
| `previous` | `KEY_PREVIOUS` | Previous track / chapter |
| `next` | `KEY_NEXT` | Next track / chapter |
| `record` | `KEY_RECORD` | Record current broadcast (PVR) |
| `pvr` | `KEY_PVR` | PVR menu |

### Numeric Keys
| Friendly Name | Raw Token | Description |
|---|---|---|
| `0` - `9` | `KEY_0` - `KEY_9` | Number keys 0 to 9 |

### Color Buttons
| Friendly Name | Raw Token | Description |
|---|---|---|
| `red` | `KEY_RED` | Red interactive button |
| `green` | `KEY_GREEN` | Green interactive button |
| `yellow` | `KEY_YELLOW` | Yellow interactive button |
| `blue` | `KEY_BLUE` | Blue interactive button |

### Direct App Shortcuts
| Friendly Name / Alias | Raw Token | Description |
|---|---|---|
| `netflix` | `KEY_NETFLIX` | Launch Netflix |
| `youtube` | `KEY_YOUTUBE` | Launch YouTube |
| `prime`, `prime_video`, `amazon` | `KEY_PRIME` | Launch Prime Video |
| `disney`, `disney_plus` | `KEY_DISNEY` | Launch Disney+ |
| `app` | `KEY_APP` | App Store / App Drawer |
| `browser` | `KEY_BROWSER` | Web Browser |
| `deezer` | `KEY_DEEZER` | Launch Deezer |
| `rakuten` | `KEY_RAKUTEN` | Launch Rakuten TV |
| `plex` | `KEY_PLEX` | Launch Plex |

### Display & Misc
| Friendly Name | Raw Token | Description |
|---|---|---|
| `picture` | `KEY_PICTURE` | Picture mode settings |
| `aspect` | `KEY_ASPECT` | Aspect ratio selector |
| `sleep` | `KEY_SLEEP` | Sleep timer |
| `zoom_in` | `KEY_ZOOMIN` | Zoom in |
| `zoom_out` | `KEY_ZOOMOUT` | Zoom out |
| `3d` | `KEY_3D` | 3D mode |
| `cc` | `KEY_CC` | Closed Captions |
