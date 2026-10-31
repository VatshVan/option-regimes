# Step 7 specification — width-controlled comparison and R1 ablations (pre-declared)

**Status:** written and committed on 2026-10-28 before any Step 7 result was computed,
under the user's instruction to continue step by step with the handoff plan.
Validation data (2020–2021) only; the 2022–2023 test file is not loaded.

## Configuration
The Step 6 adopted configuration: λ = 1e-4, K = 2, converged fits, scoring-time clipping
of scaled Q and X features to training [0.5 %, 99.5 %] quantiles
(`output/stage7_models_v2/step6_predictions_a_clip.csv`). The Step 5 unclipped baseline is
reported alongside.

## 1. Prequential scale recalibration (applied identically to B0–B4 and R1)
For each model and each 21-session refit block *b* with refit origin τ_b, a common scale
factor c_b multiplies the predicted scale σ_t for every row scored in block *b*:

- c_b = argmax_c Σ log f(y_s; μ_s, c·σ_s, ν_s) over **previously scored validation rows s
  with s ≤ τ_b − 2** (labels matured at τ_b, the same cut-off as the supervised refits);
  f is Student-t for B1–R1 and Gaussian for B0.
- c is searched on [0.25, 4] (bounded scalar maximisation); c_b = 1 when fewer than 21
  eligible rows exist (so the first block is never recalibrated).
- Recalibrated score: log f(y_t; μ_t, c_b·σ_t, ν_t). μ and ν are unchanged.
- No outcome from block *b* or later enters c_b.

Q1, Q2a, Q2b, Q3 and R1 − B4 are reported with and without recalibration, for both the
clipped (adopted) and unclipped configurations, together with the fitted c_b paths.

## 2. R1 ablations (research_protocol.md §7.2, Ablations 2 and 3)
Run in the adopted configuration with the R1 design unchanged apart from the π columns:
- **Shuffled π:** at each refit, the π rows of the supervised training set are randomly
  permuted across dates, and the π rows of the scoring block are permuted within the
  block (NumPy default_rng seeded with τ_b). Diagnostic only; never used to select a model.
- **Static RV threshold:** π₁,t = 𝟙(RV₂₀,t > median of RV₂₀ over the refit's supervised
  training rows), π₀,t = 1 − π₁,t, for training and scoring rows.

Reported: each ablation versus R1 and versus B4 (mean d, HAC DM lags 5/10/21, bootstrap CI,
ex-stress), with and without recalibration.
