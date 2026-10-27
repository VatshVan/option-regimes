# Step 6 decision rule — sigma-extrapolation controls (pre-declared)

**Status:** proposed by Claude and approved by the user on 2026-10-28, and committed
before any Step 6 control was run. Validation data (2020–2021) only; the 2022–2023
test file is not loaded.

## Baseline
Step 5 primary run: `output/stage7_models_v2/validation_predictions_primary_v2.csv`
(λ = 1e-4, K = 2, converged fits, 494 scored rows).

## Controls (one change at a time, each relative to the baseline)
- **(a) Scoring-time clipping:** each scaled Q and X feature is clipped, at scoring
  time only, to the [0.5 %, 99.5 %] quantiles of that feature in the refit's own
  supervised training rows. HMM probabilities are not clipped. Applies identically
  to B2, B3, B4 and R1.
- **(b) Collinearity reduction:** run only if (a) fails criterion 1. Each variant is
  run on its own: (b1) drop ATM_IV_30d from Q; (b2) drop QKurt_30d from Q. Applies
  to every model using Q (B2, B4, R1).
- **(c) R1 with π₁ only:** removes the exact singularity π₀ + π₁ = 1 of the R1 design.
  Always run and reported alongside. If a control is adopted, (c) is also run
  combined with that control.

B0 and B1 are unaffected by every control.

## Adoption criteria (a control is adopted only if both hold)
1. **Plausible scale:** the maximum predicted daily σ over origins dated
   2020-03-01 … 2020-04-30 is below 0.10 for every model the control applies to.
2. **No material harm:** for each of B2, B3 and B4 that the control changes:
   - validation NLL(control) − NLL(baseline) ≤ 0.005 nats, **and**
   - the paired DM test of d_t = log p_control − log p_baseline (HAC, 5 lags) does not
     reject at 5 % in the "worse" direction (one-sided test of mean d < 0).

The rule never looks at Q1 (B4 − B3), Q2, Q3 or R1 − B4, so no control can be
adopted because it changes a research comparison.

## Reporting
Q1, Q2a, Q2b, Q3 and R1 − B4 are reported under the baseline and under every control
that was run (adopted or not), labelled accordingly; the adoption decision for each
control is recorded together with the criterion values.
