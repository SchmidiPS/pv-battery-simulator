Hier ist der vollständige Bericht als reiner Text zum direkten Kopieren:

Projektentwurf – Universeller PV‑ & Batteriespeicher‑Simulator
Stand: 3. Juni 2025

1 Ziel & Vision

Ein Web‑basiertes Tool, das den gesamten Engineering‑ und Wirtschaftlichkeits‑Workflow für PV‑Anlagen und Batteriespeicher automatisiert – von Standortanalyse über Ertragssimulation und Batteriestrategien bis hin zu Visualisierung, Lebensdauerschätzung und Wirtschaftlichkeits‑Empfehlung.
Unterstützt werden alle gängigen Betriebsmodi: Eigenverbrauch, Peak‑Shaving, Inselbetrieb und Notstrom.

2 Zielgruppen & Use‑Cases
Gruppe	Anwendung	Hauptziel
Privathaushalt	Eigenverbrauch, Backup	Autarkiegrad ↑, Amortisation < 10a
KMU/Industrie	Peak‑Shaving, dynamische Tarife	Demand‑Charges ↓, NPV ↑
Off‑Grid Sites	Inselnetz, Dieselreduktion	Autonomie ↑, Kosten ↓

3 MVP‑Scope (Sprint 1 – aktualisiert)

Input:

    Adresse/Koordinaten

    Jahreslastprofil (CSV oder Dummy)

    PV‑Konfiguration (kWp, Azimut, Neigung)

    Batteriesystem (Kapazität, Leistung, Wirkungsgrad, DoD, Zyklenlebensdauer)

    Wirtschaftlichkeitsparameter (€/kWh, €/kWp, Installationskosten, Strompreise, Diskontsatz, Lebensdauer)

Funktion:

    PVGIS‑API für Strahlungsdaten

    PV‑Ertrag mit pvlib

    Batteriesimulation mit einfachem Eigenverbrauchs‑Dispatch

    Lebensdauer‑Abschätzung via Zyklenzählung

    Wirtschaftlichkeits‑Modul mit:

        Investitionskosten

        jährlicher Ersparnis

        Amortisation

        Kapitalwert (NPV)

    Visualisierungen:

        SOC‑Verlauf

        Lade-/Entladeflüsse

        Tagesenergieflüsse (Stacked Bar)

        Anteile Netz/Batterie/PV (100%-Diagramm)

UI:

    Streamlit Dashboard mit Tabs (PV, Batterie, Wirtschaftlichkeit, Simulation)

    Dynamische Eingaben & Multilingual (DE/EN)

    Standortkarte mit Marker

    PDF‑Export

4 Architektur (High‑Level – identisch)

┌───────────────┐ PVGIS/NASA ┌───────────────┐
│ Frontend │ Weather API │ CAPEX/OPEX │
│ (Streamlit) │◀───────────────▶│ Datenbank │
└──────┬────────┘ └───────┬──────┘
│REST (FastAPI) │
┌──────▼────────┐ ┌────────▼────────┐
│ Core Engine │ │ Reporting │
│ (Python) │ │ (PDF/JSON) │
└──────┬────────┘ └────────┬────────┘
│ │
┌──────▼────────┐ ┌────────▼────────┐
│ pvlib │ │ Optimizer │
│ (Ertrag) │ │ (Pyomo/GLPK) │
└───────────────┘ └──────────────────┘

5 Technologie‑Stack

    Python 3.11

    Frontend: Streamlit

    Backend: FastAPI (optional)

    Simulation: pvlib, heuristischer Dispatch

    Wirtschaftlichkeit: Eigenes CAPEX-Modul + NPV‑Berechnung

    Visualisierung: Matplotlib

    PDF‑Export: fpdf

    Datenquellen: PVGIS, CSV (Tarife & Preise)

6 Offene Punkte / TODO (aktualisiert)

    GHI-Komponenten automatisch rekonstruieren

    PDF‑Export mit Diagrammen integrieren

    Vergleichsprofil (ohne Batterie) ergänzen

    Erweiterung um Lastverschiebung oder Zeitvarianten (TOU)

7 Roadmap (aktualisiert)
Sprint	Dauer	Deliverable
Sprint 0	2 Tage	Scope, Repo‑Setup, Dummy-Daten
Sprint 1	1 Woche	MVP laut Abschnitt 3
Sprint 2	2 Wochen	Peak Shaving, Gewerbeprofile
Sprint 3	2 Wochen	Inselbetrieb, Blackout-Szenarien
Release 1.0 QA	1 Woche	Volltest, Usability, Performanceoptimierung

8 Prompt‑Guideline für andere LLM‑Sessions

System Prompt:
„Du bist Senior‑Energiesystem‑Engineer. Nutze den untenstehenden Projektentwurf als Kontext und fahre mit den definierten TODOs fort. Ändere nichts außerhalb des aktuellen Abschnitts, falls nicht explizit verlangt.“

9 Versions‑Hinweis

Dieses Dokument ist das Single Source of Truth.
Änderungen ausschließlich hier oder via Pull Request mit Verweis auf Abschnitt/Zeile.