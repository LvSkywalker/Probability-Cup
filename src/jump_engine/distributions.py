"""Small probability utilities used by the Jump Probability Cup model layer.

No external dependency is required.  The functions are intentionally simple and
transparent: they are good enough for a first production MVP and easy to audit.
"""
from __future__ import annotations

import math
from typing import Tuple


def clamp(p: float, lo: float = 1e-6, hi: float = 1 - 1e-6) -> float:
    return max(lo, min(hi, p))


def poisson_pmf(k: int, lam: float) -> float:
    if k < 0:
        return 0.0
    lam = max(lam, 1e-12)
    return math.exp(-lam + k * math.log(lam) - math.lgamma(k + 1))


def poisson_cdf(k: int, lam: float) -> float:
    if k < 0:
        return 0.0
    return sum(poisson_pmf(i, lam) for i in range(k + 1))


def poisson_ge(k: int, lam: float) -> float:
    return clamp(1.0 - poisson_cdf(k - 1, lam))


def negbin_pmf(x: int, mu: float, alpha: float) -> float:
    """Negative binomial PMF with Var[X] = mu + alpha * mu^2.

    alpha close to 0 approximates Poisson.  We parameterize via r and p:
    r = 1/alpha, p = r/(r+mu).  PMF = C(x+r-1,x) p^r (1-p)^x.
    """
    if x < 0:
        return 0.0
    mu = max(mu, 1e-12)
    alpha = max(alpha, 1e-8)
    r = 1.0 / alpha
    p = r / (r + mu)
    log_pmf = (
        math.lgamma(x + r)
        - math.lgamma(r)
        - math.lgamma(x + 1)
        + r * math.log(p)
        + x * math.log1p(-p)
    )
    return math.exp(log_pmf)


def negbin_cdf(k: int, mu: float, alpha: float) -> float:
    if k < 0:
        return 0.0
    return clamp(sum(negbin_pmf(i, mu, alpha) for i in range(k + 1)))


def negbin_ge(k: int, mu: float, alpha: float) -> float:
    return clamp(1.0 - negbin_cdf(k - 1, mu, alpha))


def prob_a_greater_b_nb(mu_a: float, mu_b: float, alpha_a: float, alpha_b: float, max_count: int = 80) -> float:
    """P(A > B) for independent negative binomials by finite summation."""
    p = 0.0
    cdf_b_cache = []
    for a in range(max_count + 1):
        cdf_b_cache.append(negbin_cdf(a - 1, mu_b, alpha_b))
    for a in range(max_count + 1):
        p += negbin_pmf(a, mu_a, alpha_a) * cdf_b_cache[a]
    return clamp(p)


def poisson_match_probs(lambda_for: float, lambda_against: float, max_goals: int = 10) -> Tuple[float, float, float]:
    """Return P(win), P(draw), P(loss) from two independent Poisson goal models."""
    p_win = p_draw = p_loss = 0.0
    for gf in range(max_goals + 1):
        pgf = poisson_pmf(gf, lambda_for)
        for ga in range(max_goals + 1):
            p = pgf * poisson_pmf(ga, lambda_against)
            if gf > ga:
                p_win += p
            elif gf == ga:
                p_draw += p
            else:
                p_loss += p
    # Tail mass is tiny for realistic soccer lambdas; normalize for safety.
    s = p_win + p_draw + p_loss
    if s > 0:
        p_win, p_draw, p_loss = p_win / s, p_draw / s, p_loss / s
    return clamp(p_win), clamp(p_draw), clamp(p_loss)


def poisson_total_le(lambda_a: float, lambda_b: float, threshold: int) -> float:
    """For independent Poissons, total is Poisson(lambda_a + lambda_b)."""
    return clamp(poisson_cdf(threshold, lambda_a + lambda_b))
