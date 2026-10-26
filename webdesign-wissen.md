# Webdesign-Wissensbasis

Stand der Datei: 2026-10-26 (Sitzung 2)
Legende: ✅ solide · ❓ lückenhaft/unbestätigt · ❌ fehlt

## Kompetenz-Status

| # | Bereich | Status |
|---|---|---|
| 1 | Aufbau/Struktur | ❓ (nur HTML-Semantik) |
| 2 | Technik-Grundlagen | ❓ (nur CSS-Teile: Grid, clamp) |
| 3 | Navigation/UX | ❓ (nur Hamburger-Studie) |
| 4 | Layout, Typografie, Farben, Animation | ❓ (Layout/Animation/Schrift teilweise; Farben ❌) |
| 5 | Responsive/Mobile | ❓ |
| 6 | Performance | ❓ (Core Web Vitals, LCP, CLS, Fonts; Hosting/Caching offen) |
| 7 | Barrierefreiheit | ❓ (Kontrast, Textabstand, Zielgröße, Reflow, Zoom, Reduced Motion; Tastatur/Fokus/Alt offen) |
| 8 | SEO | ❓ (Google-Starter-Guide) |
| 9 | Recht DE | ❓ (nur Sekundärquellen, Gesetzestext nicht abrufbar) |
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
- `font-display` (MDN): `swap` = sofort Ersatzschrift, später Wechsel (gut für Fließtext, Risiko Layoutsprung); `block` = kurz unsichtbar (Icon-Fonts); `fallback` = Kompromiss für Markenschriften; `optional` = Webfont nur, wenn sofort da (stabilstes Layout, ideal für unkritische Schriften); `auto` = Browser entscheidet.
- Zeilenhöhe/Abstände: WCAG 1.4.12 verlangt nur, dass der Inhalt bei Zeilenhöhe 1,5×, Absatzabstand 2×, Buchstabenabstand 0,12×, Wortabstand 0,16× (jeweils der Schriftgröße) nichts verliert → keine Pflichtwerte, aber Layout darf nicht auf feste Höhen bauen.
- ❓ Nicht belegt: Schriftpaarung, Schriftgrößen-Skalen, Zeilenhöhe als Gestaltungsempfehlung → offene Lücke.
- Hinweis: web.dev-Artikel ist intern widersprüchlich datiert (Update 2018, Browser-Stand Mai 2020).

### Animationen
- Performant: nur `transform` (translate/rotate/scale) und `opacity` animieren. `top`/`left`/`width` lösen Layout/Paint aus → ruckelig.
- `will-change` nicht prophylaktisch einsetzen (eigene Ebenen kosten Speicher/Leistung); nur bei nachgewiesenem Problem.
- `prefers-reduced-motion: reduce` (Baseline seit Jan. 2020) respektieren: starke Bewegung (große Verschiebungen/Skalierungen) entfernen oder durch Ein-/Ausblenden ersetzen. Nicht alleinige Lösung: Info nie nur über Bewegung vermitteln.
- Nicht sichtbare Animationen pausieren (IntersectionObserver).
- Dauer (NN/g 2020): Feedback ca. 100 ms, Modal/größere Änderungen 200–300 ms, Gesamtrahmen 100–400 ms; ab 500 ms wirkt es zäh. Animationen sind öfter zu lang als zu kurz. Einblenden etwas länger als Ausblenden. Je häufiger, desto kürzer/dezenter. Easing: Erscheinen = ease-out, Verschwinden = ease-in/in-out; linear wirkt unnatürlich.
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

❓ Offen: INP-Maßnahmen im Detail, Hosting/Caching, Bildformate-Praxis, Messwerkzeuge (PageSpeed/Lighthouse); „schlecht"-Schwellen nicht im Artikel genannt.

---

## 7. Barrierefreiheit (Teilwissen)

