from core.pv_sim import simulate_pv
import pandas as pd

def test_simulate_pv():
    pv, ghi = simulate_pv(48.2, 16.4, 5, year=2022)

    # Debug-Ausgaben
    print("\n--- DEBUG: PV & GHI Infos ---")
    print("PV-Serie:", type(pv), "Anzahl:", len(pv), "Summe:", pv.sum(), "Max:", pv.max())
    print("GHI-Serie:", type(ghi), "Anzahl:", len(ghi), "Summe:", ghi.sum(), "Max:", ghi.max())
    print("GHI-Serie (erste 5):\n", ghi.head())
    print("GHI-Serie (Typen):", ghi.dtype)

    # Tests
    assert isinstance(pv, pd.Series)
    assert len(pv) >= 8700, "PV-Serie ist zu kurz"
    assert pv.sum() > 3000, "PV-Jahresertrag zu gering"
    assert pv.max() < 6, "PV-Leistung unrealistisch hoch"

    assert isinstance(ghi, pd.Series)
    assert len(ghi) == len(pv), "GHI-Serie muss gleich lang sein"
    assert ghi.sum() > 800000, "GHI-Gesamtsumme zu gering"

