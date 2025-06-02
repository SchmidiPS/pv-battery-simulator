from core.pv_sim import simulate_pv

def test_pv_output():
    result = simulate_pv(48.2, 16.4, 5)
    assert len(result) >= 8700      # fast ganzes Jahr
    assert result.sum() > 3000      # realistische kWh
    assert result.max() < 6         # keine 100 kW-Spitzen
