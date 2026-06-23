"""
sot_gate.py — coded SOT volume controls for Jump Probability Cup.

Purpose
-------
This module turns pipeline v1.3/v1.4 SOT rules into executable checks:

SOT-1  Bottom-up gate: compare top-down SOT mu with player bottom-up SOT mu.
SOT-2  Lambda coherence: derive/check implied lambdas across correlated SOT props.
SOT-3  Single-match shrinkage: MD1/top-down evidence is directional, not a baseline.
SOT-4  Relative 2H SOT data gate: no hard caps, but >60% requires bottom-up support.
SOT-5  Context multiplier double-counting guard: cap context product unless hard-data override.

Important: these are gates/audits, not blind optimizers. A REVIEW/BLOCK flag means
"do not submit without explanation", not "the number is impossible".
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from distributions import clamp, negbin_cdf, negbin_ge, negbin_pmf, prob_a_greater_b_nb


@dataclass
class SOTGateResult:
    mu_topdown: float
    mu_bottomup: float
    divergence: float
    gated_mu: float
    flag: str                    # OK | REVIEW | BLOCK
    note: str
    hard_data_override: bool = False


@dataclass
class ContextMultiplierGuard:
    raw_mu: float
    multiplier: float
    max_multiplier: float
    capped_multiplier: float
    capped_mu: float
    flag: str                    # OK | REVIEW
    note: str


@dataclass
class SOTThresholdAudit:
    probability: float
    threshold: int
    alpha: float
    gate: SOTGateResult
    context_guard: Optional[ContextMultiplierGuard] = None
    notes: List[str] = field(default_factory=list)


@dataclass
class SOTRelativeAudit:
    probability: float
    mu_team_2h: float
    mu_opp_2h: float
    alpha_team: float
    alpha_opp: float
    team_gate: SOTGateResult
    opp_gate: SOTGateResult
    flag: str                    # OK | REVIEW | BLOCK
    notes: List[str] = field(default_factory=list)


@dataclass
class CoherenceIssue:
    severity: str                # INFO | REVIEW | BLOCK
    message: str


def _safe_hi(*values: float) -> float:
    return max([abs(float(v)) for v in values] + [1e-9])


def relative_divergence(a: float, b: float) -> float:
    """Symmetric relative divergence: |a-b| / max(|a|, |b|, eps)."""
    return abs(float(a) - float(b)) / _safe_hi(a, b)


def sot_bottom_up_gate(
    mu_topdown: float,
    mu_bottomup: float,
    *,
    divergence_threshold: float = 0.30,
    block_threshold: float = 0.60,
    shrink_to_bottomup: float = 0.65,
    evidence_score: Optional[float] = None,
    hard_data_override: bool = False,
    min_mu: float = 0.01,
) -> SOTGateResult:
    """Compare top-down and bottom-up SOT lambdas and return an audited mu.

    - If coherent (<= divergence_threshold), use the average of the two.
    - If divergent, shrink toward bottom-up.
    - If very divergent (> block_threshold), flag BLOCK unless hard_data_override=True.

    hard_data_override should only be set by an explicit external finding, e.g.
    official lineup + market/player evidence explaining why player bottom-up is too low.
    """
    mt = max(float(mu_topdown), min_mu)
    mb = max(float(mu_bottomup), min_mu)
    div = relative_divergence(mt, mb)
    # Dynamic shrink based on evidence quality (Claude fix #1).
    # evidence_score=1.0 (official lineup, fresh data) → shrink 0.75 (trust bottom-up more)
    # evidence_score=0.0 (estimated, stale data) → shrink 0.55
    # None → use the static default (backward compatible)
    if evidence_score is not None:
        shrink_to_bottomup = 0.55 + 0.20 * max(0.0, min(1.0, float(evidence_score)))

    if div <= divergence_threshold:
        gated = 0.5 * (mt + mb)
        return SOTGateResult(
            mu_topdown=mt,
            mu_bottomup=mb,
            divergence=div,
            gated_mu=gated,
            flag="OK",
            note=f"SOT gate OK: top-down and bottom-up differ by {div*100:.1f}%.",
            hard_data_override=hard_data_override,
        )

    gated = shrink_to_bottomup * mb + (1.0 - shrink_to_bottomup) * mt
    if hard_data_override:
        # Keep the shrink, but do not block.  The override still leaves an audit trail.
        flag = "REVIEW"
        note = (
            f"SOT gate divergence {div*100:.1f}% > {divergence_threshold*100:.0f}%, "
            f"but hard_data_override=True. Using bottom-up anchored mu={gated:.2f}."
        )
    else:
        flag = "BLOCK" if div > block_threshold else "REVIEW"
        note = (
            f"SOT gate {flag}: top-down={mt:.2f}, bottom-up={mb:.2f}, "
            f"divergence={div*100:.1f}%. Using bottom-up anchored mu={gated:.2f}."
        )
    return SOTGateResult(mt, mb, div, gated, flag, note, hard_data_override)


def context_multiplier_guard(
    raw_bottomup_mu: float,
    context_multiplier: float,
    *,
    max_multiplier: float = 1.65,
    hard_data_override: bool = False,
) -> ContextMultiplierGuard:
    """Guard against double-counting team strength after player bottom-up.

    If player bottom-up already represents the actual starters, very large attack/defense/
    possession multipliers may double-count team quality.  This caps the context product
    unless an explicit hard-data override is set.
    """
    raw = max(float(raw_bottomup_mu), 0.0)
    mult = max(float(context_multiplier), 0.0)
    max_mult = max(float(max_multiplier), 0.01)
    if hard_data_override or mult <= max_mult:
        return ContextMultiplierGuard(
            raw_mu=raw,
            multiplier=mult,
            max_multiplier=max_mult,
            capped_multiplier=mult,
            capped_mu=raw * mult,
            flag="OK",
            note=f"Context multiplier OK: {mult:.2f}x.",
        )
    return ContextMultiplierGuard(
        raw_mu=raw,
        multiplier=mult,
        max_multiplier=max_mult,
        capped_multiplier=max_mult,
        capped_mu=raw * max_mult,
        flag="REVIEW",
        note=(
            f"Context multiplier REVIEW: {mult:.2f}x > cap {max_mult:.2f}x. "
            f"Using capped mu={raw*max_mult:.2f}; require hard-data justification to exceed."
        ),
    )


def sot_threshold_prob(mu: float, threshold: int, alpha: float = 0.22) -> float:
    """P(SOT >= threshold) using the model's Negative Binomial, never Poisson."""
    return negbin_ge(int(threshold), max(float(mu), 1e-9), max(float(alpha), 1e-8))


