from pvlib import location, iotools
import pandas as pd

def simulate_pv(lat, lon, kwp, tilt=30, azimuth=180):
    site = location.Location(lat, lon, tz="Europe/Vienna")
    df, meta = iotools.get_pvgis_hourly(
        latitude=lat,
        longitude=lon,
        startyear=2020,
        endyear=2020,
        raddatabase="PVGIS-SARAH",
        peakpower=kwp,
        angle=tilt,
        aspect=azimuth,
        loss=14
    )
    df.index = pd.to_datetime(df.index, utc=True).tz_convert(site.tz)
    return df["P"] / 1000  # W → kW
