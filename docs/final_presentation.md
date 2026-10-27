# Stage 9 Course Presentation: Regimes in Physical Return Density Forecasting

> Markdown slide outline. Confirm whether the course requires PPTX or PDF before export. Quantitative results are from `output/stage8_test/test_metrics_summary.json` and the Gate D report.

---

## Slide 1 — Research question

**Do filtered latent market regimes add value to physical return density forecasts?**

Compare the matched non-regime model B4, \(p(y_t\mid Q_t,X_t)\), with R1, \(p(y_t\mid Q_t,X_t,\pi_t)\).

The study tests incremental predictive information. It does not claim a new Q-to-P mapping method or an investable strategy.

---

## Slide 2 — Target and timing

The adopted Proposal A target is:

\[
y_t=\ln(S_{t+2}/S_{t+1}).
\]

Date-\(t\) option and historical features forecast the return from the close at \(t+1\) to the close at \(t+2\). This shifts the target window beyond the known 16:00 cash / vendor timestamp ambiguity.

---

## Slide 3 — Data and disclosures

- SPX OptionsDX archive: 168 monthly bundles, 2010–2023.
- Gate D audited all 24 test bundles: 4,100,693 contract rows.
- 501 expected cash sessions; options observed on 496; five isolated option gaps were causally forward-filled and flagged.
- Nine extra option dates were 2022 exchange holidays.
- The test partition has historical cash-close exposure in commit `cee01a1`; the primary score excludes the 2022-01-03 origin.

---

## Slide 4 — Predictor features

**Option-derived \(Q_t\), five inputs:** `SVIX_30d`, `QSkew_30d`, `QKurt_30d`, `ATM_IV_30d`, `TermSlope_60_30`.

**Historical \(X_t\), six inputs:** `r_1d`, `r_5d`, `rv_5d`, `rv_20d`, `dsemi_20d`, `dd_20d`.

---

## Slide 5 — Model ladder

| Model | Inputs |
|---|---|
| B0 | Expanding unconditional Gaussian |
| B1 | Student-t location-scale on `rv_20d` |
| B2 | Student-t regression on five Q features |
| B3 | Student-t regression on six X features |
| B4 | Student-t regression on Q and X (11 inputs) |
| R1 | Matched B4 regression plus two filtered regime probabilities (13 inputs) |

---

## Slide 6 — Causal evaluation design

- Two-state Gaussian HMM with standardized emissions \([r_{1d},RV_{20d}]\).
- Forward-filtered probabilities only; no Viterbi or smoothing in test forecasts.
- Expanding refit every 21 sessions: 24 test refit blocks.
- Supervised labels at refit \(\tau_m\): \(t\leq\tau_m-2\).
- Frozen Stage 7 choices: K=2, \(\lambda=0.01\), Student-t density regression.

---

## Slide 7 — Primary test result

**500 scored origins**, excluding the Jan 3, 2022 origin.

| Measure | B4 | R1 |
|---|---:|---:|
| Mean NLL | -3.055344 | -3.060762 |
| Mean CRPS | 0.006616 | 0.006609 |
| 95% interval coverage | 94.0% | 94.0% |
| PIT KS p-value | 0.04997 | 0.03711 |

Lower NLL and CRPS are better. R1 is numerically lower on both, but the paired NLL result is not statistically significant.

---

## Slide 8 — Primary inference

For \(d_t=NLL_{B4,t}-NLL_{R1,t}\):

- Mean \(\bar d=+0.005417\) nats/session.
- Newey–West HAC SE = 0.003731; DM = 1.4521.
- One-sided \(p=0.0732\); two-sided \(p=0.1465\).
- Stationary bootstrap (2,000 replicates, mean block length 5): 95% CI \([-0.001979,+0.013837]\).

The interval spans zero and extends above the +0.010 practical threshold. The data neither establishes an R1 gain nor rules out a gain of that magnitude.

---

## Slide 9 — Sensitivity checks

| Trajectory | N | Mean difference | One-sided p | 95% bootstrap CI |
|---|---:|---:|---:|---:|
| Primary, Jan 3 omitted from scoring | 500 | +0.005417 | 0.0732 | [-0.001979, +0.013837] |
| Jan 3 omitted from scoring and supervised refits | 500 | +0.005506 | 0.0653 | [-0.002074, +0.013873] |
| Full test including Jan 3 (secondary) | 501 | +0.007257 | 0.0341 | [-0.000509, +0.015382] |
| Actual-quote scoring subset | 495 | +0.005426 | 0.0751 | [-0.002097, +0.013343] |

The primary and strict sensitivity remain inconclusive. The full-set result is secondary and its interval still spans zero.

---

## Slide 10 — Calibration and regime diagnostics

- Primary 50/80/95% coverage: B4 = 43.8/75.0/94.0%; R1 = 43.6/74.8/94.0%.
- Standard PIT KS tests reject uniformity at 5% for B4 (p=0.04997) and R1 (p=0.03711); interpret as descriptive tests that do not adjust for serial dependence.
- Across 24 HMM refits, minimum expected state dwell was 45.19 sessions and minimum training argmax occupancy was 29.26%; all passed the protocol thresholds.

---

## Slide 11 — Limitations

- Historically compromised test partition; disclosed and handled with primary exclusion plus a strict supervised-refit sensitivity.
- Five isolated quote gaps use flagged causal forward-fills; actual-quote subset removes these from scoring but does not remove matured gap labels from all later refits.
- Vendor `16:00` strings do not prove exchange-level synchronization.
- Single index, one observed test period, and no portfolio or transaction-cost evaluation.

---

## Slide 12 — Conclusion

The held-out test does **not** establish a statistically significant incremental advantage from latent regime features. R1's positive NLL point estimate is uncertain, and the confidence interval is compatible with both no gain and a practically meaningful positive effect.

B4 is preferred for parsimony on the available evidence; it is not proven statistically superior. No investment-performance claim is made.

---

## Slide 13 — Reproducibility and remaining course checks

- Predictions, metrics, raw-data audit, and HMM diagnostics are saved in `output/stage8_test/`.
- See `reproducibility_guide.md` for commands and data restrictions.
- Still confirm rubric, report format/page limit, required slide export, portfolio requirement, and submission portal with the instructor.
