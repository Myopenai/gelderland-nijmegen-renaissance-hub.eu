# KEAN Platform – Download-Ordner: Root-Cause-Analyse & Architektur-Lösung

**Datum**: 2025-12-12  
**Status**: Analyse + Final-Fix  

---

## 1. Executive Summary (für den Architekten)

### Das Problem
- **Symptom**: Download-Ordner / Downloads nicht im Portal sichtbar, lokale Builds nicht auffindbar
- **Root Cause**: **Fehlendes Artefakt-Management** – Artefakte werden erzeugt (Client-Seite ZIP), aber:
  - ❌ nicht zentralisiert
  - ❌ nicht registriert
  - ❌ nicht über Server erreichbar
  - ❌ nicht im Portal indexiert

### Die harte Wahrheit
> Ein Download-Ordner existiert **nicht einfach**. Er ist das Resultat einer bewussten Architektur-Entscheidung.
> 
> Eure Systeme erzeugen Artefakte (ZIP-Dateien), aber der **Fluss** (Build → Storage → Registry → Portal) ist unterbrochen.

---

## 2. Fehlerklassifizierung (Trichter-Methode)

### 2.1 Fehlerbereich eingrenzen

Typ: **Integrationsfehler + Architektur-Lücke**

| Ebene | Status | Befund |
|-------|--------|--------|
| **Build** | ✓ Funktioniert | `setup.html` erzeugt ZIP mit JSZip |
| **Artefakt** | ✓ Existiert | `kean-platform-completo.zip`, `University.zip` auf Repo |
| **Storage** | ❌ **Lücke** | Keine zentrale `/downloads` Ordner, keine Repo-Sync zu `/public` |
| **Registry** | ❌ **Lücke** | Keine Metadaten-Datei, keine API-Liste |
| **Portal** | ❌ **Lücke** | Keine Download-Seite, keine Indizierung |
| **Deployment** | ⚠️ Teilweise | Start-Skripte (`.bat`, `.sh`) vorhanden, aber Server startet als **local server only** |

---

## 3. Systemkarte (Ist-Zustand)

```
Nutzer
  ↓
setup.html (Client-Seite)
  ↓
JSZip (Client-Erzeugung)
  ↓
Browser Download (ephemer)
  ✗ Nicht: registriert, indexiert, wieder auffindbar
  
Parallel:
  Git-Repo
    ├── kean-platform-completo.zip
    ├── University.zip
    ✗ Nicht: verlinkt, katalogisiert, vom Portal nutzbar
    
Server (/src/server.js)
  ├── /public (statische Dateien)
  ├── /api/health
  ✗ Nicht: /downloads Endpunkt, kein Artefakt-Serving
  
Portal
  ├── index.html
  ✗ Nicht: Downloads-Seite, Listing-API
```

---

## 4. Invarianten (was gelten sollte, aber nicht tut)

1. **"Jedes Artefakt hat genau einen Speicherort"** → ❌ Zips überall (Repo, Browser-Downloads, nirgendwo zentral)
2. **"Jedes Artefakt ist über die Anwendung zugreifbar"** → ❌ Repo-Zips sind nicht vom Server erreichbar
3. **"Portal kennt alle verfügbaren Downloads"** → ❌ Kein Manifest, keine API
4. **"Versionierung ist konsistent"** → ❌ Multiple ZIP-Versionen, keine Versions-Metadaten

---

## 5. Root Causes (tiefste Ursachen)

### Ursache 1: Keine Artefakt-Quelle der Wahrheit
**Wo ist die authoritative Liste der Builds?**
- Setup.html: erzeugt ad-hoc (nicht persistent)
- Repo: .zips vorhanden, aber nicht automatisch deployed
- Server: hat keinen Sync-Mechanismus

→ **Fix**: Zentrale Metadaten-Registry + Server-Sync

---

### Ursache 2: Keine Storage-Invariante
**"Wo sollen Artefakte liegen, damit der Server & Portal sie finden?"**
- `/public/downloads/` nicht definiert
- Repo-ZIPs werden nicht dorthin kopiert
- Keine Deployment-Regel

→ **Fix**: Explizite Storage-Architektur (`/public/downloads/` mit Manifest)

---

### Ursache 3: Keine Download-API
**"Wie listet Portal alle Downloads auf?"**
- Keine `/api/downloads` Endpunkt
- Keine dynamische Auflistung
- Statische Seite mit Hard-Code-Links?

→ **Fix**: REST API für Artefakt-Listing + Metadaten

