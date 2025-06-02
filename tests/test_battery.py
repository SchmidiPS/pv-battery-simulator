### Test 1

from core.battery import simulate_battery
import pandas as pd
import numpy as np

def test_battery_basic_simulation():
    # 24h Dummy-Last: 2 kW konstant
    idx = pd.date_range("2022-01-01", periods=24, freq="H")
    load = pd.Series(2.0, index=idx)

    # 24h Dummy-PV: mittags 4 kW, sonst 0
    pv = pd.Series(0.0, index=idx)
    pv[10:16] = 4.0

    # Batterie mit 10 kWh, 3 kW Lade-/Entladeleistung
    result = simulate_battery(
        load=load,
        pv=pv,
        capacity_kwh=10,
        charge_power_kw=3,
        discharge_power_kw=3
    )

    # Prüfung: Ergebnisstruktur stimmt
    assert isinstance(result, pd.DataFrame)
    assert "soc" in result.columns
    assert "grid_import" in result.columns

    # Prüfung: SOC steigt während PV-Mittagsphase
    assert result.loc["2022-01-01 12:00"].soc > 0

    # Prüfung: SOC sinkt nachts
    assert result.loc["2022-01-01 04:00"].soc <= result.loc["2022-01-01 23:00"].soc


### Test 2

from core.visualize import plot_battery_result
import matplotlib.figure

def test_plot_battery_result():
    # Dummy-Daten erzeugen
    idx = pd.date_range("2022-01-01", periods=24, freq="H")
    load = pd.Series(2.0, index=idx)
    pv = pd.Series(0.0, index=idx)
    pv[10:16] = 4.0

    result = simulate_battery(
        load=load,
        pv=pv,
        capacity_kwh=10,
        charge_power_kw=3,
        discharge_power_kw=3
    )

    # Plot erzeugen
    fig = plot_battery_result(load, pv, result)

    # Prüfung: Typ ist Matplotlib-Figur
    assert isinstance(fig, matplotlib.figure.Figure)
