import pandas as pd

def simulate_battery(
    load: pd.Series,
    pv: pd.Series,
    capacity_kwh: float,
    charge_power_kw: float,
    discharge_power_kw: float,
    efficiency: float = 0.95,
    timestep_hours: float = 1.0
) -> pd.DataFrame:
    """
    Simuliert einfache Batteriespeicherung für Eigenverbrauchsoptimierung.

    Parameters:
    - load: Verbrauchsprofil (kW)
    - pv: PV-Ertrag (kW)
    - capacity_kwh: Batteriekapazität (kWh)
    - charge_power_kw / discharge_power_kw: Lade-/Entladeleistung (kW)
    - efficiency: round-trip-Wirkungsgrad (0.95 = 95%)
    - timestep_hours: Zeitschrittgröße (i.d.R. 1h)

    Returns:
    - DataFrame mit Spalten: SOC, charge, discharge, grid_import, grid_export
    """
    index = load.index
    soc = 0.0
    results = []

    for t in index:
        demand = load[t]
        generation = pv[t]
        surplus = generation - demand

        charge = 0.0
        discharge = 0.0

        # Energieüberschuss → laden
        if surplus > 0:
            available = min(surplus, charge_power_kw) * efficiency
            charge = min(available * timestep_hours, capacity_kwh - soc)
            soc += charge
            grid_export = surplus - (charge / efficiency)
            grid_import = 0.0

        # Energiemangel → entladen
        else:
            needed = min(-surplus, discharge_power_kw)
            discharge = min(soc, needed * timestep_hours)
            soc -= discharge
            grid_import = (-surplus) - (discharge / efficiency)
            grid_export = 0.0

        results.append((soc, charge, discharge, grid_import, grid_export))

    return pd.DataFrame(results, index=index, columns=["soc", "charge", "discharge", "grid_import", "grid_export"])
