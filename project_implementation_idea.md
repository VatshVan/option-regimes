# Project Implementation Plan
## Regime-Conditioned Mapping from Option-Implied Risk-Neutral Information to Physical Return Distributions for Portfolio Selection

**Status:** Proposed research implementation; literature review frozen at five core papers  
**Project type:** Empirical quantitative finance / machine learning / portfolio construction  
**Primary objective:** Test whether persistent latent market regimes improve the mapping from option-implied risk-neutral information to the physical distribution of future asset returns, and whether any improvement translates into robust out-of-sample portfolio performance.

---

## 1. Executive Summary

Option prices contain forward-looking information about the market's risk-neutral distribution of future returns. Portfolio decisions, however, depend on the physical distribution of returns that investors actually experience. These distributions are not interchangeable: the risk-neutral measure incorporates risk premia and pricing-kernel effects.

This project will build and evaluate a forecasting pipeline that uses option-implied features to estimate the **physical return distribution**. The proposed extension is to let the mapping vary with a **persistent latent market regime**, rather than relying only on a single static mapping or ordinary observable conditioning.

The central research question is:

> Does explicitly modelling persistent latent regimes improve the out-of-sample estimation of physical return distributions from option-implied information, and does that improvement lead to better portfolio decisions after realistic costs and constraints?

The novelty is a **hypothesis to test, not an established fact**. Prior work already studies option-implied portfolio selection, the relationship between physical and risk-neutral measures, non-Gaussian portfolio models, and neural-network mapping from risk-neutral information to physical densities. The project must therefore compare the proposed regime-conditioned model against strong non-regime baselines and clearly delimit any incremental contribution.

---

## 2. Research Questions and Hypotheses

### Primary research question

Does a persistent latent-regime model improve the mapping

\[
Q\text{-information}_t \longrightarrow \widehat{p}_{t+1}(r)
\]

where \(Q\) denotes risk-neutral information inferred from option prices and \(p\) denotes the physical distribution of future returns?

### Secondary questions

1. Which option-implied moments—volatility, skewness, kurtosis, and tail-risk measures—contain useful information about the physical distribution?
2. Does regime conditioning help beyond nonlinear models that already capture interactions?
3. Are improvements concentrated in particular market states, such as high-volatility or crisis periods?
4. Do better density forecasts translate into improved portfolio risk and return after transaction costs and turnover?
5. Does the model remain useful relative to simple portfolio baselines, not merely relative to a weak statistical benchmark?

### Hypotheses to test

- **H1 — Distributional forecast:** Regime conditioning improves out-of-sample density forecasts over a strong non-regime model.
- **H2 — Regime persistence:** Any gain is not merely due to using current volatility or other observable state variables; persistence contributes incremental information.
- **H3 — Portfolio relevance:** Improved density forecasts lead to better risk-adjusted portfolio performance under pre-specified constraints and costs.
- **H4 — State dependence:** Gains vary by market state and may be larger during stressed periods. This is exploratory unless specified before final testing.

A hypothesis is rejected if it fails on the held-out test data. Portfolio gains alone must not be used to retroactively claim improved density estimation.

---

## 3. Scope and Non-Goals

### In scope

- Extracting option-implied risk-neutral distribution summaries.
- Estimating physical return distributions from historical returns and option-implied features.
- A persistent latent-regime extension.
- Strict time-ordered training, validation, and test evaluation.
- Density forecast metrics and portfolio-level evaluation.
- Ablations, robustness tests, and reproducible artifacts.

### Not initially in scope

- Building a production trading system.
- High-frequency option execution.
- Claiming a new general solution to the \(P\)-to-\(Q\) transformation.
- Assuming a specific regime model is novel merely because it uses an HMM.
- Using a very large neural architecture before simpler baselines are established.
- Optimizing portfolio weights directly against the test sample.
- Assuming risk-neutral moments equal physical expected moments.

---

## 4. Core Literature Pack: Five Papers