*Stand: 2026-10-26* — alle Angaben WCAG 2.2 (W3C „Understanding"-Seiten)

| Kriterium | Anforderung (Level AA) |
|---|---|
| 1.4.3 Kontrast | Normaler Text ≥ **4,5:1**; großer Text (≥18 pt bzw. ≥14 pt fett ≈ 24 px / 18,5 px) ≥ **3:1**. Keine Rundung (4,499 besteht nicht). Gilt auch für Platzhalter und Hover/Fokus-Text. Ausnahme: Logos, Deko, deaktivierte Elemente. CI-Vorgaben befreien nicht. |
| 1.4.4 Text vergrößern | Text bis 200 % ohne Verlust vergrößerbar. |
| 1.4.10 Reflow | Bei 320 CSS-px Breite kein zweidimensionales Scrollen (≈400 % Zoom). |
| 1.4.12 Textabstand | Kein Verlust bei Zeilenhöhe 1,5×, Absatz 2×, Buchstaben 0,12×, Wort 0,16×. |
| 2.5.8 Zielgröße | Klick-/Tippziele ≥ **24×24 CSS-px** oder ausreichend Abstand (24-px-Kreis-Test). Ausnahmen u. a. Inline-Links im Text. Empfehlung als Best Practice: größer (2.5.5, ohne Zahlenangabe im abgerufenen Text). |

Außerdem: `prefers-reduced-motion` beachten, Zoom nie sperren (siehe 4/5).
**Typische Fehler:** hellgraue Schrift auf Weiß; Text auf Bildern ohne Kontrastprüfung; winzige Icon-Buttons; feste Höhen, die bei größerem Text Inhalt abschneiden.
❓ Offen: Tastaturbedienung, Fokus-Anzeige, Alt-Texte, ARIA, Formular-Labels, 1.4.11 (Nicht-Text-Kontrast, nur erwähnt).
Quellen: https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html · …/text-spacing.html · …/target-size-minimum.html · …/reflow.html

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
- ❓ Offen: Indexierung (robots/sitemap), strukturierte Daten, lokale SEO, Ranking-Einfluss der Core Web Vitals.

---

## 9. Rechtliches Deutschland (Orientierung, keine Rechtsberatung)

*Stand: 2026-10-26* — ❓ **Der Gesetzestext auf gesetze-im-internet.de war nicht abrufbar (HTTP 503, zweimal); die Angaben stammen aus Sekundärquellen und müssen gegen den Gesetzestext geprüft werden.**

- **Impressum:** Seit 14.05.2024 gilt das Digitale-Dienste-Gesetz (DDG) statt TMG; die Impressumspflicht wurde aus § 5 TMG nahezu unverändert in § 5 DDG übernommen (IHK-Merkblätter). Typisch: Name, ladungsfähige Anschrift (Postfach reicht nicht), Kontakt für schnelle direkte Erreichbarkeit (u. a. E-Mail), bei juristischen Personen Rechtsform, Vertretungsberechtigte, Registernummer/-gericht. Muss leicht erkennbar, unmittelbar erreichbar, ständig verfügbar sein (z. B. Footer-Link auf jeder Seite). Kein Gesetzesverweis nötig. ❓ Exakte Nummern § 5 Abs. 1 nicht am Original geprüft.
- **Cookies/Tracking:** § 25 TDDDG: Speichern/Auslesen auf dem Endgerät braucht grundsätzlich Einwilligung, außer unbedingt erforderlich für einen vom Nutzer ausdrücklich gewünschten Dienst (§ 25 Abs. 2 Nr. 2). Laut Sekundärquellen zur DSK-Orientierungshilfe: Warenkorb-/Login-/Spracheinstellungs-Cookies, Lastverteilung und die Speicherung der Einwilligung selbst gelten als erforderlich; Analyse und Werbung nicht. ❓ Primärquelle (DSK-OH Digitale Dienste, Gesetzestext) nicht geprüft.
- **Google Fonts:** LG München I, 20.01.2022, Az. 3 O 17493/20: dynamisch von Google-Servern eingebundene Schriften übertragen die IP-Adresse; 100 € Schadensersatz + Unterlassung. Praktische Lösung: Schriften **lokal auf eigenem Server** hosten. ❓ Spätere Rechtsprechung nicht geprüft; Urteilstext nicht gelesen (Quelle: IHK-/Kanzleibericht).
- **Praxis für KI-Builder-Seiten:** Footer mit Links „Impressum" und „Datenschutz"; Schriften lokal einbinden; keine Tracker/Einbettungen (YouTube, Maps, Analytics) ohne Einwilligungslösung; Datenschutzerklärung zu den tatsächlich genutzten Diensten passend halten.
- **Typische Fehler:** Impressum nur auf Unterseite versteckt; Vorlage ohne Anpassung; Google Fonts per CDN; Tracking vor Einwilligung.
- Quellen: IHK München, Merkblatt „Pflichtangaben Internetimpressum", Stand 05/2024 (https://ihk-muenchen.de/ihk/Merkblätter-WettbewerbsR/Pflichtangaben-Internetimpressum_Stand05_2024.pdf) · IHK Bergische, LG München I Google Fonts (https://www.ihk.de/bergische/recht-und-steuern/wettbewerbsrecht/google-fonts-5646176) · GDD-Praxishilfe 05/2024 (https://gdd.de/wp-content/uploads/2024/05/GDD-Praxishilfe-DS-GVO-ePrivacy-und-Datenschutz-beim-Onlineauftritt.pdf)

---

## Offene Lücken (Reihenfolge)
1. Recht: Primärquellen prüfen (§ 5 DDG, § 25 TDDDG, DSK-OH), Cookie-Banner-Gestaltung, Datenschutzerklärung
2. Farben (Paletten, Harmonie, Dark Mode), Schriftpaarung, Größenskalen
3. Informationsarchitektur, Startseiten-Aufbau, Call-to-Action
4. Barrierefreiheit: Tastatur/Fokus/Alt/ARIA; Performance: INP, Hosting
5. KI-Builder-Prompts + Qualitäts-Checkliste (11, 12); Trends (10) mit Aktualitätsprüfung

## Selbsttest
**Sitzung 1:** Hamburger auf Desktop? Nein, NN/g 27 % vs. 48 % ✅ · Ruckelfrei animieren? nur `transform`/`opacity` + Reduced-Motion ✅ · Barrierefreie fließende Überschrift? `clamp(1rem, 2.5vw, 2rem)`, Max ≥ 2×Min ✅
**Sitzung 2 (nur anhand der Datei):**
1. *Hero-Bild lädt langsam, was tun?* → im HTML referenzieren, `fetchpriority="high"`, nicht lazy, AVIF/WebP, width/height setzen ✅
2. *Graue Schrift #999 auf Weiß okay?* → Kontrast ≈ 2,8:1 (eigene Rechnung, nicht in der Quelle) < 4,5:1 → nein; Regel 4,5:1 bzw. 3:1 bei großem Text ✅
3. *Was gehört rechtlich in den Footer und was bei Schriften beachten?* → Impressum/Datenschutz leicht erreichbar; Schriften lokal hosten ✅ (mit ❓-Vorbehalt Primärquelle)
Nicht beantwortbar: Farbpaletten, Schriftpaarung, Informationsarchitektur → in Lücken.
