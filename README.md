# IE 612: Physical Return Density Forecasting

This repository contains the research protocol, code, derived datasets, Gate A–D audit records, and final course materials for an SPX options study of whether causally filtered latent regimes add value to physical return density forecasts.

## Final status

Gate D evaluation is complete. Its primary result is **inconclusive**: the regime model R1 does not establish a statistically significant improvement over matched non-regime model B4. B4 is favored for parsimony on this evidence; it is not proven statistically superior. Course submission details remain to be confirmed with the instructor. See [the final report](final_research_report.md), [the Gate D report](gate_d_final_test_report.md), [the presentation](final_presentation.md), and [the reproducibility guide](reproducibility_guide.md).

## Research design

The target is Proposal A, \(y_t=\ln(S_{t+2}/S_{t+1})\), forecast from date-t information. Option-derived features are `SVIX_30d`, `QSkew_30d`, `QKurt_30d`, `ATM_IV_30d`, and `TermSlope_60_30`. Historical features are `r_1d`, `r_5d`, `rv_5d`, `rv_20d`, `dsemi_20d`, and `dd_20d`.

Models B0–B4 provide unconditional, volatility-only, Q-only, X-only, and combined non-regime benchmarks. R1 uses the same combined inputs as B4 plus two causally filtered HMM regime probabilities. The HMM uses standardized daily return and 20-day realized volatility emissions. Models were evaluated with 21-session expanding refits; supervised labels at refit \(\tau_m\) are limited to \(t\leq\tau_m-2\).

## Primary Gate D result

| Quantity | Result |
|---|---:|
| Scored origins | 500 |
| B4 mean NLL | -3.055344 |
| R1 mean NLL | -3.060762 |
| Mean NLL advantage, B4 minus R1 | +0.005417 nats/session |
| Newey–West DM statistic, 5 lags | 1.4521 |
| One-sided / two-sided p-values | 0.0732 / 0.1465 |
| Stationary bootstrap 95% CI | [-0.001979, +0.013837] |
| B4 / R1 mean CRPS | 0.006616 / 0.006609 |

The bootstrap interval spans zero and extends above the +0.010 practical threshold. R1 has a numerically lower mean NLL and CRPS, but the primary paired test is not significant. The result does not support a claim of established incremental regime value. The test partition has historical cash-close exposure; see Gate D disclosures. No portfolio or trading performance is claimed.

## Repository map

- `research_protocol.md`, `stage5_modeling_specification.md`: design and frozen modeling rules.
- `implementation.md`: project implementation record and gate status.
- `gate_b_audit_report.md`, `gate_c_model_validation_report.md`, `gate_d_final_test_report.md`: audit and evaluation reports.
- `final_research_report.md`, `final_presentation.md`: final research narrative and Markdown slides.
- `reproducibility_guide.md`: commands, hashes, and licensing constraints.
- `src/`: feature, model, and evaluation modules.
- `scratch/`: staged audit and execution scripts.
- `output/stage6_features/`, `output/stage7_models/`, `output/stage8_test/`: derived artifacts and results.
- `Data/`: local raw vendor files; do not redistribute or commit.

## Reproduction

For exact commands, prerequisites, and warnings about scripts that read raw data or rerun estimation, consult [reproducibility_guide.md](reproducibility_guide.md). Raw OptionsDX files must be lawfully obtained and remain local. Running the Stage 7 or Stage 8 execution scripts re-estimates models and may overwrite generated outputs; use the saved artifacts for read-only review.

## Administrative items

Confirm the grading rubric, report format/page limit, required slide export, whether a portfolio exercise is mandatory, and the submission portal with the instructor before submission.
