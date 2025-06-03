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
        "economics_tab": "Wirtschaftlichkeit & KPIs",
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
        "economics_tab": "Economics & KPIs",
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
with result_tab:
    sim_placeholder = st.empty()

    if st.button(T["run"], use_container_width=True):
        from core.pv_sim import simulate_pv
        from core.battery import simulate_battery
        from core.visualize import plot_full_simulation_with_irradiance, plot_daily_energy_flows

        sim_placeholder.info("⏳ Simulation läuft …")

        # PV‑Summe über alle Arrays + GHI
        pv_total = None
        ghi_total = None
        for _, pv_row in st.session_state.pv_arrays.iterrows():
            pv_series, ghi_series = simulate_pv(
            lat=lat,
            lon=lon,
            kwp=pv_row["kWp"],
            tilt=pv_row["Tilt"],
            azimuth=pv_row["Azimut"],
            loss=14,
            coerce_year=year
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
            st.session_state.capacity_kwh,
            st.session_state.power_kw,
            st.session_state.power_kw,
            st.session_state.efficiency / 100
        )
        
        # Systemparameter nach Simulation anzeigen
        st.subheader("🔋 Systemübersicht")
        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("PV-Leistung (kWp)", f"{st.session_state.pv_arrays['kWp'].sum():.2f}")
        col2.metric("Batterie-Kapazität (kWh)", f"{st.session_state.capacity_kwh:.1f}")
        col3.metric("WR-Leistung (kW)", f"{st.session_state.power_kw:.1f}")
        col4.metric("Jahreslast (kWh)", f"{load_series.sum():,.0f}")
        col5.metric("PV-Ertrag (kWh)", f"{pv_total.sum():,.0f}")

        # ───────── KPIs anzeigen – nach Systemübersicht, vor Plot ─────────
        autarkie = 100 * (1 - result["grid_import"].sum() / load_series.sum())

        # Investitionskosten berechnen
        pv_kwp = st.session_state.pv_arrays["kWp"].sum()
        pv_cost = pv_kwp * st.session_state.price_pv_kwp
        batt_cost = st.session_state.capacity_kwh * st.session_state.price_batt_kwh
        install_cost = st.session_state.install_costs
        total_investment = pv_cost + batt_cost + install_cost

        # Einsparungen pro Jahr
        grid_import = result["grid_import"].sum()
        grid_export = result["grid_export"].sum()
        savings_per_year = grid_import * st.session_state.price_buy - grid_export * st.session_state.price_feed

        # Amortisation & Kapitalwert
        amortisation_years = total_investment / savings_per_year if savings_per_year > 0 else float("inf")
        npv = sum([
            savings_per_year / ((1 + st.session_state.discount_rate) ** t)
            for t in range(1, st.session_state.lifetime_years + 1)
        ]) - total_investment


        # Lebensdauerberechnung basierend auf SOC-Zyklen
        soc_normalized = result["soc_%"] / 100
        soc_diff = soc_normalized.diff().abs()
        total_cycles = soc_diff.sum() / 2  # entspricht Vollzyklen

        # Lebensdauer (Jahre) schätzen – st.session_state.cycles_dod muss vorhanden sein
        sim_years = len(result) / 8760  # 8760 Stunden/Jahr
        batt_lifetime_years = (st.session_state.cycles_dod / total_cycles) * sim_years if total_cycles > 0 else float("inf")

        st.subheader("📈 Wirtschaftlichkeit")

        # KPI‑Badges anzeigen
        col1, col2, col3 = st.columns(3)
        col1.metric("Gesamtkosten", f"{total_investment:,.0f} €")
        col2.metric("Ersparnis / Jahr", f"{savings_per_year:,.0f} €")
        col3.metric("Autarkie", f"{autarkie:.1f} %")

        col4, col5, col6 = st.columns(3)
        col4.metric("Amortisation", f"{amortisation_years:.1f} Jahre" if amortisation_years < 100 else "–")
        col5.metric("Batterielebensdauer", f"{batt_lifetime_years:.1f} Jahre")
        col6.metric("NPV", f"{npv:,.0f} €")


        st.subheader("📊 Visualisierung der Simulation")

        # Visualisierung
        fig = plot_full_simulation_with_irradiance(load_series, pv_total, ghi_total, result)
        st.pyplot(fig, use_container_width=True)

        fig_energy_flows = plot_daily_energy_flows(result)
        st.pyplot(fig_energy_flows)

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
            "capacity_kwh": st.session_state.capacity_kwh,
            "power_kw": st.session_state.power_kw,
            "efficiency": st.session_state.efficiency,
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


