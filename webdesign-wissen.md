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
| 6 | Performance | ❓ (Core Web Vitals, Caching-Grundlagen, Lighthouse; Hosting/CDN-Wahl offen) |
| 7 | Barrierefreiheit | ✅ für WCAG-Grundkriterien (Kontrast, Text, Tastatur, Fokus, Alt, Zielgröße, Motion); ❓ ARIA/Formulare/Screenreader-Test |
| 8 | SEO | ❓ (Starter-Guide, Sitemap, robots.txt/noindex; strukturierte Daten, lokale SEO offen) |
| 9 | Recht DE | ❓ Impressum, TDDDG, Art. 13 DSGVO, DSK-OH am Original; BFSG über Bundesfachstelle-FAQ; BFSG-Gesetzestext und Urteilstexte offen (siehe 9) |
| 10 | Trends | ❓ (Beobachtungen aus Inspiration-Datei, 2026-10; nicht selbst gemessen) |
| 11 | Qualitätskontrolle | ❓ Checkliste aus geprüften Punkten (Abschnitt 11); in Praxis nicht getestet |
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

**Startseiten-Prinzipien** (NN/g, Wang, 15.03.2024): Logo oben links (nicht zentriert); kurzer Slogan, der klar sagt, was angeboten wird; Alltagssprache statt Jargon; Wichtigstes über dem Falz; konkrete Beispiele statt nur Kategorien; Linktexte konkret (kein "Klicken Sie hier"/"Mehr erfahren"); Logo-Link und "Home" auf jeder Seite; Standardlayouts nutzen; Animationen/Autoplay/Parallax minimieren und steuerbar machen; keine Popups/Splash-Screens außer gesetzlich nötig (Cookie, Altersprüfung); Hauptnavigation auffällig, nicht versteckt.

**Einschränkung:** Studie ist von 2016 → ❓ ob Zahlen heute (2026) gleich ausfallen; nicht aktuell geprüft. Die Zahlen gelten für diese Studie, nicht pauschal.

