# Webdesign – Das Wichtigste auf einer Seite

Stand: 2026-10-26 (Sitzung 6) · Grundlage: `webdesign-wissen.md` (dort Quellen, Links, Messwerte)
✅ am Original/Primärquelle geprüft · ❓ Richtwert oder nicht abschließend belegt · Recht = Orientierung, keine Rechtsberatung

## 1. Aufbau
- Erst Inhalte und Seitenstruktur festlegen, dann die Navigation ✅ (NN/g)
- Eine `h1` pro Seite, danach logisch absteigend; Ebene nach Struktur, nicht nach Schriftgröße ✅ (MDN)
- `header`, `nav`, `main` (nur einmal), `footer` ✅
- Startseite: Logo oben links, klarer Slogan, Alltagssprache, Wichtigstes ohne Scrollen, konkrete Linktexte ✅ (NN/g 2024)

## 2. Navigation, Links, Buttons
- **Desktop: Menü sichtbar, kein Hamburger** ✅ (NN/g 2016: versteckt 27 % Nutzung, sichtbar 48 %); mobil bis 4 Hauptlinks sichtbar, bei mehr Hamburger plus Inhalts-Links ✅
- Menü mit Untermenüs: Button mit `aria-expanded`, Esc schließt, kein `role="menu"` ✅ (W3C APG)
- **Link = Versprechen:** Linktext konkret, Zielseite löst es sofort ein ✅ (NN/g)
- **Keine generischen Buttons** („Get Started"/„Jetzt starten") – sagen, was passiert; erst informieren, dann Anmeldung verlangen ✅ (NN/g-Studie 2017)
- Ein primärer (gefüllter) Button je Bereich, sekundär umrandet; Zustände hover/focus/pressed/disabled ✅ (NN/g 2025)
- Touch-Ziele mindestens ca. 1 cm × 1 cm ✅ (NN/g); WCAG: mindestens 24×24 px ✅
- Zahlenbasierte CTA-Tests (Farbe/Position/Conversion): ❓ nicht gefunden

## 3. Layout & Responsive
- Viewport-Tag setzen, Zoom nie sperren ✅; mobile-first, Breakpoints nach Inhalt ✅
- Bei 320 px kein horizontales Scrollen ✅ (WCAG Reflow); Zeilen höchstens ca. 80 Zeichen ✅
- CSS Grid für zweidimensionale Layouts (`fr`, `repeat`, `minmax`, `gap`) ✅
- Häufiges Muster guter Seiten: Vollbild-Bild, große Überschrift, ein Button, darunter 3 Spalten ❓ (Beobachtung)

## 4. Schrift
- Größen **relativ** (`rem`), nicht fest in Pixeln; Nutzern Größenänderung erlauben ✅ (NN/g)
- Fließtext ca. 16 px: ❓ Richtwert – NN/g nennt keine Zahl, nur „reasonably large"
- Zeilenhöhe als Zahl ohne Einheit, mindestens 1,5 ✅ (MDN)
- `clamp(min, bevorzugt, max)` mit Max mindestens doppelt so groß wie Min (200 % Zoom) ✅
- Saubere Schrift; Serif ist auf modernen Bildschirmen ok; keine Handschrift-/Gotik-Imitate ✅ (Nielsen 2015); höchstens 1–2 Familien ❓ Beobachtung
- Schriften als WOFF2, wenige Schnitte, **lokal hosten**, `font-display` bewusst (`swap` Fließtext, `optional` stabilstes Layout), Icon-Fonts durch SVG ✅
- Schriftpaarungs-Regeln und Größenskalen aus Primärquelle: ❓ nicht lesbar (Apple/Material)

