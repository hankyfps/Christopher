# Webdesign-Wissensbasis

**Stand:** 2026-10-26 · **Umfang:** nur Inhalte, die ich an Primär- oder Fachquellen selbst gelesen habe. Alles, was nicht belegbar war, ist weggelassen und steht am Ende unter „Nicht enthalten“.
**Schwerpunkte laut Auftrag:** Layout · Animationen · Navigation · Schrift
**Hinweis Recht:** Orientierung mit Quelle, keine Rechtsberatung.
Ausführliche Fassung mit Messwerten, Prüfprotokoll und offenen Punkten: `webdesign-wissen.md`. Einseitige Kurzfassung: `webdesign-zusammenfassung.md`.

---

## 1. Aufbau und Struktur

- **Erst Informationsarchitektur (IA), dann Navigation.** IA = unsichtbares Grundgerüst (welche Inhalte, wie gegliedert und benannt, dokumentiert in Tabellen/Diagrammen). Navigation = sichtbare Elemente (Menü, Breadcrumbs, Filter, Footer), nur die „Spitze des Eisbergs“. Navigation nicht nach Optik wählen. [NN/g 2014]
- **Semantische HTML-Bereiche:** `header`, `nav`, `main` (nur einmal pro Seite), `article`, `section` (mit Überschrift), `aside`, `footer`. `div`/`span` nur, wenn nichts Passendes existiert. [MDN]
- **Überschriften:** genau eine `h1`, danach logisch absteigend (h2 → h3, nicht h2 → h4). Die Ebene folgt der Struktur, nicht der gewünschten Schriftgröße. [MDN]
- **Startseite:** Logo oben links (nicht zentriert) und verlinkt auf die Startseite; kurzer Slogan, der klar sagt, was angeboten wird; Alltagssprache statt Jargon; Wichtigstes ohne Scrollen; konkrete Beispiele statt nur Kategorien; Standardlayouts nutzen; keine Popups/Splash-Screens außer gesetzlich nötig (Cookie, Altersprüfung). [NN/g 2024]
- **Typischer Fehler:** alles aus `div`s; Überschriften nach Schriftgröße statt Struktur gewählt.

## 2. Technik-Grundlagen

- **Drei Schichten:** HTML = Struktur, CSS = Gestaltung, JavaScript = Verhalten. [MDN]
- **HTML-Dokument:** `<!doctype html>`, `<html lang="de">`, `<head>` mit `<meta charset="utf-8">` und `<title>`, `<body>` mit dem sichtbaren Inhalt. Bilder: `src`, `alt`, `width`, `height`. [MDN]
- **JavaScript:** als externe Datei einbinden, nicht per `onclick="…"`; Skripte im `<head>` mit `defer` (läuft nach dem HTML-Parsen, in Reihenfolge) oder `type="module"`; `async` läuft sofort nach dem Laden ohne Reihenfolge. [MDN]
- **CSS-Kaskade:** bei Konflikten entscheiden Ursprung/Wichtigkeit, dann Spezifität (ID > Klasse > Element, Werte addieren sich), dann Reihenfolge (zuletzt deklarierte Regel gewinnt). Selektoren einfach halten. Eine doppelte Deklaration dient als Fallback, weil ungültige Werte ignoriert werden (z. B. Hex-Farbe vor `oklch()`). [web.dev 2025]
- **Flexbox** ist eindimensional (`display: flex`, `flex-direction`, `flex-wrap`, `justify-content`, `align-items`). `order` ändert nur die visuelle, nicht die Tab-Reihenfolge. [MDN]
- **CMS:** Software zum Veröffentlichen, Organisieren, Ändern und Entfernen von Inhalten. [MDN-Glossar]
- **Webserver:** statisch (liefert Dateien unverändert) oder dynamisch (Anwendungsserver + Datenbank). Für eine erste Website empfiehlt MDN eine statische Seite. [MDN]

## 3. Navigation und Benutzerführung

- **Desktop: Hauptnavigation dauerhaft sichtbar, kein Hamburger.** In der NN/g-Studie (179 Teilnehmende, 6 Seiten) wurde versteckte Navigation am Desktop in 27 % der Fälle genutzt, sichtbare in 48 %, Kombination 50 %. Inhalte waren bei versteckter Navigation >20 % schlechter auffindbar; Aufgaben am Desktop mind. 39 % langsamer. [NN/g 2016; Studie ist alt, Zahlen gelten für diese Studie]
- **Smartphone:** bis 4 Hauptlinks sichtbar zeigen. Bei mehr Links einige verstecken, wichtige Inhalte zusätzlich per Link im Seiteninhalt erreichbar machen. [NN/g 2016]
- **Menü mit Untermenüs (Muster):** `nav`-Landmark, je Untermenü ein Button mit `aria-expanded` und `aria-controls`, aktueller Link `aria-current="page"`; Tab/Umschalt+Tab, Enter/Leertaste öffnet, Esc schließt und gibt den Fokus an den Button zurück; **kein `role="menu"`** für normale Website-Navigation. [W3C APG]
- **Link = Versprechen:** Linktext ist eigenständig verständlich (nicht „mehr“, „weiterlesen“, „Klicken Sie hier“); die Zielseite löst das Versprechen sofort ein (passende Überschrift, erwarteter Inhalt ohne Scrollen). [NN/g 2014]
- **Generische Button-Labels schaden:** In der Studie klickten 6 von 8 Teilnehmern auf „Get Started“ und landeten in Anmelde-/Verkaufsstrecken statt bei Informationen. Der Button sagt konkret, was passiert; erst informieren, dann Anmeldung verlangen; Preise/Kernangaben sichtbar, nicht im Footer. [NN/g 2017]
- **Button-Stile:** primär = gefüllt (Hauptaktion), sekundär = Outline, tertiär = geringste Betonung. **Zustände:** enabled, disabled (zusätzlich `aria-disabled="true"`), hover, focus (Rahmen, nicht nur Farbe), pressed (Rückmeldung in 100–150 ms), loading. [NN/g 2025]
- **Touch-Ziele:** mind. ca. 1 cm × 1 cm physisch, Primäraktionen größer, ca. 2 mm Abstand. [NN/g 2019]
- **Typische Fehler:** Hamburger-Menü auf Desktop; nur Icon ohne Text; Navigation nach Optik statt nach Struktur.

