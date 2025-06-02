"""Streamlit Dashboard‑Gerüst für das PV‑ & Batteriespeicher‑Simulations‑Tool
--------------------------------------------------------------------------
Variante 2: Dashboard mit Tabs & Kontextkarten

• Sidebar: Standort, Lastprofil‑Upload, Modus‑Multiselect
• Tabs:
    1. PV‑Konfiguration (editierbare Tabelle für mehrere Arrays)
    2. Batterie & Modi (Basis‑Batterieparameter + dynamische Moduskarten)
    3. Simulation & Plots (Platzhalter für Ergebnisvisualisierung)
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

# ───────────────────────── Sidebar – Allgemeines ──────────────────────────
with st.sidebar:
    st.title("Allgemeine Eingaben")

    # Standortdaten
    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input("Breitengrad", value=47.26, format="%.4f")
    with col2:
        lon = st.number_input("Längengrad", value=11.38, format="%.4f")

    year = st.number_input("Simulationsjahr", value=2022, step=1)

    st.divider()

    # Lastprofil‑Upload
    st.subheader("Lastprofil")
    uploaded_file = st.file_uploader("CSV‑Datei hochladen (Zeit, kW)", type=["csv"], key="load_csv")
    if uploaded_file is not None:
        load_df = pd.read_csv(uploaded_file, parse_dates=[0], index_col=0)
        st.success("✓ Lastprofil geladen – {} Zeilen".format(len(load_df)))
    else:
        load_df = None
        st.info("Kein Lastprofil hochgeladen – es wird ein Dummy‑Profil verwendet.")

    st.divider()

    # Betriebsmodi wählen (Mehrfachauswahl)
    st.subheader("Betriebsmodi")
    mode_options = ["Eigenverbrauchs­optimierung", "Peak Shaving", "Inselbetrieb", "Notstrom"]
    selected_modes = st.multiselect("Modus/Modi auswählen", mode_options, default=["Eigenverbrauchs­optimierung"])

    st.divider()
    st.caption("© 2025 BatteriesimTool – Demo Dashboard")

# ───────────────────── Hauptbereich – TABS Dashboard ──────────────────────
st.title("PV & Batteriespeicher Simulator – Dashboard")

# KPI‑Badges (Dummy‑Platzhalter – füllen wir nach Simulation)
col_a, col_b, col_c = st.columns(3)
col_a.metric("Autarkiegrad", "–", "–")
col_b.metric("Amortisation", "–", "–")
col_c.metric("NPV", "–", "–")

st.divider()

# Tabs
pv_tab, batt_tab, result_tab = st.tabs(["PV‑Konfiguration", "Batterie & Modi", "Simulation & Plots"])

# ───────── Tab 1: PV‑Konfiguration ────────────────────────────────────────
with pv_tab:
    st.header("PV‑Arrays konfigurieren")

    st.write("Mehrere Dächer? Einfach neue Zeile hinzufügen oder Werte inline bearbeiten.")

    # Basis‑DataFrame
    if "pv_arrays" not in st.session_state:
        st.session_state.pv_arrays = pd.DataFrame(
            {
                "kWp": [10.0],
                "Neigung (°)": [30],
                "Azimut (°)": [180],
            }
        )

    edited_df = st.data_editor(
        st.session_state.pv_arrays,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
    )

    st.session_state.pv_arrays = edited_df

# ───────── Tab 2: Batterie & Modi ─────────────────────────────────────────
with batt_tab:
    st.header("Batterie‑Parameter & Modusspezifische Einstellungen")

    # Basis‑Batterieparameter
    st.subheader("Batterie‑Grunddaten")
    col1, col2, col3 = st.columns(3)
    capacity_kwh = col1.number_input("Kapazität (kWh)", value=15.0, min_value=1.0)
    power_kw = col2.number_input("Lade-/Entladeleistung (kW)", value=5.0, min_value=0.5)
    efficiency = col3.slider("Round‑Trip‑Wirkungsgrad (%)", 80, 99, 95)

    st.divider()

    # Dynamische Moduskarten
    if "Peak Shaving" in selected_modes:
        with st.expander("Peak Shaving Parameter"):
            peak_limit = st.number_input("Peak‑Limit (kW)", value=50.0)

    if "Inselbetrieb" in selected_modes:
        with st.expander("Inselbetrieb Parameter"):
            backup_days = st.slider("Autonomie (Tage)", 1, 10, 3)

    if "Notstrom" in selected_modes:
        with st.expander("Notstrom Parameter"):
            critical_load = st.number_input("Kritische Last (kW)", value=2.0)

# ───────── Tab 3: Simulation & Plots ──────────────────────────────────────
with result_tab:
    st.header("Simulation & Ergebnisse")

    if st.button("Simulation starten", use_container_width=True):
        from core.pv_sim import simulate_pv
        from core.battery import simulate_battery
        from core.visualize import plot_battery_result

        st.success("Simulation läuft …")

        # Sammle PV‑Daten aus Tabelle
        pv_series_total = None
        for _, row in st.session_state.pv_arrays.iterrows():
            pv_series = simulate_pv(lat, lon, row["kWp"], year, row["Neigung (°)"], row["Azimut (°)"])
            pv_series_total = pv_series if pv_series_total is None else pv_series_total.add(pv_series, fill_value=0)

        # Dummy‑Lastprofil
        if load_df is None:
            load_series = pd.Series(5.0, index=pv_series_total.index)
        else:
            load_series = load_df.squeeze()  # Annahme: eine Spalte
            load_series = load_series.reindex(pv_series_total.index, method="nearest").fillna(method="ffill")

        result_df = simulate_battery(load_series, pv_series_total, capacity_kwh, power_kw, power_kw, efficiency/100)
        fig = plot_battery_result(load_series, pv_series_total, result_df)
        st.pyplot(fig, use_container_width=True)

        # KPI aktualisieren (vereinfachtes Beispiel)
        autarkie = 100 * (1 - result_df["grid_import"].sum() / load_series.sum())
        amort = "–"  # placeholder
        npv = "–"     # placeholder

        col_a.metric("Autarkiegrad", f"{autarkie:.1f}%")
        col_b.metric("Amortisation", amort)
        col_c.metric("NPV", npv)

    else:
        st.info("🛈 Konfiguration vornehmen und Simulation starten.")