The initial literature set is frozen at these five papers. The goal is to extract their methods and limitations before expanding the bibliography.

### Paper 1 — DeMiguel, Plyakha, Uppal & Vilkov (2013 version)

**Title:** *Improving Portfolio Selection Using Option-Implied Volatility and Skewness*

**Role in this project**
- Establishes that option-implied volatility, volatility-risk-premium information, and skewness can improve portfolio selection.
- Provides practical ways to extract model-free implied volatility and skewness from option surfaces.
- Supplies portfolio construction and out-of-sample evaluation precedents.

**Implementation implications**
- Include option-implied volatility and skewness features.
- Use a historical-only portfolio and a simple equal-weight portfolio as benchmarks.
- Evaluate turnover and transaction costs, not just gross Sharpe ratio.
- Do not assume implied correlations automatically improve the covariance estimate.

### Paper 2 — Bianchi & Tassinari

**Title:** *Forward-Looking Portfolio Selection with Multivariate Non-Gaussian Models and the Esscher Transform*

**Role in this project**
- Connects physical (\(P\)) and risk-neutral (\(Q\)) distributions through an Esscher transform.
- Shows why skewness, kurtosis, heavy tails, and multivariate dependence can matter for portfolio risk.
- Provides a principled non-Gaussian portfolio-selection reference.

**Implementation implications**
- Treat the \(P\)-versus-\(Q\) distinction explicitly.
- Include tail-sensitive risk measures, such as expected shortfall/CVaR.
- Use a non-Gaussian benchmark if feasible; do not require a full multivariate NTS/GH implementation in the first milestone.

### Paper 3 — Chernov & Ghysels (2000)

**Title:** *A Study Towards a Unified Approach to the Joint Estimation of Objective and Risk Neutral Measures for the Purpose of Options Valuation*

**Role in this project**
- Establishes an early framework for jointly using underlying-asset and option information to estimate objective and risk-neutral dynamics.
- Highlights latent volatility and the challenges of mapping between the two measures.
- Provides econometric context for why the mapping cannot be treated as a trivial identity.

**Implementation implications**
- Compare an options-only feature set with an options-plus-historical-state feature set.
- Keep the distinction between observable features and latent-state estimates explicit.
- Use this paper as conceptual/econometric grounding rather than attempting to reproduce its full EMM/SNP estimation procedure initially.

### Paper 4 — Bali, Beckmeyer, Mörke & Weigert (2023)

**Title:** *Option Return Predictability with Machine Learning and Big Data*

**Role in this project**
- Demonstrates the value of nonlinearities and interactions in predicting option returns from large option- and stock-characteristic sets.
- Provides precedents for nonlinear models, ensembles, rolling out-of-sample evaluation, and forecast-comparison tests.
- Is primarily about the cross-section of delta-hedged option returns, not the same target as this project's physical-density estimation.

**Implementation implications**
- Use strong nonlinear baselines rather than comparing only against linear regression.
- Consider gradient-boosted trees and an ensemble.
- Use strictly time-ordered evaluation and compare forecasts statistically.
- Do not present option-return predictability as direct evidence that physical-density forecasts improve.

### Paper 5 — Ulrich, Walther, Rothfuss & Ferreira (2019)

**Title:** *Forward-looking P*

**Role in this project**
- Critical prior art: uses option-implied risk-neutral information with a neural model to estimate the physical return distribution.
- Makes a broad claim of “using ML to map option-implied information into physical expected returns/distributions” untenable as the project's novelty claim.
- Narrows the research opportunity to a carefully tested incremental extension.

**Implementation implications**
- Reconstruct its core input-target relationship as closely as the available data and paper details permit.
- Establish a strong non-regime reproduction/baseline before adding the proposed regime component.
- Document differences in data, features, targets, and evaluation rather than implying a full replication if the original setup cannot be reproduced.

