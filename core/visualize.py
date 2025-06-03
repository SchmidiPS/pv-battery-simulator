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


def plot_pv_yield(pv_series: pd.Series):
    """
    Visualisiert den simulierten PV-Ertrag über das Jahr als Tagesmittel.
    """
    daily = pv_series.resample("D").sum()
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(daily.index, daily.values, label="Täglicher Ertrag [kWh]", color="orange")
    ax.set_title("Simulierter PV-Ertrag pro Tag")
    ax.set_ylabel("kWh")
    ax.set_xlabel("Datum")
    ax.grid(True)
    ax.legend()
    return fig


def plot_daily_energy_flows(result: pd.DataFrame):
    import matplotlib.pyplot as plt

    daily = result[["grid_import", "grid_export", "from_battery", "to_battery"]].resample("D").sum()

    # Summen berechnen und in Prozent umrechnen
    daily_pct = daily.div(daily.sum(axis=1), axis=0) * 100

    colors = {
        "grid_import": "red",         # Unerwünscht
        "grid_export": "green",       # Gewünscht
        "from_battery": "blue",       # Gewünscht
        "to_battery": "gold"          # Gewünscht
    }

    fig, ax = plt.subplots(figsize=(12, 4))
    bottom = pd.Series([0] * len(daily_pct), index=daily_pct.index)
    for col in ["grid_import", "from_battery", "to_battery", "grid_export"]:
        ax.bar(daily_pct.index, daily_pct[col], bottom=bottom, label=col, color=colors[col])
        bottom += daily_pct[col]

    ax.set_ylabel("Anteil [%]")
    ax.set_title("Tägliche Energieflüsse (100 %)")
    ax.legend(loc="upper right")
    ax.grid(True)
    plt.tight_layout()
    return fig


'''
def plot_full_simulation(load: pd.Series, pv: pd.Series, result: pd.DataFrame):
    """
    Kombinierter Plot für PV-Ertrag, Last, Batterie-SOC und Netzfluss.
    """
    fig, ax = plt.subplots(4, 1, figsize=(12, 10), sharex=True)

    # PV vs Last
    ax[0].plot(load, label="Last [kW]")
    ax[0].plot(pv, label="PV [kW]")
    ax[0].set_ylabel("Leistung (kW)")
    ax[0].legend()
    ax[0].set_title("PV-Ertrag vs. Last")

    # SOC Verlauf
    ax[1].plot(result["soc"], label="SOC [%]", color="blue")
    ax[1].set_ylabel("Batterie-SOC")
    ax[1].legend()
    ax[1].set_title("Batterieladestand")

    # Netzimport/-export
    ax[2].plot(result["grid_import"], label="Netzbezug [kWh]", color="red")
    ax[2].plot(result["grid_export"], label="Einspeisung [kWh]", color="green")
    ax[2].set_ylabel("Netzfluss")
    ax[2].legend()
    ax[2].set_title("Netzimport & Einspeisung")

    # Tagesertrag PV
    daily_pv = pv.resample("D").sum()
    ax[3].plot(daily_pv.index, daily_pv.values, label="PV-Tagesertrag [kWh]", color="orange")
    ax[3].set_ylabel("PV-Ertrag")
    ax[3].legend()
    ax[3].set_title("Täglicher PV-Ertrag")

    plt.xlabel("Zeit")
    plt.tight_layout()
    return fig


def plot_full_simulation_with_irradiance(load: pd.Series, pv: pd.Series, ghi: pd.Series, result: pd.DataFrame):
    """
    Kombinierter Plot für GHI, PV-Ertrag, Last, Batterie-SOC und Netzfluss.
    """
    fig, ax = plt.subplots(5, 1, figsize=(14, 12), sharex=True)

    # Strahlung
    ax[0].plot(ghi, label="Globalstrahlung (GHI) [W/m²]", color="gold")
    ax[0].set_ylabel("GHI")
    ax[0].legend()
    ax[0].set_title("Globalstrahlung am Standort")

    # PV vs Last
    ax[1].plot(load, label="Last [kW]", linestyle="--")
    ax[1].plot(pv, label="PV [kW]", linestyle="-.")
    ax[1].set_ylabel("Leistung (kW)")
    ax[1].legend()
    ax[1].set_title("PV-Ertrag vs. Last")

    # Tagesertrag PV
    daily_pv = pv.resample("D").sum()
    ax[2].plot(daily_pv.index, daily_pv.values, label="PV-Tagesertrag [kWh]", color="orange")
    ax[2].set_ylabel("PV-Ertrag")
    ax[2].legend()
    ax[2].set_title("Täglicher PV-Ertrag")

    # SOC Verlauf
    ax[3].plot(result["soc"], label="SOC [%]", color="blue")
    ax[3].set_ylabel("Batterie-SOC")
    ax[3].legend()
    ax[3].set_title("Batterieladestand")

    # Netzimport/-export
    ax[4].plot(result["grid_import"], label="Netzbezug [kWh]", color="red")
    ax[4].plot(result["grid_export"], label="Einspeisung [kWh]", color="green")
    ax[4].set_ylabel("Netzfluss")
    ax[4].legend()
    ax[4].set_title("Netzimport & Einspeisung")

    plt.xlabel("Zeit")
    plt.tight_layout()
    return fig
'''
    
def plot_full_simulation_with_irradiance(load: pd.Series, pv: pd.Series, ghi: pd.Series, result: pd.DataFrame):
    """
    Kombinierter Plot für GHI, Tages-PV-Ertrag vs. Tageslast, Batterie-SOC und Netzfluss.
    """
    fig, ax = plt.subplots(5, 1, figsize=(14, 12), sharex=True)

    # Strahlung
    ax[0].plot(ghi, label="Globalstrahlung (GHI) [W/m²]", color="gold")
    ax[0].set_ylabel("GHI")
    ax[0].legend()
    ax[0].set_title("Globalstrahlung am Standort")

    # PV vs Last
    ax[1].plot(pv, label="PV [kW]", linestyle="-")
    ax[1].plot(load, label="Last [kW]", linestyle="-")
    ax[1].set_ylabel("Leistung (kW)")
    ax[1].legend()
    ax[1].set_title("PV-Ertrag vs. Last")

    # Tagesertrag vs Tageslast
    daily_pv = pv.resample("D").sum()
    daily_load = load.resample("D").sum()
    ax[2].plot(daily_load.index, daily_load.values, label="Tages-Last [kWh]", linestyle="-")
    ax[2].plot(daily_pv.index, daily_pv.values, label="PV-Tagesertrag [kWh]", linestyle="-", color="orange")
    ax[2].set_ylabel("Energie (kWh)")
    ax[2].legend()
    ax[2].set_title("Täglicher PV-Ertrag vs. Tages-Last")

    # SOC Verlauf
    ax[3].plot(result["soc"], label="SOC [%]", color="blue")
    ax[3].set_ylabel("Batterie-SOC")
    ax[3].legend()
    ax[3].set_title("Batterieladestand")

    # Netzimport/-export
    ax[4].plot(result["grid_import"], label="Netzbezug [kWh]", color="red")
    ax[4].plot(result["grid_export"], label="Einspeisung [kWh]", color="green")
    ax[4].set_ylabel("Netzfluss")
    ax[4].legend()
    ax[4].set_title("Netzimport & Einspeisung")

    plt.xlabel("Zeit")
    plt.tight_layout()
    return fig
