"""SOT gate tests — v7 (flag-only gate).

Run:  PYTHONPATH=src python3 tests/test_sot_gate.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from jump_engine.sot_gate import (  # noqa: E402
    context_multiplier_guard,
    sot_bottom_up_gate,
    sot_threshold_prob,
)


# --- v7: the gate flags but does not move mu ---------------------------------

def test_gate_ok_does_not_move_mu():
    r = sot_bottom_up_gate(5.0, 4.8)
    assert r.flag == "OK", f"Expected OK, got {r.flag}"
    assert abs(r.gated_mu - 5.0) < 1e-9, "flag-only gate must leave mu at top-down"


def test_gate_review_does_not_move_mu():
    r = sot_bottom_up_gate(7.5, 3.25)
    assert r.flag == "REVIEW"
    assert abs(r.gated_mu - 7.5) < 1e-9, "REVIEW must not silently shrink mu"
    assert r.divergence > 0.30


def test_gate_block_does_not_move_mu():
    r = sot_bottom_up_gate(10.0, 1.0)
    assert r.flag == "BLOCK"
    assert abs(r.gated_mu - 10.0) < 1e-9, "BLOCK must not silently shrink mu"


def test_uruguay_case_is_flagged_not_silently_cut():
    """The MD2 failure: top-down 7.5 from ONE match vs bottom-up 3.25.

    The gate must shout, and must leave the number alone so the human decides.
    """
    r = sot_bottom_up_gate(7.5, 3.25)
    assert r.flag == "REVIEW"
    assert "flag only" in r.note.lower()
    assert abs(r.gated_mu - 7.5) < 1e-9


# --- legacy behaviour still reachable, explicitly -----------------------------

def test_legacy_shrink_still_available_opt_in():
    r = sot_bottom_up_gate(7.5, 3.25, modify_mu=True)
    assert r.gated_mu < 7.5
    expected = 0.65 * 3.25 + 0.35 * 7.5
    assert abs(r.gated_mu - expected) < 0.01


def test_legacy_dynamic_shrink_with_evidence():
    r = sot_bottom_up_gate(7.5, 3.25, evidence_score=1.0, modify_mu=True)
    expected = 0.75 * 3.25 + 0.25 * 7.5  # shrink = 0.55 + 0.20*1.0
    assert abs(r.gated_mu - expected) < 0.01


def test_legacy_ok_branch_averages():
    r = sot_bottom_up_gate(5.0, 4.8, modify_mu=True)
    assert r.flag == "OK"
    assert abs(r.gated_mu - 4.9) < 0.01


# --- context multiplier guard: warns, does not clip ---------------------------

def test_context_guard_flags_without_capping():
    g = context_multiplier_guard(3.0, 2.0)  # 2.0 > advisory 1.65
    assert g.flag == "REVIEW"
    assert abs(g.capped_multiplier - 2.0) < 0.01, "flag-only guard must not clip"
    assert abs(g.capped_mu - 6.0) < 0.01


def test_context_guard_ok_below_advisory():
    g = context_multiplier_guard(3.0, 1.5)
    assert g.flag == "OK"
    assert abs(g.capped_multiplier - 1.5) < 0.01


def test_context_guard_cap_still_available_opt_in():
    g = context_multiplier_guard(3.0, 2.0, enforce_cap=True)
    assert g.flag == "REVIEW"
    assert abs(g.capped_multiplier - 1.65) < 0.01
    assert abs(g.capped_mu - 4.95) < 0.01


# --- distribution sanity ------------------------------------------------------

def test_negbin_not_poisson():
    """SOT is overdispersed. NegBin must sit meaningfully below Poisson in the tail."""
    import math

    mu, k = 7.5, 6
    p_nb = sot_threshold_prob(mu, k, alpha=0.22)
    p_pois = 1.0 - sum(math.exp(-mu) * mu ** i / math.factorial(i) for i in range(k))
    assert p_nb < p_pois, "NegBin tail must be below Poisson"
    assert (p_pois - p_nb) > 0.08, f"expected a material gap, got {p_pois - p_nb:.3f}"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed, failed = 0, []
    for t in tests:
        try:
            t()
            passed += 1
            print(f"  PASS  {t.__name__}")
        except Exception as e:
            failed.append((t.__name__, e))
            print(f"  FAIL  {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