> **Literature conclusion:** The project is not novel simply because it uses option data, neural networks, non-Gaussian distributions, or an HMM. The candidate contribution is the incremental value of persistent latent-regime conditioning in the risk-neutral-information-to-physical-density mapping, demonstrated against strong alternatives.

---

## 5. Proposed Method

### 5.1 Conceptual pipeline

\[
\text{Option prices}
\rightarrow
\text{risk-neutral features } Q_t
\rightarrow
\text{physical-density model}
\rightarrow
\widehat p_{t+1}(r)
\rightarrow
\text{portfolio decision}
\]

The proposed model adds a latent state \(z_t\):

\[
(Q_t, X_t, z_t)
\longrightarrow
\widehat p_{t+1}(r),
\]

where \(X_t\) contains historical market state variables and \(z_t\) is a persistent latent regime inferred only from information available at time \(t\).

### 5.2 Risk-neutral option features

Start with a manageable feature set, subject to data availability:

- Implied volatility level.
- Implied-volatility skew/smile summaries.
- Risk-neutral skewness.
- Risk-neutral kurtosis or a tail-risk proxy.
- Term-structure summaries across maturities.
- Put-call or downside/upside asymmetry measures.
- Option-implied variance and, where feasible, variance-risk-premium proxies.

For an index-options implementation, use a consistent maturity and moneyness grid. For individual equities, assess option availability, liquidity, quote quality, and survivorship before choosing the universe.

**Important:** Option-implied moments are under \(Q\); they are features, not direct labels for physical moments.

### 5.3 Historical and observable state features

Potential features include:

- Lagged returns at several horizons.
- Realized volatility and downside volatility.
- Drawdown and recent market trend.
- Observable liquidity/spread proxies, if reliable.
- Calendar variables only where economically justified.

All features must be available at the forecast timestamp. Feature scaling, imputation, feature selection, and dimensionality reduction must be fit on training data only.

### 5.4 Physical target

The target is the distribution of future returns under the physical measure, estimated using realized future returns.

For a first implementation, forecast a fixed horizon such as the next 21 trading days. The horizon should be selected before final testing and kept consistent across models.

Possible target representations:

1. **Parametric density:** predict distribution parameters, e.g. location, scale, skewness, and tail thickness, subject to valid parameter constraints.
2. **Mixture-density network:** predict mixture weights, component locations, and positive scales for a flexible density.
3. **Quantile distribution:** predict a pre-specified set of quantiles, with monotonicity constraints or post-processing to prevent crossing.

The mixture-density network is a plausible main model because it can represent asymmetric and multimodal predictive distributions. It is not mandatory: begin with the simplest valid distributional baseline and compare complexity against data size.

### 5.5 Non-regime baseline

The baseline should map option and historical features directly to a physical predictive distribution:

\[
\widehat p_{t+1}(r)=f_\theta(Q_t,X_t).
\]

Candidate baselines:
- Historical rolling distribution or volatility-based model.
- Linear/regularized distributional model.
- Gradient-boosted model for distributional parameters or quantiles.
- Neural mixture-density model without latent regimes.

The baseline must be strong enough that any apparent regime benefit is not just a comparison against an underfit model.

### 5.6 Proposed regime-conditioned model

Infer a latent regime \(z_t \in \{1,\ldots,K\}\) from a carefully chosen market-state representation. Start with a small number of regimes and tune \(K\) only within training/validation data.

Candidate regime inference:
- Hidden Markov model (HMM) on lagged realized volatility, returns, and selected market variables.
- Alternatively, a simpler observable-state model if HMM complexity does not yield stable regimes.

Use **filtered probabilities** \(P(z_t=k\mid\mathcal F_t)\), not smoothed probabilities that use future observations. This avoids look-ahead leakage.

A regime-conditioned density model can be written as:

\[
\widehat p_{t+1}(r\mid Q_t,X_t)
=
\sum_{k=1}^{K}
P(z_t=k\mid\mathcal F_t)\,
p_{\theta_k}(r\mid Q_t,X_t).
\]

