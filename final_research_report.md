# Empirical Evaluation of Latent Regimes in Physical Return Density Forecasting

**Course:** IE 612 (Introduction to Financial Engineering)  
**Document status:** Final research report; Gate D evaluation complete and inconclusive

**Quantitative source:** [Gate D final test report](gate_d_final_test_report.md)
**Protocol:** [Research protocol](research_protocol.md)

## Abstract

This study tests whether causally filtered latent regime probabilities add predictive information to a physical return density forecast already conditioned on option-implied moments and observable historical market features. It uses SPX end-of-day option data from OptionsDX, a six-model comparison ladder, and 21-session expanding walk-forward refits. The operational target is Proposal A, \(y_t=\ln(S_{t+2}/S_{t+1})\). On the primary 2022–2023 evaluation (500 scored origins, with the historically compromised 2022-01-03 origin excluded from scoring), R1 has a mean NLL advantage over B4 of 0.005417 nats per session. The paired Newey–West Diebold–Mariano test is not significant at 5% (one-sided \(p=0.0732\)); the stationary-bootstrap 95% interval is \([-0.001979, 0.013837]\), spanning zero and extending above the +0.010 practical threshold. R1 also has a slightly lower mean CRPS, but its PIT uniformity test rejects at 5%. The evidence does not establish incremental regime value; the simpler B4 remains the parsimonious choice.

## 1. Research question and estimand

The project compares the next target density from a non-regime model, \(p(y_t\mid Q_t,X_t)\) (B4), with a matched model that adds causally filtered regime probabilities, \(p(y_t\mid Q_t,X_t,\pi_t)\) (R1). The target is Proposal A:

\[
y_t=\ln\left(\frac{S_{t+2}}{S_{t+1}}\right).
\]

This target moves the return interval start to the next session, after the date-\(t\) option snapshot, addressing the unresolved 16:00 cash-close versus vendor option timestamp concern. It is a return over the close at \(t+1\) to the close at \(t+2\), forecast from information available at \(t\); it is not the ordinary next-session return \(\ln(S_{t+1}/S_t)\).

The primary paired score difference is \(d_t=\ln p_{R1}(y_t)-\ln p_{B4}(y_t)=NLL_{B4,t}-NLL_{R1,t}\). Positive values favor R1. The primary inferential procedure is a one-sided Diebold–Mariano test with Newey–West HAC standard error (five lags), supported by a stationary block bootstrap.

## 2. Data and features

The raw SPX archive covers 168 monthly bundles from 2010 through 2023. The Gate D audit covered the 24 monthly 2022–2023 bundles: 4,100,693 contract rows, 496 observed exchange sessions, and five isolated missing option sessions. Those five dates were causally forward-filled for option features and flagged. Nine extra option dates were classified as 2022 exchange holidays. The 2022–2023 cash session calendar contains 501 sessions.

The five option-derived inputs \(Q_t\) are `SVIX_30d`, `QSkew_30d`, `QKurt_30d`, `ATM_IV_30d`, and `TermSlope_60_30`. The six historical inputs \(X_t\) are `r_1d`, `r_5d`, `rv_5d`, `rv_20d`, `dsemi_20d`, and `dd_20d`. The primary evaluation uses complete-case supervised pairs as defined by the frozen Stage 7 pipeline; fallback option feature dates are identified separately in the test dataset.

The vendor read-time audit reports 16:00 strings across the audited option snapshots. That string alone does not establish exchange-level quote synchronization. The report therefore records the timing concern and the adopted Proposal A target rather than claiming timestamp-level proof of synchronization.

## 3. Models and evaluation design

All density regressions use the frozen location-scale Student-t implementations and \(\lambda=0.01\) where applicable. The HMM has two states and uses bivariate standardized emissions \([r_{1d},RV_{20d}]\). Model input dimensions below refer to predictor features, not total fitted parameter counts.

| Model | Inputs / architecture | Predictor dimension |
|---|---|---:|
| B0 | Expanding unconditional Gaussian benchmark | 0 |
| B1 | Student-t location-scale model using `rv_20d` | 1 |
| B2 | Student-t regression using all five \(Q_t\) features | 5 |
| B3 | Student-t regression using all six \(X_t\) features | 6 |
| B4 | Matched non-regime Student-t regression using \([Q_t,X_t]\) | 11 |
| R1 | Matched Student-t regression using \([Q_t,X_t,\pi_t]\), with K=2 | 13 |

The models were evaluated across 24 expanding walk-forward refit blocks. At refit origin \(\tau_m\), supervised target labels were restricted to \(t\leq\tau_m-2\); HMM estimation and causal filtering used observable emissions through the applicable date. The primary evaluation excludes the 2022-01-03 scoring origin because the test partition had prior cash-close exposure in Git history. A separate strict sensitivity also excludes that origin from supervised refits. The five quote-gap dates are excluded from the actual-quote scoring subset, but matured labels from earlier forward-filled dates can still enter later refits in that subset.

