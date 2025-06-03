from pvlib.iotools import get_pvgis_tmy
import pandas as pd

def simulate_pv(
    lat: float,
    lon: float,
    kwp: float,
    tilt: float = 30,
    azimuth: float = 180,
    loss: float = 14,
    timezone: str = "Europe/Vienna",
    coerce_year: int = 2022
) -> tuple[pd.Series, pd.Series]:
    """
    Simuliert den PV-Ertrag (kW) und liefert zusätzlich die Globalstrahlung (GHI) in Wh/m²
    auf Basis eines typischen meteorologischen Jahres (TMY).

    Returns:
    - Tuple(PV-Ertrag in kW, GHI in Wh/m²)
    """

    # Wetterdaten (SARAH3-TMY) abrufen
    weather, _, _, _ = get_pvgis_tmy(
        latitude=lat,
        longitude=lon,
        outputformat="json",
        usehorizon=True,
        userhorizon=None,
        startyear=None,
        endyear=None,
        map_variables=True,
        timeout=30,
        roll_utc_offset=None,
        coerce_year=coerce_year
    )

    # Zeitzone setzen und sortieren
    weather.index = weather.index.tz_convert(timezone)
    weather = weather.sort_index()

    # GHI (Wh/m²) → keine negativen Werte
    ghi = weather["ghi"]

    # Zeitschritt in Stunden (typisch: 1.0 h)
    timestep_hours = (weather.index[1] - weather.index[0]).total_seconds() / 3600

    # Umrechnung auf Leistung (kW) für Ertragsmodell
    ghi_kw_per_m2 = ghi / 1000 / timestep_hours

    # Einfache lineare PV-Ertragsschätzung (ohne Geometrie)
    pv_output_kw = kwp * ghi_kw_per_m2 * (1 - (loss / 100))

    # Debug-Ausgabe
    print("PV Output (kW) – Min/Max:", pv_output_kw.min(), pv_output_kw.max())
    print("PV Jahresertrag (kWh):", pv_output_kw.sum() * timestep_hours)
    print("GHI Jahresstrahlung (kWh/m²):", ghi.sum() / 1000)

    return pv_output_kw, ghi