This is a mixture over regime-specific predictive densities. A simpler alternative is to concatenate filtered regime probabilities to the feature vector:

\[
\widehat p_{t+1}(r)
=
f_\theta\!\left(Q_t,X_t,
P(z_t=1\mid\mathcal F_t),\ldots,
P(z_t=K\mid\mathcal F_t)\right).
\]

Test one approach first; do not build both at once. The regime-specific mixture is more interpretable, while probability concatenation may be easier to train.

### 5.7 What counts as evidence for regime persistence?

A model with regime labels is not sufficient. The evidence must show incremental value over:
- The same distribution model without regimes.
- A model conditioned on current observable volatility/state variables.
- A model with regime probabilities shuffled or otherwise ablated.
- Where feasible, a non-persistent mixture or simple volatility-threshold segmentation.

The regime model should be rejected or simplified if regimes are unstable, disappear under rolling refits, or add no held-out value.

---

## 6. Data Plan

### 6.1 Data requirements

Minimum data:
- Time-stamped option prices or a reliable implied-volatility surface.
- Underlying index/asset prices aligned to option observations.
- Risk-free rate and dividend/yield information where needed for option calculations.
- Sufficient historical returns to create physical-distribution targets.
- Trading calendar and instrument metadata.

Potential implementation choices:
- **Index-level first:** one liquid index and its options. Easier for data alignment and initial methodology validation.
- **Cross-sectional equities later:** only after verifying that option data are sufficiently complete and liquid.

Do not commit to a particular provider until access, licence, cost, historical depth, and field definitions are verified. If only implied-volatility surfaces are available, use features that can be reliably computed from them; do not claim to reconstruct exact option prices or model-free moments without the required inputs.

### 6.2 Data-quality checks

- Duplicate timestamps and option contracts.
- Stale, zero, crossed, or implausible quotes.
- Moneyness and maturity coverage.
- Missingness by date and instrument.
- Corporate actions and dividend treatment.
- Time-zone and market-close alignment.
- Survivorship and constituent-history bias for a cross-sectional universe.
- Consistent annualization and horizon conventions.
- Data availability as-of the actual prediction timestamp.

### 6.3 Leakage prevention

- Never use future returns to compute features at time \(t\).
- Do not use smoothed HMM states that depend on future observations.
- Fit scalers, imputers, PCA, regime models, and feature-selection procedures within each training window.
- Purge or embargo overlapping target windows when needed.
- Avoid random train/test splits for time-series forecasting.
- Keep a final held-out test period for the final specification (preserving raw test bundles unopened, accounting for any cash close breach in Git history).

---

## 7. Experimental Design

### 7.1 Time-ordered evaluation

Use a chronological design, such as:
1. Initial training window.
2. Validation window for hyperparameters and model selection.
3. Rolling or expanding out-of-sample test windows.
4. Final held-out test period for the frozen model specification (raw bundles unopened; cash close breach recorded in commit cee01a1).

Exact dates depend on the dataset. Define them only after inspecting coverage and missingness. If targets overlap across a 21-day horizon, account for overlap in splitting and inference.

### 7.2 Model ladder

Evaluate models in this order:

| ID | Model | Purpose |
|---|---|---|
| B0 | Historical rolling distribution / simple volatility benchmark | Establish a basic reference |
| B1 | Option-implied feature-only distribution model | Test value of \(Q\)-features |
| B2 | Historical-state-only distribution model | Test value of \(X\)-features |
| B3 | Combined \(Q+X\) non-regime model | Main baseline |
| B4 | Strong nonlinear combined model | Control for nonlinearities/interactions |
| P1 | Combined model plus filtered regime probabilities | Simple regime extension |
| P2 | Regime-specific predictive-density mixture | More structured extension, only if justified |

At minimum, B3/B4 and P1 must be compared on identical splits, targets, feature availability, and evaluation rules.

### 7.3 Ablation tests

