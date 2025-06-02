import streamlit as st
import pandas as pd
from core.pv_sim import simulate_pv
from core.battery import simulate_battery
from core.visualize import plot_battery_result

st.title("PV & Batteriespeicher Simulation")

# Eingabeparameter
lat = st.number_input("Breitengrad", value=47.26)
lon = st.number_input("Längengrad", value=11.38)
kwp = st.number_input("PV-Leistung (kWp)", value=10.0)
capacity = st.number_input("Batteriekapazität (kWh)", value=15.0)
power = st.number_input("Lade-/Entladeleistung (kW)", value=5.0)
year = st.number_input("Jahr", value=2022, step=1)

if st.button("Simulation starten"):
    with st.spinner("Lade PV-Daten..."):
        pv = simulate_pv(lat, lon, kwp, year)
        idx = pv.index
        load = pd.Series(5.0, index=idx)  # Dummy-Last

    with st.spinner("Simuliere Batterie..."):
        result = simulate_battery(load, pv, capacity, power, power)

    fig = plot_battery_result(load, pv, result)
    st.pyplot(fig)
