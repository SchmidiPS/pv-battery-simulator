"""Streamlit Dashboard – multilingual, themable, save/load, PDF stub
-------------------------------------------------------------------
Variante 2 (Dashboard‑Tabs) mit folgenden Extras:
• Sprachumschalter (DE / EN)
• Light/Dark‑Theme‑Toggle
• Logo (batteriespeicher24.ch)
• Szenario speichern & laden (JSON)
• PDF‑Export‑Stub
"""

from __future__ import annotations

import json
import datetime as dt
from pathlib import Path

import pandas as pd
import streamlit as st
from fpdf import FPDF
import io
import geopy
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium
from PIL import Image
from core.theme import set_theme_css

# ───────────────────────── Streamlit Page Config ─────────────────────────
st.set_page_config(
    page_title="BatterySim Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)




# ─────────────────────────── Sidebar (UI) ───────────────────────────────
from ui.sidebar import build_sidebar
state = build_sidebar()

T = state["T"]
lat = state["lat"]
lon = state["lon"]
year = state["year"]
selected_modes = state["selected_modes"]
load_df = state["load_df"]      # ersetzt st.session_state.load_df


# ─────────────────────────── Haupttitel ────────────────────────────────
st.title(T["title"])

# Kartenvorschau im Hauptbereich
if "lat" in st.session_state and "lon" in st.session_state:
    st.subheader("Standortvorschau")
    import folium
    from streamlit_folium import st_folium

    map_view = folium.Map(
        location=[st.session_state["lat"], st.session_state["lon"]],
        zoom_start=22,
        tiles="OpenStreetMap"
    )
    folium.Marker(
        [st.session_state["lat"], st.session_state["lon"]],
        tooltip="Simulationsstandort"
    ).add_to(map_view)

    st_folium(map_view, use_container_width=True, height=700)

st.divider()


if "simulation_done" not in st.session_state:
    st.session_state.simulation_done = False

# Tabs
pv_tab, batt_tab, econ_tab, result_tab = st.tabs([
    T["pv_tab"],
    T["batt_tab"],
    T["economics_tab"],
    T["result_tab"],
])


# ───────── Tab 1 – PV Konfiguration ───────────────────────────────────
with pv_tab:
    st.header(T["pv_tab"])
    if "pv_arrays" not in st.session_state:
        st.session_state.pv_arrays = pd.DataFrame({"kWp": [10.0], "Tilt": [30], "Azimut": [180]})
    st.session_state.pv_arrays = st.data_editor(
        st.session_state.pv_arrays,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
    )

# ───────── Tab 2 – Batterie & Modi ─────────────────────────────────────
with batt_tab:
    st.header(T["batt_tab"])
    c1, c2, c3 = st.columns(3)
    st.session_state.capacity_kwh = c1.number_input("Batterie kWh", value=15.0, min_value=1.0)
    st.session_state.power_kw = c2.number_input("Inverter Leistung kW", value=5.0, min_value=0.5)
    st.session_state.efficiency = c3.slider("Wirkungsgrad %", 80, 99, 95)
    c4 = st.columns(1)[0]
    st.session_state.cycles_dod = c4.number_input("Zyklen bei 70% DoD", value=4000, min_value=100, max_value=20000)


    st.divider()
    if "Peak Shaving" in selected_modes:
        with st.expander("Peak Shaving"):
            peak_limit = st.number_input("Peak‑Limit kW", value=50.0)
    if "Inselbetrieb" in selected_modes:
        with st.expander("Inselbetrieb"):
            backup_days = st.slider("Autonomie (Tage)", 1, 10, 3)
    if "Notstrom" in selected_modes:
        with st.expander("Notstrom"):
            critical_load = st.number_input("Kritische Last kW", value=2.0)


with econ_tab:
    st.header("💰 Wirtschaftlichkeitsparameter")

    c1, c2, c3 = st.columns(3)
    st.session_state.price_pv_kwp = c1.number_input("PV‑Kosten (€/kWp)", value=1000.0, min_value=0.0)
    st.session_state.price_batt_kwh = c2.number_input("Batterie‑Kosten (€/kWh)", value=700.0, min_value=0.0)
    st.session_state.install_costs = c3.number_input("Installationskosten pauschal (EUR)", value=3000.0, min_value=0.0)

    c4, c5 = st.columns(2)
    st.session_state.price_buy = c4.number_input("Strombezugspreis (€/kWh)", value=0.30, format="%.2f")
    st.session_state.price_feed = c5.number_input("Einspeisetarif (€/kWh)", value=0.08, format="%.2f")

    c6, c7 = st.columns(2)
    st.session_state.discount_rate = c6.number_input("Diskontsatz (%)", value=5.0, format="%.1f") / 100
    st.session_state.lifetime_years = c7.number_input("Nutzungsdauer (Jahre)", value=20, step=1)



# ───────── Tab 3 – Simulation & Plots ──────────────────────────────────
from services.simulation import run as run_sim
from core.visualize import (
    plot_full_simulation_with_irradiance,
    plot_daily_energy_flows,
)

with result_tab:
    sim_placeholder = st.empty()

    if st.button(T["run"], use_container_width=True):
        sim_placeholder.info("⏳ Simulation läuft …")
        result = run_sim(st.session_state)

        # Serien + KPIs abholen
        pv_total   = result["pv_total"]
        ghi_total  = result["ghi_total"]
        load       = result["load"]
        batt       = result["batt"]
        kpi        = result["kpi"]

        # ---------- UI-Anzeige ----------
        st.subheader("🔋 Systemübersicht")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("PV-Leistung (kWp)",  f"{st.session_state.pv_arrays['kWp'].sum():.2f}")
        col2.metric("Batterie (kWh)",     f"{st.session_state.capacity_kwh:.1f}")
        col3.metric("WR-Leistung (kW)",   f"{st.session_state.power_kw:.1f}")
        col4.metric("Jahreslast (kWh)",   f"{load.sum():,.0f}")
        col5.metric("PV-Ertrag (kWh)",    f"{pv_total.sum():,.0f}")

        st.subheader("📈 Wirtschaftlichkeit")
        c1, c2, c3 = st.columns(3)
        c1.metric("Gesamtkosten",  f"{kpi['invest']:,.0f} €")
        c2.metric("Ersparnis / Jahr", f"{kpi['savings']:,.0f} €")
        c3.metric("Autarkie",      f"{kpi['autarkie']:.1f} %")
        c4, c5, c6 = st.columns(3)
        c4.metric("Amortisation",  f"{kpi['amort']:.1f} Jahre" if kpi['amort']<100 else "–")
        c5.metric("Batterielebensdauer", f"{kpi['batt_lifetime']:.1f} Jahre")
        c6.metric("NPV",           f"{kpi['npv']:,.0f} €")

        # Plots
        st.subheader("📊 Visualisierung")
        st.pyplot(plot_full_simulation_with_irradiance(load, pv_total, ghi_total, batt))
        st.pyplot(plot_daily_energy_flows(batt))

        # Ergebnisse in session_state für PDF / Download
        st.session_state["sim_result"] = result
        st.session_state["autarkie"]   = kpi["autarkie"]

        sim_placeholder.success("✅ Simulation abgeschlossen")