- Remove option-implied features.
- Remove historical-state features.
- Remove regime features.
- Replace filtered regime probabilities with current observable state variables.
- Vary the number of regimes within validation only.
- Compare regime-specific mixture against a single shared density model.
- Compare alternative feature groups: volatility, skewness, tails, and term structure.
- Evaluate high-volatility and low-volatility periods separately, with state definitions fixed without using the final test results.

### 7.4 Statistical comparison

Use paired out-of-sample loss differences. Depending on the target and metric, consider:
- Diebold–Mariano-style tests for forecast loss differences, with dependence/overlap adjustments.
- Block bootstrap confidence intervals for density-score and portfolio-performance differences.
- Newey–West or other appropriate HAC inference for overlapping returns.

Do not treat daily forecast observations as independent when horizons overlap. Pre-specify the primary metric to reduce multiple-testing problems.

---

## 8. Evaluation Metrics

### 8.1 Distribution forecast quality

Primary candidate:
- **Negative log-likelihood (NLL)** or log predictive score on realized future returns.

Secondary metrics:
- Continuous ranked probability score (CRPS), where applicable.
- Quantile/pinball loss.
- Calibration of predictive intervals.
- Probability integral transform (PIT) diagnostics.
- Tail-event calibration and expected-shortfall forecast performance.
- Error in predicted moments, with clear recognition that moment error does not fully assess density quality.

A lower NLL is better, provided densities are numerically stable and evaluated on the same observations.

### 8.2 Economic portfolio evaluation

Use the estimated physical distribution to make portfolio decisions only after the forecasting comparison is defined.

Candidate portfolio objectives:
- Mean-variance utility using predicted physical means and covariance.
- Mean-CVaR / expected-shortfall minimization.
- Long-only constrained allocation as a robust initial setting.

Benchmarks:
- Equal weight \(1/N\).
- Historical mean/covariance portfolio with regularization.
- Minimum variance.
- Option-informed portfolio without regime conditioning.
- Proposed regime-conditioned portfolio.

Report:
- Annualized return and volatility.
- Sharpe ratio, with the risk-free-rate convention stated.
- Maximum drawdown.
- Turnover.
- Transaction costs and net performance.
- Expected shortfall / CVaR.
- Weight concentration and constraint violations.
- Confidence intervals and sensitivity to cost assumptions.

Portfolio optimization is highly sensitive to forecast error. Use shrinkage/regularization and weight constraints; do not let the optimizer magnify noisy predicted means.

### 8.3 Decision rule

The project should not declare success from a higher Sharpe ratio alone. The strongest result would show:
1. Better out-of-sample density scores.
2. Reasonable calibration.
3. Incremental improvement over a strong non-regime baseline.
4. Robustness across reasonable splits and cost assumptions.
5. Economic relevance under realistic portfolio constraints.

If only the portfolio metric improves while density forecasts do not, report that as an economic result requiring further diagnosis—not proof of a better physical-density mapping.

---

## 9. Implementation Roadmap

### Phase 0 — Feasibility and literature extraction

- Read the five papers with a structured extraction sheet.
- Record each paper's data, target, model, split design, metrics, and limitations.
- Verify data access and licensing.
- Choose the first asset universe and forecast horizon.
- Freeze the primary research question and metrics.

**Deliverable:** `literature_matrix.md` and a one-page experimental protocol.

### Phase 1 — Data ingestion and feature construction

- Load and align option and underlying data.
- Build quality filters.
- Compute or ingest implied-volatility surfaces.
- Construct option-implied and historical features.
- Create forward return targets for the chosen horizon.
- Save feature/target datasets with timestamp and provenance metadata.

**Deliverable:** reproducible dataset build, data-quality report, feature dictionary.

### Phase 2 — Basic baselines

- Implement historical rolling and option-feature baselines.
- Implement the combined non-regime model.
- Validate density normalization and numerical stability.
- Add time-ordered validation and evaluation.
- Save all out-of-sample predictions.

**Deliverable:** baseline report with density scores, calibration plots, and ablations.

