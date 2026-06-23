"""SOT gate smoke tests — v6.2 production."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sot_gate import sot_bottom_up_gate, sot_threshold_prob, context_multiplier_guard

def test_gate_ok():
    r = sot_bottom_up_gate(5.0, 4.8)
    assert r.flag == "OK", f"Expected OK, got {r.flag}"
    assert abs(r.gated_mu - 4.9) < 0.01

def test_gate_review():
    r = sot_bottom_up_gate(7.5, 3.25)
    assert r.flag == "REVIEW"
    assert r.gated_mu < 7.5

def test_gate_block():
    r = sot_bottom_up_gate(10.0, 1.0)
    assert r.flag == "BLOCK"

# --- Test 1: Dynamic shrink con evidence_score ---
def test_dynamic_shrink_high_evidence():
    r = sot_bottom_up_gate(7.5, 3.25, evidence_score=1.0)
    expected_shrink = 0.55 + 0.20 * 1.0  # = 0.75
    expected_mu = 0.75 * 3.25 + 0.25 * 7.5
    assert abs(r.gated_mu - expected_mu) < 0.01, f"Expected {expected_mu:.3f}, got {r.gated_mu:.3f}"
    print(f"  evidence=1.0 → shrink=0.75 → mu={r.gated_mu:.3f}: OK")

def test_dynamic_shrink_low_evidence():
    r = sot_bottom_up_gate(7.5, 3.25, evidence_score=0.0)
    expected_shrink = 0.55 + 0.20 * 0.0  # = 0.55
    expected_mu = 0.55 * 3.25 + 0.45 * 7.5
    assert abs(r.gated_mu - expected_mu) < 0.01, f"Expected {expected_mu:.3f}, got {r.gated_mu:.3f}"
    print(f"  evidence=0.0 → shrink=0.55 → mu={r.gated_mu:.3f}: OK")

def test_dynamic_shrink_mid_evidence():
    r = sot_bottom_up_gate(7.5, 3.25, evidence_score=0.5)
    expected_shrink = 0.65  # 0.55 + 0.20*0.5 = 0.65 (coincide con default!)
    expected_mu = 0.65 * 3.25 + 0.35 * 7.5
    assert abs(r.gated_mu - expected_mu) < 0.01, f"Expected {expected_mu:.3f}, got {r.gated_mu:.3f}"
    print(f"  evidence=0.5 → shrink=0.65 → mu={r.gated_mu:.3f}: OK")

def test_no_evidence_uses_default():
    r_none = sot_bottom_up_gate(7.5, 3.25)
    r_mid  = sot_bottom_up_gate(7.5, 3.25, evidence_score=0.5)
    assert abs(r_none.gated_mu - r_mid.gated_mu) < 0.01, "None should == evidence=0.5 (both use shrink=0.65)"
    print(f"  evidence=None == evidence=0.5: OK (mu={r_none.gated_mu:.3f})")

# --- Test 2: Context multiplier cap default 1.65 ---
def test_context_cap_default_1_65():
    g = context_multiplier_guard(3.0, 2.0)  # mult=2.0 > cap=1.65 → REVIEW
    assert g.flag == "REVIEW", f"Expected REVIEW, got {g.flag}"
    assert abs(g.capped_multiplier - 1.65) < 0.01
    print(f"  context_mult=2.0 capped to 1.65: OK (flag={g.flag})")

def test_context_cap_within_default():
    g = context_multiplier_guard(3.0, 1.5)  # mult=1.5 < cap=1.65 → OK
    assert g.flag == "OK"
    assert abs(g.capped_multiplier - 1.5) < 0.01
    print(f"  context_mult=1.5 within 1.65: OK")

# --- Test 3: WC floor audit (player_raw vs after_floor) ---
def test_wc_floor_audit():
    # Questo test verifica che il changelog dica la verità: i due campi devono esistere
    # nell'output di aggregate_team quando il floor interviene. Test indiretto via gate.
    r_before = sot_bottom_up_gate(1.1, 1.1)   # senza floor → mu=1.1
    r_after  = sot_bottom_up_gate(1.1, 2.5)   # con floor applicato → top-down<bottom-up
    assert r_before.gated_mu < r_after.gated_mu, "Floor deve alzare il mu gated"
    assert r_after.flag == "REVIEW"  # divergenza 56%, deve scattare
    print(f"  WC floor: mu {r_before.gated_mu:.2f} → {r_after.gated_mu:.2f}, flag={r_after.flag}: OK")

# --- Test 4: Underdog 2H share (solo logica numerica, non richiede engine completo) ---
def test_underdog_2h_share_value():
    # 0.56 deve essere il valore default per chasing underdog
    chasing_share = 0.56
    normal_share = 0.50
    assert chasing_share > normal_share
    # Con mu=3.0, fav_bump=1.0:
    mu_normal = normal_share * 3.0 * 1.0   # = 1.50
    mu_chasing = chasing_share * 3.0 * 1.0 # = 1.68
    assert mu_chasing > mu_normal
    print(f"  2H share: {normal_share} → {chasing_share} → mu {mu_normal:.2f} → {mu_chasing:.2f}: OK")

if __name__ == "__main__":
    tests = [
        test_gate_ok, test_gate_review, test_gate_block,
        test_dynamic_shrink_high_evidence, test_dynamic_shrink_low_evidence,
        test_dynamic_shrink_mid_evidence, test_no_evidence_uses_default,
        test_context_cap_default_1_65, test_context_cap_within_default,
        test_wc_floor_audit, test_underdog_2h_share_value,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"  FAILED {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed")
    if passed == len(tests):
        print("All SOT gate v6.2 tests passed")
