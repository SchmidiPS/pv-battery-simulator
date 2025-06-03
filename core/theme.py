# core/theme.py

import streamlit as st

def set_theme_css(theme_name: str):
    if theme_name == "light":
        st.markdown(
            """
            <style>
            /* Hauptbereich Hintergrund und Text */
            [data-testid="stAppViewContainer"] > div:first-child {
                background-color: rgb(254, 251, 248) !important;
                color: #000000 !important;
            }
            /* Sidebar Hintergrund */
            [data-testid="stSidebar"] {
                background-color: rgb(254, 251, 248) !important;
                color: #000000 !important;
            }
            /* Hauptinhalt */
            [data-testid="stMain"] {
                background-color: rgb(254, 251, 248) !important;
                color: #000000 !important;
            }
            /* Eingabeelemente - Input, Slider, Select */
            .stTextInput > div > div > input,
            .stNumberInput > div > div > input,
            .stSelectbox > div > div > div > div,
            .stSlider > div > div > input {
                background-color: #e6f0ff !important;  /* sehr helles Blau */
                color: #004080 !important;  /* dunkles Blau */
                border: 1px solid #a0c4ff !important;  /* helles Blau als Rahmen */
                border-radius: 5px !important;
            }
            /* Buttons */
            .stButton>button {
                background-color: #007acc !important;
                color: white !important;
                border: none !important;
                border-radius: 5px !important;
                font-weight: 600;
            }
            /* Überschriftenfarbe */
            h1, h2, h3, h4, h5 {
                color: #003366 !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        pass