### Phase 3 — Nonlinear baseline

- Train a strong nonlinear model, such as gradient boosting for distributional targets or a mixture-density neural network.
- Tune only on training/validation windows.
- Compare with the simpler baselines.
- Freeze the best non-regime comparator.

**Deliverable:** documented best non-regime baseline.

### Phase 4 — Regime model

- Fit an HMM or selected regime model within each training window.
- Produce filtered probabilities without look-ahead.
- Add regime probabilities to the baseline or use regime-specific densities.
- Monitor regime stability and state occupancy.
- Tune regime count only on validation data.

**Deliverable:** regime model, regime diagnostics, and paired out-of-sample comparisons.

### Phase 5 — Portfolio translation

- Convert predicted physical distributions into expected returns, covariance, and tail-risk estimates.
- Implement constrained portfolios.
- Include turnover and transaction costs.
- Compare against simple and option-informed non-regime benchmarks.

**Deliverable:** portfolio backtest with gross/net results and risk diagnostics.

### Phase 6 — Robustness and audit

- Run pre-specified ablations.
- Evaluate different volatility regimes and major stress periods.
- Test alternative horizons only as secondary analyses.
- Apply paired statistical comparisons and uncertainty estimates.
- Audit leakage, survivorship, and hyperparameter selection.
- Record failed experiments as well as successful ones.

**Deliverable:** final results report and reproducible experiment configuration.

### Phase 7 — Research write-up

- State the contribution narrowly.
- Explain why the five-paper literature prevents broader novelty claims.
- Report negative and null results.
- Separate forecast improvement from portfolio improvement.
- Document data and reproducibility limitations.

**Deliverable:** paper/report draft, figures, tables, and implementation instructions.

---

## 10. Suggested Repository Structure

```text
option-to-physical-density/
├── README.md
├── configs/
│   ├── data.yaml
│   ├── features.yaml
│   ├── models.yaml
│   └── evaluation.yaml
├── data/
│   ├── raw/                 # not committed if licensed/restricted
│   ├── interim/
│   └── processed/
├── notebooks/
│   ├── 01_data_audit.ipynb
│   ├── 02_option_features.ipynb
│   ├── 03_target_construction.ipynb
│   └── 08_result_analysis.ipynb
├── src/
│   ├── data/
│   │   ├── ingest.py
│   │   ├── validation.py
│   │   └── align.py
│   ├── features/
│   │   ├── option_moments.py
│   │   ├── historical_state.py
│   │   └── transforms.py
│   ├── targets/
│   │   └── forward_returns.py
│   ├── models/
│   │   ├── historical_baseline.py
│   │   ├── linear_density.py
│   │   ├── nonlinear_density.py
│   │   ├── regime_model.py
│   │   └── regime_density.py
│   ├── evaluation/
│   │   ├── density_metrics.py
│   │   ├── calibration.py
│   │   ├── forecast_tests.py
│   │   └── portfolio_metrics.py
│   ├── portfolio/
│   │   ├── optimizers.py
│   │   ├── constraints.py
│   │   └── costs.py
│   └── pipeline/
│       ├── train.py
│       ├── predict.py
│       └── backtest.py
├── tests/
│   ├── test_no_lookahead.py
│   ├── test_density_validity.py
│   ├── test_time_splits.py
│   └── test_portfolio_constraints.py
├── reports/
│   ├── literature_matrix.md
│   ├── data_audit.md
│   └── results.md
└── artifacts/
    ├── predictions/
    ├── metrics/
    └── figures/
```

This is a proposed structure, not a requirement to create every file at the outset.

---

## 11. Engineering and Reproducibility Requirements

- Set and record random seeds.
- Store data timestamps, feature versions, model configuration, and split boundaries.
- Save every out-of-sample prediction and model-selection decision.
- Keep raw licensed data out of public version control.
- Unit-test the absence of future information in feature construction.
- Verify predicted densities integrate to one and have valid parameters.
- Log failed fits, numerical warnings, and dropped observations.
- Use identical evaluation dates when comparing models.
- Distinguish research results from hypothetical investable performance.
- Avoid repeated tuning against the final test period.

