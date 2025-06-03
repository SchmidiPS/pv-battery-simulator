from __future__ import annotations
import pandas as pd
from pvlib import iotools


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
) -> tuple[pd.Series, pd.Series]:
    """
    Simuliert stündlichen PV-Ertrag (kW) und liefert zusätzlich Globalstrahlung (GHI) in Wh/m².
    
    Returns:
    - Tuple(PV-Ertrag in kW, GHI in Wh/m²)
    """

    # PV-Ertrag abrufen
    df_pv, _, _ = iotools.get_pvgis_hourly(
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
        components=True
    )

    df_pv.index = pd.to_datetime(df_pv.index, utc=True).tz_convert(timezone)
    pv_output = df_pv["P"] / 1000  # W → kW

    # GHI separat abrufen
    df_rad, _, _ = iotools.get_pvgis_hourly(
        latitude=lat,
        longitude=lon,
        start=year,
        end=year,
        raddatabase=raddatabase,
        surface_tilt=0,
        surface_azimuth=0,
        pvcalculation=False,
        components=True  # notwendig für G(h)
    )

    df_rad.index = pd.to_datetime(df_rad.index, utc=True).tz_convert(timezone)

    if "G(h)" in df_rad.columns:
        ghi = df_rad["G(h)"]
    else:
        print("⚠️ Kein 'G(h)' gefunden – GHI wird mit Nullen ersetzt.")
        ghi = pd.Series(0, index=df_rad.index)

    return pv_output, ghi
