# Step 8 — post-hoc test re-score protocol (pre-declared)

**Status:** approved by the user on 2026-10-28 (option 1) and committed **before** the
2022–2023 test features were loaded in this branch.

**Post-hoc label (mandatory in every use of these results):** the 2022–2023 test partition
was already scored at Gate D (`output/stage8_test/`, commit history before `7f06ab7`), and its
outcomes were known when the modelling fixes were designed. These results are a post-hoc
re-score under a configuration frozen on validation data; they are not an untouched
confirmatory test. A confirmatory claim requires data that has not been used (e.g. 2024+).

## Frozen configuration (fixed on validation, Steps 3–6; no changes after loading test data)
- Models B0, B1, B2, B3, B4, R1 exactly as in `src/models/` at the commit of this file.
- Converged float64 fits (L-BFGS + Newton polish; convergence gate: every fit and every HMM
  fit converged, else the run is invalid).
- λ = 1e-4, K = 2, expanding window from 2010-01-04, 21-session refits, labels t ≤ τ − 2.
- Adopted Step 6 control: scoring-time clipping of scaled Q and X features to the refit's
  training [0.5 %, 99.5 %] quantiles.
- Training at each test refit includes all matured development and validation labels
  (standard prequential), as at Gate D.

## Samples (Gate D definitions)
- **Primary:** N = 500 test origins, 2022-01-03 excluded from scoring.
- Secondary: full N = 501; actual-quote subset N = 495 (also excluding 2022-05-11, 2022-06-17,
  2022-06-24, 2022-12-16, 2023-01-03); strict isolation N = 500 (2022-01-03 also removed from
  every supervised training set).

## Primary comparison and test (decided now)
- **Q1: B4 vs B3**, d_t = log p_B4(y_t) − log p_B3(y_t) on the primary sample,
  frozen configuration (clipped, no recalibration).
- One-sided Diebold–Mariano test of mean d > 0 with Newey–West HAC, **5 lags**, α = 0.05.
  Also reported, not used for the decision: lags 10 and 21, stationary block bootstrap 95 %
  CI (2000 reps, mean block 5, seed 42), by year and by 21-session block.

## Secondary (reported, no decision attached)
- Q2a B2 vs B1, Q2b B2 vs B0, Q3 B3 vs B1, R1 vs B4.
- Each comparison also: unclipped configuration (Step 5), prequential scale recalibration
  (Step 7 specification, factors from matured past test rows only), all secondary samples.
- Per-model NLL, CRPS, PIT KS (per-row parameters), 50/80/95 % coverage, max predicted σ.
- Side-by-side with the Gate D numbers in `output/stage8_test/test_metrics_summary.json`.

## Rules
- The test file is loaded only by `scratch/run_stage8_v2_test_rescore.py`, once, after this
  file is committed. No model, feature, λ, control or sample change is made in response to
  test results; any later modelling is developed on validation and cannot be re-confirmed
  on 2022–2023.
- Outputs go to `output/stage8_test_v2/`; `output/stage8_test/` is not modified.