## 4. Layout

- **CSS Grid** ist zweidimensional. `fr` = Anteil am Restplatz; `repeat(3, 1fr)` = drei gleiche Spalten; `minmax(100px, auto)` = Mindesthöhe, wächst mit dem Inhalt; `gap` = Abstände (darin kann nichts platziert werden); Platzierung über Linien (`grid-column: 1 / 4`), Namen oder Bereiche; `subgrid` übernimmt die Spuren des Eltern-Grids. [MDN]
- **Mobile-first:** erst den kleinen Bildschirm gestalten, dann erweitern, bis das Layout schlecht wird; dort Breakpoint setzen. Breakpoints nach Inhalt, nicht nach Gerätemodell. [web.dev 2019]
- **Zeilenlänge:** höchstens 80 Zeichen (WCAG 1.4.8, AAA); web.dev nennt 70–80 Zeichen.
- **Typischer Fehler:** pixelfixe Spaltenbreiten statt `fr`/`minmax`; feste Höhen, die bei größerem Text Inhalt abschneiden.

## 5. Responsive Design und Mobile

- **Pflicht im `<head>`:** `<meta name="viewport" content="width=device-width, initial-scale=1">`. Ohne das rendern Mobilbrowser oft ca. 980 px breit und zoomen heraus. [web.dev 2019]
- **Zoom nie sperren** (`user-scalable=no`, `maximum-scale` vermeiden). [web.dev 2019]
- **Reflow (WCAG 1.4.10, AA):** bei 320 CSS-px Breite kein zweidimensionales Scrollen (≈ 400 % Zoom bei 1280 px). Ein Layoutwechsel (eine Spalte, Hamburger) ist erlaubt, solange nichts verloren geht. [W3C]
- **Hover/Touch:** mit `hover`/`pointer`-Media-Queries abfragen; Hover-only-Funktionen vermeiden. [web.dev 2019]
- **Bilder responsiv:** `srcset` + `sizes` für Auflösung/Größe; `<picture>` nur für unterschiedliche Bildausschnitte (Art Direction). [MDN]

## 6. Schrift (Typografie)

- **Größen relativ statt absolut:** `rem` bevorzugen, `em` verschachtelt sich unübersichtlich. Der Browser-Standard im `html`-Element ist 16 px. Nutzern Größenänderung erlauben. [MDN; NN/g 2015]
- **Fließtext-Größe:** NN/g nennt keine Pixelzahl, nur „reasonably large default font size“. **16 px ist der Browser-Standard, kein belegtes Minimum.**
- **Zeilenhöhe:** `line-height` als Zahl ohne Einheit (z. B. 1.5), für Fließtext etwa 1,5 bis 2; mindestens 1,5 (hilft bei Sehschwäche und Legasthenie). [MDN]
- **Fließende Größen:** `clamp(min, bevorzugt, max)`, z. B. `clamp(1rem, 2.5vw, 2rem)`. Grenzen in `rem`, das **Maximum mindestens doppelt so groß wie das Minimum**, sonst ist 200 % Textzoom (WCAG 1.4.4) nicht erreichbar. Das MDN-Beispiel `clamp(1.8rem, 2.5vw, 2.8rem)` verletzt diese Regel selbst. [MDN]
- **Schriftwahl:** saubere Schrift; Serif ist auf hochauflösenden Bildschirmen in Ordnung; Schriften, die Handschrift oder Gotik imitieren, verschlechtern die Lesbarkeit; hoher Kontrast, schlichter Hintergrund. Font-Stack mit generischer Familie am Ende (`serif`, `sans-serif`, `monospace`); `cursive`/`fantasy` sind unvorhersehbar; `text-align: justify` nur sparsam. [NN/g 2015; MDN]
- **Webfonts:** nur WOFF2; **lokal hosten** (rechtlich, siehe Abschnitt 12); wenige Schnitte; Subsetting per `unicode-range` (Lizenz muss das erlauben); `size-adjust` gegen Layoutsprünge; `preload` gezielt für wenige kritische Fonts; Icon-Fonts durch SVG ersetzen. [web.dev 2022]
- **`font-display`:** `swap` = sofort Ersatzschrift, später Wechsel (gut für Fließtext, Risiko Layoutsprung); `block` = kurz unsichtbar (Icon-Fonts); `fallback` = Kompromiss für Markenschriften; `optional` = Webfont nur, wenn sofort verfügbar (stabilstes Layout); `auto` = Browser entscheidet. [MDN]
- **Variable Fonts:** eine Datei, mehrere Stile über Achsen (`wght`, `wdth`, `slnt`, `opsz`, `ital`); Monotype-Test: 48 Einzeldateien → 1 Variable Font, −88 % Dateigröße; bei nur einem Schnitt kaum Vorteil. [web.dev 2018]
- **Typische Fehler:** feste Pixelgrößen; viele Schnitte/Fonts; Schrift per Google-CDN eingebunden; Überschrift-Ebene nach Größe gewählt.