---

### Ursache 4: Keine Deployment-Pipeline
**"Wie kommen Repo-Artefakte zum Server & Portal?"**
- Keine automatisierte Deploy
- Manuelle Kopie (fehleranfällig)
- Keine Versionierung

→ **Fix**: Deploy-Skript + Versionierungs-Manifest

---

## 6. Soll-Architektur (die Lösung)

```
┌─────────────────────────────────────────────────────┐
│ GIT REPO (Single Source of Truth für Builds)       │
│  ├── /public/downloads/                            │
│  │    ├── kean-platform-v1.0.zip                   │
│  │    ├── university-project-v2.1.zip              │
│  │    └── downloads.json (Manifest)                │
│  └── src/server.js                                 │
└─────────────────────────────────────────────────────┘
           ↓ (Deploy / Sync)
┌─────────────────────────────────────────────────────┐
│ SERVER (Running Application)                       │
│  ├── /public/downloads/                            │
│  │    ├── *.zip (mirrored from repo)               │
│  │    └── downloads.json                           │
│  ├── GET /api/downloads                            │
│  │    └── JSON list + metadata                     │
│  └── GET /downloads/:filename                      │
│       └── Serves ZIP (with guards)                 │
└─────────────────────────────────────────────────────┘
           ↓ (API + static serve)
┌─────────────────────────────────────────────────────┐
│ PORTAL (User-Facing)                               │
│  ├── /downloads.html (reads /api/downloads)        │
│  ├── List of available artifacts                   │
│  └── Download links                                │
└─────────────────────────────────────────────────────┘
```

---

## 7. Implementierungs-Strategie

### Phase 1: Storage-Struktur etablieren
- Erstelle `/public/downloads/` Ordner
- Verschiebe Repo-ZIPs dorthin
- Erstelle `downloads.json` Manifest (Name, Version, Größe, Hash, Beschreibung)

### Phase 2: Server-Integration
- Füge `/api/downloads` GET-Endpunkt hinzu (liest Manifest)
- Füge `/downloads/:filename` GET-Endpunkt hinzu (serves ZIP mit Content-Disposition)
- Guards/Validierung: nur erlaubte Dateien, keine Path-Traversal

### Phase 3: Portal-UI
- Erstelle `/downloads.html` Seite
- Nutze `/api/downloads` für Listing
- Zeige Version, Größe, Beschreibung
- Download-Buttons zu `/downloads/filename`

### Phase 4: Deployment-Automatisierung
- Deploy-Skript kopiert `public/downloads/*` vom Repo zum Laufende Server (falls needed)
- Optional: GitHub Actions / CI für Artefakt-Versioning (später)

### Phase 5: Guards & Monitoring
- Unit Tests für `/api/downloads` API
- Integration Tests für Download-Fluss
- Monitoring: Download-Counts, Fehlerraten

---

## 8. Warum bisherige Versuche scheiterten

| Versuch | Fehler | Grund |
|---------|--------|-------|
| "Download-Ordner erstellen" | Ordner leer | Keine Sync-Regel |
| "Automatische Reparatur" | Funktioniert nicht konsistent | Symptom-Bekämpfung, nicht Ursache |
| "Manuelle Kopie" | Fehleranfällig, keine Versionierung | Keine Automatisierung |

➜ **Der Fehler war: Am Ordner arbeiten statt an der Architektur.**

---

## 9. Acceptance-Kriterien (wann ist es „endgültig"?)

✅ Repo enthält `/public/downloads/*.zip` + `downloads.json`  
✅ Server startet, `GET /api/downloads` antwortet mit JSON-Liste  
✅ `GET /downloads/kean-platform-v1.0.zip` lädt ZIP herunter  
✅ `/downloads.html` Portal zeigt alle verfügbaren Builds  
✅ Neue ZIPs hinzufügen = Manifest updaten, Deploy, fertig  
✅ Keine "Sucherei" mehr: alles ist katalogisiert  

---

## 10. Monitoring & Fehler-Prevention (damit es nie wieder passiert)

- **Alert**: If `/api/downloads` Status != 200, alert
- **Metric**: Download-Count pro Artefakt (Observability)
- **Health Check**: Server Startup sollte `/public/downloads/` Existenz prüfen
- **Test**: Integration-Test: "Manifest vorhanden + Dateien auffindbar"

---

**NÄCHSTER SCHRITT**: Siehe `IMPLEMENTATION_PLAN.md` für konkrete Code-Changes.
