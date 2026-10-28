## Filter-Agent

**Urteil: WEITER** · Note: B (mit Vorbehalt, siehe unten)
**Entscheidend:** L50, L75, L8–L12, L70–L71, L79–L81 belegen alle sieben Anforderungen der Ersatz-Anzeige; aber L2/L17/L7 verwirren die Feld-Zuordnung (aktueller Titel, „UMSCHULUNG“ ohne Standardüberschrift), und nur 5 von 10 Anzeigen-Begriffen stehen wörtlich im Text.

Geprüft mit der Ausbildungs-Anzeige als Ersatz-Maßstab (Bewerbungsziel: Praktikum in der Praxisphase). Ohne die echte Praktikumsausschreibung. Die Anzeige trennt nicht zwischen Muss und Kann: alle sieben Punkte zählen als Muss, Kann-Anforderungen gibt es nicht. Ein „A“ (alle Muss und die meisten Kann) lässt sich deshalb nicht sauber vergeben, ich vergebe B.

### Note
B. Alle Muss erfüllt (M1–M7, Zeilen siehe Tabelle). Abzug gegenüber A nur wegen Auslese-Risiko (L2, L7, L17, L34) und fehlender Anzeigen-Begriffe.

### Auslese-Befunde
- Textebene vorhanden, keine Tabellen, Textboxen, Kopf-/Fußzeilen. Name (L1) und Kontakt (L3–L4) stehen oben im Text. Sauber.
- **Feld „aktueller Jobtitel“:** Ein System nimmt die erste Station im Abschnitt „BERUFSERFAHRUNG“ (L16). Das ist L17 „03/2026 – 06/2026 Berufliche Neuorientierung“, also kein Jobtitel und kein Arbeitgeber. Die IT-Station (L8) steht davor in einem Abschnitt „UMSCHULUNG“ (L7), den es als Standardfeld nicht gibt.
- **Feld „Ausbildung“:** Mit Standardüberschrift „AUSBILDUNG UND SCHULE“ (L47) landet dort als erste Zeile L48 „Ausbildung zum Gebäudereiniger“. Die laufende IHK-Umschulung zum Fachinformatiker (L8) fehlt in diesem Feld, wenn das System „UMSCHULUNG“ nicht zuordnet.
- **Gruppenzeile L34** „Gebäude- und Industriereinigung“ hat weder Titel noch Arbeitgeber noch Zeitraum. Die darunterliegenden Stationen L35–L36 sind einzeilig gesetzt (Titel · Arbeitgeber: Tätigkeit), L37–L45 dagegen mit Aufzählungen: unterschiedliche Struktur, mittleres Risiko beim Parsen.
- **Berufsjahre:** Rechenbar, alle Zeiträume MM/JJJJ. Einzeldaten im Fließtext („18.10.2027“ L6, „10/2026“ L12) sind uneinheitlich, stören aber nicht.
- **Störwörter:** keine Platzhalter. Ein eingebettetes Bild trägt Alternativtext, wird hier nicht bewertet.

### Tabelle
| Anforderung (wörtlich aus der Anzeige) | Muss/Kann | Status | Fundstelle |
|---|---|---|---|
| Mittleren Schulabschluss erfolgreich abgeschlossen | Muss | erfüllt, aber schwach geschrieben: als Station „Mittlerer Schulabschluss · Berufsschule“ ohne Abschlussjahr als Datum eines Abschlusses, daneben L53 „ohne Abschluss beendet“ | L50, L53 |
| gute Deutschkenntnisse | Muss | erfüllt | L75 „Deutsch: Muttersprache“ |
| ausgeprägtes technisches Verständnis | Muss | erfüllt | L10–L12, L68–L69, L79–L81, L52, L65 |
| Interesse an IT-Systemen, Netzwerken und digitalen Technologien | Muss | erfüllt (belegt durch Umschulung, Praktika, eigene Projekte) | L8–L12, L54–L57, L71, L79–L81 |
| arbeitet konzentriert, sorgfältig, denkt analytisch | Muss | teilweise: Beleg indirekt (Dokumentation, Prüfung, Testfälle), Wort fehlt | L30–L31, L12, L25 |
| Freude an der Zusammenarbeit mit Kolleginnen, Kollegen sowie Kunden | Muss | erfüllt für Kollegen, für Kunden/Anwender nur privat | L26–L27, L38–L39, L70 |
| neugierig, lernbereit | Muss | erfüllt (Belege statt Behauptung) | L8, L59–L62 |