def sot_threshold_audit(
    mu_topdown: float,
    mu_bottomup: float,
    threshold: int,
    *,
    alpha: float = 0.22,
    divergence_threshold: float = 0.30,
    block_threshold: float = 0.60,
    shrink_to_bottomup: float = 0.65,
    hard_data_override: bool = False,
) -> SOTThresholdAudit:
    gate = sot_bottom_up_gate(
        mu_topdown,
        mu_bottomup,
        divergence_threshold=divergence_threshold,
        block_threshold=block_threshold,
        shrink_to_bottomup=shrink_to_bottomup,
        hard_data_override=hard_data_override,
    )
    p = sot_threshold_prob(gate.gated_mu, threshold, alpha)
    return SOTThresholdAudit(
        probability=p,
        threshold=int(threshold),
        alpha=float(alpha),
        gate=gate,
        notes=[gate.note],
    )


def sot_relative_2h_audit(
    team_mu_topdown_total: float,
    team_mu_bottomup_total: float,
    opp_mu_topdown_total: float,
    opp_mu_bottomup_total: float,
    *,
    team_2h_share: float = 0.50,
    opp_2h_share: float = 0.50,
    team_2h_bump: float = 1.0,
    opp_2h_bump: float = 1.0,
    alpha_team: float = 0.30,
    alpha_opp: float = 0.30,
    high_prob_review_threshold: float = 0.60,
    divergence_threshold: float = 0.30,
    block_threshold: float = 0.60,
    hard_data_override: bool = False,
) -> SOTRelativeAudit:
    """Audit P(team > opponent in 2H SOT).

    No hard cap is applied.  If the resulting probability is >60%, it is allowed only
    if both team lambdas pass the bottom-up gate or an explicit hard-data override exists.
    """
    tg = sot_bottom_up_gate(
        team_mu_topdown_total,
        team_mu_bottomup_total,
        divergence_threshold=divergence_threshold,
        block_threshold=block_threshold,
        hard_data_override=hard_data_override,
    )
    og = sot_bottom_up_gate(
        opp_mu_topdown_total,
        opp_mu_bottomup_total,
        divergence_threshold=divergence_threshold,
        block_threshold=block_threshold,
        hard_data_override=hard_data_override,
    )
    mu_t_2h = max(tg.gated_mu * team_2h_share * team_2h_bump, 1e-9)
    mu_o_2h = max(og.gated_mu * opp_2h_share * opp_2h_bump, 1e-9)
    p = prob_a_greater_b_nb(mu_t_2h, mu_o_2h, alpha_team, alpha_opp, max_count=60)

    notes = [tg.note, og.note]
    flags = {tg.flag, og.flag}
    flag = "BLOCK" if "BLOCK" in flags else ("REVIEW" if "REVIEW" in flags else "OK")

    if p > high_prob_review_threshold and not hard_data_override:
        if tg.flag != "OK" or og.flag != "OK":
            flag = "BLOCK" if flag == "BLOCK" else "REVIEW"
            notes.append(
                f"Relative 2H SOT data gate: probability={p*100:.1f}% > "
                f"{high_prob_review_threshold*100:.0f}% but bottom-up gates are not both OK."
            )
        else:
            notes.append(
                f"Relative 2H SOT > {high_prob_review_threshold*100:.0f}% is permitted: "
                f"both bottom-up gates are OK."
            )

    return SOTRelativeAudit(
        probability=p,
        mu_team_2h=mu_t_2h,
        mu_opp_2h=mu_o_2h,
        alpha_team=alpha_team,
        alpha_opp=alpha_opp,
        team_gate=tg,
        opp_gate=og,
        flag=flag,
        notes=notes,
    )


