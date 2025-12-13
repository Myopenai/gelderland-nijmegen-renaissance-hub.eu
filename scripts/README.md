# Scripts für Systemarchitektur & Qualitätssicherung

Sammlung von Skripten für Audits, Reparaturen und Validierung der gesamten Produktionsstruktur.

---

## 1. `crawl-mojibake.js` — Headless Crawler für Encoding-Fehler

Detektiert **Mojibake** (fehlerhaft encodierte Umlaute) über alle Seiten hinweg.

### Features
- ✅ Auto-Erkennung von Sitemaps (aus `robots.txt`)
- ✅ Filesystem-Scanning (HTML-Dateien)
- ✅ Unterstützt `file://` und `http(s)://` URLs
- ✅ Link-Folge (same-origin)
- ✅ Dry-run (read-only, keine Änderungen)
- ✅ JSON-Report mit detaillierten Funden

### Voraussetzungen

```bash
npm install playwright
npx playwright install --with-deps
```

### Verwendung

**Crawl lokal (file://):**
```bash
node scripts/crawl-mojibake.js
```

**Crawl über HTTP:**
```bash
# Stelle sicher, dass der Server läuft (z.B. npm run dev)
node scripts/crawl-mojibake.js http://localhost:3000
```

**Custom max-pages:**
```bash
node scripts/crawl-mojibake.js file://... 100
```

### Output

- **Konsole**: Live-Fortschritt + Top-Funde
- **`scripts/crawl-mojibake-report.json`**: Vollständiger Report (alle URLs mit Mojibake-Funden)

### Beispiel-Report
```json
{
  "start": "http://localhost:3000",
  "scanned": 42,
  "findings": [
    {
      "url": "http://localhost:3000/about",
      "mojibake": ["Ã¤", "Ã¶"],
      "entities": ["&auml;"],
      "snippet": "Überblick..."
    }
  ]
}
```

### Exit-Codes
- `0` — Keine Mojibake-Funde (OK)
- `1` — Mojibake entdeckt (Fehler)

---

## 2. `FixHtmlUmlautsRobust.ps1` — PowerShell Umlaut-Reparatur

Scannt alle HTML-Dateien und ersetzt echte Umlaute (`ä, ö, ü, ß`) durch HTML-Entities.

### Features
- ✅ Automatische Encoding-Erkennung
- ✅ Backups aller Originalfiles
- ✅ Rollback-Script (automatisch erzeugt)
- ✅ Detailliertes Logging
- ✅ Safe file writing (temp + verify + move)

### Voraussetzungen

- PowerShell (als **Administrator**)
- Bearbeitungsrechte auf Zielverzeichnis

### Konfiguration

Öffne `scripts/FixHtmlUmlautsRobust.ps1` und setze:

```powershell
$rootDir   = "D:\\path\\to\\your\\html\\files"
$backupDir = "C:\\Backups\\..."
$logFile   = "C:\\Logs\\..."
```

### Verwendung

```powershell
# Als Administrator ausführen
cd D:/busineshuboffline\ CHATGTP/KEAN
powershell -ExecutionPolicy Bypass -File scripts/FixHtmlUmlautsRobust.ps1
```

### Output

- **Backups**: Originalfiles in `$backupDir` (Datum+Uhrzeit)
- **Log**: `$logFile` (UTF-8 encoded)
- **Rollback-Script**: `$backupDir/Rollback-HtmlUmlautFixes.ps1`
- **Desktop-Shortcut**: Link zum Log (falls `WScript.Shell` verfügbar)

### Rollback (falls nötig)

```powershell
powershell -ExecutionPolicy Bypass -File "C:\\Backups\\...\\Rollback-HtmlUmlautFixes.ps1"
```

---

## 3. `health-check-downloads.js` — Validierung Downloads-Struktur

Prüft, ob Manifest (`public/downloads/downloads.json`) existiert und korrekt ist.

### Verwendung

```bash
node scripts/health-check-downloads.js
```

### Output

Sicherheit- und Konsistenzprüfungen:
- ✅ `downloads.json` existiert und ist gültiges JSON
- ✅ Manifest enthält `id`, `filename`, `name` für jedes Artefakt
- ✅ Keine unsicheren Zeichen in Dateinamen (z.B. `../`)

---

## 4. `ps_syntax_check.ps1` — PowerShell Syntax-Validator

Validiert PowerShell-Syntax **ohne Ausführung**.

### Verwendung

```powershell
pwsh -NoProfile -File scripts/ps_syntax_check.ps1
```

### Ausgabe

- `Syntax OK` — Keine Fehler
- Fehlerauflistung bei Problemen

---

## CI/CD Integration (GitHub Actions)

Beispiel in `.github/workflows/quality-check.yml`:

```yaml
name: Quality Checks

on: [push, pull_request]

jobs:
  mojibake-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - run: npm install playwright
      - run: npx playwright install --with-deps
      - name: Scan for Mojibake
        run: node scripts/crawl-mojibake.js file://$(pwd)/public
```

---

## Best Practices

### Für Fejler-Suche (Mojibake/Encoding)

1. **Lokal mit `crawl-mojibake.js` starten** (file:// mode)
2. **Dann gegen Dev-Server** (`http://localhost:3000`)
3. **Report reviewed + diskutieren**
4. **Root-Cause suchen** (DB encoding, HTTP headers, Template engine)
5. **Fix implementieren** (zentral, nicht überall)
6. **Tests + Crawler re-run** zur Validierung

### Für PowerShell-Reparatur

1. **Erst ein Dry-Run / Test-Folder** (nicht auf Produktion starten)
2. **Backup prüfen**
3. **Log reviewen**
4. **Rollback-Script speichern** (falls nötig)
5. **Produktion reparieren**

### Monitoring & Alerts

Für Produktion:
- Crawler regelmäßig (z.B. täglich) laufen lassen
- Report in Monitoring-Dashboard
- Alert, falls Mojibake-Count > 0
- Regression-Detector in CI

---

## Fehlerbehandlung

### Playwright install schlägt fehl

**Symptom:** `browserType.launch: Executable doesn't exist`

**Lösung:**
```bash
npx playwright install --with-deps
```

Falls Netzwerkprobleme: Cache manuell löschen
```bash
rm -rf ~/.cache/ms-playwright
npx playwright install --with-deps
```

### PowerShell Execution Policy

**Symptom:** `PS1 cannot be loaded because running scripts is disabled`

**Lösung:**
```powershell
powershell -ExecutionPolicy Bypass -File scripts/FixHtmlUmlautsRobust.ps1
```

---

## Kontakt & Support

Bei Fragen oder Problemen:
- Check `ARCHITECTURE_ANALYSIS.md` (Root-Cause Analyse)
- Check `IMPLEMENTATION_PLAN.md` (Technische Details)
- Check `VALIDATION_SUMMARY.md` (Validierungsergebnisse)
