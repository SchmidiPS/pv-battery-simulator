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

    Returns:
    - DataFrame mit Spalten:
      soc [%], charge, discharge, grid_import, grid_export,
      from_battery, to_battery
    """
    index = load.index
    soc = 0.0  # in kWh
    results = []

    pv = pv.clip(lower=0)

    for t in index:
        demand = load[t]
        generation = pv[t]
        surplus = generation - demand

        charge = 0.0
        discharge = 0.0

        if surplus > 0:
            # Laden
            available = min(surplus, charge_power_kw) * efficiency
            charge = min(available * timestep_hours, capacity_kwh - soc)
            soc += charge
            grid_export = surplus - (charge / efficiency)
            grid_import = 0.0

        else:
            # Entladen
            needed = min(-surplus, discharge_power_kw)
            discharge = min(soc, needed * timestep_hours)
            soc -= discharge
            grid_import = (-surplus) - (discharge / efficiency)
            grid_export = 0.0

        grid_import = max(grid_import, 0.0)
        grid_export = max(grid_export, 0.0)

        # Energieflüsse (nach außen sichtbare Energie, keine Verluste inkludiert)
        to_battery = charge
        from_battery = discharge

        results.append((
            soc, charge, discharge, grid_import, grid_export,
            from_battery, to_battery
        ))

    df = pd.DataFrame(results, index=index, columns=[
        "soc", "charge", "discharge", "grid_import", "grid_export",
        "from_battery", "to_battery"
    ])
    df["soc_%"] = df["soc"] / capacity_kwh * 100

    return df