## 4. Held-out results

### 4.1 Primary run

| Model | Mean NLL | Mean CRPS | PIT KS statistic | PIT KS p-value | Coverage 50% | Coverage 80% | Coverage 95% |
|---|---:|---:|---:|---:|---:|---:|---:|
| B0 | -2.964796 | 0.006743 | 0.0424 | 0.3211 | 0.508 | 0.786 | 0.916 |
| B1 | -3.030097 | 0.006678 | 0.0603 | 0.0507 | 0.414 | 0.722 | 0.932 |
| B2 | -3.054678 | 0.006629 | 0.0762 | 0.0057 | 0.412 | 0.742 | 0.940 |
| B3 | -3.036488 | 0.006687 | 0.0733 | 0.0088 | 0.436 | 0.736 | 0.938 |
| B4 | -3.055344 | 0.006616 | 0.0604 | 0.0500 | 0.438 | 0.750 | 0.940 |
| R1 | -3.060762 | 0.006609 | 0.0628 | 0.0371 | 0.436 | 0.748 | 0.940 |

Lower NLL and CRPS are better. R1 is numerically better on both metrics in this primary sample; the paired comparison does not establish that the NLL difference generalizes. The standard PIT KS p-values are descriptive diagnostics; they do not account for serial dependence in PIT observations. At the 5% nominal level, the reported B4 and R1 PIT p-values are below 0.05 (B4 is borderline at 0.04997; R1 is 0.03711).

For R1 versus B4, \(\bar d=+0.005417\), HAC SE = 0.003731, DM = 1.4521, one-sided \(p=0.0732\), and two-sided \(p=0.1465\). The 2,000-replication stationary bootstrap with mean block length 5 gives a 95% interval of \([-0.001979,+0.013837]\). The point estimate is below +0.010, but the interval does not rule out an effect at or above that threshold.

### 4.2 Sensitivity trajectories

| Evaluation trajectory | N | Mean \(d\) | DM | One-sided p | Bootstrap 95% interval |
|---|---:|---:|---:|---:|---:|
| Primary; Jan 3 origin omitted from scoring | 500 | +0.005417 | 1.4521 | 0.0732 | [-0.001979, +0.013837] |
| Strict sensitivity; Jan 3 origin omitted from scoring and supervised refits | 500 | +0.005506 | 1.5118 | 0.0653 | [-0.002074, +0.013873] |
| Full set, including Jan 3 origin (secondary) | 501 | +0.007257 | 1.8240 | 0.0341 | [-0.000509, +0.015382] |
| Actual-quote scoring subset; refits may include matured gap labels | 495 | +0.005426 | 1.4389 | 0.0751 | [-0.002097, +0.013343] |

The primary and strict sensitivity both remain statistically inconclusive. The full-set one-sided p-value is secondary and does not supersede the pre-specified primary sample; its two-sided p-value is 0.0682 and its bootstrap interval includes zero.

## 5. Integrity, limitations, and conclusion

The test partition was historically exposed to the 2022-01-03 and 2022-01-04 cash closes in commit `cee01a1`; it must not be described as fully untouched. The 2022-01-03 origin is omitted from primary scoring. In the primary prequential run, its matured label enters later supervised refits; the strict sensitivity excludes that origin from supervised refits as well. The strict sensitivity is not a claim that the date was erased from all unsupervised HMM emissions or from prior project knowledge.

Cash closes through 2024-01-03 were retained to mature the final Proposal A targets for 2023-12-28 and 2023-12-29. Closes through 2024-01-09 had previously been retrieved and were truncated from the active cache; that historical access is disclosed. No 2024 option bundles or forecast origins were used. Raw OptionsDX files are not redistributed.

The study is limited to one index and the observed sample, has a documented historical test breach, includes five causally forward-filled option-feature dates, and does not test a portfolio or trading strategy. Proposal A changes the horizon relative to the original next-day target. These limits constrain generalization and claims of economic value.

**Conclusion:** The evaluation does not establish a statistically significant incremental density-forecasting advantage from adding filtered regimes. R1 has a positive but uncertain NLL point estimate; both models have borderline or rejecting standard PIT KS diagnostics, and the bootstrap interval is wide enough to include practically meaningful positive effects. B4 is the more parsimonious choice for this evidence, not a statistically proven superior forecaster. No investment or portfolio-performance conclusion follows.

## Reproducibility artifacts

- Test metrics: `output/stage8_test/test_metrics_summary.json`
- Primary predictions: `output/stage8_test/test_predictions.csv`
- Strict sensitivity predictions: `output/stage8_test/test_predictions_strict_isolation.csv`
- Raw-data audit: `output/stage8_test/raw_data_audit_2022_2023.json`
- HMM diagnostics: `output/stage8_test/hmm_refit_diagnostics_test.json`
- Reproduction instructions and licensing notes: [reproducibility guide](reproducibility_guide.md)
