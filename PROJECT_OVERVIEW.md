Projektentwurf – Universeller PV‑ & Batteriespeicher‑Simulator

Stand: 2. Juni 2025

1 Ziel & Vision

Ein Web‑basiertes Tool, das den gesamten Engineering‑ und Wirtschaftlichkeits‑Workflow für PV‑Anlagen und Batteriespeicher automatisiert – von Standortanalyse über Ertragssimulation bis hin zur Wirtschaftlichkeits‑Empfehlung. Alle gängigen Betriebsmodi (Eigenverbrauch, Peak‑Shaving, Insel, Notstrom) werden unterstützt.

2 Zielgruppen & Use‑Cases

Gruppe

Anwendung

Hauptziel

Privathaushalt

Eigenverbrauch, Backup

Autarkiegrad ↑, Amortisation < 10 a

KMU/Industrie

Peak‑Shaving, Dynamische Tarife

Demand‑Charges ↓, NPV ↑

Off‑Grid Site

Inselnetz

Tage Autonomie ↑, Diesel ↓

3 MVP‑Scope (Sprint 1)

Input: Adresse/Koordinaten, Jahreslastprofil (CSV oder Vorlagen), 3 vordefinierte Batteriespeichergrößen

Funktion:

- Strahlungsdaten via PVGIS‑API (SARAH3, G(h)-Spalte optional)
- PV‑Ertrag mit pvlib
- Heuristische Dispatch‑Strategie (Eigenverbrauch)
- CAPEX/OPEX‑Modell (Listenpreise)
- Empfehlung (grösster NPV unter 10a Amortisation)
- GHI optional auf Basis von G(h) oder Komponenten (Summe Diffus+Direkt)

UI: Einfache Streamlit‑App, Download PDF‑Bericht

4 Architektur (High‑Level)

┌───────────────┐   PVGIS/NASA    ┌───────────────┐
│  Frontend     │  Weather API    │  CAPEX/OPEX   │
│  (Streamlit)  │◀───────────────▶│  Datenbank    │
└──────┬────────┘                 └───────┬──────┘
       │REST (FastAPI)                    │
┌──────▼────────┐               ┌────────▼────────┐
│  Core Engine  │               │   Reporting     │
│  (Python)     │               │  (PDF/JSON)     │
└──────┬────────┘               └────────┬────────┘
       │                                    │
┌──────▼────────┐               ┌────────▼────────┐
│   pvlib       │               │  Optimizer      │
│  (Ertrag)     │               │ (Pyomo/GLPK)    │
└───────────────┘               └──────────────────┘

5 Technologie‑Stack

Python 3.11

Frameworks: FastAPI, Streamlit

Simulation: pvlib, PyPSA (optional ab Sprint 2)

Optimierung: Pyomo + CBC/GLPK

Daten: PVGIS, Open‑Nem Stromtarife, eigene Preis‑CSV

CI/CD: GitHub Actions, Docker

6 Offene Punkte / TODO

- G(h) vs. poa_direct + poa_diffuse GHI‑Rekonstruktion automatisieren
- PDF‑Export implementieren
- Wirtschaftlichkeitsmodul verfeinern
- Interpolation bei Lücken im Lastprofil

7 Roadmap (Grob)

Sprint

Dauer

Deliverable

0

2 Tage

Detail‑Scope, Repo‑Setup

1

1 Woche

MVP laut Abschnitt 3

2

2 Wochen

Peak‑Shaving & Gewerbe‑Profiles

3

2 Wochen

Off‑Grid & Verschattung



Release 1.0 QA

8 Prompt‑Guideline für andere LLM‑Sessions

System Prompt: „Du bist Senior‑Energiesystem‑Engineer. Nutze den untenstehenden Projektentwurf als Kontext und fahre mit den definierten TODOs fort. Ändere nichts außerhalb des aktuellen Abschnitts, falls nicht explizit verlangt.“

Kontext: Platziere den Inhalt dieses Dokuments vor jede neue Session oder teile den Link zum Canvas.

9 Versions‑Hinweis

Dieses Dokument ist das Single Source of Truth. Änderungen bitte hier oder per Pull‑Request mit Verweis auf die Zeile/Section.
