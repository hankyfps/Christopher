# Webdesign-Wissensbasis

Stand der Datei: 2026-10-26 (Sitzung 1)
Legende: ✅ solide · ❓ lückenhaft/unbestätigt · ❌ fehlt

## Kompetenz-Status

| # | Bereich | Status |
|---|---|---|
| 1 | Aufbau/Struktur | ❌ |
| 2 | Technik-Grundlagen | ❓ (nur CSS-Teile: Grid, clamp) |
| 3 | Navigation/UX | ❓ (nur Hamburger-Studie) |
| 4 | Layout, Typografie, Farben, Animation | ❓ (Layout/Animation/Schrift teilweise; Farben ❌) |
| 5 | Responsive/Mobile | ❓ |
| 6 | Performance | ❓ (nur Animation/Webfonts) |
| 7 | Barrierefreiheit | ❓ (Reflow, Resize, Reduced Motion) |
| 8 | SEO | ❌ |
| 9 | Recht DE | ❌ |
| 10 | Trends | ❌ |
| 11 | Qualitätskontrolle | ❌ |
| 12 | KI-Builder-Prompts | ❌ |

---

## 3. Navigation und Benutzerführung

*Stand: 2026-10-26*

**Kernwissen**
- Versteckte Navigation (Hamburger-Icon) wird seltener genutzt als sichtbare. In der NN/g-Studie (179 Personen, 6 Seiten) am Desktop: versteckt 27 %, sichtbar 48 %, Kombination 50 %; am Smartphone: versteckt 57 %, Kombination 86 %.
- Inhalte waren bei versteckter Navigation >20 % schlechter auffindbar; Aufgaben am Desktop mind. 39 % langsamer, am Smartphone 15 % (gegenüber Kombination).
- Gründe laut Autoren: kleines Icon fällt wenig auf, Label sagt wenig aus, Extra-Klick, fehlende Standards.

**Praxis**
- Desktop: Hauptnavigation dauerhaft sichtbar (oben oder links), kein Hamburger.
- Smartphone: bis 4 Hauptlinks sichtbar zeigen. Bei mehr: Rest verstecken, aber wichtige Inhalte zusätzlich per Links im Seiteninhalt erreichbar machen.
- Hamburger bei Reflow (320 px) ist laut WCAG erlaubt, solange alle Funktionen bleiben.

**Typische Fehler**
- Desktop-Seite mit Hamburger-Menü nur wegen „modernem Look".
- Nur Icon ohne Text.

**Einschränkung:** Studie ist von 2016 → ❓ ob Zahlen heute (2026) gleich ausfallen; nicht aktuell geprüft. Die Zahlen gelten für diese Studie, nicht pauschal.

**Quellen**
- Pernice & Budiu: „Hamburger Menus and Hidden Navigation Hurt UX Metrics", NN/g, 26.06.2016 – https://www.nngroup.com/articles/hamburger-menus/
- Hinweis: NN/g-Seite „navigation-design-guide" lieferte 404, nicht ausgewertet.

---

## 4. Layout, Typografie, Animationen

*Stand: 2026-10-26*

### Layout (CSS Grid)
- Grid = zweidimensional (Zeilen + Spalten). `fr` = Anteil am Restplatz; `repeat(3, 1fr)` = drei gleiche Spalten; `minmax(100px, auto)` = Mindesthöhe, wächst mit Inhalt; `gap` = Abstände zwischen Spuren (darin kann nichts platziert werden).
- Explizites Grid (`grid-template-*`) vs. implizites (`grid-auto-rows/columns`). Platzierung über Linien (`grid-column: 1 / 4`), Namen oder Bereiche. `subgrid` übernimmt Spuren des Eltern-Grids.
- Grid und Flexbox lassen sich kombinieren. ❓ Genauer Grid-vs-Flexbox-Vergleich und `auto-fit` nicht aus dieser Quelle belegt (MDN-Seite las ich nur bis Zeichen 100.000 von ~149.000).
- Typischer Fehler: Pixelfixe Spaltenbreiten statt `fr`/`minmax`.

### Typografie
- Variable Fonts: eine Datei, mehrere Stile über Achsen (`wght`, `wdth`, `slnt`, `opsz`, `ital`). Klassische Einzeldateien pro Schnitt können zusammen ≥500 KB sein; Monotype-Test: 48 Dateien → eine Variable Font, −88 % Dateigröße. Bei nur einem Schnitt kaum Vorteil.
- Fließende Schrift: `clamp(min, bevorzugt, max)`, z. B. `clamp(1rem, 2.5vw, 2rem)`. Grenzen in `rem` setzen, Maximum ≥ 2 × Minimum, sonst ist 200 % Textzoom (WCAG 1.4.4) nicht erreichbar. Das MDN-Beispiel `clamp(1.8rem, 2.5vw, 2.8rem)` verletzt diese Regel selbst.
- Lesbare Zeilenlänge: ca. 70–80 Zeichen pro Zeile (web.dev).
- Google Fonts: `preconnect` zu fonts.gstatic.com empfohlen.
- ❓ Nicht belegt: `font-display`-Werte, Zeilenhöhe, Schriftpaarung, Schriftgrößen-Skalen → offene Lücke.
- Hinweis: web.dev-Artikel ist intern widersprüchlich datiert (Update 2018, Browser-Stand Mai 2020).

