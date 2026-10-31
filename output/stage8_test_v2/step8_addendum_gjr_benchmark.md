# Step 8 addendum — GJR-GARCH benchmark on the test partition (pre-declared)

**Status:** approved by the user on 2026-10-28 and committed **before** the test file was
loaded for this purpose. It amends the rule in `step8_test_protocol.md` that the test file
is loaded only by `run_stage8_v2_test_rescore.py`: it may be loaded once more, by
`scratch/run_benchmark_gjr_test.py`, solely to fit and score the benchmark below.
**POST-HOC label applies** (2022–2023 was observed at Gate D and in the Step 8 re-score).

## What is frozen
- Benchmark B5 exactly as in `output/stage7_models_v2/benchmark_gjr_specification.md` and
  `src/models/garch_benchmark.py` at this commit (GJR-GARCH(1,1), constant mean,
  standardised Student-t, `arch` 8.0.0, two-step-ahead density for y_t = r_{t+2}).
- Refit origins and scoring windows identical to the Step 8 test re-score (21-session
  expanding refits from 2010-01-04; first test refit at the last 2021 session).
- B0–B4 and R1 predictions are **not refitted**: they are read from
  `output/stage8_test_v2/test_predictions_clipped.csv` (frozen Step 6 configuration) and
  `test_predictions_unclipped.csv`.

## Comparisons (reported; d > 0 favours the first model)
- **Pre-declared headline: B4 − GJR** on the primary sample (N = 500, 2022-01-03 not scored),
  clipped configuration, one-sided HAC DM with 5 lags, α = 0.05.
- Also reported, without decision: B2 − GJR, B3 − GJR, B1 − GJR, GJR − B0; lags 10/21,
  stationary bootstrap CI, by year and block; prequential scale recalibration; the
  unclipped configuration; N = 501 and N = 495 samples.
