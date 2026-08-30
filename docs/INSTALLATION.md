# Installation & Einrichtung — Schritt für Schritt

Diese Anleitung beschreibt die Installation der Hisense-TV-Integration über
HACS und das erste Pairing am TV (inkl. PIN-Eingabe). Der Ablauf entspricht
1:1 dem der offiziellen RemoteNOW-App beim ersten Verbinden.

---

## Teil 1 — Voraussetzungen prüfen

| # | Voraussetzung | So prüfst du es |
|---|---|---|
| 1 | Home Assistant ≥ 2024.1 läuft | *Einstellungen → Info* |
| 2 | **HACS** ist installiert | *HACS* erscheint in der Seitenleiste. Falls nicht: [hacs.xyz](https://hacs.xyz/docs/setup/download) |
| 3 | TV und HA sind im **selben Netzwerk/Subnet** | TV-Menü → Netzwerkstatus (IP notieren!) |
| 4 | TV ist **eingeschaltet** (nicht Eco-Standby) | Bild sichtbar |
| 5 | Die RemoteNOW-Handy-App kann den TV steuern | Bestätigt, dass der MQTT-Dienst am TV aktiv ist |

> 💡 Notiere dir die IP des TVs (z. B. `192.168.1.50`) — sie erspart dir im
> Setup die Netzwerksuche, falls SSDP in deinem Netz (VLAN/AP-Isolation)
> blockiert ist.

---

## Teil 2 — Installation über HACS

1. Öffne in Home Assistant **HACS** in der Seitenleiste.
2. Rechts unten auf die **drei Punkte (⋮)** klicken → **Eigenes Repository hinzufügen** *(Custom repository)*.
3. Folgende Daten eintragen:
   - **Repository:** `https://github.com/V4n1X/ha_hisensetv`
   - **Kategorie:** `Integration`
4. **Hinzufügen** bestätigen. Das Repository erscheint danach in HACS.
5. In HACS nach **„Hisense TV"** suchen (oder das neue Repository öffnen) und auf **Herunterladen** klicken.
6. Die Meldung „Neustart erforderlich" bestätigen: **Einstellungen → System → Neu starten**.

<details>
<summary>Alternative: Manuelle Installation</summary>

```bash
cd <config-verzeichnis>
git clone https://github.com/V4n1X/ha_hisensetv /tmp/ha_hisensetv
mkdir -p custom_components
cp -r /tmp/ha_hisensetv/custom_components/hisense_tv custom_components/
rm -rf /tmp/ha_hisensetv
```
Danach Home Assistant neu starten. (Nicht parallel zur HACS-Variante nutzen.)
</details>

> ⚠️ **Vorherige hisense_tv-Integration entfernt?** Diese Integration nutzt
> denselben Namen (`hisense_tv`) wie z. B. `sehaas/ha_hisense_tv`. Ist eine
> andere Version bereits installiert, deinstalliere sie zuerst (HACS → entfernen
> und Ordner `custom_components/hisense_tv` löschen), sonst gibt es Konflikte.

---

## Teil 3 — TV vorbereiten

Damit Einschalten per Automation später funktioniert und der Broker erreichbar
ist, empfehle ich diese TV-Einstellungen (Menüpfade variieren je nach Modell):

| # | Einstellung | Wo |
|---|---|---|
| 1 | **Netzwerk-Standby / Quick Start** aktivieren | *Einstellungen → System → Energie* |
| 2 | WLAN **oder** LAN fest verbinden (beides geht; MAC wird je Interface erfasst) | *Einstellungen → Netzwerk* |
| 3 | Fernwartung/Steuerung durch Apps zulassen (falls dein TV so eine Option hat) | *Einstellungen → System → …* |

Der MQTT-Dienst des TVs lauscht standardmäßig auf Port **36669**.

---

## Teil 4 — Integration einrichten

1. **Einstellungen → Geräte & Dienste**
2. Unten rechts **Integration hinzufügen**
3. Nach **„Hisense TV"** suchen und auswählen
4. Im erscheinenden Dialog:
   - **Variante A (empfohlen):** Feld *Host/IP* **leer lassen** → die Integration durchsucht das Netzwerk per SSDP → im nächsten Schritt die gefundene TV aus der Liste wählen
   - **Variante B:** IP direkt eintragen (*Host*) und Port unverändert lassen (**36669**)
5. Die Verbindung wird jetzt validiert:
   - Aufbau der MQTT-Verbindung zum TV (bei neueren Firmware-Generationen automatisch mit verschlüsseltem TLS inkl. gebündeltem Client-Zertifikat)
   - Testabfrage des TV-Status

### Wenn der TV eine Freigabe anfordert → **PIN-Pairing**

Bei aktuelleren Firmware-Ständen zeigt der TV beim ersten unbekannten Client
(genau wie bei der ersten Einrichtung der Handy-App) einen **4-stelligen Code
auf dem Bildschirm** an:

1. 📺 Der TV zeigt: *Kopplungscode* (vier Ziffern)
2. 🖥️ In Home Assistant erscheint automatisch das Fenster **„Mit dem TV koppeln"**
3. ⌨️ Die vier Ziffern **innerhalb der Gültigkeit** eingeben (der Code läuft
   am TV zeitlich ab — bei Fehler einfach warten, bis der TV einen neuen
   anzeigt, oder den Vorgang abbrechen und erneut starten)
4. ✅ Bei Erfolg schließt sich das Fenster und die Einrichtung ist fertig

> ⚠️ **Wichtig für eine reibungslose Kopplung** (live am Gerät verifiziert):
>
> * **Offizielle RemoteNOW-/VIDAA-App vorher komplett schließen** — der TV
>   erlaubt nur *einen* aktiven Client. Ist die Handy-App noch verbunden,
>   zeigt der TV zwar ein Pairing-Fenster in HA, aber **keinen Code**; er
>   meldet stattdessen nur „verbundenes Gerät ist besetzt".
> * Der Code ist **nur ca. 30 Sekunden gültig**, danach schließt der TV den
>   Dialog selbst. Die Integration fordert bei einem neuen Versuch automatisch
>   einen neuen Code an.
> * System-Overlays (z. B. der Abschalt-Countdown im Eco-Modus) können den
>   Code **verdecken** — kurz mit der Fernbedienung wegdrücken.

**Fehlerbilder im Pairing-Fenster:**

| Meldung | Bedeutung | Lösung |
|---|---|---|
| *Der eingegebene Kopplungscode wurde vom TV abgelehnt* | Code falsch oder abgelaufen | Neuen Code abwarten und frisch eingeben |
| *Keine Antwort vom TV* | Timeout während der Prüfung | Erneut versuchen; TV nicht zwischenzeitlich ausschalten |
| Kein PIN-Fenster, Setup schließt direkt | Ältere Firmware ohne Kopplungszwang | Alles gut — kein Pairing nötig |
| Code erscheint gar nicht auf dem TV | Remote-Slot belegt (Handy-App läuft) oder Overlay verdeckt ihn | App schließen / Overlay wegdrücken und Setup erneut starten |

5. Danach legt die Integration das Gerät in der **Geräteregistrierung** an:
   Hersteller *Hisense*, Modell, Firmware-Version und MAC-Adresse werden
   automatisch befüllt.

---

## Teil 5 — Funktion prüfen

Nach der Einrichtung existieren folgende Entitäten (Beispielname „Wohnzimmer TV"):

| Entität | Zweck |
|---|---|
| `media_player.wohnzimmer_tv` | Ein/Aus, Lautstärke, Mute, Quelle, Play/Pause |
| `remote.wohnzimmer_tv_remote` | Alle Fernbedienungstasten |
| `sensor.wohnzimmer_tv_volume` | Lautstärke in % |
| `sensor.wohnzimmer_tv_source` | Aktive Eingangsquelle |
| `sensor.wohnzimmer_tv_status` | Roh-Status des TVs (diagnostisch) |

> ℹ️ **Verfügbarkeit = TV läuft.** Der MQTT-Broker steckt im TV selbst — ist
> das Gerät aus, gibt es technisch nichts abzufragen. Deshalb gehen alle
> Entitäten dieser Integration in den Zustand **`unavailable`**, sobald der TV
> aus ist, statt einen Scheinzustand („aus") zu melden. Einschalten geht
> ausschließlich per **Wake-on-LAN** (siehe unten).

**Schnelltest in Entwicklerwerkzeuge → Aktionen:**

```yaml
action: remote.send_command
target:
  entity_id: remote.wohnzimmer_tv_remote
data:
  command: volume_up
```

Lautstärke sollte sich am TV ändern. Für Volllautstärke-Tests:

```yaml
action: media_player.volume_set
target:
  entity_id: media_player.wohnzimmer_tv
data:
  volume_level: 0.3
```

---

## Teil 6 — Optionen anpassen (optional)

*Einstellungen → Geräte & Dienste → Hisense TV → ⚙️ Optionen* (über die drei Punkte):

| Option | Default | Sinn |
|---|---|---|
| Abfrageintervall | 30 s | Statusaktualisierung; kleiner (10–15 s), falls Werte verzögert kommen |
| Wake-on-LAN | an | Einschalten per Magic Packet statt Power-Taste (Einschalten ist **nur** per WOL möglich) |
| Befehlsverzögerung | 30 ms | Pacing bei Kettenbefehlen (`command: "back, ok"`) |

**Einschalten per WOL — Alternative mit Boardmitteln:** Die Integration
versendet das Magic Packet selbst (`media_player.turn_on` bzw.
`remote.turn_on`, MAC wird automatisch aus der SSDP-Erkennung übernommen).
Du kannst aber genauso Home Assistants **native `wake_on_lan`-Integration**
nutzen: *Einstellungen → Geräte & Dienste → Integration hinzufügen →
Wake-on-LAN*, dann einen Switch mit der TV-MAC anlegen (MAC steht in den
Entitäts-Attributen des Status-Sensors bzw. im Diagnose-Download). Für
`turn_on`-Aktionen in Automatisierungen funktioniert beides.

**IP hat sich geändert?** Kein Neu-Einrichten nötig: Die Integration erkennt
die TV über ihre MAC wieder (Reconfirm) — oder du änderst die Adresse manuell
über *Konfigurieren* (Reconfigure).

---

## Problemlösung

| Problem | Ursache | Behebung |
|---|---|---|
| „Verbindung fehlgeschlagen" im Setup | TV im Tiefstandby, VLAN-Trennung, Firewall | TV einschalten; Port 36669/TCP vom HA-Host aus testen (`telnet <tv-ip> 36669`); AP-Client-Isolation deaktivieren |
| TV wird beim Scan nicht gefunden | SSDP/Multicast blockiert (häufig bei Mesh/WLAN-Bridges) | Variante B mit manueller IP nutzen |
| Entities dauerhaft `unavailable` | TV tief im Standby → Broker aus | Das ist der OFF-Zustand; für Automatisierungen „Verfügbarkeit" ignorieren oder Netzwerk-Standby aktivieren |
| Keine Lautstärke-/Statuswerte | Manche Modelle pushen erst auf Poll | Abfrageintervall auf 10–15 s senken |
| PIN-Fenster kommt nie | Alte Firmware ohne Kopplungszwang | Normal — Setup schließt automatisch |

Noch Fragen zum Protokoll dahinter? → [`PROTOCOL.md`](PROTOCOL.md)
