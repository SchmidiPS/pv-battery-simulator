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

# ───────────────────────── Streamlit Page Config ─────────────────────────
st.set_page_config(
    page_title="BatterySim Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ────────────────────────────── I18N Dict ───────────────────────────────
LANG: dict[str, dict[str, str]] = {
    "Deutsch": {
        "title": "PV‑ & Batteriespeicher‑Simulator",
        "general": "Allgemeine Eingaben",
        "latitude": "Breitengrad",
        "longitude": "Längengrad",
        "year": "Jahr",
        "upload": "CSV‑Datei hochladen (Zeit, kW)",
        "no_load": "Kein Lastprofil hochgeladen – Dummy‑Profil wird genutzt.",
        "modes": "Betriebsmodi",
        "pv_tab": "PV‑Konfiguration",
        "batt_tab": "Batterie & Modi",
        "result_tab": "Simulation & Plots",
        "run": "Simulation starten",
        "save": "Szenario speichern",
        "load": "Szenario laden (JSON)",
        "export": "PDF‑Export",
    },
    "English": {
        "title": "PV & Battery Storage Simulator",
        "general": "General inputs",
        "latitude": "Latitude",
        "longitude": "Longitude",
        "year": "Year",
        "upload": "Upload CSV (time,kW)",
        "no_load": "No load profile uploaded – using dummy profile.",
        "modes": "Operating modes",
        "pv_tab": "PV configuration",
        "batt_tab": "Battery & modes",
        "result_tab": "Simulation & plots",
        "run": "Run simulation",
        "save": "Save scenario",
        "load": "Load scenario (JSON)",
        "export": "PDF export",
    },
}

# ─────────────────────────── Sidebar (UI) ───────────────────────────────
with st.sidebar:
    logo_path = Path(__file__).resolve().parents[2] / "images" / "logo.png"
    logo_img = Image.open(logo_path)
    st.image(logo_img, use_container_width=True)

    st.title("Language / Sprache")
    col1, col2 = st.columns(2)
    if "language" not in st.session_state:
        st.session_state.language = "Deutsch"

    with col1:
        if st.button("🇩🇪", use_container_width=True):
            st.session_state.language = "Deutsch"

    with col2:
        if st.button("🇬🇧", use_container_width=True):
            st.session_state.language = "English"

    T = LANG[st.session_state.language]


    theme_choice = st.selectbox("Theme", ["light", "dark"], key="theme_select")
    st.session_state["theme"] = theme_choice

    st.title(T["general"])

    # Adresse oder Koordinaten
    use_address = st.checkbox("Adresse statt Koordinaten")

    if use_address:
        address_input = st.text_input("Adresse", "Fürstenweg 42, Innsbruck")
        if address_input:
            from geopy.geocoders import Nominatim
            geolocator = Nominatim(user_agent="battery-sim")
            location = geolocator.geocode(address_input)
            if location:
                lat, lon = location.latitude, location.longitude
                st.session_state["lat"] = lat
                st.session_state["lon"] = lon
            else:
                st.warning("Adresse nicht gefunden.")
                lat = lon = None
    else:
        lat = st.number_input(T["latitude"], value=47.26, format="%.4f")
        lon = st.number_input(T["longitude"], value=11.38, format="%.4f")
        st.session_state["lat"] = lat
        st.session_state["lon"] = lon

    year = st.number_input(T["year"], value=2022, step=1)

    st.subheader("Lastprofil")
    upload = st.file_uploader(T["upload"], type="csv")
    if upload is not None:
        load_df = pd.read_csv(upload, parse_dates=[0], index_col=0)
        st.success(f"✓ {len(load_df)} Zeilen geladen")
    else:
        load_df = None
        st.info(T["no_load"])

    st.subheader(T["modes"])
    mode_opts = ["Eigenverbrauch", "Peak Shaving", "Inselbetrieb", "Notstrom"]
    selected_modes = st.multiselect(T["modes"], mode_opts, default=["Eigenverbrauch"])

    st.subheader(T["load"])
    load_json = st.file_uploader(T["load"], type="json")
    if load_json is not None:
        cfg = json.load(load_json)
        st.session_state.update(cfg)
        st.success("Szenario geladen – Seite neu laden!")

    st.caption("© 2025 batteriespeicher24.ch")


# ─────────────────────────── Haupttitel ────────────────────────────────
st.title(T["title"])

# Kartenvorschau im Hauptbereich
if "lat" in st.session_state and "lon" in st.session_state:
    st.subheader("Standortvorschau")
    import folium
    from streamlit_folium import st_folium

    map_view = folium.Map(
        location=[st.session_state["lat"], st.session_state["lon"]],
        zoom_start=13,
        tiles="OpenStreetMap"
    )
    folium.Marker(
        [st.session_state["lat"], st.session_state["lon"]],
        tooltip="Simulationsstandort"
    ).add_to(map_view)

    st_folium(map_view, use_container_width=True, height=700)


# KPI‑Badges (Dummy bis zur Simulation)
col_a, col_b, col_c = st.columns(3)
col_a.metric("Autarkie", "–")
col_b.metric("Amortisation", "–")
col_c.metric("NPV", "–")

st.divider()


if "simulation_done" not in st.session_state:
    st.session_state.simulation_done = False

# Tabs
pv_tab, batt_tab, result_tab = st.tabs([T["pv_tab"], T["batt_tab"], T["result_tab"]])

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
    capacity_kwh = c1.number_input("Batterie kWh", value=15.0, min_value=1.0)
    power_kw = c2.number_input("Leistung kW", value=5.0, min_value=0.5)
    efficiency = c3.slider("Wirkungsgrad %", 80, 99, 95)

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


# ───────── Tab 3 – Simulation & Plots ──────────────────────────────────
with result_tab:
    sim_placeholder = st.empty()

    if st.button(T["run"], use_container_width=True):
        from core.pv_sim import simulate_pv
        from core.battery import simulate_battery
        from core.visualize import plot_full_simulation_with_irradiance

        sim_placeholder.info("⏳ Simulation läuft …")

        # PV‑Summe über alle Arrays + GHI
        pv_total = None
        ghi_total = None
        for _, pv_row in st.session_state.pv_arrays.iterrows():
            pv_series, ghi_series = simulate_pv(
                lat, lon,
                pv_row["kWp"],
                year,
                pv_row["Tilt"],
                pv_row["Azimut"]
            )
            pv_total = pv_series if pv_total is None else pv_total.add(pv_series, fill_value=0)
            ghi_total = ghi_series if ghi_total is None else ghi_total.add(ghi_series, fill_value=0)

        # Lastserie
        if load_df is None:
            load_series = pd.Series(5.0, index=pv_total.index)
        else:
            load_series = load_df.squeeze().reindex(pv_total.index, method="nearest").fillna(method="ffill")

        # Batteriesimulation
        result = simulate_battery(
            load_series,
            pv_total,
            capacity_kwh,
            power_kw,
            power_kw,
            efficiency / 100
        )

        # Visualisierung
        fig = plot_full_simulation_with_irradiance(load_series, pv_total, ghi_total, result)
        st.pyplot(fig, use_container_width=True)

        # KPI minimal
        autarkie = 100 * (1 - result["grid_import"].sum() / load_series.sum())
        amort = "–"  # TODO: Wirtschaftlichkeits‑Modul
        npv = "–"    # TODO: Wirtschaftlichkeits‑Modul
        col_a.metric("Autarkie", f"{autarkie:.1f}%")
        col_b.metric("Amortisation", amort)
        col_c.metric("NPV", npv)

        # Ergebnisse speichern
        st.session_state["sim_result"] = result
        st.session_state["load_series"] = load_series
        st.session_state["lat"] = lat
        st.session_state["lon"] = lon
        st.session_state["autarkie"] = autarkie

        # Szenario speichern – JSON in Download‑Button
        scenario = {
            "lat": lat,
            "lon": lon,
            "year": year,
            "pv_arrays": st.session_state.pv_arrays.to_dict(),
            "capacity_kwh": capacity_kwh,
            "power_kw": power_kw,
            "efficiency": efficiency,
            "selected_modes": selected_modes,
        }
        json_bytes = json.dumps(scenario, indent=2).encode()
        st.download_button(
            T["save"],
            data=json_bytes,
            file_name="scenario.json",
            mime="application/json"
        )

        sim_placeholder.success("✅ Simulation abgeschlossen")

    # PDF‑Export (außerhalb vom Button-Block)
    if "sim_result" in st.session_state and st.button(T["export"]):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        report_text = (
            "BatterySimTool - Simulation Report\n"
            f"Datum:   {dt.datetime.now():%d.%m.%Y %H:%M}\n"
            f"Standort: {st.session_state['lat']:.4f}, {st.session_state['lon']:.4f}\n"
            f"Autarkie: {st.session_state['autarkie']:.1f}%"
        )
        pdf.multi_cell(0, 10, report_text)

        # Als Bytes exportieren
        pdf_bytes = pdf.output(dest="S").encode("latin1")
        pdf_buffer = io.BytesIO(pdf_bytes)

        st.download_button(
            label="📄 PDF Download",
            data=pdf_buffer,
            file_name=f"report_{dt.datetime.now():%Y%m%d_%H%M%S}.pdf",
            mime="application/pdf",
        )


