# services/simulation.py  (neu sortiert)
# ---------------------------------------------------------------
from __future__ import annotations    # ← ganz nach oben!

# --- pvlib-Kompatibilität (≥0.10 liefert nur 2 Werte) ----------
from pvlib.iotools import get_pvgis_tmy as _orig_get_pvgis_tmy
import core.pv_sim                     # erst pv_sim importieren

def _compat_get_pvgis_tmy(*args, **kwargs):
    result = _orig_get_pvgis_tmy(*args, **kwargs)
    if len(result) == 2:               # neue API
        weather, meta = result
        return weather, meta, None, None
    return result                      # alte API

core.pv_sim.get_pvgis_tmy = _compat_get_pvgis_tmy
# ---------------------------------------------------------------

import datetime as dt
import pandas as pd
from core.pv_sim import simulate_pv
from core.battery import simulate_battery

def run(state) -> dict:
    """
    Führt PV- & Batterieberechnung durch.
    Erwartet einen st.session_state-ähnlichen Dict.
    Gibt ein Dict mit allen Serien und KPIs zurück.
    """
    lat, lon, year = state["lat"], state["lon"], state["year"]

    # PV-Summierung
    pv_total, ghi_total = None, None
    for _, row in state["pv_arrays"].iterrows():
        pv, ghi = simulate_pv(
            lat, lon,
            kwp=row["kWp"], tilt=row["Tilt"], azimuth=row["Azimut"],
            loss=14, coerce_year=year,
        )
        pv_total = pv if pv_total is None else pv_total.add(pv, fill_value=0)
        ghi_total = ghi if ghi_total is None else ghi_total.add(ghi, fill_value=0)

    # Lastprofil
    if state.get("load_df") is None:
        load = pd.Series(state.get("constant_load", 5.0), index=pv_total.index)
    else:
        load = (
            state["load_df"]
            .squeeze()
            .reindex(pv_total.index, method="nearest")
            .fillna(method="ffill")
        )

    # Batterie
    batt = simulate_battery(
        load, pv_total,
        state["capacity_kwh"],
        state["power_kw"], state["power_kw"],
        state["efficiency"] / 100,
    )

    # KPIs
    autarkie = 100 * (1 - batt["grid_import"].sum() / load.sum())
    pv_kwp = state["pv_arrays"]["kWp"].sum()
    pv_cost   = pv_kwp * state["price_pv_kwp"]
    batt_cost = state["capacity_kwh"] * state["price_batt_kwh"]
    invest    = pv_cost + batt_cost + state["install_costs"]

    grid_imp  = batt["grid_import"].sum()
    grid_exp  = batt["grid_export"].sum()
    baseline  = load.sum() * state["price_buy"]
    actual    = grid_imp * state["price_buy"] - grid_exp * state["price_feed"]
    savings   = baseline - actual

    amort = invest / savings if savings > 0 else float("inf")
    npv = sum(
        savings / ((1 + state["discount_rate"]) ** t)
        for t in range(1, state["lifetime_years"] + 1)
    ) - invest

    # zyklische Lebensdauer
    soc_diff = (batt["soc_%"] / 100).diff().abs()
    cycles = soc_diff.sum() / 2
    batt_lifetime = (
        (state["cycles_dod"] / cycles) * (len(batt) / 8760)
        if cycles > 0 else float("inf")
    )

    return {
        "pv_total": pv_total,
        "ghi_total": ghi_total,
        "load": load,
        "batt": batt,
        "kpi": dict(
            autarkie=autarkie,
            invest=invest,
            savings=savings,
            amort=amort,
            npv=npv,
            batt_lifetime=batt_lifetime,
        ),
        "timestamp": dt.datetime.now(),
    }
