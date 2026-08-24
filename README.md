# Hisense TV für Home Assistant

Custom-Integration, die Hisense-Vidaa-TVs über den **in der TV eingebetteten MQTT-Broker** steuert – mit dem rückentwickelten Protokoll der offiziellen **Hisense RemoteNOW**-App (`com.universal.remote.ms` 5.01.011).

> **Migration:** Diese Integration ist ein eigenständiger Ersatz für `sehaas/ha_hisense_tv` und nutzt dieselbe Domain `hisense_tv`. Vor der Installation eine bestehende `hisense_tv`-Integration deinstallieren.

## Funktionen

- **media_player** – Ein/Aus, Lautstärke setzen/stummschalten, Play/Pause/Stop, Nächster/Vorheriger Titel, Quellwahl (HDMI/TV/…)
- **remote** – alle 60+ Fernbedienungs-Keys via `remote.send_command`
- **Sensoren** – Lautstärke (%), aktive Quelle, TV-Status (`sourceswitch`, `app`, `livetv`, … inkl. Fake-Sleep/Bildschirmzustand) + Diagnose-Attribute (Firmware, Chip-Plattform, Capabilities)
- **Auto-Discovery** – SSDP-basiert (wie die App), plus manueller Netzwerkscan im Setup und IP-Reparatur per DHCP/MAC
- **First-Pairing wie die App** – erscheint auf dem TV ein 4-stelliger Kopplungscode, fragt das Setup ihn ab; bei neueren Firmware-Generationen mit verschlüsselter MQTT-Verbindung wird das gebündelte RemoteNOW-Client-Zertifikat automatisch verwendet
- **Device-Registry** – Modell, Hersteller, Firmware, MAC und Name werden aus UPnP/Discovery/Capability-Daten registriert
- Reconfigure (IP ändern), Reconfirm (IP durch DHCP geändert), Reauth (Kopplung verfallen), Options-Flow (Polling, WOL, Befehls-Pacing)

## Unterstützte Geräte

Getestet gegen die Protokollgeneration von RemoteNOW 5.x (Vidaa-U/VIDAA-TVs, Standard-MQTT-Port 36669). TVs mit Client-Zertifikats-Pflicht (z. B. A71-Serie) werden durch das gebündelte Zertifikat abgedeckt. Ältere Firmware ohne Push-Feedback funktioniert ohne Kopplungsschritt.

## Installation

### HACS (empfohlen)

1. Repository als *Custom Repository* (Kategorie: Integration) in HACS hinzufügen oder nach Veröffentlichung direkt suchen.
2. Home Assistant neu starten.
3. *Einstellungen → Geräte & Dienste → Integration hinzufügen → Hisense TV*.

### Manuell

```
cp -r custom_components/hisense_tv <config>/custom_components/
```

Danach HA neu starten.

## Einrichtung

> 📖 **Ausführliche Schritt-für-Schritt-Anleitung** (HACS-Installation, PIN-Pairing am TV, Schnelltest, Troubleshooting): [`docs/INSTALLATION.md`](docs/INSTALLATION.md)

1. Integration auswählen → Feld *Host* leer lassen für Netzwerkscan, oder IP direkt eingeben.
2. Die Verbindung wird validiert (MQTT auf Port 36669, automatische TLS-Eskalation falls die Firmware sie verlangt).
3. Fordert der TV eine Freigabe an, zeigt er einen **4-stelligen Code** an – diesen im Setup-Fenster eingeben (entspricht exakt dem Pairing der RemoteNOW-App).
4. Fertig – Gerät wird mit Modell/Firmware/MAC registriert.

### Nachträgliche Änderungen

| Aktion | Wo |
|---|---|
| IP/Port ändern | *Integration → Konfigurieren* (Reconfigure, mit Revalidierung) |
| Polling/WOL/Pacing | *Integration → Optionen* |
| IP wurde vom DHCP geändert | passiert automatisch (Reconfirm via gerätegebundener MAC) |
| TV wurde zurückgesetzt / Kopplung futsch | Integration meldet sich; Reauth fragt erneut den PIN ab |

## Remote-Befehle

```yaml
service: remote.send_command
target:
  entity_id: remote.wohnzimmer_tv_remote
data:
  command: power            # oder: menu, home, back, ok, up/down/left/right,
                            # volume_up/volume_down/mute, channel_up/channel_down,
                            # play/pause/stop/rewind/forward/previous/next,
                            # info/sources/epg/subtitle/audio, red/green/yellow/blue,
                            # 0–9 als KEY_0..KEY_9, oder beliebige rohe KEY_*-Tokens
```

Mehrere Tasten: `command: "back, ok"` · Pacing über Option `command_delay` oder `delay_secs`.

## Technische Details

Das komplette reverse-engineerte Protokoll (Topics, Payloads, Credentials-Ableitung, Pairing-Sequenz, Discovery, WOL, Diskrepanzen zu Community-Quellen) ist in [`docs/PROTOCOL.md`](docs/PROTOCOL.md) dokumentiert.

Kurzform:

- MQTT auf `tcp://<TV>:36669`, User `hisenseservice`, Pass `multimqttservice` (statisch in jeder RemoteNOW-Installation)
- Befehle: `/remoteapp/tv/<service>/<clientId>/actions/<action>` · Feedback: `/remoteapp/mobile/broadcast/#` + `/remoteapp/mobile/<clientId>/#`
- `changevolume` nimmt Klartext-Zahlen (0–100); Mute ist `KEY_MUTE`
- Einschalten per Wake-on-LAN: Magic Packet 5× alle 100 ms an UDP-Port **33129**

## Fehlerbehebung

| Symptom | Ursache/Lösung |
|---|---|
| `cannot_connect` im Setup | TV schläft tief / VLAN blockiert 36669/TCP · „Network Wake-on-LAN" am TV aktivieren? Erst TV einschalten, dann einrichten |
| PIN-Fenster kommt nicht | Alte Firmware ohne Kopplungszwang – Flow überspringt nach Timeout automatisch |
| `invalid_pin` | Code läuft am TV zeitlich ab → neuen anzeigen lassen (erneut versuchen) |
| Entities `unavailable` obwohl TV Bild zeigt | Broker nur im „schnellen" Standby erreichbar; Eco-Standby prüfen |
| Keine Volumen-/Statuswerte | Einige Modelle pushen erst nach erstem `getvolume`-Poll (Option: Intervall verringern) |

## Danksagung

Die Reverse-Engineering-Gemeinschaft, auf deren Erkenntnissen dieses Projekt aufbaut:

- [Krazy998/mqtt-hisensetv](https://github.com/Krazy998/mqtt-hisensetv) – erste öffentliche Protokolldokumentation
- [sehaas/ha_hisense_tv](https://github.com/sehaas/ha_hisense_tv) – Mosquitto-Bridge-Ansatz, PIN-Flow, Client-Zert-Erfahrungen
- [newAM/hisensetv_hass](https://github.com/newAM/hisensetv_hass)
- [d3nd3/Hisense-mqtt-keyfiles](https://github.com/d3nd3/Hisense-mqtt-keyfiles)

## Lizenz

MIT – siehe [LICENSE](LICENSE).