## 5. Farben
- Kontrast: Text **4,5:1**, großer Text **3:1** (AA); AAA 7:1 / 4,5:1 ✅; Information nie nur über Farbe ✅
- **Nicht blasses Grau** für Wichtiges – wirkt deaktiviert, in Sonne unlesbar ✅ (NN/g 2015)
- Basisfarbe + Neutraltöne, **möglichst wenige Farben**, Farbe zur Hervorhebung ✅ (MDN); Schemata monochrom/komplementär/triadisch ✅
- CSS: eine Schreibweise im Projekt; `oklch()` (Helligkeit/Intensität/Farbton getrennt) ✅; Dark Mode per `prefers-color-scheme` ✅
- Farbwirkung/Psychologie („Blau = Vertrauen"): ❓ nur Faustregel; analoge Schemata ❓

## 6. Animationen
- Nur `transform` und `opacity` animieren; `will-change` nicht vorsorglich ✅
- 100–400 ms, ab 500 ms zäh; Erscheinen = ease-out ✅ (NN/g)
- **`prefers-reduced-motion` respektieren**; Information nie nur über Bewegung; Autoplay/Parallax minimieren ✅

## 7. Barrierefreiheit (WCAG 2.2)
Alles per Tastatur bedienbar, keine Tastaturfalle · Fokus sichtbar (`:focus-visible`, ≥ 3:1) und nicht von Sticky-Header/Banner verdeckt · Skip-Link oder Landmarks · Klickziele ≥ 24×24 px · Formularfelder mit `<label>` und `autocomplete`, Fehler als Text mit Korrekturvorschlag · Alt-Texte (dekorativ `alt=""`) · ARIA nur wenn nötig ✅
Echter Screenreader-Test: ❓ nicht möglich in meiner Umgebung

## 8. Performance
- Zielwerte (Felddaten, 75. Perzentil): LCP ≤ 2,5 s · INP ≤ 200 ms · CLS ≤ 0,1 ✅
- Hero-Bild nie lazy, `fetchpriority="high"`; Bilder mit `width`/`height`; Fotos WebP/AVIF mit Fallback, Icons SVG; `srcset`/`sizes` ✅
- INP: lange Tasks aufteilen, kleines DOM; CDN und Caching nutzen (statisch lang, HTML `no-cache`) ✅
- Lab (Lighthouse) und Feld (CrUX) weichen ab – **Felddaten haben Vorrang** ✅; Core Web Vitals fließen ins Ranking ein, garantieren aber keine Top-Platzierung ✅ (Google)

## 9. SEO
Eigener `<title>` und Beschreibung je Seite · sprechende URLs · Alt-Texte · hilfreiche aktuelle Inhalte · Testseiten mit `noindex` (nicht `robots.txt`) · Sitemap meist automatisch · JSON-LD optional, kein Ranking-Versprechen · lokal: Google-Unternehmensprofil pflegen ✅

## 10. Recht Deutschland (Orientierung)
- **Impressum** nach § 5 DDG (Name, Anschrift, E-Mail/Kontakt; je nach Rechtsform mehr), leicht erreichbar, im Footer jeder Seite ✅
- **Datenschutzerklärung** nach Art. 13 DSGVO: Zwecke, Rechtsgrundlagen, Empfänger, Speicherdauer, Rechte; muss zu den **tatsächlich genutzten Diensten** passen ✅
- **Cookies** (§ 25 TDDDG): Einwilligung nötig, außer „unbedingt erforderlich" (z. B. Spracheinstellung ohne User-ID) ✅
- **Cookie-Banner** (DSK-OH 11/2024): Ablehnen so einfach wie Zustimmen und gleichwertig gestaltet; „Einstellungen oder Ablehnen" reicht nicht ✅ (Urteilstext VG Hannover ❓ nur aus Fachberichten)
- **Google Fonts** lokal hosten ✅ (LG München I, 20.01.2022, 3 O 17493/20: 100 € Schadensersatz, Entscheidungstext gelesen; Einzelfall, spätere Rechtsprechung ❓)
- **BFSG** (seit 28.06.2025): betrifft Online-Shops/Verbraucher-Dienstleistungen; reine Infoseiten voraussichtlich nicht; Kleinstunternehmen bei Dienstleistungen ausgenommen ✅ Bundesfachstelle; Gesetzestext/EU-Richtlinie im Original und Reichweite (ganze Website?) ❓

## 11. Anweisungen an KI-Website-Builder
Ein Prompt = **Was** (kleiner Baustein) + **echter Text** + **Stil-Stichwörter** + **Ort/Verhalten** + **Grenzen**. Eine Änderung pro Prompt, in der Vorschau prüfen, Zwischenstände speichern, Rückfragen zulassen ✅ (Lovable)
Framer: Seiten, Inhalte, Komponenten, responsives Verhalten und visuelle Richtung im ersten Prompt ✅ · Webflow: ein Prompt mit Look & Feel, Tätigkeit, Ziel; **Neu-Generieren verwirft manuelle Änderungen** ✅ · Wix, v0: ❓ nicht geprüft

## 12. Vor dem Start klären
Zielgruppe · **eine** Hauptaktion pro Seite · Seitenbaum · echte Texte und Bilder (Nutzungsrechte!) · Impressum-/Datenschutz-Angaben bereithalten

## Noch offen ❓ (geht in dieser Umgebung nicht oder fand ich nicht)
BFSG-Gesetzestext/EU-Richtlinie im Original · VG-Hannover-Urteilstext · Banner/Cookies mit deutscher IP · Screenreader-Test · Schriftpaarungs-Regeln, Größenskalen, Farbpsychologie, 16-px-Standard · Wix/v0 · Trends mit Aktualitätsprüfung