def implied_mu_for_threshold_nb(
    probability: float,
    threshold: int,
    *,
    alpha: float = 0.22,
    lo: float = 0.001,
    hi: float = 30.0,
    tol: float = 1e-5,
    max_iter: int = 80,
) -> float:
    """Invert P(NB(mu, alpha) >= threshold) by binary search."""
    p = clamp(float(probability), 1e-6, 1 - 1e-6)
    k = int(threshold)
    a, b = float(lo), float(hi)
    for _ in range(max_iter):
        mid = 0.5 * (a + b)
        pmid = sot_threshold_prob(mid, k, alpha)
        if abs(pmid - p) < tol:
            return mid
        if pmid < p:
            a = mid
        else:
            b = mid
    return 0.5 * (a + b)


def p_one_plus(mu: float, alpha: float = 0.22) -> float:
    return sot_threshold_prob(mu, 1, alpha)


def p_two_plus(mu: float, alpha: float = 0.22) -> float:
    return sot_threshold_prob(mu, 2, alpha)


def both_1plus_probability(mu_a: float, mu_b: float, alpha_a: float = 0.30, alpha_b: float = 0.30) -> float:
    """Independent approximation for P(A>=1 and B>=1)."""
    return p_one_plus(mu_a, alpha_a) * p_one_plus(mu_b, alpha_b)


