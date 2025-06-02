from pvlib import location, iotools
import pandas as pd

def simulate_pv(
    lat: float,
    lon: float,
    kwp: float,
    year: int = 2022,
    tilt: float = 30,
    azimuth: float = 180,
    raddatabase: str = "PVGIS-SARAH3",
    loss: float = 14,
    timezone: str = "Europe/Vienna"
) -> pd.Series:
    """
    Simuliert stündlichen PV-Ertrag (kW) basierend auf PVGIS-Daten.

    Parameters:
    - lat, lon: Standortkoordinaten
    - kwp: PV-Anlagenleistung in kWp
    - year: Simulationsjahr (z. B. 2022)
    - tilt: Neigungswinkel der Module in Grad
    - azimuth: Ausrichtung (180 = Süden)
    - raddatabase: Strahlungsdatenbank
    - loss: Systemverluste in Prozent
    - timezone: Zeitzone für Zeitreihe

    Returns:
    - Pandas Series mit stündlichem Ertrag in kW
    """
    df, meta, _ = iotools.get_pvgis_hourly(
        latitude=lat,
        longitude=lon,
        start=year,
        end=year,
        raddatabase=raddatabase,
        surface_tilt=tilt,
        surface_azimuth=azimuth,
        peakpower=kwp,
        loss=loss,
        pvcalculation=True,
        components=False
    )

    df.index = pd.to_datetime(df.index, utc=True).tz_convert(timezone)
    return df["P"] / 1000  # W → kW
