# Flight Animation

Isoliertes Python-Unterprojekt für FR24-KML-Flugspuren und stereoskopische
Side-by-Side-Animationen.

## Installation

```bash
cd tools/flightanimation
python -m venv .venv && . .venv/bin/activate
pip install -e '.[dev,gui]'
```

`Pillow` ist für Rendern/Export erforderlich, `PySide6` nur für die Oberfläche.
FFmpeg wird als externes Programm benötigt. Der Kern lässt sich ohne GUI und
ohne Netzwerk testen.

```bash
flightanimation route.kml --output route-sbs.mp4 --duration 20 --fps 25
pytest tools/flightanimation/tests
```

Standardmäßig werden zusätzlich 3 Sekunden Standbild vor und nach der
Bewegung angefügt. Das lässt sich ändern oder abschalten:

```bash
flightanimation route.kml --output route-sbs.mp4 --duration 20 --lead-in 3 --lead-out 3
flightanimation route.kml --output route-sbs.mp4 --duration 20 --lead-in 0 --lead-out 0
```

Das Flugzeugsymbol ist ein kursorientiertes Top-down-Silhouette. Seine
Stereo-Parallaxe wird während des Fluges aus der aktuellen Flughöhe abgeleitet.
Standardmäßig ist das Symbol weiß und damit für Anaglyph-Tests neutral. Rot oder
Gelb kann über `--aircraft-color red` bzw. `--aircraft-color yellow` gewählt
werden.
Die Infotafel ist standardmäßig weiß/schwarz und liegt nahezu flach als
Overlay. Mit `--overlay-style matrix` kann ein dezenter grün-schwarzer
Matrix-Stil getestet werden. Die Overlay-Tiefe bleibt separat steuerbar.
Mit `--overlay-parallax 0` bleibt die Schrift nahezu flach; positive Werte
setzen sie etwas vor, negative Werte etwas hinter die Kartenebene, zum Beispiel
`--overlay-parallax 1.5` oder `--overlay-parallax -1`.
Die Karte erhält standardmäßig eine sehr leichte Tiefenstaffelung
(`--map-tilt 4`). Dabei wird ihre Parallaxe über die Bildhöhe verändert; das
Flugzeug übernimmt die lokale Kartentiefe an seiner Position und addiert die
Höhenwirkung. Für einen flacheren Test kann `--map-tilt 0` verwendet werden.
Für die stereoskopische Analyse kann das Video zusätzlich in Schwarzweiß
gerendert werden:

```bash
flightanimation route.kml --output route-gray.mp4 --grayscale
```
Die Standard-Tiefenwirkung ist ein zurückhaltender Popout (`--aircraft-parallax 3.5`,
`--altitude-gain 1.0`): Die Höhenänderung bleibt erkennbar, ohne auf einem
Notebook unnötige Doppelbilder zu erzeugen. Bei Bedarf können beide Werte
vorsichtig erhöht werden.

Die KML-Höhe und Geschwindigkeit werden bevorzugt aus der Placemark-
Beschreibung gelesen; das dritte Koordinatenfeld wird nicht als Höhe vertraut.
Zeitstempel werden sortiert, fehlende optionale Werte bleiben leer. Der
Strecken-Offset wird in km gesetzt und als km/NM angezeigt. Die Höheninformation
steuert eine visuelle Tiefe, keine physikalische 3D-Skalierung.

Der CLI-Prototyp lädt OSM-Kacheln mit lokalem Cache und nutzt Web Mercator für
die Georeferenzierung. Ohne Netz oder bei einem Downloadfehler bleibt der
Export mit neutralem Hintergrund möglich. Die sichtbare Attribution
`© OpenStreetMap-Mitwirkende` bleibt im Bild.

## Kartenentscheidung

| Option | Vorteil | Risiko/Entscheidung |
| --- | --- | --- |
| OSM-Kacheln mit Python-Tilebibliothek | Schnell zu einem geografisch passenden Kartenbild und Overlays | Provider-Limits, Cache-/Lizenzpflichten und Online-Abhängigkeit; deshalb nicht automatisch im Prototyp geladen |
| Lokales OSM-Vektor-Rendering | Reproduzierbare Offline-Ausgabe und volle Stilkontrolle | Größere Daten- und Renderingpipeline; als späterer `MapProvider` vorgesehen |

Für den ersten funktionsfähigen Prototyp ist eine lokale Rasterkarte bzw. der
neutrale Hintergrund die robuste Wahl: Tests bleiben deterministisch und laden
keine fremden Kartendaten herunter. Bei jeder OSM-Ausgabe muss die Attribution
im Bild sichtbar bleiben.

SBS ist immer links gefolgt von rechts. Parallaxe wird auf maximal 3 % der
Bildbreite begrenzt. Die Vorschau kann über `Renderer.anaglyph()` geprüft
werden.