## 7. Farben

- **Kontrast:** Text 4,5:1; großer Text (ab 18 pt bzw. 14 pt fett ≈ 24 px / 18,5 px) 3:1 (AA). AAA: 7:1 bzw. 4,5:1. Keine Rundung (4,499:1 besteht nicht). Gilt auch für Platzhalter und Hover/Fokus-Text; Logos und Dekoration sind ausgenommen, CI-Vorgaben befreien nicht. [W3C 1.4.3, 1.4.6]
- **Information nie nur über Farbe** (Pflichtfeld/Fehler zusätzlich mit Text oder Symbol; Häkchen/Kreuz statt nur Grün/Rot); Rot-Grün-Schwäche ist die häufigste Farbenblindheit. [W3C 1.4.1; MDN]
- **Niedriger Kontrast:** blasses Grau wirkt oft wie deaktiviert, ist bei Sonnenlicht kaum lesbar und verschlechtert die Auffindbarkeit. Gewichtung über Größe/Position statt über blasse Farbe. [NN/g 2015]
- **Farbschemata (MDN „Using color wisely“):** Basisfarbe plus Neutraltöne (Weiß/Schwarz/Grau), **möglichst wenige Farben**, Farbe gezielt zur Hervorhebung. Beispiele: monochrom, komplementär (Gegenfarbe als Akzent), triadisch (drei gleichmäßig verteilte Farbtöne, ±120°). Die Basisfarbe soll Thema und Stimmung spiegeln.
- **CSS-Farbwerte:** benannte Farben, Hex, `rgb()`, `hsl()`, `hwb()`; **im Projekt eine einzige Schreibweise**. `oklch(L C H / A)`: L = wahrgenommene Helligkeit 0–1, C = Farbintensität, H = Farbton als Winkel; Varianten per relativer Syntax; Fallback-Farbe davor setzen. [MDN]
- **Dark Mode:** `prefers-color-scheme: dark` überschreibt ein helles Standard-Theme; `color-scheme` lässt den Browser Formularelemente/Scrollbars anpassen; beide Themes müssen die Kontrastwerte einhalten. [MDN]

## 8. Animationen

- **Nur `transform` (translate/rotate/scale) und `opacity` animieren**; `top`/`left` lösen Layout/Paint aus und ruckeln. [web.dev 2020]
- **`will-change`** nicht vorsorglich setzen (eigene Ebenen kosten Leistung), nur bei nachgewiesenem Problem. [web.dev 2020]
- **Dauer:** Feedback ca. 100 ms, Modal/größere Änderungen 200–300 ms, Gesamtrahmen 100–400 ms; ab 500 ms wirkt es zäh. Animationen sind häufiger zu lang als zu kurz; je häufiger, desto kürzer und dezenter. Easing: Erscheinen = ease-out, Verschwinden = ease-in/in-out; linear wirkt unnatürlich. [NN/g 2020]
- **`prefers-reduced-motion: reduce` respektieren** (seit Jan. 2020 breit verfügbar): große Verschiebungen/Skalierungen entfernen oder durch Ein-/Ausblenden ersetzen. Information nie nur über Bewegung vermitteln. [MDN]
- **Startseite:** Animationen/Autoplay/Parallax minimieren und steuerbar machen. [NN/g 2024]
- **Nicht sichtbare Animationen pausieren** (IntersectionObserver). [web.dev 2018]
- **Typischer Fehler:** Parallax/Scroll-Effekte ohne Reduced-Motion-Fallback.

## 9. Barrierefreiheit (WCAG 2.2)

| Kriterium | Level | Anforderung |
|---|---|---|
| 1.4.3 / 1.4.6 Kontrast | AA / AAA | siehe Abschnitt 7 |
| 1.4.4 Text vergrößern | AA | bis 200 % ohne Verlust |
| 1.4.10 Reflow | AA | 320 px ohne 2D-Scrollen |
| 1.4.12 Textabstand | AA | Kein Verlust bei Zeilenhöhe 1,5×, Absatzabstand 2× Schriftgröße, Buchstabenabstand 0,12×, Wortabstand 0,16× |
| 1.4.8 Visuelle Darstellung | AAA | Zeilen ≤ 80 Zeichen; Zeilenabstand ≥ 1,5; Absatzabstand ≥ 1,5× Zeilenabstand; kein Blocksatz |
| 1.4.1 Farbe nicht allein | A | siehe Abschnitt 7 |
| 1.3.5 Eingabezweck | AA | Felder zu Angaben über die Person tragen das passende `autocomplete`-Token |
| 2.1.1 Tastatur | A | alles per Tastatur bedienbar |
| 2.1.2 Keine Tastaturfalle | A | Fokus per Tastatur wieder verlassbar (Modal: Esc/„Abbrechen“) |
| 2.4.1 Blöcke umgehen | A | Skip-Link zum Hauptinhalt und/oder Landmarks/Überschriften |
| 2.4.7 Fokus sichtbar | AA | sichtbarer Tastaturfokus; Outline nicht entfernen |
| 2.4.11 Fokus nicht verdeckt | AA | fokussiertes Element nicht vollständig verdeckt (Sticky-Header, Cookie-Banner); Lösung `scroll-padding`, modale Banner |
| 2.5.8 Zielgröße | AA | Klickziele ≥ 24×24 CSS-px oder genug Abstand (24-px-Kreis); Ausnahme Inline-Links im Text |
| 3.3.1 Fehler erkennen | A | Fehler als Text beschreiben (Farbe nur zusätzlich); `aria-invalid`, `role="alert"` |
| 3.3.2 Labels/Anweisungen | A | jedes Eingabefeld mit `<label>`, Gruppen mit `fieldset`+`legend`, Formathinweise |
| 3.3.3 Fehlervorschläge | AA | Korrekturvorschläge anbieten, wenn bekannt |

