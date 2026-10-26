# Webdesign-Wissensbasis

Stand der Datei: 2026-10-26 (Sitzung 5)
Legende: ✅ solide · ❓ lückenhaft/unbestätigt · ❌ fehlt

## Kompetenz-Status

| # | Bereich | Status |
|---|---|---|
| 1 | Aufbau/Struktur | ❓ (nur HTML-Semantik) |
| 2 | Technik-Grundlagen | ❓ (nur CSS-Teile: Grid, clamp) |
| 3 | Navigation/UX | ❓ (Hamburger-Studie, IA vs. Navigation, Startseiten-Prinzipien) |
| 4 | Layout, Typografie, Farben, Animation | ❓ (Layout/Animation/Schrift teilweise; Farben ❌) |
| 5 | Responsive/Mobile | ❓ |
| 6 | Performance | ❓ (CWV, Caching, Lighthouse, INP-Maßnahmen, CDN, Bildformate, Lab vs. Feld; konkrete Hosting-Wahl offen) |
| 7 | Barrierefreiheit | ✅ für WCAG-Grundkriterien (Kontrast, Text, Tastatur, Fokus, Alt, Zielgröße, Motion); ❓ ARIA/Formulare/Screenreader-Test |
| 8 | SEO | ❓ (Starter-Guide, Sitemap, robots.txt/noindex; strukturierte Daten, lokale SEO offen) |
| 9 | Recht DE | ❓ Impressum, TDDDG, Art. 13 DSGVO, DSK-OH am Original; BFSG über Bundesfachstelle-FAQ; BFSG-Gesetzestext und Urteilstexte offen (siehe 9) |
| 10 | Trends | ❓ (Beobachtungen aus Inspiration-Datei, 2026-10; nicht selbst gemessen) |
| 11 | Qualitätskontrolle | ❓ Checkliste aus geprüften Punkten (Abschnitt 11); einmal an apple.com/de erprobt, ohne Lighthouse/Screenreader |
| 12 | KI-Builder-Prompts | ❓ offizielle Lovable-Doku ausgewertet; andere Builder nicht |

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

**Informationsarchitektur (IA) vs. Navigation** (NN/g, Cardello, 22.06.2014): IA = unsichtbares Grundgerüst (welche Inhalte, wie gegliedert und benannt; dokumentiert in Tabellen/Diagrammen). Navigation = sichtbare Elemente (Hauptmenü, Breadcrumbs, Filter, Footer) und nur die "Spitze des Eisbergs". Reihenfolge: **erst IA, dann Navigation gestalten**; Navigation nicht nach Optik wählen (Beispiel: Inverted-L-Layout trägt nur bis ~4 Ebenen).

**Buttons, Links und Call-to-Action (NN/g):**
- **Link = Versprechen** (Pernice 2014): Linktext eigenständig verständlich (nicht „mehr", „weiterlesen"), und die Zielseite löst das Versprechen sofort ein (Überschrift passt zum Linktext, erwarteter Inhalt ohne Scrollen sichtbar).
- **Generische Labels schaden** („Get Started", Harley/Flaherty 2017): in der Studie klickten 6 von 8 Teilnehmern darauf und landeten in Anmelde-/Verkaufsstrecken statt bei Informationen → Button sagt konkret, was passiert („Stilquiz starten"); erst Informationen geben, dann Daten/Anmeldung verlangen; Preise/Kernangaben sichtbar, nicht im Footer.
- **Button-Stile** (Gordon 2025): *primär* = gefüllt, stärkste Betonung (Hauptaktion); *sekundär* = Outline; *tertiär* = geringste Betonung. **Zustände:** enabled, disabled (zusätzlich `aria-disabled="true"`), hover (leichte Abdunklung), focus (Rahmen, nicht nur Farbe), pressed (Rückmeldung in 100–150 ms), loading. Das entspricht dem gefüllt/umrandet-Paar bei Apple (Abschnitt 10).
- **Touch-Ziele** (Harley 2019): mindestens ca. **1 cm × 1 cm** physisch (kein Pixelwert), Primäraktionen größer; Abstand ca. 2 mm; erst Größe, dann Abstand.
- ❓ Zahlenbasierte CTA-Tests (Farbe, Position, Conversion) wurden nicht gefunden – NN/g liefert Prinzipien, keine Conversion-Zahlen.

**Startseiten-Prinzipien** (NN/g, Wang

**Einschränkung:** Studie ist von 2016 → ❓ ob Zahlen heute (2026) gleich ausfallen; nicht aktuell geprüft. Die Zahlen gelten für diese Studie, nicht pauschal.

**Quellen**
- Pernice & Budiu: „Hamburger Menus and Hidden Navigation Hurt UX Metrics", NN/g, 26.06.2016 – https://www.nngroup.com/articles/hamburger-menus/
- Hinweis: NN/g-Seite „navigation-design-guide" lieferte 404, nicht ausgewertet.
- Cardello: „The Difference Between Information Architecture (IA) and Navigation", NN/g, 22.06.2014 – https://www.nngroup.com/articles/ia-vs-navigation/
- Pernice: „A Link is a Promise", NN/g, 14.12.2014 – https://www.nngroup.com/articles/link-promise/
- Harley & Flaherty: „„Get Started" Stops Users", NN/g, 20.08.2017 – https://www.nngroup.com/articles/get-started/
- Gordon: „Button States: Communicate Interaction", NN/g, 25.04.2025 – https://www.nngroup.com/articles/button-states-communicate-interaction/
- Harley: „Touch Targets on Touchscreens", NN/g, 05.05.2019 – https://www.nngroup.com/articles/touch-target-size/
- Wang: „Homepage Design: 5 Fundamental Principles", NN/g, 15.03.2024 – https://www.nngroup.com/articles/homepage-design-principles/

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
- `font-display` (MDN): `swap` = sofort Ersatzschrift, später Wechsel (gut für Fließtext, Risiko Layoutsprung); `block` = kurz unsichtbar (Icon-Fonts); `fallback` = Kompromiss für Markenschriften; `optional` = Webfont nur, wenn sofort da (stabilstes Layout, ideal für unkritische Schriften); `auto` = Browser entscheidet.
- Zeilenhöhe/Abstände: WCAG 1.4.12 verlangt nur, dass der Inhalt bei Zeilenhöhe 1,5×, Absatzabstand 2×, Buchstabenabstand 0,12×, Wortabstand 0,16× (jeweils der Schriftgröße) nichts verliert → keine Pflichtwerte, aber Layout darf nicht auf feste Höhen bauen.
- `line-height` (MDN): als **Zahl ohne Einheit** angeben (z. B. `1.5`), bleibt beim Zoom/Vererben proportional; für Fließtext **mindestens 1,5** (hilft bei Sehschwäche, Legasthenie). Das 1,7 aus dem Beispiel-CSS der Inspiration-Datei ist kein Standard, aber ≥ 1,5 passt.
- Webfont-Best-Practices (web.dev, 04.10.2022): nur **WOFF2**; Self-Hosting spart Drittverbindung (Vorteil nicht garantiert; CDN + HTTP/2); `preload` gezielt nur für wenige kritische Fonts; `font-display: optional` am stabilsten, Kombination möglich (`swap` für Marke, `optional` für Fließtext); **Subsetting** per `unicode-range` (Lizenz muss das erlauben); `size-adjust` gegen CLS; jeder weitere Font kostet Ladezeit, `system-ui` braucht keinen Download; **Icon-Fonts durch SVG ersetzen**.
- **Schriftgröße/Paarung (NN/g, Nielsen 15.11.2015):** „reasonably large default font size", Nutzern Größenänderung erlauben, Größen **relativ statt absolut in Pixeln** (NN/g „Top 10 Mistakes"); hoher Kontrast, schlichter Hintergrund; saubere Schrift – Serif ist auf hochauflösenden Bildschirmen ok, Schriften, die Handschrift/Gotik nachahmen, schaden der Lesbarkeit. NN/g nennt **keine feste Pixelzahl** → die **16-px-Mindestgröße ist kein belegter Standard**, sondern Praxisrichtwert (Webdesign Journal; Apple misst 17 px). Zeilenlänge behandelt der Artikel nicht.
- ❓ Weiter offen: Schriftpaarungs-Regeln und Größenskalen aus Primärquelle (Apple-HIG- und Material-3-Seite lieferten nur den Titel, da JavaScript-Seiten).
- Hinweis: web.dev-Artikel ist intern widersprüchlich datiert (Update 2018, Browser-Stand Mai 2020).