def sot_lambda_coherence_check(
    *,
    team_mus_2h: Dict[str, float] | None = None,
    team_mus_total: Dict[str, float] | None = None,
    props: Sequence[Dict[str, object]] = (),
    alpha_2h: float = 0.30,
    alpha_total: float = 0.22,
    divergence_threshold: float = 0.30,
) -> List[CoherenceIssue]:
    """General coherence checks across correlated SOT props.

    Supported prop dictionaries:
      {'type':'both_1plus_2h', 'teams':('A','B'), 'prob':0.52}
      {'type':'team_threshold_2h', 'team':'A', 'threshold':2, 'prob':0.22}
      {'type':'team_threshold_total', 'team':'A', 'threshold':6, 'prob':0.82}
      {'type':'relative_2h', 'team':'A', 'opp':'B', 'prob':0.63}

    This returns warnings instead of mutating probabilities.
    """
    issues: List[CoherenceIssue] = []
    mus2 = team_mus_2h or {}
    must = team_mus_total or {}

    # Bounds and implied-lambda checks.
    for pr in props:
        p = float(pr.get("prob", 0.0))
        typ = str(pr.get("type", ""))

        if typ == "both_1plus_2h":
            teams = tuple(pr.get("teams", ()))
            if len(teams) != 2:
                continue
            a, b = str(teams[0]), str(teams[1])
            if a in mus2 and b in mus2:
                pa, pb = p_one_plus(mus2[a], alpha_2h), p_one_plus(mus2[b], alpha_2h)
                if p > min(pa, pb) + 0.02:
                    issues.append(CoherenceIssue(
                        "BLOCK",
                        f"P(both 1+ 2H)={p*100:.1f}% exceeds marginal bound min({a}={pa*100:.1f}%, {b}={pb*100:.1f}%).",
                    ))
                independent = pa * pb
                div = relative_divergence(p, independent)
                if div > divergence_threshold:
                    issues.append(CoherenceIssue(
                        "REVIEW",
                        f"P(both 1+ 2H)={p*100:.1f}% diverges from independent lambda estimate {independent*100:.1f}% by {div*100:.1f}%.",
                    ))

        elif typ in {"team_threshold_2h", "team_threshold_total"}:
            team = str(pr.get("team", ""))
            thr = int(pr.get("threshold", 1))
            alpha = alpha_2h if typ.endswith("2h") else alpha_total
            base_mu = (mus2 if typ.endswith("2h") else must).get(team)
            if base_mu is not None:
                implied = implied_mu_for_threshold_nb(p, thr, alpha=alpha)
                div = relative_divergence(implied, base_mu)
                if div > divergence_threshold:
                    issues.append(CoherenceIssue(
                        "REVIEW",
                        f"{team} {thr}+ {'2H' if typ.endswith('2h') else 'total'} SOT prob={p*100:.1f}% implies mu={implied:.2f}, but sheet/model mu={base_mu:.2f} (div={div*100:.1f}%).",
                    ))

        elif typ == "relative_2h":
            team = str(pr.get("team", ""))
            opp = str(pr.get("opp", ""))
            if team in mus2 and opp in mus2:
                model_p = prob_a_greater_b_nb(mus2[team], mus2[opp], alpha_2h, alpha_2h, max_count=60)
                div = relative_divergence(p, model_p)
                if div > divergence_threshold:
                    issues.append(CoherenceIssue(
                        "REVIEW",
                        f"P({team}>{opp} 2H SOT)={p*100:.1f}% diverges from lambda model {model_p*100:.1f}% by {div*100:.1f}%.",
                    ))

    return issues


def underdog_sot_variance_guard(
    probability: float,
    *,
    prop_description: str,
    underdog_has_min_offense: bool,
    threshold: int,
    period: str = "2H",
    soft_floor: float = 0.25,
) -> Optional[CoherenceIssue]:
    """Warning, not an automatic floor, for low underdog SOT-half probabilities."""
    if underdog_has_min_offense and threshold >= 2 and period.upper() in {"2H", "1H", "HALF"} and probability < soft_floor:
        return CoherenceIssue(
            "REVIEW",
            f"Underdog SOT variance guard: {prop_description} is {probability*100:.1f}% below soft floor {soft_floor*100:.0f}%. Justify with bottom-up/lineup data before submitting.",
        )
    return None