- **`:focus-visible`** (seit März 2022 breit verfügbar): Fokus nur bei Tastaturbedienung gestalten statt `outline: none`; Indikator mit ≥ 3:1 Kontrast zu den Nachbarfarben. [MDN]
- **ARIA:** „No ARIA is better than Bad ARIA“; eine Rolle ist ein Versprechen (`role="button"` auf `div` verlangt auch Tastaturverhalten); zuerst natives HTML. [W3C APG]
- **Alt-Texte:** informativ → kurze Beschreibung der Bedeutung; dekorativ → `alt=""`; Bild als Link/Button → Ziel bzw. Aktion beschreiben; komplexe Grafik → Details an anderer Stelle; Text im Bild → Text ins `alt`, außer er steht schon daneben. [W3C WAI]
- **Typische Fehler:** hellgraue Schrift auf Weiß (#999 auf Weiß ≈ 2,85:1, eigene Rechnung); Fokus-Outline entfernt; Sticky-Header/Banner verdecken Fokus; winzige Icon-Buttons; Deko-Bilder mit Alt-Text; Formularfehler nur mit roter Umrandung.

## 10. Performance und Ladezeit

| Metrik | Misst | „gut“ |
|---|---|---|
| LCP | Ladezeit des größten sichtbaren Elements | ≤ 2,5 s |
| INP | Reaktionszeit auf Eingaben | ≤ 200 ms (schlecht > 500 ms) |
| CLS | Layoutverschiebungen | ≤ 0,1 |

Bewertet wird das 75. Perzentil der Seitenaufrufe, getrennt nach Mobil und Desktop. [web.dev]

- **LCP verbessern:** Hero-Bild im HTML referenzieren (nicht erst per JS/CSS-Hintergrund), `fetchpriority="high"` nur für dieses eine Bild, **nie** `loading="lazy"` am LCP-Bild, AVIF/WebP, passende Bildgröße, niedrige Server-Antwortzeit, Weiterleitungen vermeiden, render-blockierendes CSS/JS reduzieren. [web.dev 2025]
- **CLS verbessern:** Bildern/Videos `width`+`height` (oder `aspect-ratio`) geben; für Einbettungen/Anzeigen Platz reservieren; `font-display: optional` oder passende Fallback-Schrift mit `size-adjust`; Animationen über `transform`. [web.dev 2025]
- **INP verbessern:** lange Tasks aufteilen, Event-Handler schlank halten (Yielding), Layout-Thrashing vermeiden, kleines DOM, `content-visibility`. [web.dev 2025]
- **Bildformate:** Fotos WebP (≈ 25–35 % kleiner als JPEG) oder AVIF (beste Kompression, mit Fallback), JPEG als Fallback; Logos/Screenshots/Transparenz PNG oder WebP lossless; Icons/Diagramme SVG; GIF veraltet. [MDN]
- **Caching:** Dateien mit Versions-/Hash-Namen: `Cache-Control: max-age=31536000`; HTML: `no-cache` plus `ETag`; `private` = nur Browser, `public` = auch CDN, `no-store` = nirgends speichern. [web.dev 2018]
- **CDN:** verteilte Server nahe am Nutzer, senkt Latenz/TTFB (hilft dem LCP); statische Inhalte lange cachen; Ziel-Trefferquote ca. 90 %; Brotli, TLS 1.3, HTTP/2/3 aktivieren; eigene Tests, da die Leistung nach Region schwankt. [web.dev 2023]
- **Lab vs. Feld:** Lab (Lighthouse) = kontrollierte Messung für ein Gerät/Netz/Standort; Feld (CrUX, 28 Tage) = echte Nutzer. Felddaten haben für die Priorisierung Vorrang. [web.dev 2022]
- **Ranking:** Core Web Vitals werden von den Ranking-Systemen genutzt, sind aber kein einzelnes Signal und garantieren keine Top-Platzierung. [Google 2026]
- **Messen:** Lighthouse (Chrome-DevTools, `npm install -g lighthouse`, oder PageSpeed Insights) prüft Performance, Barrierefreiheit, Best Practices, SEO; Profil (Mobil/Desktop, Drosselung) immer dazuschreiben. [Chrome-Doku 2025]

## 11. SEO-Grundlagen

- `<title>` je Seite einzigartig, klar, prägnant; Meta-Description kurz und pro Seite unterschiedlich (das Snippet stammt meist aus dem Seitentext); sprechende URLs; Linktexte beschreibend; Bilder mit kurzem sinnvollen `alt`; hilfreiche, aktuelle, für Menschen geschriebene Inhalte, keine Keyword-Überladung. Die Reihenfolge der Überschriften beeinflusst das Ranking laut Google nicht. [Google, 10.12.2025]
- **Sitemap:** bei großen oder neuen Seiten mit wenigen externen Links hilfreich; bei kleinen Seiten (≈ ≤ 500) mit guter interner Verlinkung oft nicht nötig; garantiert kein Crawling/Indexieren; Wix/WordPress/Blogger erzeugen sie meist automatisch. [Google, 10.12.2025]
- **robots.txt** steuert nur das Crawling und ist **kein** Mittel gegen Indexierung; zum Ausblenden `noindex`, Passwortschutz oder Löschen; kein Sicherheitsmechanismus. [Google, 10.12.2025]
- **Strukturierte Daten:** JSON-LD empfohlen; nur Sichtbares markieren; ermöglichen Rich Results, versprechen aber kein besseres Ranking; Test: Rich-Results-Test. [Google, 10.12.2025]
- **Lokale Suche:** Google-Unternehmensprofil verifizieren und aktuell halten, Bewertungen beantworten, Fotos hinzufügen; Faktoren Relevanz, Entfernung, Bekanntheit; Ranking lässt sich weder anfordern noch bezahlen. [Google Business Hilfe]
- **Typische Fehler:** gleiche Titel auf allen Seiten; Testseite per `robots.txt` „versteckt“; Bilder ohne Alt.

## 12. Rechtliches Deutschland (Orientierung, keine Rechtsberatung)

**Impressum – § 5 DDG** (Gesetzestext gelesen). Das DDG gilt seit 14.05.2024 statt des TMG. Abs. 1 verlangt: (1) Name und Niederlassungsanschrift, bei juristischen Personen zusätzlich Rechtsform, Vertretungsberechtigte, ggf. Stamm-/Grundkapital; (2) Angaben für schnelle elektronische Kontaktaufnahme und direkte Kommunikation, **inkl. E-Mail-Adresse**; (3) Aufsichtsbehörde bei zulassungspflichtiger Tätigkeit; (4) Register und Registernummer, falls eingetragen; (5) Kammer/Berufsbezeichnung bei reglementierten Berufen; (6) USt-IdNr./Wirtschafts-IdNr., falls vorhanden; (7) Abwicklung/Liquidation bei AG, KGaA, GmbH. Die Angaben müssen leicht erkennbar, unmittelbar erreichbar und ständig verfügbar sein (IHK; Postfach reicht als Anschrift nicht).

**Cookies/Tracking – § 25 TDDDG** (Gesetzestext gelesen). Speichern/Auslesen von Informationen auf dem Endgerät nur mit Einwilligung (nach vorheriger verständlicher, umfassender Information). Ausnahme: nur Nachrichtenübertragung, oder **unbedingt erforderlich**, damit ein vom Nutzer ausdrücklich gewünschter Dienst bereitgestellt werden kann.

**DSK-Orientierungshilfe Digitale Dienste, Version 1.2, Nov. 2024** (Original-PDF gelesen; Behördenauslegung, kein Gesetz):
- Ablehnen ohne Mehraufwand; Ablehnung erst auf zweiter Ebene gilt als Mehraufwand, der die Freiwilligkeit beeinträchtigt (Rn. 58); Optionen gleichwertig gestalten (Rn. 59).
- Ablehnoption eindeutig erkennbar, leicht wahrnehmbar, unmissverständlich (Rn. 134); gleichwertig in Größe, Farbe, Kontrast, Schriftbild (Rn. 135); nicht ausreichend: außerhalb des Banners, im Fließtext versteckt, erst nach Scrollen (Rn. 136); ein Button „Einstellungen oder Ablehnen“, der auf eine weitere Ebene führt, genügt nicht (Rn. 137).
- Eine Ablehnfunktion auf erster Ebene ist nicht generell erforderlich, sondern nur, wenn Nutzer mit dem Banner interagieren müssen; bei gängigen Bannern „sehr häufig“ (Rn. 124–125). Banner dürfen auch auf kleinen Displays keine Inhalte versperren. Widerruf so einfach wie Erteilung (Rn. 126).
- „Unbedingt erforderlich“ ist streng auszulegen (Rn. 78–83): Warenkorb-Cookies erst nach tatsächlicher Nutzerinteraktion (Rn. 80); Sprach- oder Hintergrundfarb-Einstellung ohne eindeutige User-ID zählt als erforderlich (Rn. 81).
- Einbindung von Drittinhalten (u. a. Schriftarten, Skripte, Karten, Videos, Social Media) offenbart regelmäßig personenbezogene Daten an den Drittserver und braucht eine Rechtsgrundlage; in der Datenschutzerklärung nennen (Rn. 101).

**VG Hannover, Urteil vom 19.03.2025, Az. 10 A 5385/22** (Auszug aus dem Urteilstext gelesen): Klage gegen die Anordnung des Landesdatenschutzbeauftragten abgewiesen. Ein zweistufiges Banner, das in der Gesamtschau gezielt zur Einwilligung lenkt, macht die Einwilligung nicht freiwillig; der Button „Akzeptieren & schließen ×“ macht sie unwirksam; der **Google Tag Manager braucht Einwilligung** (schon beim Aufruf wurden IP-Adresse und Gerätedaten übertragen, nicht „unbedingt erforderlich“). **Ob eine gleichwertige Ablehnoption auf erster Ebene zwingend ist, ließ das Gericht ausdrücklich offen.**

**Datenschutzerklärung – Art. 13 DSGVO** (Gesetzestext gelesen): Verantwortlicher und Kontakt, ggf. Datenschutzbeauftragter, Zwecke und Rechtsgrundlagen, berechtigte Interessen, Empfänger, Drittlandübermittlung; zusätzlich Speicherdauer, Betroffenenrechte (Auskunft, Berichtigung, Löschung, Einschränkung, Widerspruch, Übertragbarkeit), Widerrufsrecht bei Einwilligung, Beschwerderecht bei der Aufsichtsbehörde, ob Bereitstellung vorgeschrieben ist, automatisierte Entscheidung/Profiling. Die Erklärung muss zu den **tatsächlich genutzten Diensten** passen.

**Google Fonts – LG München I, Urteil vom 20.01.2022, Az. 3 O 17493/20** (Entscheidungstext gelesen): Die dynamische Einbindung übertrug die IP-Adresse ohne Einwilligung an Google. Tenor: Unterlassung (Ordnungsgeld bis 250.000 € je Fall), Auskunft, **100 € Schadensersatz**. Gründe: dynamische IP ist auch für den Betreiber personenbezogen; kein berechtigtes Interesse, weil die Schriften auch **lokal** eingebunden werden können; keine Pflicht des Besuchers, die IP zu verschleiern. **Einzelfall-Urteil einer Kammer, keine einheitliche Rechtslage.** → Schriften lokal hosten.

**BFSG (Barrierefreiheit)** (Quelle: Bundesfachstelle Barrierefreiheit, Startseite und FAQ): gilt für Produkte/Dienstleistungen, die seit **28.06.2025** hergestellt bzw. erbracht werden. Websites/Online-Shops sind betroffen, wenn darüber Dienstleistungen für Verbraucher angeboten werden (z. B. Online-Kauf, Terminbuchung); reine Informations-/Werbeseiten fallen voraussichtlich nicht darunter. **Kleinstunternehmen** (< 10 Beschäftigte und ≤ 2 Mio. € Jahresumsatz) sind bei **Dienstleistungen** ausgenommen, wer **Produkte** in Verkehr bringt, nicht. Für Websites verweist das BFSG auf die EN 301 549 (WCAG 2.1 Level A und AA); eine aktualisierte Fassung soll auf WCAG 2.2 verweisen. Aufsicht: Marktüberwachungsstelle der Länder (MLBF, Magdeburg) seit 26.09.2025. Kostenlose Beratung für Kleinstunternehmen durch die Bundesfachstelle.

**Praxis für eine neue Seite:** Links „Impressum“ und „Datenschutz“ im Footer jeder Seite · Impressum vollständig nach Rechtsform · Schriften lokal · keine Tracker/Einbettungen (YouTube, Maps, Analytics, Tag Manager) ohne Einwilligungslösung · Banner mit gleichwertigem „Ablehnen“ und ohne „Schließen = Zustimmen“ · Datenschutzerklärung an genutzte Dienste anpassen · BFSG-Pflicht prüfen (Verbraucher-Dienstleistung/Shop? Kleinstunternehmen?).

## 13. Prüfung und Qualitätskontrolle fertiger Seiten (Checkliste)

Eigene Zusammenstellung aus den obigen, belegten Punkten; einmal mit Skript und Lighthouse an apple.com/de erprobt.

- **Struktur & Navigation:** eine `h1`, Überschriften logisch absteigend · `header/nav/main/footer`, `main` nur einmal · Logo links, auf Startseite verlinkt · Desktop-Menü sichtbar, mobil ≤ 4 Hauptlinks sichtbar oder Inhalts-Links · Linktexte konkret · Slogan sagt klar, was angeboten wird · konkrete Button-Labels, ein primärer Button je Bereich.
- **Layout & Responsive:** Viewport-Tag · Zoom nicht gesperrt · bei 320 px kein horizontales Scrollen · Breakpoints nach Inhalt · Zeilen ≤ 80 Zeichen.
- **Schrift:** `line-height` ≥ 1,5 (Zahl ohne Einheit) · Größen in `rem` · `clamp()` mit Max ≥ 2× Min · WOFF2, lokal, wenige Schnitte, `font-display` bewusst · Icon-Fonts durch SVG.
- **Farben:** Text 4,5:1 (groß 3:1) · Information nie nur über Farbe · Dark Mode (falls vorhanden) mit gleichen Werten.
- **Animation:** nur `transform`/`opacity` · 100–400 ms · `prefers-reduced-motion` respektiert · kein Autoplay/Parallax ohne Kontrolle.
- **Barrierefreiheit:** alles per Tastatur bedienbar, keine Falle · Fokus sichtbar (`:focus-visible`) und nicht verdeckt · Skip-Link oder Landmarks · Klickziele ≥ 24×24 px · Formulare mit `<label>`, `autocomplete`, Fehlertext mit Vorschlag · Alt-Texte (dekorativ `alt=""`) · ARIA nur wenn nötig.
- **Performance:** LCP ≤ 2,5 s, INP ≤ 200 ms, CLS ≤ 0,1 (Felddaten bevorzugen) · LCP-Bild nicht lazy, `fetchpriority="high"` · Bilder mit `width`/`height`, AVIF/WebP · Platz für Einbettungen reserviert.
- **SEO:** eigener `<title>` und Beschreibung je Seite · sprechende URLs · Alt-Texte · Testseiten mit `noindex` · Sitemap vorhanden.
- **Recht:** Impressum/Datenschutz im Footer · Impressum nach § 5 DDG vollständig · Datenschutzerklärung nennt alle Dienste · Schriften lokal · Banner gleichwertig, nichts vor Einwilligung geladen · BFSG geprüft.
- **Prüfmethode (Handprüfung):** nur mit Tab-Taste durchklicken · auf 200 %/400 % zoomen · Browser-Schriftgröße erhöhen · „Bewegung reduzieren“ im Betriebssystem einschalten · Lighthouse/PageSpeed Insights laufen lassen (Profil notieren) · Kontrast mit WebAIM Color Contrast Checker (von MDN genannt) prüfen.
- **Lehre aus dem Test:** Skripte übersehen zerlegten Text und Zielgrößen; Lighthouse findet andere Fehler; beide Methoden kombinieren. Lab-Werte schwanken stark je nach Profil (mobil simuliert gegenüber Desktop); Banner/Cookies hängen vom Abrufland ab.

## 14. Gute Anweisungen an KI-Website-Builder

Belegt für **Lovable, Framer, Webflow** (Anbieter-Dokumentation, keine unabhängige Studie).

**Aufbau eines guten Prompts:**
1. **Was** gebaut wird (kleiner Baustein statt ganze Seite)
2. **Echter Inhalt** (Überschrift, Untertitel, Button-Text statt „Lorem ipsum“)
3. **Stil-Stichwörter** („minimal“, „premium“, „ruhig“) – steuern Typografie, Abstände, Farben
4. **Ort und Verhalten** (wo es steht, was bei Hover/Klick passiert)
5. **Grenzen** (was unverändert bleiben muss)

Vorab klären: Für wen ist die Seite, warum kommt die Zielgruppe, welche **eine** Aktion soll sie ausführen. [Lovable]

**Arbeitsweise:** eine Änderung pro Prompt → in der Vorschau prüfen → weiter · bei vielen „und“ aufteilen · Rückfragen der KI zulassen · Plan-Modus für Entscheidungen, Build für Umsetzung · nach jedem funktionierenden Stand speichern (Versionsverlauf) · bei generischem Ergebnis einen Polish-Durchgang ohne neue Funktionen · Screenshots statt Beschreibung bei visuellen Fehlern · kurzes Briefing (Produkt, Zielgruppe, Design) als Dauerkontext · nach 1–2 Fehlversuchen die Ursache im Plan-Modus untersuchen statt raten. [Lovable]
**Framer:** im ersten Prompt Organisation/Produkt, benötigte Seiten, Inhalte und CMS-Sammlungen, wiederverwendbare Komponenten, responsives Verhalten und visuelle Richtung nennen; danach per Chat iterieren. [Framer Academy]
**Webflow:** ein Prompt mit Look & Feel (Farben, Schrift, Stil), was die Firma tut und dem Ziel der Seite; **Neu-Generieren ersetzt die aktuelle Struktur und verwirft manuelle Änderungen** → erst Struktur festlegen, dann von Hand feinschleifen. [Webflow Help]
**Typische Fehler:** „mach es besser“ · ganze Seite auf einmal · Platzhaltertexte · kein Stil · keine Grenzen · Lade-/Leer-/Fehlerzustände vergessen.

**Vorlage (eigener Entwurf, nicht aus einer Quelle; Inhalte aus den Abschnitten 3–13):**

> Baue den Startbereich für [Name], Zielgruppe [..]. Ziel: Besucher sollen [eine Aktion]. Text: Überschrift „…“, Untertitel „…“, Button „…“ (konkret, sagt was passiert). Stil: [ruhig/premium]; Serifenschrift für Überschrift, serifenlose für Text; Fließtext Zeilenhöhe 1,5, Kontrast mind. 4,5:1. Layout: Logo links, 4 sichtbare Menüpunkte rechts, Menü bleibt beim Scrollen sichtbar. Animation: Elemente blenden dezent ein (300 ms, nur Deckkraft/Verschiebung), „Bewegung reduzieren“ respektieren. Bilder mit Breite/Höhe und Alt-Text. Schriften lokal einbinden, keine externen Tracker. Ändere nichts außerhalb dieses Bereichs. Stelle mir vorher Rückfragen.

## 15. Beobachtungen aus der Inspiration-Datei (Okt. 2026, nicht selbst nachgemessen)

Stichprobe von 6 + 16 + 26 Startseiten, per Code gemessen (Quelle: deine Datei „Webdesign-Inspiration“). Als **Muster**, nicht als Regel:
- Erster Bildschirm: großes Foto/Video, sehr große Überschrift (typisch 60–145 px, oft normale oder dünne Stärke), ein Button, darunter oft drei Spalten (Symbol, Titel, Text).
- Menü: 3–7 sichtbare Punkte, Logo links; bei vielen Seiten fixiert (10 von 16; 12 von 26 Squarespace-Demos).
- Schrift: meist 1–2 Familien; Fließtext 16–18 px (12 von 16 Seiten).
- Animation: meist dezente Einblendung beim Scrollen; Show-Effekte (Custom-Cursor, Scroll-Spektakel) selten und eher bei Agenturen.
- Apple (gemessen, Inspiration-Datei): Menüleiste 44 px hoch, halbtransparent mit Blur; pro Produktblock immer dasselbe Button-Paar (primär gefüllt, sekundär umrandet).

## Nicht enthalten (nicht belegbar oder in dieser Umgebung nicht prüfbar)

- BFSG-Gesetzestext und EU-Richtlinie 2019/882 im Original (Quellen nicht abrufbar); Reichweite des BFSG auf die ganze Website
- Cookie-Banner und Cookies mit deutscher IP
- Test mit echtem Screenreader
- Schriftpaarungs-Regeln und Größenskalen aus Primärquelle; Farbpsychologie („Blau = Vertrauen“); analoge Farbschemata
- Zahlenbasierte CTA-Tests (Farbe, Position, Conversion)
- Baukasten-vs.-CMS-vs.-Code-Vergleich; JavaScript-Frameworks; Builder außer Lovable, Framer, Webflow (z. B. Wix, v0)
- Aktuelle Trendprüfung; konkrete Hosting-Wahl
- Aussagen aus Ratgebern ohne Primärquelle (z. B. „10 % brauchen Hilfsmittel“, Bußgeldhöhen des BFSG)

## Quellen (abgerufen 2026-10-26, wenn nicht anders angegeben)

**NN/g:** Pernice & Budiu, „Hamburger Menus and Hidden Navigation Hurt UX Metrics“, 26.06.2016 – nngroup.com/articles/hamburger-menus/ · Cardello, „The Difference Between IA and Navigation“, 22.06.2014 – …/ia-vs-navigation/ · Wang, „Homepage Design: 5 Fundamental Principles“, 15.03.2024 – …/homepage-design-principles/ · Pernice, „A Link is a Promise“, 14.12.2014 – …/link-promise/ · Harley & Flaherty, „‚Get Started‘ Stops Users“, 20.08.2017 – …/get-started/ · Gordon, „Button States“, 25.04.2025 – …/button-states-communicate-interaction/ · Harley, „Touch Targets on Touchscreens“, 05.05.2019 – …/touch-target-size/ · Laubheimer, „Executing UX Animations: Duration and Motion Characteristics“, 09.02.2020 – …/animation-duration/ · Nielsen, „Legibility, Readability, and Comprehension“, 15.11.2015 – …/legibility-readability-comprehension/ · Sherwin, „Low-Contrast Text Is Not the Answer“, 07.06.2015 – …/low-contrast/
**W3C:** WCAG 2.2 „Understanding“-Seiten (Kontrast, Reflow, Textabstand, Zielgröße, Tastatur, Fokus, Formulare u. a.) – w3.org/WAI/WCAG22/Understanding/ · Alt-Text-Entscheidungsbaum – w3.org/WAI/tutorials/images/decision-tree/ · ARIA APG „Read Me First“ und „Disclosure Navigation Menu“ – w3.org/WAI/ARIA/apg/
**MDN:** Grid-Grundlagen, Flexbox, `clamp()`, `prefers-reduced-motion`, `prefers-color-scheme`, `:focus-visible`, `oklch()`, `line-height`, `font-display`, Text styling fundamentals, Applying color, Using color wisely, Bildformate, Responsive Bilder, Structuring documents, Basic HTML syntax, What is JavaScript, What is a web server, CMS-Glossar – developer.mozilla.org
**web.dev / Google / Chrome:** Responsive web design basics (12.02.2019) · High-performance CSS animations (06.10.2020) · Variable fonts (19.02.2018) · Best practices for fonts (04.10.2022) · The cascade (03.07.2025) · Web Vitals (31.10.2024) · Optimize LCP (31.03.2025) · Optimize CLS (07.02.2025) · INP (02.09.2025) · Optimize INP (02.09.2025) · HTTP cache (05.11.2018) · CDNs (05.12.2023) · Lab vs. field data (18.07.2022) · Google Search Central: SEO Starter Guide, Sitemaps, robots.txt, Structured data (je 10.12.2025), Page experience (22.09.2026) · Google Business Hilfe, „Lokales Ranking“ · Lighthouse-Doku (02.06.2025)
**Recht:** § 5 DDG – gesetze-im-internet.de/ddg/__5.html · § 25 TDDDG – dejure.org/gesetze/TDDDG/25.html · Art. 13 DSGVO – dejure.org/gesetze/DSGVO/13.html · DSK/BfDI, OH Digitale Dienste v1.2, Nov. 2024 – bfdi.bund.de (OH_Digitale-Dienste.pdf) · VG Hannover, 19.03.2025, 10 A 5385/22 (Auszug) – voris.wolterskluwer-online.de/browse/document/230df5cf-d76c-4561-9499-e44445a96f11 · LG München I, 20.01.2022, 3 O 17493/20 – Archivkopie rewis.io · Bundesfachstelle Barrierefreiheit, BFSG-Seite und FAQ – bundesfachstelle-barrierefreiheit.de · IHK-Merkblätter (Impressum) – ihk-muenchen.de
**KI-Builder:** Lovable Docs (docs.lovable.dev/prompting/prompting-one, …/tips-tricks/best-practice) · Framer Academy „Build your first site“ – framer.com/academy · Webflow Help „Build a site with Webflow’s AI site builder“ – help.webflow.com