### Animationen
- Performant: nur `transform` (translate/rotate/scale) und `opacity` animieren. `top`/`left`/`width` lösen Layout/Paint aus → ruckelig.
- `will-change` nicht prophylaktisch einsetzen (eigene Ebenen kosten Speicher/Leistung); nur bei nachgewiesenem Problem.
- `prefers-reduced-motion: reduce` (Baseline seit Jan. 2020) respektieren: starke Bewegung (große Verschiebungen/Skalierungen) entfernen oder durch Ein-/Ausblenden ersetzen. Nicht alleinige Lösung: Info nie nur über Bewegung vermitteln.
- Nicht sichtbare Animationen pausieren (IntersectionObserver).
- Dauer (NN/g 2020): Feedback ca. 100 ms, Modal/größere Änderungen 200–300 ms, Gesamtrahmen 100–400 ms; ab 500 ms wirkt es zäh. Animationen sind öfter zu lang als zu kurz. Einblenden etwas länger als Ausblenden. Je häufiger, desto kürzer/dezenter. Easing: Erscheinen = ease-out, Verschwinden = ease-in/in-out; linear wirkt unnatürlich.
- Typischer Fehler: Parallax/Scroll-Effekte ohne Reduced-Motion-Fallback.

### Farben / Dark Mode (Teilwissen)
- `prefers-color-scheme: light|dark` (Baseline seit Jan. 2020): helles Standard-Theme, per Media Query für Dunkel überschreiben. `color-scheme` (CSS/Meta) lässt den Browser Formularelemente/Scrollbars automatisch anpassen.
- Beide Themes müssen die Kontrastwerte aus Abschnitt 7 einhalten.
- Farbwerte in CSS (MDN „Applying color"): benannte Farben, Hex, `rgb()`, `hsl()`, `hwb()`; **im Projekt eine einzige Schreibweise** verwenden. **`oklch(L C H / A)`** (MDN, Baseline „Widely available" seit Mai 2023): L = wahrgenommene Helligkeit 0–1, C = Farbintensität (100 % = 0,4), H = Farbton als Winkel; Helligkeit/Intensität/Farbton einzeln einstellbar; Varianten per relativer Syntax `oklch(from var(--basis) calc(l + 0.15) c h)` (Teile davon noch uneinheitlich unterstützt → Fallback-Farbe davor setzen).
- Kontrast bewusst prüfen (MDN verweist auf den WebAIM Color Contrast Checker); hoher Kontrast hilft auch bei Blendung (Smartphone in der Sonne). Pflichtfelder z. B. mit Sternchen **und** Farbe kennzeichnen (MDN „CSS and JavaScript accessibility best practices").
- Hover/Fokus: Cursor und Fokus-Outline nicht entfernen; Mauszustände (`mouseover`) brauchen Tastatur-Gegenstück (`focus`). **`:focus-visible`** (MDN, Baseline seit März 2022): Fokus nur bei Tastaturbedienung sichtbar gestalten statt `outline: none`, z. B. `outline: 2px solid …; outline-offset: 2px`; Indikator braucht ≥ 3:1 Kontrast (WCAG 1.4.11).
- Quelle: MDN „prefers-color-scheme" (abgerufen 2026-10-26; zu ~77 % gelesen) – https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme
- **Farbschemata (MDN „Using color wisely"):** Basisfarbe + Neutralfarben (Weiß/Schwarz/Grau), **möglichst wenige Farben**, Farbe gezielt zur Hervorhebung; Beispiele **monochrom**, **komplementär** (Gegenfarbe als Akzent), **triadisch** (drei gleichmäßig verteilte Farbtöne, ±120°). *Analog* behandelt MDN nicht; Material Design sagt nur, dass Farben mit nahen Farbtönen harmonischer wirken (Blog „Designing Harmony into Dynamic Color", nicht selbst gelesen, nur Suchausschnitt ❓). Farbwirkung: Basisfarbe soll Thema/Stimmung spiegeln; **MDN geht nicht ins Detail zur Psychologie einzelner Farben** → feste Aussagen wie „Blau = Vertrauen" bleiben ❓ Faustregel. Rot-Grün-Schwäche ist die häufigste Farbenblindheit → Häkchen/Kreuz statt nur Grün/Rot; Palettenwerkzeuge mit Farbenblindheits-Simulation existieren (Paletton, laut MDN).
- **Niedriger Kontrast (NN/g, Sherwin 07.06.2015):** Low-Contrast-Text verschlechtert Lesbarkeit und Auffindbarkeit; Grau wirkt oft wie deaktiviert; bei Sonnenlicht kaum lesbar; Alternative: Gewichtung über Größe/Position statt blasser Farbe.

**Quellen**
- MDN: „Basic concepts of grid layout" (teilweise gelesen) – https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout/Basic_concepts_of_grid_layout
- MDN: „clamp()" (abgerufen 2026-10-26) – https://developer.mozilla.org/en-US/docs/Web/CSS/clamp
- web.dev: „Best practices for fonts", 04.10.2022 – https://web.dev/articles/font-best-practices
- MDN: „line-height" (zu ~76 % gelesen) – https://developer.mozilla.org/en-US/docs/Web/CSS/line-height
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

## 1. Aufbau und Struktur (Teilwissen)

*Stand: 2026-10-26*

- Semantische HTML-Bereiche (MDN): `header` (Kopf), `nav` (Hauptnavigation), `main` (Hauptinhalt, nur **einmal** pro Seite), `article` (in sich geschlossen), `section` (Themenblock, mit Überschrift), `aside` (Nebeninhalt), `footer` (Abschluss, z. B. Impressum-Link/Copyright). `div`/`span` nur, wenn nichts Passendes existiert.
- Überschriften: genau eine `h1`, danach logisch absteigend (h2 → h3, nicht h2 → h4). Die Ebene folgt der Struktur, nicht der gewünschten Größe (Optik per CSS).
- Nutzen: Screenreader können gezielt zu Navigation/Hauptinhalt springen.
- Typischer Fehler: alles aus `div`s, Überschriften nach Schriftgröße statt Struktur gewählt.
- ❓ Offen: Informationsarchitektur (Seitenbaum, Content-Planung), typische Abschnitte einer Startseite.
- Quelle: MDN, „Structuring documents" (abgerufen 2026-10-26) – https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content/Structuring_documents

---

## 6. Performance und Ladezeit (Teilwissen)

*Stand: 2026-10-26*

**Core Web Vitals** (web.dev „Web Vitals", zuletzt aktualisiert 31.10.2024): Maßstab ist das 75. Perzentil der Seitenaufrufe, getrennt nach Mobil und Desktop.

| Metrik | Misst | Zielwert „gut" |
|---|---|---|
| LCP | Ladezeit des größten sichtbaren Elements | ≤ 2,5 s |
| INP | Reaktionszeit auf Eingaben | ≤ 200 ms |
| CLS | Layoutverschiebungen | ≤ 0,1 |

**LCP verbessern** (web.dev, aktualisiert 31.03.2025): Hero-/LCP-Bild im HTML referenzieren (nicht erst per JS/CSS-Hintergrund), `fetchpriority="high"` nur für dieses eine Bild, **nie** `loading="lazy"` am LCP-Bild, moderne Formate (AVIF/WebP), passende Bildgröße, niedrige Server-Antwortzeit (TTFB), Weiterleitungen vermeiden, CDN/Caching, render-blockierendes CSS/JS reduzieren.

**CLS verbessern** (web.dev, aktualisiert 07.02.2025): Bildern/Videos immer `width`+`height` (oder `aspect-ratio`) geben; für Einbettungen/Anzeigen Platz reservieren (`min-height`); `font-display: optional` oder passende Fallback-Schrift mit `size-adjust`; kritische Fonts per `preload`; Animationen über `transform`; neue Inhalte nur nach Nutzeraktion einfügen.

**Typische Fehler:** großes Hero-Bild ohne Maße und lazy geladen; viele Schnitte/Webfonts; Einbettungen ohne reservierten Platz.

**Quellen:** web.dev „Web Vitals" (https://web.dev/articles/vitals) · „Optimize Largest Contentful Paint" (https://web.dev/articles/optimize-lcp) · „Optimize Cumulative Layout Shift" (https://web.dev/articles/optimize-cls)

**INP** (web.dev, veröffentlicht 06.05.2022, aktualisiert 02.09.2025): misst die Latenz aller Klicks/Taps/Tastatureingaben über den ganzen Besuch (nicht Scrollen/Hover/Zoom), bis zum nächsten gemalten Frame. **gut ≤ 200 ms · verbesserungswürdig 200–500 ms · schlecht > 500 ms** (75. Perzentil, getrennt nach Mobil/Desktop). https://web.dev/articles/inp

**HTTP-Caching** (web.dev, 05.11.2018): Dateien mit Versionsnamen/Hash (`style.x234dff.css`) → `Cache-Control: max-age=31536000` (1 Jahr), optional `immutable`. HTML ist nicht versionierbar → `no-cache` (Browser fragt vor Nutzung nach) plus `ETag` (Antwort `304 Not Modified` spart den Download). `no-store` = nirgends speichern, `private` = nur Browser, `public` = auch CDN. Fehlender Header deaktiviert Caching nicht, Browser raten → explizit setzen. Bei Baukästen/KI-Hostern meist automatisch, ❓ nicht prüfbar ohne Messung. https://web.dev/articles/http-cache

**Lighthouse** (Chrome, aktualisiert 02.06.2025): Open-Source-Audit mit Kategorien Performance (u. a. FCP, LCP, TBT), Accessibility, Best Practices, SEO. Start: Chrome-DevTools → Reiter „Lighthouse", per `npm install -g lighthouse` + `lighthouse <url>`, oder **PageSpeed Insights** ohne Installation. Fehlgeschlagene Audits sind Hinweise mit Erklärung. Lab-/Felddaten-Unterschied erklärte die Seite nicht (❓). https://developer.chrome.com/docs/lighthouse/overview

**Lab vs. Feld** (web.dev, 18.07.2022): Lab (Lighthouse) = kontrollierte, reproduzierbare Messung für **ein** Gerät/Netz/Standort; Feld (CrUX, 28 Tage, 75. Perzentil) = echte Nutzer. Abweichungen u. a.: Lab misst kalten Cache, Feld oft Cache-Treffer; CLS im Feld über die gesamte Lebensdauer, im Lab meist nur beim Laden. **Felddaten haben Vorrang**; Lab zum Debuggen. https://web.dev/articles/lab-and-field-data-differences
**INP verbessern** (web.dev, aktualisiert 02.09.2025): lange Tasks im Hauptthread vermeiden/aufteilen, Event-Handler schlank halten und per Yielding Arbeit aufteilen, Layout-Thrashing vermeiden, **kleines DOM**, `content-visibility`, nicht große HTML-Mengen per Client-JS erzeugen. https://web.dev/articles/optimize-inp
**Bildformate** (MDN): Fotos → **WebP** (≈25–35 % kleiner als JPEG) oder **AVIF** (beste Kompression, mit Fallback; Safari ab 16.1), JPEG als Fallback; Logos/Screenshots/Transparenz → PNG oder WebP lossless; **Icons/Diagramme → SVG**; GIF veraltet. **Responsive Bilder:** `srcset` + `sizes` (Auflösung/Größe), `<picture>` nur für Art Direction, `alt` und `src` am `img` Pflicht; Austausch per JS/CSS käme zu spät (Preload). https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Formats/Image_types
**CDN** (web.dev, 05.12.2023): verteilte Server nahe am Nutzer, senkt Latenz/TTFB (hilft LCP); statisch lange cachen, dynamisch kurz; `private`/`no-store` nicht ins CDN; Ziel Cache-Hit-Ratio ca. 90 %; bei der Auswahl Performance, Funktionen, Preis, Support; **eigene Tests**, da Leistung nach Region/Tageszeit schwankt; Brotli, TLS 1.3, HTTP/2/3 aktivieren. https://web.dev/articles/content-delivery-networks
**Ranking-Einfluss** (Google, „Understanding page experience", aktualisiert 22.09.2026): Core Web Vitals werden von den Ranking-Systemen genutzt, aber **kein einzelnes Page-Experience-Signal**; gute Werte garantieren kein Top-Ranking; nicht nur für SEO auf perfekte Scores optimieren. https://developers.google.com/search/docs/appearance/page-experience
❓ Offen: konkrete Hosting-/CDN-Wahl für Baukästen (nicht prüfbar ohne Anbieterdaten).

---

## 7. Barrierefreiheit

*Stand: 2026-10-26* — alle Angaben WCAG 2.2 (W3C „Understanding"-Seiten, selbst abgerufen)

| Kriterium | Level | Anforderung |
|---|---|---|
| 1.4.3 Kontrast (Minimum) | AA | Normaler Text ≥ **4,5:1**; großer Text (≥18 pt bzw. ≥14 pt fett ≈ 24 px / 18,5 px) ≥ **3:1**. Keine Rundung. Gilt auch für Platzhalter, Hover/Fokus-Text. Ausnahme: Logos, Deko, deaktivierte Elemente; CI-Vorgaben befreien nicht. |
| 1.4.6 Kontrast (Enhanced) | AAA | Normaler Text ≥ **7:1**, großer Text ≥ **4,5:1**. |
| 1.4.4 Text vergrößern | AA | bis 200 % ohne Verlust. |
| 1.4.10 Reflow | AA | 320 CSS-px Breite ohne 2D-Scrollen (≈400 % Zoom). |
| 1.4.12 Textabstand | AA | Kein Verlust bei Zeilenhöhe 1,5×, Absatzabstand **2× Schriftgröße**, Buchstaben 0,12×, Wort 0,16×. |
| 1.4.8 Visuelle Darstellung | AAA | Zeilen ≤ **80 Zeichen**; Zeilenabstand ≥ 1,5; Absatzabstand ≥ **1,5× Zeilenabstand**; kein Blocksatz; Farben wählbar. |
| 2.1.1 Tastatur | A | Alles per Tastatur bedienbar (außer Freihandbewegungen); nur-Maus-Handler und Skripte, die den Fokus entfernen, sind typische Fehler. |
| 2.4.7 Fokus sichtbar | AA | Sichtbarer Tastaturfokus; `outline` nicht entfernen/unsichtbar machen. Fokusindikator unterliegt auch Nicht-Text-Kontrast (1.4.11). |
| 2.4.11 Fokus nicht verdeckt | AA | Fokussiertes Element darf nicht **vollständig** verdeckt sein – typische Ursachen: Sticky Header/Footer, Cookie-Banner. Lösung: `scroll-padding`, modale Banner. |
| 2.5.8 Zielgröße | AA | Klickziele ≥ **24×24 CSS-px** oder genug Abstand (24-px-Kreis); Ausnahme u. a. Inline-Links im Text. |

| 1.4.1 Farbe nicht allein | A | Farbe darf nicht das einzige Mittel sein (Pflichtfeld nicht nur rot, gültig/ungültig nicht nur grün/rot); Helligkeitsunterschied ≥ 3:1 gilt als zusätzliches Merkmal. |
| 2.4.1 Blöcke umgehen | A | Mechanismus zum Überspringen wiederkehrender Blöcke: **Skip-Link** zum Hauptinhalt, Landmarks (`nav`, `main`), Überschriften pro Abschnitt. |
| 3.3.1 Fehler erkennen | A | Automatisch erkannte Eingabefehler: Feld identifizieren und Fehler **als Text** beschreiben (Farbe/Symbol nur zusätzlich); Techniken: `aria-invalid`, `role="alert"`/Live-Region; empfohlen: Sprung zu Fehlern, Erfolgsmeldung. Native Browser-Validierung zeigt oft generische Meldungen, nur den ersten Fehler, nicht zoomfest → prüfen. |
| 3.3.2 Labels/Anweisungen | A | Jedes Eingabefeld hat Label/Anweisung (`<label>`, `fieldset`+`legend` für Gruppen); Formathinweise (z. B. Datum). |
| 3.3.3 Fehlervorschläge | AA | Sind Korrekturvorschläge bekannt, müssen sie angeboten werden (z. B. gültige Werte oder „Meinten Sie Dezember?"); Ausnahme: gefährdet Sicherheit/Zweck. |
| 1.3.5 Eingabezweck | AA | Felder zu Angaben über die Person (Name, E-Mail, Adresse, Telefon) tragen das passende `autocomplete`-Token (`given-name`, `email`, `tel` …); falsche Werte sind ein Fehler. |
| 2.1.2 Keine Tastaturfalle | A | Fokus muss per Tastatur wieder verlassbar sein; Modal darf Fokus halten, wenn Esc/„Abbrechen" funktioniert; Ursachen: eigene Widgets, eingebettete Inhalte, Editoren. |

**ARIA** (W3C APG „Read Me First"): *„No ARIA is better than Bad ARIA"*; eine Rolle ist ein Versprechen (`role="button"` auf `div` verlangt auch Tastaturverhalten per JS); ARIA kann Semantik überdecken. Folgerung: zuerst natives HTML (`button`, `a`, `nav`, `label`), ARIA nur ergänzend, mit Assistenztechnik testen. (Die Seite nennt „natives HTML zuerst" nicht wörtlich.)

**Alt-Texte** (W3C WAI Entscheidungsbaum): informatives Bild → kurze Beschreibung der Bedeutung; **dekorativ → leeres `alt=""`**; Bild als Link/Button → Ziel bzw. Aktion beschreiben; komplexe Grafik → Details an anderer Stelle der Seite; Text im Bild → Text ins `alt`, außer er steht schon als echter Text daneben.

**Abgleich Absatzabstand:** Die Angabe „1,5× Zeilenabstand" (Webdesign Journal) stammt aus 1.4.8 (AAA) und ist korrekt; für AA (1.4.12) gilt nur: Layout darf bei 2× Schriftgröße nichts verlieren. Beide Aussagen gleichzeitig wahr.

Außerdem: `prefers-reduced-motion` beachten, Zoom nie sperren (siehe 4/5).
**Typische Fehler:** hellgraue Schrift auf Weiß (#999 ≈ 2,85:1, eigene Rechnung); Fokus-Outline per CSS entfernt; Sticky-Header/Cookie-Banner verdecken Fokus; winzige Icon-Buttons; feste Höhen, die bei größerem Text Inhalt abschneiden; Deko-Bilder mit Alt-Text.
**ARIA-Muster Navigation** (W3C APG „Disclosure Navigation Menu"): `nav`-Landmark mit Namen, Liste, je Untermenü ein **Button mit `aria-expanded` und `aria-controls`**, aktueller Link `aria-current="page"`; Tab/Umschalt+Tab, Enter/Leertaste öffnet, **Esc schließt und gibt Fokus an den Button zurück**; **kein `role="menu"`** für normale Website-Navigation (dafür wäre komplexes Tastaturverhalten nötig). https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/examples/disclosure-navigation/
❓ Offen: Test mit echtem Screenreader (NVDA/VoiceOver/JAWS) – in dieser Umgebung nicht möglich; weitere ARIA-Muster (Tabs, Dialog, Akkordeon) nicht gelesen.
Quellen (WCAG 2.2 Understanding, W3C, abgerufen 2026-10-26): …/contrast-minimum.html · …/contrast-enhanced.html · …/visual-presentation.html · …/text-spacing.html · …/reflow.html · …/keyboard.html · …/bypass-blocks.html · …/labels-or-instructions.html · …/use-of-color.html · …/error-identification.html · …/focus-visible.html · …/focus-not-obscured-minimum.html · …/target-size-minimum.html (alle unter https://www.w3.org/WAI/WCAG22/Understanding/) · Alt-Texte: https://www.w3.org/WAI/tutorials/images/decision-tree/ · ARIA: https://www.w3.org/WAI/ARIA/apg/practices/read-me-first/
(zusätzlich abgerufen: …/error-suggestion.html · …/identify-input-purpose.html · …/no-keyboard-trap.html)

---

## 8. SEO-Grundlagen (Teilwissen)

*Stand: 2026-10-26* — Quelle: Google Search Central „SEO Starter Guide", zuletzt aktualisiert 10.12.2025 – https://developers.google.com/search/docs/fundamentals/seo-starter-guide

- `<title>`: je Seite einzigartig, klar, prägnant, inhaltlich zutreffend.
- Meta-Description: kurz, pro Seite unterschiedlich; Google nimmt das Snippet meist aus dem Seitentext, selten aus der Description.
- URLs: sprechende Wörter statt Zufalls-IDs.
- Überschriften gliedern Inhalt für Menschen; Reihenfolge/Anzahl beeinflussen laut Guide das Ranking nicht.
- Linktexte beschreibend; fremde/nutzererzeugte Links mit `nofollow` o. Ä.
- Bilder: scharf, nah am passenden Text, kurzer sinnvoller `alt`-Text.
- Inhalte: hilfreich, lesbar, aktuell, für Menschen geschrieben; Keywords nicht überladen.
- Typische Fehler: gleiche Titel auf allen Seiten, „Klick hier"-Links, Bilder ohne Alt, Keyword-Stuffing.
- **Sitemap** (Google, 10.12.2025): Datei mit Seiten/Medien der Website; hilfreich bei großen oder neuen Seiten mit wenigen externen Links; bei kleinen Seiten (~≤500 Seiten) mit guter interner Verlinkung oft nicht nötig. Garantiert kein Crawling/Indexieren; Wix/WordPress/Blogger erzeugen sie meist automatisch. https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview
- **robots.txt** (Google, 10.12.2025): steuert **Crawling** (Serverlast), ist **kein** Mittel gegen Indexierung – blockierte URL kann ohne Beschreibung trotzdem in den Ergebnissen erscheinen. Aus der Suche heraushalten: `noindex` (Meta-Tag/Header), Passwortschutz oder löschen. Kein Sicherheitsmechanismus. Skripte/Stylesheets nur blockieren, wenn die Seite ohne sie nicht leidet. https://developers.google.com/search/docs/crawling-indexing/robots/intro
- Typischer Fehler: Seite mit `robots.txt` „verstecken" statt `noindex`; Test-/Entwurfsseiten öffentlich lassen.
- **Strukturierte Daten** (Google, 10.12.2025): standardisierte Beschreibung von Seiteninhalt (z. B. Rezept, Produkt); **JSON-LD empfohlen** (Skript-Tag, getrennt vom Text), Microdata/RDFa gleichwertig. Nur Sichtbares markieren, Seiten nicht nur dafür bauen. Ermöglichen **Rich Results**, **versprechen aber kein besseres Ranking**. Tests: Rich-Results-Test, Status-Berichte, URL-Prüftool. https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data
- **Lokale Suche** (Google-Unternehmensprofil-Hilfe): Profil **verifizieren**, Adresse/Öffnungszeiten/Branche aktuell halten, Bewertungen beantworten, Fotos hinzufügen. Ranking-Faktoren: **Relevanz, Entfernung, Bekanntheit** (Links, Anzahl/Bewertung der Rezensionen); Ranking lässt sich weder anfordern noch bezahlen. https://support.google.com/business/answer/7091
- Ranking-Einfluss der Core Web Vitals: siehe Abschnitt 6 (Google: werden genutzt, aber keine Garantie).

---

## 9. Rechtliches Deutschland (Orientierung, keine Rechtsberatung)

*Stand: 2026-10-26*

**Impressum – § 5 DDG** (Gesetzestext gelesen: gesetze-im-internet.de/ddg/__5.html; Seite nennt keinen Fassungsstand). DDG gilt seit 14.05.2024 statt TMG (IHK-Merkblätter). Abs. 1 verlangt:
1. Name + Niederlassungsanschrift; bei juristischen Personen zusätzlich Rechtsform, Vertretungsberechtigte, ggf. Stamm-/Grundkapital und ausstehende Einlagen
2. Angaben für schnelle elektronische Kontaktaufnahme und direkte Kommunikation, **inkl. E-Mail-Adresse**
3. Aufsichtsbehörde bei zulassungspflichtiger Tätigkeit
4. Register + Registernummer, falls eingetragen
5. Kammer/Berufsbezeichnung/Berufsregeln bei reglementierten Berufen
6. USt-IdNr. bzw. Wirtschafts-IdNr., falls vorhanden
7. Hinweis auf Abwicklung/Liquidation bei AG, KGaA, GmbH
Form: leicht erkennbar, unmittelbar erreichbar, ständig verfügbar (IHK; „Postfach reicht nicht" nach IHK). ❓ Anforderungen an Erreichbarkeit/Benennung („Impressum"-Link) aus Gesetzestext nicht geprüft.

**Cookies/Tracking – § 25 TDDDG** (Gesetzestext gelesen via dejure.org): Abs. 1: Speichern/Auslesen von Informationen auf dem Endgerät **nur mit Einwilligung**, nach vorheriger verständlicher, umfassender Information (Einwilligung nach DSGVO). Abs. 2: **keine Einwilligung nötig**, wenn (1) einziger Zweck die Übertragung einer Nachricht über ein öffentliches Netz ist oder (2) der Vorgang **unbedingt erforderlich** ist, damit der Anbieter einen vom Nutzer **ausdrücklich gewünschten** digitalen Dienst bereitstellen kann. Beispiele „erforderlich" (Kanzlei/GDD-Sekundärquellen, ❓ nicht an der DSK-Orientierungshilfe geprüft): Warenkorb, Login, Spracheinstellung, Lastverteilung, Speicherung der Einwilligung selbst; Analyse/Werbung gelten nicht als erforderlich.

**DSK-Orientierungshilfe Digitale Dienste, Version 1.2, Stand November 2024** (Original-PDF von DSK/BfDI selbst gelesen, 36 Seiten; Rn. = Randnummer):
- **Banner-Gestaltung:** Ablehnen muss **ohne Mehraufwand** möglich sein; Ablehnung erst auf einer zweiten Ebene gilt als Mehraufwand, der die Freiwilligkeit beeinträchtigt (Rn. 58). Optionen **gleichwertig gestalten** (Rn. 59). Fehlt ohne sachlichen Grund eine Ablehnung mit gleichem Aufwand auf erster Ebene, verstößt das gegen Treu und Glauben (Rn. 60).
- **Ablehnoption:** eindeutig erkennbar, leicht wahrnehmbar, unmissverständlich (Rn. 134); gleichwertig, z. B. Button „Weiter ohne Einwilligung" in **Größe, Farbe, Kontrast und Schriftbild** vergleichbar mit „Einwilligung erteilen" (Rn. 135). Nicht ausreichend: Ablehnen nur außerhalb des Banners, im Fließtext versteckt oder erst nach Scrollen sichtbar (Rn. 136). Ein Button **„Einstellungen oder Ablehnen"**, der auf eine weitere Ebene führt, genügt **nicht** (Rn. 137).
- **Wichtige Einschränkung (Rn. 124/125):** Eine Ablehnfunktion auf erster Ebene ist „nicht generell erforderlich", sondern nur, wenn Nutzer mit dem Banner **interagieren müssen**, um weiterzumachen (Inhalte verdeckt). Bei gängigen Bannern sind die Voraussetzungen „sehr häufig" erfüllt. Banner dürfen auch auf kleinen Displays keine Inhalte versperren.
- **Widerruf** muss so einfach sein wie die Erteilung (Rn. 126). Kein allgemeiner Standard für Farbe/Größe/Kontrast des Banners (Rn. 127).
- **„Unbedingt erforderlich" (Rn. 78–83):** streng auszulegen (Zeitpunkt, Laufzeit, Inhalt, Domäne auf Minimum reduzieren). Warenkorb-Cookies erst nach tatsächlicher Nutzerinteraktion (Artikel im Warenkorb), nicht schon beim Stöbern (Rn. 80). **Sprach- oder Hintergrundfarb-Einstellungen** ohne eindeutige User-ID (z. B. `language: de`) zählen als erforderlich (Rn. 81). Login-Schutz-Cookies nur bei erfüllten Voraussetzungen (Rn. 83). Consent-Management-Plattformen mit eindeutiger Benutzerkennung sind kritisch (Rn. 92).
- **Drittinhalte:** Einbindung (u. a. **Schriftarten**, Skripte, Karten, Videos, Fotos, Social-Media) offenbart regelmäßig personenbezogene Daten an den Drittserver und braucht eine Rechtsgrundlage; Rechenschaftspflicht, in der Datenschutzerklärung nennen (Rn. 101).
- Quelle: DSK/BfDI, „Orientierungshilfe der Aufsichtsbehörden für Anbieter:innen von digitalen Diensten (OH Digitale Dienste) Version 1.2", Nov. 2024 – https://www.bfdi.bund.de/SharedDocs/Downloads/DE/DSK/Orientierungshilfen/OH_Digitale-Dienste.pdf?__blob=publicationFile&v=1 — Behördenauslegung, kein Gesetz; keine Rechtsberatung.

**Gericht (Banner):** VG Hannover, 19.03.2025, Az. 10 A 5385/22 (laut zm-online am 19.05.2025 bekanntgegeben; **Urteilstext nicht gefunden**, nur Kanzlei-/Fachberichte: WBS.LEGAL, Dr. Datenschutz): Banner mit „Alle akzeptieren"/„Einstellungen" ohne gleichwertiges Ablehnen auf erster Ebene → Einwilligung unwirksam; vorausgewählte Felder unzulässig; Google Tag Manager einwilligungspflichtig. Deckt sich mit DSK-OH (Rn. 58–60, 137). ❓ Wortlaut/Randnummern des Urteils nicht geprüft.

**Datenschutzerklärung – Art. 13 DSGVO** (Gesetzestext gelesen via dejure.org). Bei Datenerhebung mitzuteilen: Verantwortlicher + Kontakt, ggf. Datenschutzbeauftragter, **Zwecke und Rechtsgrundlage**, berechtigte Interessen (bei Art. 6 Abs. 1 lit. f), Empfänger(kategorien), Drittlandübermittlung + Garantien; zusätzlich **Speicherdauer**, Betroffenenrechte (Auskunft, Berichtigung, Löschung, Einschränkung, Widerspruch, Übertragbarkeit), **Widerrufsrecht** bei Einwilligung, **Beschwerderecht** bei Aufsichtsbehörde, ob Bereitstellung vorgeschrieben/erforderlich ist, automatisierte Entscheidung/Profiling. → Die Erklärung muss zu den **tatsächlich genutzten Diensten** passen (Schriften, Formulare, Einbettungen, Analytics).

**Google Fonts:** LG München I, 3. Zivilkammer, Urteil vom **20.01.2022** (Zitierempfehlung der Fundstelle nennt 19.01.2022), Az. 3 O 17493/20 — **Entscheidungstext gelesen** (Archivkopie von rewis.io): *Tenor:* Unterlassen der IP-Weitergabe an Google über Google Fonts, Ordnungsgeld bis 250.000 € je Fall; Auskunft nach Art. 15 DSGVO; **100 € Schadensersatz**. *Gründe (Kurzfassung):* dynamische IP-Adresse ist auch für den Betreiber personenbezogen (BGH VI ZR 135/13); ohne Einwilligung Eingriff in informationelle Selbstbestimmung; kein berechtigtes Interesse, weil Google Fonts auch **ohne Verbindung zu Google-Servern** eingebunden werden kann (lokal); keine Pflicht des Besuchers, die IP zu verschleiern; Wiederholungsgefahr entfällt nicht durch bloße Umstellung (nur strafbewehrte Unterlassungserklärung); immaterieller Schaden: Kontrollverlust, Übermittlung in die USA, Höhe 100 € nicht angegriffen. ❓ Spätere Rechtsprechung anderer Gerichte nicht geprüft; Einzelfall-Urteil einer Kammer, keine einheitliche Rechtslage.

**BFSG (Barrierefreiheit)** — Quelle: Bundesfachstelle Barrierefreiheit (Bund), Startseite BFSG + FAQ (selbst gelesen; Gesetzestext gesetze-im-internet 503, nicht abrufbar):
- Gilt für Produkte/Dienstleistungen, die **seit 28.06.2025** hergestellt bzw. erbracht werden.
- **Websites/Online-Shops:** betroffen, wenn darüber **Dienstleistungen für Verbraucher** angeboten werden (Online-Banking, elektronischer Geschäftsverkehr – z. B. Online-Kauf, Online-Terminbuchung). **Reine Informations-/Werbeseiten fallen voraussichtlich nicht darunter** (fehlende „individuelle Anfrage" des Verbrauchers). Für Shops gelten Informationspflichten zur Barrierefreiheit und barrierefreie Identifizierungs-, Authentifizierungs-, Signatur- und Zahlungsfunktionen.
- **Kleinstunternehmen** (< 10 Beschäftigte und ≤ 2 Mio. € Jahresumsatz): bei **Dienstleistungen** ausgenommen; wer **Produkte** in Verkehr bringt, nicht. Kostenlose Beratung durch die Bundesfachstelle.
- **Standard:** Für Websites gilt EN 301 549, die auf **WCAG 2.1 Level A und AA** verweist; eine aktualisierte Fassung soll auf WCAG 2.2 verweisen. → Die WCAG-2.2-Kriterien in Abschnitt 7 sind eine Obermenge/Annäherung; maßgeblich für die Pflicht ist die Norm.
- **Aufsicht:** Seit 26.09.2025 Marktüberwachungsstelle der Länder (MLBF) in Magdeburg; bei Dienstleistungen stichprobenartig; bei Verstoß Aufforderung zur Herstellung der Konformität, dann Bußgelder bis zur Untersagung. (Bußgeldhöhe „bis 100.000 €" nur aus Sekundärquellen/IHK, ❓ nicht am Gesetz geprüft.)
- Offen/Streit: Betrifft die Anforderung die ganze Website oder nur den Bestellprozess? Sekundärquelle (Kanzlei) sagt: ganze Website; ❓ ungeklärt. Bundesfachstelle-FAQ (Rest gelesen): Verbraucher können sich an die Marktüberwachung wenden, bei Ablehnung Verwaltungsgericht; **Verbandsklage** vorgesehen; kostenlose **Schlichtungsstelle BGG** für Verbraucher; **kostenlose Beratung** (§ 15 BFSG) für Kleinstunternehmen (Beratungsteam laut Seite noch im Aufbau). EU-Richtlinie 2019/882 und BFSG-Gesetzestext: Abruf scheiterte (EUR-Lex leer, gesetze-im-internet 503) → ❓ im Original ungeprüft.
- Quelle: Bundesfachstelle Barrierefreiheit – https://www.bundesfachstelle-barrierefreiheit.de/DE/Fachwissen/Produkte-und-Dienstleistungen/Barrierefreiheitsstaerkungsgesetz/barrierefreiheitsstaerkungsgesetz_node.html · FAQ: …/Barrierefreiheitsstaerkungsgesetz/FAQ/faq_node.html (abgerufen 2026-10-26; FAQ zu ~88 % gelesen)

**Praxis für KI-Builder-Seiten:** Footer-Links „Impressum"/„Datenschutz" auf jeder Seite; Impressum vollständig nach Rechtsform; Schriften lokal; keine Tracker/Einbettungen (YouTube, Maps, Analytics) ohne Einwilligungslösung; Cookie-Banner mit „Alles ablehnen" (statt „Einstellungen oder Ablehnen") gleichwertig in Größe/Farbe/Kontrast auf Ebene 1; Datenschutzerklärung an genutzte Dienste anpassen.
**Typische Fehler:** Impressum versteckt; Vorlage ungeprüft; Google Fonts per CDN; Tracking vor Einwilligung; Banner nur mit „Akzeptieren"/„Einstellungen".

**Quellen:** Gesetze: DDG § 5 – https://www.gesetze-im-internet.de/ddg/__5.html · TDDDG § 25 – https://dejure.org/gesetze/TDDDG/25.html · DSGVO Art. 13 – https://dejure.org/gesetze/DSGVO/13.html · Bundesfachstelle Barrierefreiheit (BFSG) – https://www.bundesfachstelle-barrierefreiheit.de/DE/Fachwissen/Produkte-und-Dienstleistungen/Barrierefreiheitsstaerkungsgesetz/barrierefreiheitsstaerkungsgesetz_node.html · Sekundär: IHK München Merkblatt 05/2024 (https://ihk-muenchen.de/ihk/Merkblätter-WettbewerbsR/Pflichtangaben-Internetimpressum_Stand05_2024.pdf) · DSK/BfDI OH Digitale Dienste (s. o.) · WBS.LEGAL zu VG Hannover (https://www.wbs.legal/it-und-internet-recht/datenschutzrecht/vg-hannover-zu-einwilligungsbutton-cookie-banner-brauchen-alles-ablehnen-schaltflaeche-82973/) · IHK Bergische zu Google Fonts (https://www.ihk.de/bergische/recht-und-steuern/wettbewerbsrecht/google-fonts-5646176)

---

## 11. Prüfung und Qualitätskontrolle fertiger Seiten (Checkliste)

*Stand: 2026-10-26* — eigene Zusammenstellung **nur aus den oben geprüften Quellen**; erster Praxistest siehe unten (apple.com/de). Die 90-Punkte-Checkliste des Webdesign Journals war nicht einsehbar (Anmeldeformular) und ist **nicht** Grundlage.

**Struktur & Navigation:** eine `h1`, Überschriften logisch absteigend · `header/nav/main/footer`, `main` nur einmal · Logo links, verlinkt auf Startseite · Hauptnavigation auf Desktop sichtbar (kein Hamburger), mobil ≤4 Hauptlinks sichtbar oder wichtige Inhalte auch per Inhalts-Links · Linktexte konkret (nicht „Mehr erfahren") · Slogan sagt klar, was angeboten wird.
**Layout & Responsive:** Viewport-Meta-Tag · Zoom nicht gesperrt · bei 320 px kein horizontales Scrollen · Breakpoints nach Inhalt · Fließtext-Zeilen ≤ 80 Zeichen.
**Schrift:** Fließtext `line-height` ≥ 1,5 (Zahl ohne Einheit) · Größen relativ (`rem`), nicht fest in Pixeln · Buttons mit konkreten Labels, ein primärer (gefüllter) Button je Bereich ·, `clamp()` mit Max ≥ 2× Min · WOFF2, lokal gehostet, wenige Schnitte, `font-display` bewusst gesetzt · Icon-Fonts durch SVG ersetzt.
**Farben & Kontrast:** Text 4,5:1 (groß 3:1) · Information nie nur über Farbe · Dark Mode (falls vorhanden) mit gleichen Kontrastwerten.
**Animation:** nur `transform`/`opacity` · 100–400 ms, ease-out beim Erscheinen · `prefers-reduced-motion` respektiert · kein Autoplay/Parallax ohne Kontrolle · keine Info nur über Bewegung.
**Barrierefreiheit:** Formularfehler als Text beschrieben · alles per Tastatur bedienbar · Fokus sichtbar und nicht von Sticky-Header/Banner verdeckt · Skip-Link · Klickziele ≥ 24×24 px · Formularfelder mit `<label>` und passendem `autocomplete` · Fehler mit Korrekturvorschlag · Fokus per `:focus-visible` gestaltet (≥ 3:1) · Alt-Texte (dekorativ = `alt=""`) · ARIA nur wenn nötig.
**Performance:** LCP ≤ 2,5 s, INP ≤ 200 ms, CLS ≤ 0,1 · LCP-Bild nicht lazy, mit `fetchpriority="high"` · Bilder mit `width`/`height` · AVIF/WebP · Platz für Einbettungen reserviert.
**SEO:** eigener `<title>` je Seite · Testseiten mit `noindex`, nicht mit robots.txt · Sitemap vorhanden (meist automatisch) · aussagekräftige Meta-Description · sprechende URLs · Bilder mit Alt · hilfreiche, aktuelle Inhalte.
**Recht:** Impressum und Datenschutz im Footer jeder Seite · Impressum nach § 5 DDG vollständig (inkl. E-Mail) · Datenschutzerklärung nennt alle genutzten Dienste (Art. 13 DSGVO) · Schriften lokal · Banner mit gleichwertigem „Alles ablehnen" · keine Tracker vor Einwilligung · BFSG-Pflicht prüfen (Verbraucher-Dienstleistung/Shop? Kleinstunternehmen?).
**Prüfwerkzeuge (belegt; Lighthouse 13.5.0 selbst im Container ausgeführt):** Lighthouse/PageSpeed Insights (Performance, Accessibility, Best Practices, SEO; Hinweise zu Fehlern); WebAIM Color Contrast Checker (laut MDN genannt, selbst nicht geöffnet); BIK BITV-Test und barrierefreies-webdesign.de (laut Bundesfachstelle für Prüfschritte empfohlen). ❓ WAVE, axe, Screenreader-Test nicht recherchiert. Handprüfung: nur mit Tab-Taste durchklicken, auf 200 %/400 % zoomen, Browser-Schriftgröße erhöhen, „Bewegung reduzieren" im Betriebssystem einschalten.

### Praxistest der Checkliste: apple.com/de (aufgerufen über apple.de, 2026-10-26)

Methode: Seite mit Chromium (Playwright) geladen, Desktop 1280 px und 320 px, Werte per Skript aus dem gerenderten Dokument gelesen, zwei Screenshots angesehen. **Nur Startseite, nur Momentaufnahme, kein Lighthouse, kein Screenreader.** Standort des Abrufs war nicht Deutschland (Apple blendete ein Länder-Banner „Choose another country…" ein) → Tab-Reihenfolge und Banner-Befund dadurch verfälscht.

| Prüfpunkt | Messung | Status |
|---|---|---|
| Viewport-Tag | `width=device-width, initial-scale=1, viewport-fit=cover`, kein Zoom-Sperren | ✅ |
| Sprache | `lang="de-DE"` | ✅ |
| `<title>` / Description | „Apple (Deutschland)"; Description (og:description) vorhanden | ✅ |
| Landmarks | `main` 1×, `nav` 2×, `footer` ja, **`header`-Element nicht gefunden** | ❓ (kein Fehler, nur andere Umsetzung) |
| Überschriften | eine `h1` („Apple"), **visuell versteckt** (`visuallyhidden`), danach h2/h3 | ✅ Struktur / ❓ h1 unsichtbar |
| Bilder | 54 Bilder, 0 ohne `alt`, 37 mit `alt=""` (dekorativ) | ✅ |
| Bilder `width`/`height` | bei 54 Bildern nicht als Attribute gesetzt; **gemessener CLS 0,057** (Lab, Cloud-Container, ≤ 0,1) → kein Layoutsprung beobachtet | ✅ Lab / ❓ Felddaten |
| LCP-Bild | LCP-Element = Hero-Bild (`<img>` iPad mini), **nicht lazy**, kein `fetchpriority`-Attribut; **LCP ≈ 1,7 s** (Lab, Cloud, ohne Drosselung; ≤ 2,5 s) | ✅ Lab / ❓ Felddaten |
| Fließtext | 17 px, Zeilenhöhe 25 px (≈1,47), Farbe rgb(29,29,31) auf Weiß, Schrift SF Pro Text/Display | ✅ Größe; Zeilenhöhe knapp < 1,5 (Richtwert aus MDN/WCAG-AAA) |
| Schriftfamilien | 2 (SF Pro Text, SF Pro Display) | ✅ passt zu „1–2 Familien" |
| Kontrast Buttons | „Weitere Infos" weiß auf rgb(0,113,227): **4,70:1**; „Preise ansehen" rgb(0,102,204) auf rgb(245,245,247): **5,11:1** (eigene Berechnung nach WCAG-Formel) | ✅ ≥ 4,5:1 |
| Kontrast Hero-Untertitel | nachgemessen: rgb(110,110,115) auf rgb(245,245,247), 19 px → **4,66:1** (≥ 4,5:1); übriger Text: 0 von 381 Elementen unter Schwelle | ✅ (knapp) |
| Fokus | beim Tab-Test `outline: solid 2px` auf allen 6 geprüften Elementen; keine `outline:none`-Regel auf `:focus` gefunden | ✅ (nur 6 Elemente geprüft) |
| Reduced Motion | 4 `prefers-reduced-motion`-Regeln im CSS | ✅ |
| Dark Mode | keine `prefers-color-scheme`-Regel im CSS | ❓ nicht vorhanden (kein Muss) |
| Reflow 320 px | `scrollWidth` = 320 = Viewport → kein horizontales Scrollen | ✅ |
| Navigation | Desktop: 11 Kategorien + Suche + Tasche sichtbar; 320 px: Logo, Suche, Tasche, **Hamburger** | ✅ passt zur NN/g-Empfehlung (Desktop sichtbar; mobil Kompromiss bei vielen Punkten) |
| Skip-Link | kein Link mit Sprungziel gefunden; beim Tab-Test war der **erste Fokus der Apple-Logo-Link** (danach Store, Mac, iPad …) → **kein Skip-Link beobachtet**. WCAG 2.4.1 lässt Landmarks/Überschriften als Alternative zu (Landmarks `main`/`nav` vorhanden) | ❓ kein klarer Verstoß |
| Klickziele ≥ 24×24 (Lighthouse/axe bestätigt) | **Lighthouse meldet Verstoß:** Footer-Rechtslinks nur 16 px hoch (z. B. Datenschutzrichtlinie 135×16, Nutzungsbedingungen 144×16, Rechtliche Hinweise 129×16), Sicherheitsabstand nur 19–20,6 px statt 24 px. Eigener Vortest: 11 Menü-Schaltflächen je 22×44 px (Breite < 24); bei 6 davon liegt ein weiteres Ziel mit Mittelpunkt < 24 px entfernt (vereinfachter Test, kein exakter 24-px-Kreis-Test; der Link und die „Menü“-Schaltfläche überlagern sich evtl.); Schließen-Button des Länder-Banners 18×18 | ❌ Footer-Links (Lab, Lighthouse); ❓ Menüleiste unklar |
| Ladezeit (einzelne Messung) | TTFB ≈ 527 ms, DCL ≈ 2,6 s, Load ≈ 2,6 s (Cloud-Container, kein Feldwert, **keine CWV-Aussage**) | ❓ |
| Caching HTML | `cache-control: max-age=294` | ❓ keine Bewertung möglich |
| Drittanbieter | nur `apple.com`-Hosts + `securemetrics.apple.com` | ✅ keine fremden Fonts/Tracker beobachtet (Momentaufnahme) |
| Footer-Rechtslinks | vorhanden: Datenschutz, Datenschutzrichtlinie, Verwendung von Cookies, Nutzungsbedingungen, Rechtliche Hinweise, Barrierefreiheit | ✅ |
| Impressum (§ 5 DDG) | Link „Impressum“ im Footer nicht gefunden; Seite „Rechtliche Hinweise“ (`/de/legal/`) enthält das Wort „Impressum“/„Anbieterkennzeichnung“ nicht | ❓ nicht belegt, ob Angaben anderswo stehen; keine Rechtsbewertung |
| Cookies/Consent | ohne Interaktion wurden 11 Cookies (u. a. `geo`, `ac_bnd`, `s_fid`, `s_vi`, `s_cc`, `dssid2`, `dssf`) und localStorage-Einträge gesetzt; **kein Consent-Banner angezeigt** (nur Länderauswahl, Abruf aus anderem Land). Wofür die Cookies dienen und ob § 25 TDDDG gilt, habe ich nicht geprüft | ❓ keine Bewertung |

**Lighthouse 13.5.0 (Mobil, simulierte Drosselung, aus Cloud-Container über Proxy, 2026-10-26 14:15 UTC) – Lab-Werte, keine Felddaten, nicht mit Desktop-Messung oben vergleichbar:**

| Kategorie | Wert |
|---|---|
| Performance | **0,31** (FCP 3,6 s · **LCP 9,1 s** · TBT 1.680 ms · **CLS 0,164** · Speed Index 4,9 s) |
| Accessibility | **0,89** |
| Best Practices | 1,00 |
| SEO | 1,00 |

- **Barrierefreiheit – 4 fehlgeschlagene Audits:** (1) `color-contrast`: Element `button button-neutral media-gallery-button` mit `aria-hidden="true"`, Kontrast **1,64:1** (#383839 auf #585859, 14 px) – vermutlich inaktive/versteckte Galerie-Pfeile, ❓ nicht geklärt; (2) `target-size`: Footer-Links (s. o.); (3) `label-content-name-mismatch`: sichtbarer Text steckt nicht im zugänglichen Namen (z. B. Einkaufstasche, Galerie-Links); (4) `aria-required-children`: Liste mit `role="list"` enthält nicht erlaubte `tabpanel`-Kinder.
- **Performance-Befunde:** LCP-Element = Hero-Bild iPad mini, im HTML auffindbar und nicht lazy, aber ohne `fetchpriority="high"`; LCP-Aufschlüsselung: TTFB 504 ms, Ladeverzögerung 39 ms, Ladedauer 116 ms, **Render-Verzögerung 708 ms** → Hauptproblem ist das Rendern, nicht das Bild selbst. Render-blockierend: `ac-analytics.js` (104 KB), `globalheader.umd.js` (167 KB) u. a. (geschätzt 1.900 ms). CLS 0,164 (1 Verschiebung im Hero-Bereich der Startseite); 54 Bilder ohne explizite `width`/`height` (Lighthouse: 0,5). Schriften: `font-display`-Hinweis (SF Pro, geschätzt 50–70 ms je Datei); Cache-Lebensdauern der Schriften nur 12–53 Minuten (Lighthouse: Einsparung ≈ 1.635 KiB bei Wiederbesuch); ungenutztes JS ≈ 173 KiB.
- **Einordnung:** Die Werte weichen stark von meiner Desktop-Messung ab (LCP 1,7 s, CLS 0,057, ungedrosselt). Ursache: Mobil-Profil mit simulierter Drosselung + Container/Proxy → **nicht als Aussage über echte Apple-Besucher verwenden** (dafür CrUX/PageSpeed-Felddaten nötig, nicht abgerufen). Als Methode zeigt der Test: Lab-Werte schwanken je nach Profil; immer Profil und Gerät dazuschreiben, Felddaten bevorzugen.

**Erkenntnisse für die Checkliste:** (1) Automatik-Skripte übersehen Texte, die in mehrere Elemente zerlegt sind → gezielt nachmessen (hier gelungen). (2) Standort/Region kann Banner und Reihenfolge verändern → für Recht/Banner mit deutscher IP prüfen. (3) `width`/`height` fehlt bei Apple als Attribut, gemessener CLS war trotzdem 0,057 → erst messen, dann urteilen. (4) Consent-/Cookie-Befund hängt vom Abrufland ab und ist ohne deutsche IP nicht aussagekräftig. (5) Lighthouse findet Dinge, die mein Skript nicht fand (Zielgröße Footer, Namen/Labels, ARIA-Struktur) – beide Methoden kombinieren. (6) Eine versteckte `h1` ist eine Designentscheidung, die Struktur bleibt zugänglich.

---

## 12. Gute Anweisungen an KI-Website-Builder

*Stand: 2026-10-26* — Quellen: **Lovable-Dokumentation**, **Framer** (Academy/Help), **Webflow** (Help) – alles Anbieter-Selbstaussagen, keine unabhängige Studie. ❓ Wix, v0 und andere nicht gefunden/geprüft; Prinzipien der drei geprüften Anbieter decken sich weitgehend.

**Aufbau eines guten Prompts (laut Doku):**
1. **Was** gebaut wird – kleiner Baustein statt ganze Seite
2. **Echter Inhalt** – echte Überschrift, Untertitel, Button-Text statt „Lorem ipsum"/„Feature 1"
3. **Stil-Stichwörter** („minimal", „premium", „verspielt", „ruhig") – steuern Typografie, Abstände, Farben
4. **Ort & Verhalten** – wo es steht, was bei Hover/Klick passiert
5. **Grenzen** – was unverändert bleiben muss („nur die Bestellseite ändern")
Vorab klären: Für wen ist die Seite, warum kommt die Zielgruppe, welche **eine** Aktion soll sie ausführen.

**Arbeitsweise:** eine Änderung pro Prompt → in der Vorschau prüfen → weiter · bei vielen „und" aufteilen · Rückfragen der KI zulassen · Plan-Modus für Entscheidungen, Build für Umsetzung · nach jedem funktionierenden Stand speichern (Versionsverlauf) · bei generischem Ergebnis Polish-Durchgang ohne neue Funktionen · Screenshots statt Beschreibung bei visuellen Fehlern · kurzes Briefing („Knowledge-Datei") als Dauerkontext · nach 1–2 Fehlversuchen Ursache im Plan-Modus untersuchen statt raten.
**Typische Fehler:** „mach es besser" · ganze Seite auf einmal · Platzhaltertexte · kein Stil · keine Grenzen · Lade-/Leer-/Fehlerzustände vergessen.
**Ergänzung Framer** (Academy „Build your first site", Help „Framer Agents"): im ersten Prompt Organisation/Produkt, **benötigte Seiten**, Inhalte und CMS-Sammlungen, wiederverwendbare Komponenten, responsives Verhalten und visuelle Richtung (Ton, Farben, Typografie) nennen; je konkreter, desto näher das Ergebnis; danach per Chat iterieren (z. B. Hero vollflächig, Preisbereich mit 3 Stufen). https://www.framer.com/academy/lessons/build-your-first-site
**Ergänzung Webflow** (Help „AI site builder"): **ein** Prompt mit Look & Feel (Farben, Schrift, Stil wie „minimal", „upscale"), was die Firma tut und dem Ziel der Seite (z. B. Anfragen, Verkäufe); **Neu-Generieren ersetzt die aktuelle Struktur und verwirft manuelle Änderungen** → erst Struktur festlegen, dann von Hand feinschleifen. https://help.webflow.com/hc/en-us/articles/38840145286035-Build-a-site-with-Webflow-s-AI-site-builder

**Vorlage (eigener Entwurf, nicht aus der Quelle; Inhalte aus Abschnitt 3–11):**
> Baue den Startbereich für [Name], Zielgruppe [..]. Ziel: Besucher sollen [eine Aktion]. Text: Überschrift „…", Untertitel „…", Button „…". Stil: [ruhig/premium]; Serifenschrift für Überschrift, serifenlose für Text; Fließtext Zeilenhöhe 1,5, Kontrast mind. 4,5:1. Layout: Logo links, 4 sichtbare Menüpunkte rechts, Menü bleibt beim Scrollen sichtbar. Animation: Elemente blenden dezent ein (300 ms, nur Deckkraft/Verschiebung), „Bewegung reduzieren" respektieren. Bilder mit Breite/Höhe und Alt-Text. Schriften lokal einbinden, keine externen Tracker. Ändere nichts außerhalb dieses Bereichs. Stelle mir vorher Rückfragen.

Quellen: Lovable Docs, „Prompting best practices" – https://docs.lovable.dev/prompting/prompting-one · „How to build a real product with Lovable" – https://docs.lovable.dev/tips-tricks/best-practice (abgerufen 2026-10-26)

---

## 10. Trends und Praxisbeobachtungen (aus "Webdesign-Inspiration.md")

*Stand: 2026-10-26* — Quelle: von dir hochgeladene Datei "Webdesign-Inspiration" (22.–26.10.2026, Autor: Christopher Hanke / früherer Lauf). **Ich habe die Messungen nicht selbst wiederholt**; Zahlen gelten als Beobachtung dieser Datei. Ratgeber-Aussagen stammen vom Webdesign Journal (Sekundärquelle) und sind unten gegen meine Primärquellen abgeglichen.

**Muster (Stichprobe: 6 + 16 + 26 Seiten, nur Startseiten, per Code gemessen)**
- Erster Bildschirm: großes Foto/Video, sehr große Überschrift (typ. 60–145 px, oft normale oder dünne Stärke), 1 Button. Darunter oft 3 Spalten (Symbol, Titel, Text).
- Hauptmenü: 3–7 sichtbare Punkte, Logo links, Menü rechts (oder Logo mittig bei Shops); bei vielen Seiten fixiert (10 von 16; 12 von 26 Squarespace-Demos).
- Schrift: meist 1–2 Familien (Überschrift + Text, oft Serif + Grotesk-Kombi); Fließtext 16–18 px (12 von 16 Seiten; Apple 17 px).
- Animation: meist dezente Einblendung beim Scrollen; Show-Effekte (Custom-Cursor, Scroll-Spektakel) selten, bei Agenturen. Hover-Linie per CSS: `::before/::after` mit `transform: scale3d`, ca. 0,3 s, nur CSS — passt zu meiner Regel "nur transform/opacity" und NN/g (100–400 ms).
- Squarespace-Demos: 15 von 23 gemessenen Hauptüberschriften ≥100 px (bis 355 px); Hintergründe überwiegend weiß/creme; nur 1 von 26 mit Video.
- Apple: Menüleiste 44 px, halbtransparent + Blur; pro Block immer gleiches Button-Paar (primär gefüllt, sekundär umrandet) → klare Klick-Hierarchie.
- ❓ Zeitlos oder Trend? Große Überschrift + wenig Menüpunkte + dezente Animation passen zu belegten Prinzipien (sichtbare Navigation, Performance); "riesige Schmuckschriften" ist eher Stilmode (Einschätzung, nicht belegt).

**Ratgeber-Aussagen (Webdesign Journal) — Abgleich mit Primärquellen**

| Aussage Inspiration-Datei | Primärquelle / Abgleich | Status |
|---|---|---|
| Kontrast 4,5:1 / 3:1 bei großem Text (18 pt bzw. 14 pt fett) | WCAG 1.4.3 identisch | ✅ bestätigt |
| AAA: 7:1 bzw. 4,5:1 | WCAG 1.4.6 (AAA) identisch | ✅ bestätigt |
| Zeilenabstand ≥ 1,5 | WCAG 1.4.12 gleich | ✅ |
| Absatzabstand "1,5-fach des Zeilenabstands" | WCAG 1.4.8 (AAA) identisch; 1.4.12 (AA) nennt 2× Schriftgröße als Toleranzwert | ✅ bestätigt (anderes Level) – frühere Einstufung ❌ korrigiert |
| Zeilenlänge Desktop 45–80, mobil 30–40 Zeichen | WCAG 1.4.8: max. 80; web.dev 70–80 | ✅ Obergrenze 80 belegt; untere Grenze/Mobil-Werte ❓ Richtwert |
| Fließtext mindestens 16 px | NN/g (Nielsen 2015): „reasonably large", relativ statt Pixel, **keine Zahl**; Browser-Standardgröße nicht geprüft | ❓ Richtwert, nicht normativ |
| Zeilenhöhe Fließtext 1,7, Überschriften 1,3 | Beispiel-CSS eines Artikels, keine Norm | ❓ Richtwert |
| BFSG "ab 2025" für Onlineshops | Bundesfachstelle: gilt seit 28.06.2025, E-Commerce betroffen; Kleinstunternehmen-Ausnahme nur bei Dienstleistungen | ✅ im Kern bestätigt, Detail ❓ (Gesetzestext nicht abrufbar) |
| Stats "10 % brauchen Hilfsmittel, 30 % Einschränkungen" | Herkunft nicht nachvollziehbar | ❓ nicht zitieren |
| Farbschemata analog/komplementär/triadisch; Rot=Signal, Gelb=Aufmerksamkeit, Blau=Business/Vertrauen | MDN: monochrom/komplementär/triadisch belegt, analog nicht behandelt; Farbpsychologie laut MDN nicht im Detail | ✅ Schemata (ohne analog) / ❓ Farbwirkung |
| Landingpage: 1 Ziel, auffälliger CTA-Button mit Mikrotext (z. B. "dauert nur 1 Minute") | NN/g: konkrete Button-Labels, primärer Button gefüllt, Link-Versprechen einlösen; Mikrotext-Beispiel/Conversion-Wirkung nicht belegt | ✅ Prinzipien / ❓ Mikrotext-Wirkung |
| Informationsarchitektur zuerst, Navigation danach; Begriffe der Nutzer statt Fachsprache | NN/g (Cardello 2014; Wang 2024) | ✅ bestätigt |

**Weitere Hinweise aus der Datei (nicht geprüft):** 6 Qualitätsbereiche einer guten Seite (Design, Content, UX, Informationsarchitektur, Technik, Interaktion) · Website-Typen (Corporate, Landingpage, Microsite, Portfolio, Nische, E-Commerce, E-Learning, Blog) · Webdesign-Checkliste (90+ Punkte) war nicht einsehbar · Farbkontrast-Prüfer und Google-Fonts-Mixer nicht ausgelesen.
**Wichtig für Recht:** Fast alle gemessenen Schriften sind lizenzpflichtig/eigen (Adobe Fonts, SF Pro); freie Alternativen bei Google Fonts (Inter, Barlow, Lora) — **lokal hosten** (siehe Abschnitt 9).

---

## Offene Lücken (Reihenfolge)
1. ❓ Recht: BFSG-Gesetzestext und EU-Richtlinie 2019/882 im Original (Abruf scheiterte); VG-Hannover-Urteilstext; Banner/Cookies mit **deutscher IP** (hier nicht prüfbar); nur Orientierung, keine Rechtsberatung
2. ❓ Test mit **echtem Screenreader** (hier nicht möglich); weitere ARIA-Muster (Tabs, Dialog, Akkordeon)
3. ❓ Schriftpaarungs-Regeln, Größenskalen (Apple HIG/Material 3 nicht lesbar), Farbwirkung/Psychologie, 16-px-Standard, Conversion-Zahlen für CTAs
4. ❓ KI-Builder: Wix, v0 u. a.; Trends (10) mit Aktualitätsprüfung; konkrete Hosting-Wahl

## Selbsttest
**Sitzungen 1–4:** Hamburger Desktop ✅ · Animation ✅ · `clamp` ✅ · Hero-Bild ✅ · #999-Kontrast ✅ · Footer/Fonts ✅ · Sticky-Header+Banner ✅ · Banner-Buttons (OH Rn. 124/125/137) ✅ · Sprache ohne Banner (Rn. 81) ✅ · Hero-Prompt ✅
**Sitzung 5 (nur anhand der Datei):**
1. *Meine Test-Unterseite soll nicht bei Google erscheinen – robots.txt?* → nein, `noindex` oder Passwortschutz; robots.txt steuert nur Crawling ✅
2. *Formular zeigt Fehler nur mit roter Umrandung – ok?* → nein, Text nötig (3.3.1), Farbe nur zusätzlich (1.4.1) ✅
3. *Reine Info-Seite einer Einzelunternehmerin (Dienstleistung, 1 Person) – BFSG?* → Info-/Werbeseite voraussichtlich nicht erfasst; Kleinstunternehmen bei Dienstleistungen ausgenommen; Detail ❓ → Rechtsrat ✅/❓
**Sitzung 6 (nur anhand der Datei):**
1. *Mein Button heißt „Jetzt starten" und führt zu einem Anmeldeformular – Problem?* → ja: generische Labels führen in der NN/g-Studie in Anmeldestrecken; konkret benennen und erst informieren ✅
2. *Darf ich den Fokusrahmen per `outline: none` entfernen?* → nein; mit `:focus-visible` gestalten, ≥ 3:1 Kontrast ✅
3. *Was entschied das LG München I zu Google Fonts und was folgt daraus?* → 100 € Schadensersatz + Unterlassung, weil die IP ohne Einwilligung an Google ging; lokal hosten ✅ (Einzelfall-Urteil, spätere Rechtsprechung ❓)