---

## 12. Risks and Failure Modes

### Data availability

Historical option surfaces can be expensive or incomplete. If the data do not support reliable option-implied moments over a sufficiently long period, the intended study may not be feasible in its full form.

### Model instability

An HMM may produce unstable state assignments or too few observations in some regimes. Regime labels can switch across refits, and a regime model may simply proxy for volatility.

### Distribution misspecification

Mixture-density networks can be overconfident or numerically unstable. A flexible density may fit tails poorly despite good average loss.

### Evaluation leakage

Overlapping targets, full-sample normalization, smoothed latent states, survivorship bias, and repeated test-set tuning can all inflate apparent performance.

### Portfolio optimizer amplification

Small errors in predicted means can generate extreme weights. Use constraints, regularization, and cost-aware rebalancing.

### Weak novelty

The core mapping from risk-neutral option information to a physical distribution already has prior art. The project is only defensible if the persistent-regime extension provides a clearly measured, robust incremental contribution.

### No positive result

The regime extension may not outperform the non-regime model. A well-designed null result remains informative if the evaluation is rigorous and the comparison is fair.

---

## 13. Candidate Contribution Statement

Use this as a provisional statement, not as a final novelty claim:

> We investigate whether persistent latent market regimes provide incremental information for mapping option-implied risk-neutral features into the physical distribution of future returns. We compare regime-conditioned distributional forecasts against strong nonlinear non-regime baselines and evaluate both probabilistic forecast quality and downstream portfolio performance under realistic constraints and transaction costs.

The final contribution statement must be revised after checking the exact methods and results of *Forward-looking P* and the other four papers, and after verifying that the chosen implementation is materially different from existing work.

---

## 14. Minimum Viable Experiment

If time or data access is constrained, run the following experiment first:

1. Select one liquid underlying with sufficiently complete option data.
2. Define one fixed forecast horizon.
3. Construct a compact option-implied feature set plus historical volatility and return features.
4. Fit a simple non-regime predictive density model.
5. Fit a regime model using filtered probabilities and the same input information.
6. Compare both on identical rolling out-of-sample dates using NLL, calibration, and tail metrics.
7. Only if the density forecast comparison is credible, translate predictions into one constrained portfolio objective.
8. Compare against equal weight, historical-only, and non-regime option-informed portfolios.
9. Include transaction costs and turnover.
10. Freeze the test set before model selection and report all primary outcomes.

**Go/no-go criterion:** Do not expand into a complex multivariate non-Gaussian portfolio model until the data pipeline, leakage checks, and baseline density evaluation work end to end.

---

## 15. Decisions Still Open

These decisions must be resolved before the main training run:

- Asset universe: index first or cross-sectional equities.
- Option data source and permitted use.
- Forecast horizon.
- Exact option-implied feature definitions.
- Target density family.
- Regime inference method and number of states.
- Expanding versus rolling training window.
- Primary density metric.
- Portfolio objective and constraints.
- Transaction-cost assumptions.
- Final test period.

Choose these based on data feasibility and a written protocol, not after inspecting which choices produce the best final-test results.

---

## 16. Final Project Definition

The implementation will test whether **persistent latent regime information improves the conversion of option-implied risk-neutral information into physical predictive distributions**, and whether any improvement survives translation into portfolio allocation.

The implementation order is deliberate:

1. Audit the five-paper literature and data.
2. Establish valid features and targets.
3. Build strong non-regime baselines.
4. Add regime conditioning as the only primary model extension.
5. Test density quality before portfolio performance.
6. Run controlled ablations and leakage audits.
7. Report the incremental contribution—or lack of one—without overstating novelty.

This document is the project blueprint. It does not claim that the proposed model is already validated, profitable, or novel.
