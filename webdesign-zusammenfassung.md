# Webdesign – Das Wichtigste auf einer Seite

Stand: 2026-10-26 · Grundlage: `webdesign-wissen.md` (dort Quellen, Links, Messwerte)
✅ am Original/Primärquelle geprüft · ❓ Richtwert oder nicht abschließend belegt · Recht = Orientierung, keine Rechtsberatung

## 1. Aufbau
- Erst Inhalte und Seitenstruktur festlegen, dann die Navigation gestalten ✅ (NN/g)
- Pro Seite eine `h1`, danach logisch absteigend (h2 → h3); Ebene nach Struktur, nicht nach Schriftgröße ✅ (MDN)
- Bausteine: `header`, `nav`, `main` (nur einmal), `footer` ✅
- Startseite: Logo oben links, Slogan sagt klar, was angeboten wird, Alltagssprache, Wichtigstes ohne Scrollen, konkrete Linktexte statt „Mehr erfahren" ✅ (NN/g 2024)

## 2. Navigation
- **Desktop: Menü sichtbar, kein Hamburger** ✅ (NN/g-Studie 2016: versteckt 27 % Nutzung, sichtbar 48 %)
- Mobil: bis 4 Hauptlinks sichtbar; bei mehr Hamburger, aber wichtige Inhalte zusätzlich im Seiteninhalt verlinken ✅
- Typisch bei guten Seiten: 3–7 Menüpunkte, Logo links, Menü beim Scrollen sichtbar ❓ (Beobachtung)
- Skip-Link („Zum Inhalt springen") und `nav`/`main` für Tastatur-Nutzer ✅

## 3. Layout & Responsive
- Pflicht: `<meta name="viewport" content="width=device-width, initial-scale=1">`, Zoom nie sperren ✅
- Mobile-first gestalten; Breakpoints nach Inhalt, nicht nach Gerätemodell ✅
- Bei 320 px darf nichts horizontal scrollen ✅ (WCAG Reflow)
- Zeilenlänge höchstens ca. 80 Zeichen ✅; CSS Grid für zweidimensionale Layouts (`fr`, `repeat`, `minmax`, `gap`) ✅
- Häufiges Muster: Vollbild-Bild, große Überschrift, ein Button, darunter 3 Spalten ❓ (Beobachtung)

## 4. Schrift
- Höchstens 1–2 Schriftfamilien (Überschrift + Text) ❓ Beobachtung
- Fließtext ca. 16 px oder mehr ❓ Richtwert (nicht in Primärquelle); Zeilenhöhe als Zahl ohne Einheit, mindestens 1,5 ✅ (MDN)
- Größen in `rem`; fließend mit `clamp(min, bevorzugt, max)`, Max mindestens doppelt so groß wie Min (sonst Zoom auf 200 % unmöglich) ✅
- Schriften als WOFF2, wenige Schnitte, **lokal hosten** (Recht), `font-display` bewusst setzen (`swap` Fließtext, `optional` stabilstes Layout) ✅
- Icon-Fonts durch SVG ersetzen ✅

## 5. Farben
- Kontrast: Text **4,5:1**, großer Text (ab ca. 24 px bzw. 18,5 px fett) **3:1** ✅ (WCAG AA); AAA: 7:1 / 4,5:1 ✅
- Information nie nur über Farbe (Fehler: Text + Farbe) ✅
- Dark Mode: `prefers-color-scheme`, gleiche Kontrastwerte ✅
- Farbharmonien/Farbwirkung: ❓ keine Primärquelle gefunden (nur Ratgeber-Faustregeln)

## 6. Animationen
- Nur `transform` und `opacity` animieren (flüssig); `will-change` nicht vorsorglich ✅
- Dauer 100–400 ms, ab 500 ms zäh; Erscheinen = ease-out ✅ (NN/g 2020)
- **`prefers-reduced-motion` respektieren**; Information nie nur über Bewegung ✅
- Autoplay/Parallax minimieren oder abschaltbar machen ✅

## 7. Barrierefreiheit (WCAG 2.2)
Alles per Tastatur bedienbar · Fokus sichtbar und nicht von Sticky-Header/Banner verdeckt · Klickziele mindestens 24×24 px · Formularfelder mit `<label>`, Fehler als Text · Alt-Texte (rein dekorativ: `alt=""`) · ARIA nur wenn nötig („Keine ARIA ist besser als schlechte ARIA") ✅

## 8. Performance (Zielwerte, Google)
LCP ≤ 2,5 s · INP ≤ 200 ms · CLS ≤ 0,1 (75. Perzentil, Felddaten) ✅
Hero-Bild nie `loading="lazy"`, `fetchpriority="high"`, AVIF/WebP, Bilder mit `width`/`height`, Platz für Einbettungen reservieren ✅
Messen mit Lighthouse/PageSpeed Insights; Lab-Werte schwanken stark je nach Profil, Felddaten bevorzugen ✅ (eigener Test an apple.com/de)

## 9. SEO
Eigener `<title>` und Beschreibung je Seite · sprechende URLs · Bilder mit Alt · hilfreiche aktuelle Inhalte · Testseiten mit `noindex` (nicht `robots.txt`) · Sitemap meist automatisch ✅ · strukturierte Daten (JSON-LD) optional, kein Ranking-Versprechen ✅ · lokal: Google-Unternehmensprofil pflegen ✅

## 10. Recht Deutschland (Orientierung)
- **Impressum** nach § 5 DDG (Name, Anschrift, E-Mail/Kontakt; je nach Rechtsform mehr), leicht erreichbar, am besten im Footer jeder Seite ✅
- **Datenschutzerklärung** nach Art. 13 DSGVO: Zwecke, Rechtsgrundlagen, Empfänger, Speicherdauer, Rechte, Beschwerderecht; muss zu den **tatsächlich genutzten Diensten** passen ✅
- **Cookies/Tracking** (§ 25 TDDDG): Einwilligung nötig, außer „unbedingt erforderlich" (z. B. Spracheinstellung ohne User-ID) ✅
- **Cookie-Banner** (DSK-Orientierungshilfe 11/2024): Ablehnen so einfach wie Zustimmen, gleichwertig gestaltet; „Einstellungen oder Ablehnen" reicht nicht ✅
- **Google Fonts** nicht von Google-Servern laden, lokal hosten ❓ (Urteil LG München I 2022 nur aus Berichten)
- **BFSG** (seit 28.06.2025): betrifft Online-Shops/Verbraucher-Dienstleistungen; reine Infoseiten voraussichtlich nicht; Kleinstunternehmen bei Dienstleistungen ausgenommen ✅ Bundesfachstelle; Gesetzestext und Reichweite ❓

## 11. Anweisungen an KI-Website-Builder
Ein Prompt = **Was** (kleiner Baustein) + **echter Text** + **Stil-Stichwörter** + **Ort/Verhalten** + **Grenzen** („nur dies ändern"). Eine Änderung pro Prompt, in der Vorschau prüfen, Zwischenstände speichern, Rückfragen zulassen ✅ (Lovable-Doku; andere Builder ❓)

## 12. Vor dem Start klären
Zielgruppe · **eine** Hauptaktion pro Seite · Seitenbaum · echte Texte und Bilder (Nutzungsrechte!) · Impressum-/Datenschutz-Angaben bereithalten

## Noch offen ❓
Farbpaletten aus Primärquelle · Call-to-Action-Tests · BFSG-Gesetzestext und Urteilstexte · Banner/Cookies mit deutscher IP · Screenreader-Test · Builder außer Lovable
