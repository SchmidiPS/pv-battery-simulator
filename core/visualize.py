import pandas as pd
import matplotlib.pyplot as plt
from core.pv_sim import simulate_pv
from core.battery import simulate_battery

def demo_battery_sim():
    # 24h Zeitachse
    idx = pd.date_range("2022-06-01", periods=24, freq="H")
    
    # Verbrauch: 2 kW konstant
    load = pd.Series(2.0, index=idx)
    
    # PV: 0 am Morgen/Abend, 4 kW von 10–16 Uhr
    pv = pd.Series(0.0, index=idx)
    pv[10:17] = 4.0

    # Batterie-Simulation
    result = simulate_battery(
        load=load,
        pv=pv,
        capacity_kwh=10,
        charge_power_kw=3,
        discharge_power_kw=3
    )

    # Plot
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
    plt.suptitle("Batterie-Simulation – 1 Tag")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    demo_battery_sim()
