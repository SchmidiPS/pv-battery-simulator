# core/theme.py

import streamlit as st

def set_theme_css(theme_name: str):
    if theme_name == "light":
        st.markdown(
            """
            <style>
            /* Hauptbereich & Sidebar Hintergrund und Text */
            [data-testid="stAppViewContainer"] > div:first-child,
            [data-testid="stSidebar"],
            [data-testid="stMain"] {
                background-color: rgb(254, 251, 248) !important;
                color: #004080 !important;  /* Blaue Schrift */
            }

            /* Überschriften */
            h1, h2, h3, h4, h5 {
                color: #003366 !important;
            }

            /* Text- und Number Input */
            .stTextInput > div > div > input,
            .stNumberInput > div > div > input {
                background-color: #e6f0ff !important;
                color: #004080 !important;
                border: 1px solid #a0c4ff !important;
                border-radius: 5px !important;
            }

            /* Selectbox Dropdown (nur das sichtbare Feld) */
            .stSelectbox > div > div > div > div {
                background-color: #e6f0ff !important;
                color: #004080 !important;
                border: 1px solid #a0c4ff !important;
                border-radius: 5px !important;
            }

            /* Checkbox Label und Text */
            .stCheckbox > label > div[data-baseweb="checkbox"] {
                border: 1px solid #a0c4ff !important;
                background-color: #e6f0ff !important;
                border-radius: 3px !important;
            }
            .stCheckbox > label > div > span {
                color: #004080 !important;
            }

            /* Radio Buttons */
            .stRadio > label > div[data-baseweb="radio"] {
                border: 1px solid #a0c4ff !important;
                background-color: #e6f0ff !important;
                border-radius: 50% !important;
            }
            .stRadio > label > div > span {
                color: #004080 !important;
            }

            /* Buttons */
            .stButton > button {
                background-color: #007acc !important;
                color: white !important;
                border: none !important;
                border-radius: 5px !important;
                font-weight: 600;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        pass