### Fehlende Begriffe
| Begriff der Anzeige | Im Text? | Wo er hingehört, falls wahr |
|---|---|---|
| IT-Systeme | nein | Kurzprofil L6 („IT-Systeme“ statt nur „IT-Infrastruktur“) |
| Netzwerke | ja | L11, L71 |
| Systemintegration | ja | L2, L6, L8 |
| konfigurieren | als „Konfiguration“ | L69, L71, L79; Verb „konfiguriert“ fehlt |
| vernetzte Systeme | nein | Firmennetz L12 („vernetztes Firmennetz“) wäre wahr |
| Inbetriebnahme | nein | Frage: wurden Server/Netz nach Einrichtung getestet und in Betrieb genommen (L10, L12)? |
| Fehler (erkennen, analysieren, beheben) | als „Fehlerbehebung“, „Fehlersuche“ | L68, L55, L57; „Fehleranalyse“ fehlt |
| IT-Sicherheit | ja, aber nur als Zukunft und Schulung | L15, L61; als angewendet nicht belegt |
| Anwenderinnen und Anwender beraten/unterstützen | nein („SAP (Anwender)“ L24, L73 meint das Gegenteil) | L70 IT-Support: „Anwender unterstützt“ |
| Digitalisierungsprojekte | nein | nur wenn wahr; Platzhalter-Frage |

Wörtlich oder in Wortstamm gefunden: 5 von 10 (Netzwerke, Systemintegration, konfigurieren/Konfiguration, Fehler-, IT-Sicherheit).

### Such-Test
1. `Systemintegration UND (Netzwerk ODER Netzwerke) UND (Windows ODER Active Directory)` → **gefunden** (L2, L11, L10).
2. `IT-Support UND Anwender UND Fehleranalyse UND IT-Sicherheit` → **nicht gefunden**: „Anwender“ steht nur als SAP-Anwender (L24), „Fehleranalyse“ fehlt, „IT-Sicherheit“ nur als Schulung/Zukunft (L61, L15).

### Knock-out-Punkte, die der Lebenslauf offenlässt
- Schulabschluss „Mittlerer Schulabschluss: ja/nein“: L50 beantwortet es, aber L53 „ohne Abschluss beendet“ stört das Bild.
- **Zeugnisse:** Anzeige verlangt die letzten zwei Zeugnisse zum Hochladen, L82 sagt „auf Anfrage“. Für das Praktikum unbekannt.
- **Verfügbarkeit:** Praxisphase ab 18.10.2027 steht nur im Fließtext L6, nicht als eigene Zeile. (Für die echte Ausbildungsstelle, Beginn 01.08.2027, würde die Umschulung bis 07/2028 L8–L9 ein Knock-out sein. Für das Praktikum nicht.)
- Ort: Norderstedt (Anzeige: Norderstedt). Kein Knock-out.
- Führerschein: nicht verlangt.

### Datei-Check
Word-Datei, textbasiert, kein versteckter Text, keine KI-Anweisungen. Größe ca. 2,0 MB, nur knapp unter der Greenhouse-Grenze von 2,5 MB (wissen/bewerbung-fakten.md); fast die gesamte Größe stammt vom eingebetteten Bild. Auf unter 500 KB verkleinern oder Bild komprimieren.

### Kritikpunkte (höchstens 5, wichtigster zuerst)
1. L7, L16–L17 · Das System findet keine IT-Station als „aktuelle Stelle“ und ordnet „UMSCHULUNG“ nicht zu; es liest „Berufliche Neuorientierung“ als letzte Station · Abschnitt nach Standard benennen (Ausbildung/Umschulung unter „Ausbildung“ oder IT-Station mit Titel, Träger, Zeitraum an erster Stelle), „Neuorientierung“ mit Titel und Zeitraum als Einzeiler · Frage: Soll die Umschulung als Ausbildung oder als aktuelle Berufsstation geführt werden? (Empfehlung: unter „Ausbildung“ als erste Zeile, im Kurzprofil als Ziel.)
2. L2, L6 · Kopfzeile nennt Status („Umschüler“), nicht das Ziel; ein Praktikum bei der Anzeige „Fachinformatiker für Systemintegration“ wird so schlecht gefunden · Zielzeile mit Anzeigen-Titel und Zeitraum der Praxisphase · Frage: Gewünschter Praktikumszeitraum (Start 18.10.2027, Ende?) und Vollzeit?
3. L10–L12, L68–L71 · Fünf Begriffe der Anzeige fehlen (IT-Systeme, vernetzte Systeme, Inbetriebnahme, Anwender beraten, Digitalisierungsprojekte) · nur dort einsetzen, wo wahr (L70 „Anwender unterstützt“, L12 „vernetztes Firmennetz“) · Frage: Hast du Server/Netz nach der Einrichtung in Betrieb genommen und geprüft (L10, L12)? Hast du an Digitalisierungsprojekten mitgearbeitet?
4. L50, L53 · Mittlerer Schulabschluss steht als Station, daneben „ohne Abschluss beendet“ · eigene Zeile „Mittlerer Schulabschluss, Abschlussjahr“ und L53 neutral formulieren (Berufsfachschule 1 Jahr, MSA später in der Berufsschule erworben, wie L50 sagt) · Frage: In welchem Monat/Jahr wurde der MSA erworben (L50 nennt 06/2012)?
5. L82 · „Zeugnisse auf Anfrage“ widerspricht der Anzeige („letzte zwei Zeugnisse“ zum Hochladen) · „Zeugnisse als Anlage“ oder Satz streichen · Frage: Hast du die letzten zwei Zeugnisse als Scan bereit?
