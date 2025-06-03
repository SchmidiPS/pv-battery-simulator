from core.pv_sim import simulate_pv
import pytest
import pandas as pd

def test_simulate_pv():
    pv, ghi = simulate_pv(48.2, 16.4, 5)

    assert isinstance(pv, pd.Series)
    assert isinstance(ghi, pd.Series)
    assert len(pv) == 8760
    assert len(ghi) == 8760
    assert ghi.sum() > 800_000
    assert pv.sum() > 3000
    assert pv.max() < 6
