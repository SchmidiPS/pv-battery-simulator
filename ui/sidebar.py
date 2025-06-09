# ui/sidebar.py
from pathlib import Path
import json
import pandas as pd
import streamlit as st
from PIL import Image
from geopy.geocoders import Nominatim
from core.theme import set_theme_css
from i18n import LANG

def build_sidebar() -> dict:
    """zeichnet die komplette Sidebar und liefert zentrale Eingaben zurück"""
    with st.sidebar:
        # Logo
        logo_path = Path(__file__).resolve().parents[1] / "images" / "logo.png"
        st.image(Image.open(logo_path), use_container_width=True)

        # Sprache
        col1, col2 = st.columns(2)
        if "language" not in st.session_state:
            st.session_state.language = "Deutsch"
        if col1.button("🇩🇪"): st.session_state.language = "Deutsch"
        if col2.button("🇬🇧"): st.session_state.language = "English"
        T = LANG[st.session_state.language]

        # Theme
        theme = st.selectbox("Theme", ["light", "dark"], key="theme_select")
        st.session_state["theme"] = theme
        set_theme_css(theme)

        st.title(T["general"])

        # Standort
        use_address = st.checkbox("Adresse statt Koordinaten")
        if use_address:
            addr = st.text_input("Adresse", "Fürstenweg 42, Innsbruck")
            if addr:
                loc = Nominatim(user_agent="battery-sim", timeout=5).geocode(addr)
                lat = loc.latitude if loc else None
                lon = loc.longitude if loc else None
        else:
            lat = st.number_input(T["latitude"], value=47.26, format="%.4f")
            lon = st.number_input(T["longitude"], value=11.38, format="%.4f")
        year = st.number_input(T["year"], value=2022, step=1)

                # → hier sicherstellen, dass Keys existieren
        st.session_state["lat"] = lat
        st.session_state["lon"] = lon
        st.session_state["year"] = year

        # Lastprofil
        st.subheader("Lastprofil")
        mode = st.radio("Lastprofil wählen", ("CSV-Upload", "Konstanter Verbrauch"), index=1)
        if mode == "CSV-Upload":
            up = st.file_uploader(T["upload"], type="csv")
            load_df = pd.read_csv(up, parse_dates=[0], index_col=0) if up else None
            if load_df is not None:
                st.success(f"✓ {len(load_df)} Zeilen geladen")
            else:
                st.info(T["no_load"])
        else:
            load_df = None
            st.session_state.constant_load = st.number_input(
                "Konstanter Verbrauch pro Stunde (kW)", min_value=0.0, value=5.0
            )

        # Modi
        mode_opts = ["Eigenverbrauch", "Peak Shaving", "Inselbetrieb", "Notstrom"]
        selected_modes = st.multiselect(T["modes"], mode_opts, default=["Eigenverbrauch"])

        # Szenario-Load
        load_json = st.file_uploader(T["load"], type="json")
        if load_json:
            cfg = json.load(load_json)
            st.session_state.update(cfg)
            st.success("Szenario geladen – Seite neu laden!")

        st.caption("© 2025 batteriespeicher24.ch")

    return dict(T=T, lat=lat, lon=lon, year=year,
                selected_modes=selected_modes, load_df=load_df)