### Animationen
- Performant: nur `transform` (translate/rotate/scale) und `opacity` animieren. `top`/`left`/`width` lösen Layout/Paint aus → ruckelig.
- `will-change` nicht prophylaktisch einsetzen (eigene Ebenen kosten Speicher/Leistung); nur bei nachgewiesenem Problem.
- `prefers-reduced-motion: reduce` (Baseline seit Jan. 2020) respektieren: starke Bewegung (große Verschiebungen/Skalierungen) entfernen oder durch Ein-/Ausblenden ersetzen. Nicht alleinige Lösung: Info nie nur über Bewegung vermitteln.
- Nicht sichtbare Animationen pausieren (IntersectionObserver).
- Typischer Fehler: Parallax/Scroll-Effekte ohne Reduced-Motion-Fallback.

**Quellen**
- MDN: „Basic concepts of grid layout" (teilweise gelesen) – https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout/Basic_concepts_of_grid_layout
- MDN: „clamp()" (abgerufen 2026-10-26) – https://developer.mozilla.org/en-US/docs/Web/CSS/clamp
- MDN: „prefers-reduced-motion" (abgerufen 2026-10-26) – https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion
- web.dev: „How to create high-performance CSS animations", 06.10.2020 – https://web.dev/articles/animations-guide
- web.dev: „Introduction to variable fonts on the web", 19.02.2018 – https://web.dev/articles/variable-fonts

---

## 5. Responsive Design und Mobile

*Stand: 2026-10-26*

**Kernwissen**
- Pflicht im `<head>`: `<meta name="viewport" content="width=device-width, initial-scale=1">`. Ohne: Mobilbrowser rendern oft ~980 px breit und zoomen raus.
- Kein `user-scalable=no`/`maximum-scale` → verhindert Zoomen (Barrierefreiheit).
- Mobile-first: erst kleinen Bildschirm gestalten, dann erweitern, bis Layout schlecht wird; dort Breakpoint setzen. Breakpoints nach Inhalt, nicht nach Gerätemodellen.
- Media Queries auch für `hover`/`pointer` (Touch vs. Maus); `any-hover`/`any-pointer` mit Vorsicht.
- WCAG 1.4.10 Reflow (AA): Inhalt muss bei 320 CSS-px Breite ohne horizontales Scrollen nutzbar sein (≈ 400 % Zoom bei 1280 px). Ausnahmen: Karten, Diagramme, Datentabellen u. Ä. Layoutwechsel (1 Spalte, Hamburger) ist erlaubt, solange nichts verloren geht.

**Typische Fehler**
- Viewport-Tag fehlt; feste Pixelbreiten; Breakpoints nur für „iPhone/iPad"; horizontales Scrollen bei 320 px; Hover-only-Funktionen.

**Quellen**
- LePage & Andrew: „Responsive web design basics", web.dev, 12.02.2019 – https://web.dev/articles/responsive-web-design-basics
- W3C WAI: „Understanding SC 1.4.10 Reflow" (WCAG 2.2) – https://www.w3.org/WAI/WCAG22/Understanding/reflow.html

---

## 7. Barrierefreiheit (Teilwissen)
*Stand: 2026-10-26* — Details siehe Abschnitte 4 und 5: Textzoom 200 % (1.4.4), Reflow 320 px (1.4.10), Reduced Motion, Zoom nicht sperren. ❓ Kontrast (1.4.3), Tastaturbedienung, Alt-Texte, Fokus: noch nicht recherchiert.

---

## Offene Lücken (Reihenfolge)
1. Rechtliches DE (Impressum/DDG, DSGVO, Cookies/TDDDG) – ❌, rechtlich folgenreich
2. Farben + Kontrast (WCAG 1.4.3), `font-display`, Zeilenhöhe, Schriftpaarung
3. Aufbau/Informationsarchitektur, Performance (Core Web Vitals), SEO
4. KI-Builder-Prompts (Anweisungen), Qualitätscheckliste
5. Trends (mit Aktualitätsprüfung)

## Selbsttest (Sitzung 1, nur anhand dieser Datei)
1. *Hamburger auf Desktop?* → Nein; Hauptnavigation sichtbar. Beleg: NN/g 2016 (27 % vs. 48 %). ✅
2. *Wie animiere ich ruckelfrei?* → nur `transform`/`opacity`; Reduced-Motion-Fallback. ✅
3. *Fließende Überschrift, barrierefrei?* → `clamp(1rem, 2.5vw, 2rem)`, rem-Grenzen, Max ≥ 2×Min. ✅
Nicht beantwortbar aus Datei: Zeilenhöhe, `font-display`, Farbkontrast → bewusst als Lücke geführt.
