import matplotlib.pyplot as plt
import pandas as pd

def plot_battery_result(load: pd.Series, pv: pd.Series, result: pd.DataFrame):
    """
    Erstellt einen 3-teiligen Plot: Last/PV, SOC, Netzimport/-export.
    Gibt die Matplotlib-Figur zurück.
    """
    fig, ax = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

    ax[0].plot(load, label="Last [kW]", linestyle="--")
    ax[0].plot(pv, label="PV [kW]", linestyle="-.")
    ax[0].set_ylabel("Leistung (kW)")
    ax[0].legend()

    ax[1].plot(result["soc"], label="SOC [kWh]")
    ax[1].set_ylabel("Batterie-SOC")
    ax[1].legend()

    ax[2].plot(result["grid_import"], label="Netzbezug", color="red")
    ax[2].plot(result["grid_export"], label="Netzeinspeisung", color="green")
    ax[2].set_ylabel("Energie (kWh)")
    ax[2].legend()

    plt.xlabel("Zeit")
    plt.tight_layout()
    return fig
