# GJR-GARCH benchmark — specification (pre-declared)

**Status:** written and committed on 2026-10-28 before the benchmark was fitted, after the
user agreed to add standard benchmarks only if necessary and cheap (no data downloads).
Validation 2020–2021 only. Scoring it on 2022–2023 would be a new look at the test
partition and requires separate user approval and an addendum to the Step 8 protocol.

## Model (B5: GJR-t)
- Daily log returns r_t = `r_1d` (= ln S_t / S_{t−1}) from the committed Stage 7 datasets,
  scaled by 100.
- Constant mean, GJR-GARCH(1,1) variance (Glosten, Jagannathan & Runkle 1993), standardised
  Student-t innovations; Python `arch` 8.0.0, `arch_model(..., mean='Constant', vol='GARCH',
  p=1, o=1, q=1, dist='t')`.
- Refit at the same 21-session origins τ_b as B0–R1 (expanding window from 2010-01-04),
  parameters estimated on r_0 … r_τ only (the same information as the supervised models,
  whose latest label uses S_τ).
- Forecast for origin t (target y_t = ln S_{t+2}/S_{t+1} = r_{t+2}): two-step-ahead forecast
  from information through r_t with parameters frozen at τ_b; predictive density
  Student-t with location μ, degrees of freedom ν and scale √(h_{t+2|t}·(ν−2)/ν).
- A fit counts as converged when `arch` reports convergence_flag = 0; otherwise the run is
  invalid.

## Comparisons (validation, 494 scored rows; d > 0 favours the first model)
Reported for the Step 6 adopted (clipped) configuration and the Step 5 (unclipped) one:
B4 − GJR, B2 − GJR, B3 − GJR, B1 − GJR, GJR − B0. Mean d, HAC DM (lags 5/10/21),
stationary bootstrap CI, by year and block, excluding 2020-03-01 … 2020-04-30, with and
without the Step 7 prequential scale recalibration. Descriptive; no adoption decision.