**Quellen**
- Pernice & Budiu: „Hamburger Menus and Hidden Navigation Hurt UX Metrics", NN/g, 26.06.2016 – https://www.nngroup.com/articles/hamburger-menus/
- Hinweis: NN/g-Seite „navigation-design-guide" lieferte 404, nicht ausgewertet.
- Cardello: „The Difference Between Information Architecture (IA) and Navigation", NN/g, 22.06.2014 – https://www.nngroup.com/articles/ia-vs-navigation/
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
- ❓ Nicht belegt: Schriftpaarung, Schriftgrößen-Skalen, Mindestgröße 16 px → offene Lücke (Webdesign Journal: ≥16 px, Apple misst 17 px – nur Beobachtung).
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
- Farbwerte in CSS (MDN „Applying color"): benannte Farben, Hex, `rgb()`, `hsl()`, `hwb()`; **im Team/Projekt eine einzige Schreibweise** verwenden. `oklch()` wurde dort nur verwiesen, nicht erklärt (❓).
- Kontrast bewusst prüfen (MDN verweist auf den WebAIM Color Contrast Checker); hoher Kontrast hilft auch bei Blendung (Smartphone in der Sonne). Pflichtfelder z. B. mit Sternchen **und** Farbe kennzeichnen (MDN „CSS and JavaScript accessibility best practices").
- Hover/Fokus: Cursor und Fokus-Outline nicht entfernen; Mauszustände (`mouseover`) brauchen Tastatur-Gegenstück (`focus`). (`:focus-visible` steht nicht in der MDN-Seite; Hinweis aus meinem Vorwissen, ❓ nicht belegt.)
- Quelle: MDN „prefers-color-scheme" (abgerufen 2026-10-26; zu ~77 % gelesen) – https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme
- ❓ Weiter offen: Farbharmonien/Palettenaufbau und Farbwirkung – MDN behandelt sie nicht, Material-Design-Seite lieferte nur den Titel; bisher nur Sekundärquelle Webdesign Journal (siehe 10). Keine Primärquelle gefunden.

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

❓ Offen: Bildformate-Praxis im Detail, CDN-/Hosting-Auswahl, INP-Maßnahmen im Detail.

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

**ARIA** (W3C APG „Read Me First"): *„No ARIA is better than Bad ARIA"*; eine Rolle ist ein Versprechen (`role="button"` auf `div` verlangt auch Tastaturverhalten per JS); ARIA kann Semantik überdecken. Folgerung: zuerst natives HTML (`button`, `a`, `nav`, `label`), ARIA nur ergänzend, mit Assistenztechnik testen. (Die Seite nennt „natives HTML zuerst" nicht wörtlich.)

**Alt-Texte** (W3C WAI Entscheidungsbaum): informatives Bild → kurze Beschreibung der Bedeutung; **dekorativ → leeres `alt=""`**; Bild als Link/Button → Ziel bzw. Aktion beschreiben; komplexe Grafik → Details an anderer Stelle der Seite; Text im Bild → Text ins `alt`, außer er steht schon als echter Text daneben.

**Abgleich Absatzabstand:** Die Angabe „1,5× Zeilenabstand" (Webdesign Journal) stammt aus 1.4.8 (AAA) und ist korrekt; für AA (1.4.12) gilt nur: Layout darf bei 2× Schriftgröße nichts verlieren. Beide Aussagen gleichzeitig wahr.

Außerdem: `prefers-reduced-motion` beachten, Zoom nie sperren (siehe 4/5).
**Typische Fehler:** hellgraue Schrift auf Weiß (#999 ≈ 2,85:1, eigene Rechnung); Fokus-Outline per CSS entfernt; Sticky-Header/Cookie-Banner verdecken Fokus; winzige Icon-Buttons; feste Höhen, die bei größerem Text Inhalt abschneiden; Deko-Bilder mit Alt-Text.
❓ Offen: 1.3.5 Autocomplete, 3.3.3 Fehlervorschläge, 2.1.2 Tastaturfalle, konkrete ARIA-Muster, Test mit echtem Screenreader.
Quellen (WCAG 2.2 Understanding, W3C, abgerufen 2026-10-26): …/contrast-minimum.html · …/contrast-enhanced.html · …/visual-presentation.html · …/text-spacing.html · …/reflow.html · …/keyboard.html · …/bypass-blocks.html · …/labels-or-instructions.html · …/use-of-color.html · …/error-identification.html · …/focus-visible.html · …/focus-not-obscured-minimum.html · …/target-size-minimum.html (alle unter https://www.w3.org/WAI/WCAG22/Understanding/) · Alt-Texte: https://www.w3.org/WAI/tutorials/images/decision-tree/ · ARIA: https://www.w3.org/WAI/ARIA/apg/practices/read-me-first/

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
- ❓ Offen: strukturierte Daten, lokale SEO, Ranking-Einfluss der Core Web Vitals.

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

**Gericht (Banner):** VG Hannover, 19.03.2025, Az. 10 A 5385/22 (nur laut Kanzleibericht WBS.LEGAL, Urteilstext nicht gelesen): Banner mit „Alle akzeptieren"/„Einstellungen" ohne gleichwertiges Ablehnen auf erster Ebene → Einwilligung unwirksam. Passt zur OH (Rn. 58–60, 137). Google Tag Manager als einwilligungspflichtig bewertet.

**Datenschutzerklärung – Art. 13 DSGVO** (Gesetzestext gelesen via dejure.org). Bei Datenerhebung mitzuteilen: Verantwortlicher + Kontakt, ggf. Datenschutzbeauftragter, **Zwecke und Rechtsgrundlage**, berechtigte Interessen (bei Art. 6 Abs. 1 lit. f), Empfänger(kategorien), Drittlandübermittlung + Garantien; zusätzlich **Speicherdauer**, Betroffenenrechte (Auskunft, Berichtigung, Löschung, Einschränkung, Widerspruch, Übertragbarkeit), **Widerrufsrecht** bei Einwilligung, **Beschwerderecht** bei Aufsichtsbehörde, ob Bereitstellung vorgeschrieben/erforderlich ist, automatisierte Entscheidung/Profiling. → Die Erklärung muss zu den **tatsächlich genutzten Diensten** passen (Schriften, Formulare, Einbettungen, Analytics).

**Google Fonts:** LG München I, 20.01.2022, Az. 3 O 17493/20 (laut IHK-/Kanzleibericht, Urteilstext nicht gelesen): dynamische Einbindung überträgt IP-Adresse an Google; 100 € Schadensersatz + Unterlassung; Lösung: Schriften **lokal hosten**. ❓ Spätere Rechtsprechung nicht geprüft.

**BFSG (Barrierefreiheit)** — Quelle: Bundesfachstelle Barrierefreiheit (Bund), Startseite BFSG + FAQ (selbst gelesen; Gesetzestext gesetze-im-internet 503, nicht abrufbar):
- Gilt für Produkte/Dienstleistungen, die **seit 28.06.2025** hergestellt bzw. erbracht werden.
- **Websites/Online-Shops:** betroffen, wenn darüber **Dienstleistungen für Verbraucher** angeboten werden (Online-Banking, elektronischer Geschäftsverkehr – z. B. Online-Kauf, Online-Terminbuchung). **Reine Informations-/Werbeseiten fallen voraussichtlich nicht darunter** (fehlende „individuelle Anfrage" des Verbrauchers). Für Shops gelten Informationspflichten zur Barrierefreiheit und barrierefreie Identifizierungs-, Authentifizierungs-, Signatur- und Zahlungsfunktionen.
- **Kleinstunternehmen** (< 10 Beschäftigte und ≤ 2 Mio. € Jahresumsatz): bei **Dienstleistungen** ausgenommen; wer **Produkte** in Verkehr bringt, nicht. Kostenlose Beratung durch die Bundesfachstelle.
- **Standard:** Für Websites gilt EN 301 549, die auf **WCAG 2.1 Level A und AA** verweist; eine aktualisierte Fassung soll auf WCAG 2.2 verweisen. → Die WCAG-2.2-Kriterien in Abschnitt 7 sind eine Obermenge/Annäherung; maßgeblich für die Pflicht ist die Norm.
- **Aufsicht:** Seit 26.09.2025 Marktüberwachungsstelle der Länder (MLBF) in Magdeburg; bei Dienstleistungen stichprobenartig; bei Verstoß Aufforderung zur Herstellung der Konformität, dann Bußgelder bis zur Untersagung. (Bußgeldhöhe „bis 100.000 €" nur aus Sekundärquellen/IHK, ❓ nicht am Gesetz geprüft.)
- Offen/Streit: Betrifft die Anforderung die ganze Website oder nur den Bestellprozess? Sekundärquelle (Kanzlei) sagt: ganze Website; ❓ ungeklärt. IHK Berlin und e-recht24 widersprachen sich zum Shop eines Kleinstunternehmens → die Bundesfachstelle-FAQ deckt sich mit IHK Berlin nur für Dienstleistungen; **Rechtsrat einholen**.
- Quelle: Bundesfachstelle Barrierefreiheit – https://www.bundesfachstelle-barrierefreiheit.de/DE/Fachwissen/Produkte-und-Dienstleistungen/Barrierefreiheitsstaerkungsgesetz/barrierefreiheitsstaerkungsgesetz_node.html · FAQ: …/Barrierefreiheitsstaerkungsgesetz/FAQ/faq_node.html (abgerufen 2026-10-26; FAQ zu ~88 % gelesen)

**Praxis für KI-Builder-Seiten:** Footer-Links „Impressum"/„Datenschutz" auf jeder Seite; Impressum vollständig nach Rechtsform; Schriften lokal; keine Tracker/Einbettungen (YouTube, Maps, Analytics) ohne Einwilligungslösung; Cookie-Banner mit „Alles ablehnen" (statt „Einstellungen oder Ablehnen") gleichwertig in Größe/Farbe/Kontrast auf Ebene 1; Datenschutzerklärung an genutzte Dienste anpassen.
**Typische Fehler:** Impressum versteckt; Vorlage ungeprüft; Google Fonts per CDN; Tracking vor Einwilligung; Banner nur mit „Akzeptieren"/„Einstellungen".

**Quellen:** Gesetze: DDG § 5 – https://www.gesetze-im-internet.de/ddg/__5.html · TDDDG § 25 – https://dejure.org/gesetze/TDDDG/25.html · DSGVO Art. 13 – https://dejure.org/gesetze/DSGVO/13.html · Bundesfachstelle Barrierefreiheit (BFSG) – https://www.bundesfachstelle-barrierefreiheit.de/DE/Fachwissen/Produkte-und-Dienstleistungen/Barrierefreiheitsstaerkungsgesetz/barrierefreiheitsstaerkungsgesetz_node.html · Sekundär: IHK München Merkblatt 05/2024 (https://ihk-muenchen.de/ihk/Merkblätter-WettbewerbsR/Pflichtangaben-Internetimpressum_Stand05_2024.pdf) · DSK/BfDI OH Digitale Dienste (s. o.) · WBS.LEGAL zu VG Hannover (https://www.wbs.legal/it-und-internet-recht/datenschutzrecht/vg-hannover-zu-einwilligungsbutton-cookie-banner-brauchen-alles-ablehnen-schaltflaeche-82973/) · IHK Bergische zu Google Fonts (https://www.ihk.de/bergische/recht-und-steuern/wettbewerbsrecht/google-fonts-5646176)

---

## 11. Prüfung und Qualitätskontrolle fertiger Seiten (Checkliste)

*Stand: 2026-10-26* — eigene Zusammenstellung **nur aus den oben geprüften Quellen**; in der Praxis noch nicht erprobt. Die 90-Punkte-Checkliste des Webdesign Journals war nicht einsehbar (Anmeldeformular) und ist **nicht** Grundlage.

**Struktur & Navigation:** eine `h1`, Überschriften logisch absteigend · `header/nav/main/footer`, `main` nur einmal · Logo links, verlinkt auf Startseite · Hauptnavigation auf Desktop sichtbar (kein Hamburger), mobil ≤4 Hauptlinks sichtbar oder wichtige Inhalte auch per Inhalts-Links · Linktexte konkret (nicht „Mehr erfahren") · Slogan sagt klar, was angeboten wird.
**Layout & Responsive:** Viewport-Meta-Tag · Zoom nicht gesperrt · bei 320 px kein horizontales Scrollen · Breakpoints nach Inhalt · Fließtext-Zeilen ≤ 80 Zeichen.
**Schrift:** Fließtext `line-height` ≥ 1,5 (Zahl ohne Einheit) · `rem`-Größen, `clamp()` mit Max ≥ 2× Min · WOFF2, lokal gehostet, wenige Schnitte, `font-display` bewusst gesetzt · Icon-Fonts durch SVG ersetzt.
**Farben & Kontrast:** Text 4,5:1 (groß 3:1) · Information nie nur über Farbe · Dark Mode (falls vorhanden) mit gleichen Kontrastwerten.
**Animation:** nur `transform`/`opacity` · 100–400 ms, ease-out beim Erscheinen · `prefers-reduced-motion` respektiert · kein Autoplay/Parallax ohne Kontrolle · keine Info nur über Bewegung.
**Barrierefreiheit:** Formularfehler als Text beschrieben · alles per Tastatur bedienbar · Fokus sichtbar und nicht von Sticky-Header/Banner verdeckt · Skip-Link · Klickziele ≥ 24×24 px · Formularfelder mit `<label>` · Alt-Texte (dekorativ = `alt=""`) · ARIA nur wenn nötig.
**Performance:** LCP ≤ 2,5 s, INP ≤ 200 ms, CLS ≤ 0,1 · LCP-Bild nicht lazy, mit `fetchpriority="high"` · Bilder mit `width`/`height` · AVIF/WebP · Platz für Einbettungen reserviert.
**SEO:** eigener `<title>` je Seite · Testseiten mit `noindex`, nicht mit robots.txt · Sitemap vorhanden (meist automatisch) · aussagekräftige Meta-Description · sprechende URLs · Bilder mit Alt · hilfreiche, aktuelle Inhalte.
**Recht:** Impressum und Datenschutz im Footer jeder Seite · Impressum nach § 5 DDG vollständig (inkl. E-Mail) · Datenschutzerklärung nennt alle genutzten Dienste (Art. 13 DSGVO) · Schriften lokal · Banner mit gleichwertigem „Alles ablehnen" · keine Tracker vor Einwilligung · BFSG-Pflicht prüfen (Verbraucher-Dienstleistung/Shop? Kleinstunternehmen?).
**Prüfwerkzeuge (belegt):** Lighthouse/PageSpeed Insights (Performance, Accessibility, Best Practices, SEO; Hinweise zu Fehlern); WebAIM Color Contrast Checker (laut MDN genannt, selbst nicht geöffnet); BIK BITV-Test und barrierefreies-webdesign.de (laut Bundesfachstelle für Prüfschritte empfohlen). ❓ WAVE, axe, Screenreader-Test nicht recherchiert. Handprüfung: nur mit Tab-Taste durchklicken, auf 200 %/400 % zoomen, Browser-Schriftgröße erhöhen, „Bewegung reduzieren" im Betriebssystem einschalten.

---

## 12. Gute Anweisungen an KI-Website-Builder

*Stand: 2026-10-26* — Quelle: **Lovable-Dokumentation** (Anbieter-Selbstaussagen, keine unabhängige Studie). ❓ Andere Builder (Wix, Framer, Webflow AI, v0, Claude Design …) nicht geprüft; Prinzipien vermutlich übertragbar, aber nicht belegt.

**Aufbau eines guten Prompts (laut Doku):**
1. **Was** gebaut wird – kleiner Baustein statt ganze Seite
2. **Echter Inhalt** – echte Überschrift, Untertitel, Button-Text statt „Lorem ipsum"/„Feature 1"
3. **Stil-Stichwörter** („minimal", „premium", „verspielt", „ruhig") – steuern Typografie, Abstände, Farben
4. **Ort & Verhalten** – wo es steht, was bei Hover/Klick passiert
5. **Grenzen** – was unverändert bleiben muss („nur die Bestellseite ändern")
Vorab klären: Für wen ist die Seite, warum kommt die Zielgruppe, welche **eine** Aktion soll sie ausführen.

**Arbeitsweise:** eine Änderung pro Prompt → in der Vorschau prüfen → weiter · bei vielen „und" aufteilen · Rückfragen der KI zulassen · Plan-Modus für Entscheidungen, Build für Umsetzung · nach jedem funktionierenden Stand speichern (Versionsverlauf) · bei generischem Ergebnis Polish-Durchgang ohne neue Funktionen · Screenshots statt Beschreibung bei visuellen Fehlern · kurzes Briefing („Knowledge-Datei") als Dauerkontext · nach 1–2 Fehlversuchen Ursache im Plan-Modus untersuchen statt raten.
**Typische Fehler:** „mach es besser" · ganze Seite auf einmal · Platzhaltertexte · kein Stil · keine Grenzen · Lade-/Leer-/Fehlerzustände vergessen.

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
| Fließtext mindestens 16 px | in meinen Primärquellen nicht belegt | ❓ plausibel, als Praxisrichtwert führen |
| Zeilenhöhe Fließtext 1,7, Überschriften 1,3 | Beispiel-CSS eines Artikels, keine Norm | ❓ Richtwert |
| BFSG "ab 2025" für Onlineshops | Bundesfachstelle: gilt seit 28.06.2025, E-Commerce betroffen; Kleinstunternehmen-Ausnahme nur bei Dienstleistungen | ✅ im Kern bestätigt, Detail ❓ (Gesetzestext nicht abrufbar) |
| Stats "10 % brauchen Hilfsmittel, 30 % Einschränkungen" | Herkunft nicht nachvollziehbar | ❓ nicht zitieren |
| Farbschemata analog/komplementär/triadisch; Rot=Signal, Gelb=Aufmerksamkeit, Blau=Business/Vertrauen | Gestaltungslehre, Sekundärquelle | ❓ Faustregeln, kulturabhängig |
| Landingpage: 1 Ziel, auffälliger CTA-Button mit Mikrotext (z. B. "dauert nur 1 Minute") | Sekundärquelle | ❓ Praxisregel, nicht belegt/getestet |
| Informationsarchitektur zuerst, Navigation danach; Begriffe der Nutzer statt Fachsprache | NN/g (Cardello 2014; Wang 2024) | ✅ bestätigt |

**Weitere Hinweise aus der Datei (nicht geprüft):** 6 Qualitätsbereiche einer guten Seite (Design, Content, UX, Informationsarchitektur, Technik, Interaktion) · Website-Typen (Corporate, Landingpage, Microsite, Portfolio, Nische, E-Commerce, E-Learning, Blog) · Webdesign-Checkliste (90+ Punkte) war nicht einsehbar · Farbkontrast-Prüfer und Google-Fonts-Mixer nicht ausgelesen.
**Wichtig für Recht:** Fast alle gemessenen Schriften sind lizenzpflichtig/eigen (Adobe Fonts, SF Pro); freie Alternativen bei Google Fonts (Inter, Barlow, Lora) — **lokal hosten** (siehe Abschnitt 9).

---

## Offene Lücken (Reihenfolge)
1. ❓ Recht: BFSG-Gesetzestext (§§ 1, 3, BFSGV) und Urteilstexte (LG München I, VG Hannover) im Original; Reichweite BFSG (ganze Website?); aktuelle Rechtsprechung Google Fonts; nur Orientierung, keine Rechtsberatung
2. Farben: Palettenaufbau/Harmonien und Farbwirkung aus Primär-/Fachquelle (keine gefunden); Schriftpaarung, Größenskalen, Mindestgröße 16 px
3. Call-to-Action mit belegten Tests (NN/g-Artikel nicht auffindbar; Suche lieferte nur Sekundärquellen)
4. Praxistest der Checkliste (11) an einer echten Seite; WAVE/axe/Screenreader
5. Weitere KI-Builder (neben Lovable), strukturierte Daten/lokale SEO, Trends (10) mit Aktualitätsprüfung

## Selbsttest
**Sitzungen 1–4:** Hamburger Desktop ✅ · Animation ✅ · `clamp` ✅ · Hero-Bild ✅ · #999-Kontrast ✅ · Footer/Fonts ✅ · Sticky-Header+Banner ✅ · Banner-Buttons (OH Rn. 124/125/137) ✅ · Sprache ohne Banner (Rn. 81) ✅ · Hero-Prompt ✅
**Sitzung 5 (nur anhand der Datei):**
1. *Meine Test-Unterseite soll nicht bei Google erscheinen – robots.txt?* → nein, `noindex` oder Passwortschutz; robots.txt steuert nur Crawling ✅
2. *Formular zeigt Fehler nur mit roter Umrandung – ok?* → nein, Text nötig (3.3.1), Farbe nur zusätzlich (1.4.1) ✅
3. *Reine Info-Seite einer Einzelunternehmerin (Dienstleistung, 1 Person) – BFSG?* → Info-/Werbeseite voraussichtlich nicht erfasst; Kleinstunternehmen bei Dienstleistungen ausgenommen; Detail ❓ → Rechtsrat ✅/❓
