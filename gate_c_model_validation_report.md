# Gate C Model Validation & Stage 7 Evaluation Report: Physical Return Density Forecasting

**Project Title:** Empirical Evaluation of Latent Market Regimes in Physical Return Density Forecasting  
**Author:** Antigravity (Advanced Agentic Coding Pair Programmer)  
**Date:** 24 October 2026  
**Document Status:** Formal Stage 7 Deliverable & Gate C Determination Report (Reconciled with Analytical CRPS & Per-Refit Diagnostics)  
**Authoritative References:** [research_protocol.md](file:///D:/IE612_Project/research_protocol.md), [stage5_modeling_specification.md](file:///D:/IE612_Project/stage5_modeling_specification.md), [gate_b_audit_report.md](file:///D:/IE612_Project/gate_b_audit_report.md), [implementation.md](file:///D:/IE612_Project/implementation.md)

---

## 1. Executive Summary & Gate C Determination

### 1.1 Gate C Status: **QUALIFIED PASS / PASSED WITH VALIDATION CAVEATS**
This report documents the completion of **Stage 7 Modeling and Validation** for the IE 612 research project, evaluating whether forward-looking option-implied risk-neutral moments ($Q_t \in \mathbb{R}^5$) and trailing historical market state ($X_t \in \mathbb{R}^6$) augmented with causally filtered latent market regime probabilities ($\pi_t \in \Delta^{K-1}$) produce superior physical density forecasts compared to a matched non-regime comparator:

$$\text{Hypothesis Test: } \quad p(y_t \mid Q_t, X_t, \pi_t) \quad \text{versus} \quad p(y_t \mid Q_t, X_t)$$

Under strict **User-Authorized Project Decisions** (Proposal A timing, complete-case filtering, test breach disclosure & exclusion rule, test continuity deferral to Gate D), models $B0$ through $B4$ and matched challenger $R1$ were fit on Development data (2010–2019) and evaluated via 21-session expanding-window walk-forward validation across the entire 2020–2021 Validation partition (494 complete-case scoring sessions).

**Core Validation Caveats:**
1. **Prequential Walk-Forward Evaluation:** The expanding-window walk-forward sequentially incorporates previously matured validation labels ($t \le \tau_m - 2$) into the training set for later validation blocks. The 2020–2021 results are therefore sequential prequential validation, not a static holdout from all model fitting.
2. **Exploratory Hyperparameter Selection:** Because the same 2020–2021 validation partition informed hyperparameter selection ($K=2, \lambda=0.01$) and diagnostic checks, reported significance levels are exploratory rather than a final confirmatory test.
3. **Calibration Limitations:** Kolmogorov-Smirnov tests on probability integral transforms reject uniformity at the 5% level for both primary models ($B4: p = 0.0109, R1: p = 0.0176$), and central interval empirical coverage departs from nominal levels. Gate C indicates numerical and optimization stability under the stated thresholds; it does not establish well-calibrated probabilistic forecasts.
4. **Sensitivity Sign Reversal Is Inconclusive:** Truncating training to mid-2012 flips the point estimate differential from positive ($+0.0056$ nats) to negative ($-0.0052$ nats), but both full-sample and sensitivity 95% bootstrap intervals include zero. This finding demonstrates sensitivity to the training origin, but does not prove that $Q_t$ subsumes regimes or that the full-sample estimate was strictly an artifact of early monthly option gaps.
5. **MDN Check Is Exploratory:** A 2-component Mixture Density Network attained an exploratory validation NLL of $-3.1388$ nats, but rolling-refit mode-collapse and component separation checks were not performed, and no matched regime MDN was evaluated. Single-component Student-$t$ remains the governing primary comparator.

---

### 1.2 Summary of Primary Findings
1. **Model Ladder Validation Hierarchy:**
   - Model $B0$ (Unconditional Gaussian): $\text{NLL} = -2.1245$ nats, $\text{CRPS} = 0.007778$
   - Model $B1$ (Trailing RV Student-$t$): $\text{NLL} = -3.0636$ nats, $\text{CRPS} = 0.007332$
   - Model $B3$ ($X$-Only Student-$t$): $\text{NLL} = -3.0837$ nats, $\text{CRPS} = 0.010774$
   - Model $B4$ (Combined $[Q, X]$ Primary Baseline): $\text{NLL} = -3.1120$ nats, $\text{CRPS} = 0.007732$
   - Model $B2$ ($Q$-Only Student-$t$): $\text{NLL} = -3.1188$ nats, $\text{CRPS} = 0.007501$
   - Model $R1$ (Matched Regime Challenger): $\text{NLL} = -3.1176$ nats, $\text{CRPS} = 0.007935$
2. **Paired Statistical Comparison ($R1$ vs. $B4$):**
   - Mean log-score differential: $\bar{d} = \mathbf{+0.005573\text{ nats/session}}$ (~$1.40$ nats/year).
   - Newey-West HAC Standard Error ($L=5$ lags): $0.007704$
   - Diebold-Mariano test statistic: $\text{DM} = 0.7234$ ($p_{\text{one-sided}} = 0.2347$, $p_{\text{two-sided}} = 0.4694$).
   - Stationary Block Bootstrap 95% CI ($B=2,000$): $[-0.009480, +0.019914]$ (**strictly includes zero**).
   - **Conclusion on Full Development Sample:** The regime challenger $R1$ exhibits a positive average point estimate over baseline $B4$, but this difference is **statistically indistinguishable from zero** ($p = 0.235 > 0.05$) and fails the pre-registered threshold for practical significance ($\bar{d} < 0.010$ nats/session).
3. **Mid-2012 Sensitivity Benchmark Finding ($N_{\text{train}} = 1,844$ Usable Supervised Pairs):**
   - Truncating training to start on `2012-07-02` (eliminating the early monthly-only strike depth deficit in 2010–2011) changes the differential:
     - Baseline $B4$ NLL: **$-3.1146$ nats**;
     - Challenger $R1$ NLL: **$-3.1094$ nats**;
     - Mean differential becomes **negative**: $\bar{d} = \mathbf{-0.005240\text{ nats/session}}$ ($\text{DM} = -0.5455, p = 0.7073$);
     - Bootstrap 95% CI: $[-0.026132, +0.012317]$.
   - Both the full-sample point estimate ($+0.0056$) and the sensitivity point estimate ($-0.0052$) have confidence intervals spanning zero; this demonstrates empirical sensitivity to the estimation window without establishing that $R1$ definitively harms forecasting or that the full-sample estimate was purely an artifact.
4. **Gate C Stability Criteria Verified:**
   - Predictive densities integrate to $1.0000$ (numerical quadrature error $< 6 \times 10^{-6}$ across calm and extreme volatility sessions).
   - Volatility scales remain strictly positive ($\sigma_t \ge 10^{-4}$ everywhere; empirical range $[0.0039, 0.6767]$).
   - Degrees of freedom satisfy heavy-tail bound ($\nu \ge 5.01 \ge 2.1$).
   - Latent regimes satisfy occupancy ($\ge 5\%$) and dwell time ($\ge 5$ sessions) constraints at **every single one of the 25 refit blocks** without parameter forcing.
   - Zero NaN or Inf losses across all 494 scoring sessions.
5. **Student-$t$ CRPS Exact Closed-Form Implementation:**
   - Vectorized Student-$t$ CRPS audited against high-accuracy numerical quadrature; previous 30-node quadrature truncated to $[\mu - 12\sigma, \mu + 12\sigma]$ reached empirical errors up to $1.89 \times 10^{-6}$ on extreme standardized observations.
   - Replaced with the exact closed-form analytical expression from Jordan, Krüger, and Lerch (2019), guaranteeing $< 10^{-14}$ error over the entire real line $(-\infty, \infty)$.
6. **Test Partition Integrity:**
   - Disclosed that the 2022-01-03 and 2022-01-04 cash closes and derived 2021-12-31 validation return remain in Git history (`cee01a1`), pre-registered for exclusion from eventual test scoring.
   - Raw 2022–2023 option bundles in `Data/SPX Options Chain/` remain **strictly unopened and unread**.
   - Stage 6 candidate CSV hashes remain 100% invariant.

---

## 2. Summary of Documentation Reconciliation & Protocol Decisions

Prior to model fitting, the core project documentation ([gate_b_audit_report.md](file:///D:/IE612_Project/gate_b_audit_report.md), [stage5_modeling_specification.md](file:///D:/IE612_Project/stage5_modeling_specification.md), [implementation.md](file:///D:/IE612_Project/implementation.md), and [research_protocol.md](file:///D:/IE612_Project/research_protocol.md)) was reconciled with five approved **User-Authorized Project Decisions**:

| Decision ID | Area | Approved Protocol Rule | Operational Implementation |
|---|---|---|---|
| **UD-1** | **Timing & Estimand Shift** | Adopt **Proposal A (Lagged Close-to-Close)**: features at session $t$ close predict $y_t \equiv \ln(S_{t+2}/S_{t+1})$. | Delays return window until after the 16:00/16:15 option quote cutoff, eliminating lookahead leakage. Stage 6 CSVs ($r_{t+1}$) preserved as historical candidate artifacts; separate Stage 7 operational datasets generated. |
| **UD-2** | **Label Availability Rule** | Supervised model training at refit date $\tau_m$ uses strictly $t \le \tau_m - 2$. | Target $y_t$ concludes at session $t+2$; requiring $t \le \tau_m - 2$ guarantees realized returns are observed by session close $\tau_m$. Contemporaneous HMM emissions and scalers use $t \le \tau_m$. |
| **UD-3** | **Missing Feature Policy** | **Complete-Case Filtering** on supervised origins with `valid_Q_all5 == True`, plus mid-2012 sensitivity benchmark (`2012-07-02`). | Development: 2,233 feature-complete rows, 2,231 usable pairs (terminal rows 2019-12-30 and 2019-12-31 targets nulled). Validation: 496 feature-complete rows, 494 usable scoring rows (terminal rows 2021-12-30 and 2021-12-31 targets nulled). Mid-2012: 1,846 rows, 1,844 pairs. |
| **UD-4** | **Test Partition Disclosure** | Disclose 2022-01-03 and 2022-01-04 cash closes and 2021-12-31 target in Git history (`cee01a1`). | Pre-register exclusion of the known Jan 3-to-Jan 4 return from any eventual test score. Never describe test partition as untouched. Raw 2022–2023 option bundles remain unopened. |
| **UD-5** | **Continuity Deferral & Authority** | Defer 2022–2023 daily option session continuity audit to Gate D. Record decisions as **User-Authorized**. | Raw option bundles protected until Gate D. No course-instructor sign-off claimed. |

---

## 3. Model Architectures, Regularization & Optimization

### 3.1 Model Ladder Specifications
All models were implemented in Python 3.12 using PyTorch 2.14.1 and SciPy 1.14.1:

* **Model B0 (Unconditional Gaussian):**
  $$\widehat{p}_{t+2 \mid t}^{(B0)}(y) = \mathcal{N}\big(\mu_\tau, \sigma_\tau^2\big)$$
  Estimated via sample mean and Bessel-corrected sample standard deviation on $\mathcal{T}_{\text{sup},\tau_m}$.
* **Model B1 (Trailing RV Student-$t$):**
  $$\sigma_t = \alpha_0 + \alpha_1 \text{RV}_{20d,t}, \quad \mu_t = \mu, \quad \nu \ge 2.1$$
  Parameterization: $\alpha_0 = \text{softplus}(\theta_0) + 10^{-4}$, $\alpha_1 = \text{softplus}(\theta_1)$, $\nu = \text{softplus}(\theta_\nu) + 2.1$. Estimated via maximum likelihood using L-BFGS with Strong Wolfe line search.
* **Models B2, B3, B4, and R1 (Location-Scale Student-$t$ Regression):**
  $$\mu_t = \mathbf{w}_\mu^\top \widetilde{\mathbf{x}}_t + b_\mu$$
  $$\sigma_t = \text{softplus}\big(\mathbf{w}_\sigma^\top \widetilde{\mathbf{x}}_t + b_\sigma\big) + 10^{-4}$$
  $$\nu = \text{softplus}(w_\nu) + 2.1$$
  * Inputs $\widetilde{\mathbf{x}}_t$:
    - $B2$ ($Q$-Only): $\widetilde{Q}_t \in \mathbb{R}^5$
    - $B3$ ($X$-Only): $\widetilde{X}_t \in \mathbb{R}^6$
    - $B4$ (Combined Baseline): $[\widetilde{Q}_t, \widetilde{X}_t] \in \mathbb{R}^{11}$
    - $R1$ (Challenger): $[\widetilde{Q}_t, \widetilde{X}_t, \pi_t] \in \mathbb{R}^{11 + K}$, where $\pi_t \in \Delta^{K-1}$
  * Loss: Regularized Negative Log-Likelihood:
    $$\mathcal{L}(\boldsymbol{\theta}) = -\sum_{s \in \mathcal{T}_{\text{sup},\tau_m}} \ln p\big(y_s \mid \mu_s, \sigma_s, \nu\big) + \lambda \big(\|\mathbf{w}_\mu\|_2^2 + \|\mathbf{w}_\sigma\|_2^2\big)$$
  * Optimization: L-BFGS with Strong Wolfe line search, maximum 60 iterations, initialized with sample statistics.

### 3.2 Hyperparameter Tuning & Selection ($K$ and $\lambda$)
Evaluated across 25 walk-forward blocks on the 494 complete-case validation sessions:

```
+---------------------------------------------------------------------------------------------------------------------+
|                                 Validation Hyperparameter Tuning Grid (N=494 Sessions)                             |
+---------------------------------------------------------------------------------------------------------------------+
| Latent Regimes (K) | L2 Penalty (lambda) | B4 Val NLL (nats) | R1 Val NLL (nats) | Mean Diff d (nats) | DM Stat (p) |
+--------------------+---------------------+-------------------+-------------------+--------------------+-------------+
| K = 2              | lambda = 1e-4       |      -3.1103      |      -3.1175      |      +0.007190     | 0.95 (0.17) |
| K = 2              | lambda = 1e-3       |      -3.1107      |      -3.1173      |      +0.006590     | 0.88 (0.19) |
| K = 2 (SELECTED)   | lambda = 1e-2       |     **-3.1120**   |     **-3.1176**   |      +0.005573     | 0.72 (0.23) |
| K = 3              | lambda = 1e-4       |      -3.1103      |      -3.1114      |      +0.001068     | 0.20 (0.42) |
| K = 3              | lambda = 1e-3       |      -3.1107      |      -3.1116      |      +0.000934     | 0.18 (0.43) |
| K = 3              | lambda = 1e-2       |      -3.1120      |      -3.1122      |      +0.000196     | 0.04 (0.48) |
+---------------------------------------------------------------------------------------------------------------------+
```

* **Selection of $\lambda$:** $\lambda = 0.01$ achieved the lowest validation NLL for baseline $B4$ ($-3.1120$ nats) and challenger $R1$ ($-3.1176$ nats), demonstrating the protective benefit of moderate $\ell_2$ shrinkage against overfitting.
* **Selection of $K$:**
  - Governing rule (Section 5.6): Default to $K=2$. Adopt $K=3$ if and only if all states satisfy occupancy $\ge 5\%$ and $\Delta\text{NLL} \ge 0.020$ nats.
  - While $K=3$ satisfied empirical occupancy ($32.0\%, 38.5\%, 29.6\%$), $K=3$ produced an NLL of $-3.1122$ nats, which is **worse** than $K=2$ ($-3.1176$ nats) by $\Delta\text{NLL} = -0.0054$ nats.
  - **Decision:** **Adopt $K=2$** (Low-Volatility / High-Volatility) under the pre-specified parsimony tie-breaker.

### 3.3 Handling of MDN Fallback Check
* **Architecture:** 2-component Mixture Density Network ($M=2$) on $[Q_t, X_t] \in \mathbb{R}^{11}$:
  $$\widehat{p}(y \mid \mathbf{u}_t) = w_1(\mathbf{u}_t) \frac{1}{\sigma_1(\mathbf{u}_t)} f_{\nu_1}\left(\frac{y - \mu_1(\mathbf{u}_t)}{\sigma_1(\mathbf{u}_t)}\right) + w_2(\mathbf{u}_t) \frac{1}{\sigma_2(\mathbf{u}_t)} f_{\nu_2}\left(\frac{y - \mu_2(\mathbf{u}_t)}{\sigma_2(\mathbf{u}_t)}\right)$$
  with mixing weight $w_1 = \text{sigmoid}(\mathbf{w}_w^\top \mathbf{u}_t + b_w)$.
* **Validation Performance:** $B4_{\text{MDN}}$ achieved validation NLL of **$-3.1388$ nats** ($0.0267$ nats lower than the single-component Student-$t$ NLL under this run).
* **Protocol Resolution (OD-2):** Single-component Student-$t$ remains the primary comparator for the $R1$ hypothesis test. The saved run does not document mode-collapse diagnostics, component separation, or rolling-refit stability, and no matched regime-conditioned MDN was evaluated. The MDN result is therefore exploratory and does not satisfy the protocol's requirement to establish improved validation performance with zero mode collapse; it does not by itself establish multimodality.

---

## 4. Verification of Label Availability at Walk-Forward Refits

To guarantee strict compliance with user-authorized Proposal A ($y_t \equiv \ln(S_{t+2}/S_{t+1})$), the walk-forward engine enforced the following separation across all 25 refit blocks:

1. **Information Cutoff at Refit Date $\tau_m$:**
   - Feature scaling statistics and HMM emission parameters were fit on contemporaneous session observations $t \le \tau_m$.
   - For every origin $t \le \tau_m$, $S_t, r_{1d,t}$, and $\text{RV}_{20d,t}$ are fully observed by session close $\tau_m$.
2. **Supervised Target Availability Restriction ($t \le \tau_m - 2$):**
   - At refit date $\tau_m$, supervised training was strictly restricted to origins:
     $$\mathcal{T}_{\text{sup},\tau_m} \equiv \{t : 1 \le t \le \tau_m - 2\}$$
   - Target $y_t$ concludes at the close of session $t+2$. For $t = \tau_m - 1$, $S_{t+2} = S_{\tau_m + 1}$ (1 day in the future). For $t = \tau_m$, $S_{t+2} = S_{\tau_m + 2}$ (2 days in the future). Excluding $\tau_m - 1$ and $\tau_m$ mathematically guarantees that zero future return data entered supervised model fitting.
3. **Partition Boundary Target Nulled Rows:**
   - On `2019-12-30` and `2019-12-31`, targets $y_t$ require cash closes from `2020-01-02` and `2020-01-03` (Validation). Both were set to `NaN` and excluded from Development training ($N=2,231$ pairs).
   - On `2021-12-30` and `2021-12-31`, targets $y_t$ require cash closes from `2022-01-03` and `2022-01-04` (Test). Both were set to `NaN` and excluded from Validation scoring ($N=494$ rows).

---

## 5. Empirical Performance & Statistical Hypothesis Testing

### 5.1 Out-of-Sample Validation Metrics (2020–2021, $N=494$ Complete-Case Sessions)

```
+----------------------------------------------------------------------------------------------------------------------------+
|                                    Comprehensive Out-of-Sample Validation Performance Table                                |
+----------------------------------------------------------------------------------------------------------------------------+
| Metric / Diagnostic            | B0 (Uncond) | B1 (RV-t)   | B2 (Q-Only) | B3 (X-Only) | B4 (Combined) | R1 (Regime)   |
+--------------------------------+-------------+-------------+-------------+-------------+---------------+---------------+
| **Negative Log-Likelihood**    | -2.1245     | -3.0636     | -3.1188     | -3.0837     | **-3.1120**   | **-3.1176**   |
| **CRPS (Analytical Exact)**    | 0.007778    | 0.007332    | 0.007501    | 0.010774    | **0.007732**   | **0.007935**   |
| **Mean Predictive Scale**      | 0.010000    | 0.008529    | 0.011852    | 0.026405    | 0.012680      | 0.013942      |
| **Mean Degrees of Freedom**    | -- (Gauss)  | 5.021       | 5.016       | 5.017       | 5.014         | 5.012         |
+--------------------------------+-------------+-------------+-------------+-------------+---------------+---------------+
| **PIT KS-Test Statistic**      | 0.0618      | 0.0691      | 0.0658      | 0.0569      | 0.0723        | 0.0689        |
| **PIT KS-Test p-value**        | 0.0438      | 0.0170      | 0.0265      | 0.0782      | 0.0109        | 0.0176        |
+--------------------------------+-------------+-------------+-------------+-------------+---------------+---------------+
| **50% Central Coverage (0.50)**| 0.5445      | 0.4433      | 0.4069      | 0.4474      | 0.4069        | 0.4109        |
| **80% Central Coverage (0.80)**| 0.8057      | 0.7530      | 0.7247      | 0.7551      | 0.7166        | 0.7227        |
| **95% Central Coverage (0.95)**| 0.9049      | 0.9231      | 0.9312      | 0.9474      | 0.9271        | 0.9332        |
+--------------------------------+-------------+-------------+-------------+-------------+---------------+---------------+
| **Pinball Loss alpha=0.01**    | 0.001312    | 0.000808    | 0.000636    | 0.001125    | 0.000678      | 0.000724      |
| **Pinball Loss alpha=0.05**    | 0.002365    | 0.001968    | 0.001927    | 0.003273    | 0.002072      | 0.002118      |
| **Pinball Loss alpha=0.10**    | 0.003194    | 0.002816    | 0.002960    | 0.004900    | 0.003150      | 0.003257      |
| **Pinball Loss alpha=0.90**    | 0.002572    | 0.002168    | 0.002305    | 0.004366    | 0.002433      | 0.002556      |
| **Pinball Loss alpha=0.95**    | 0.001839    | 0.001320    | 0.001396    | 0.002819    | 0.001481      | 0.001565      |
| **Pinball Loss alpha=0.99**    | 0.000971    | 0.000379    | 0.000417    | 0.000908    | 0.000456      | 0.000483      |
+----------------------------------------------------------------------------------------------------------------------------+
```

### 5.2 Paired Statistical Hypothesis Test ($R1$ versus $B4$)
* **Daily Paired Differential:** $d_t \equiv \ln \widehat{p}^{(R1)}(y_t) - \ln \widehat{p}^{(B4)}(y_t) = \ell_t^{(B4)} - \ell_t^{(R1)}$.
* **Sample Size:** $N = 494$ active validation trading sessions.
* **Mean Loss Differential ($\bar{d}$):** $\mathbf{+0.005573\text{ nats/session}}$ ($\approx +1.40$ nats annualized).
* **Newey-West HAC Standard Error ($L=5$ lags):** $0.007704$.
* **Diebold-Mariano Statistic:** $\text{DM} = \frac{0.005573}{0.007704} = \mathbf{0.7234}$.
* **$p$-values:** $p_{\text{one-sided}} = \mathbf{0.2347}$; $p_{\text{two-sided}} = \mathbf{0.4694}$.
* **Stationary Block Bootstrap ($B = 2,000$ replications, mean block length $b=5$):**
  - Bootstrap Mean: $+0.005468$ nats
  - 95% Percentile Confidence Interval: $[\mathbf{-0.009480}, \mathbf{+0.019914}]$
  - **Excludes Zero:** **FALSE**.

### 5.3 In-Sample Development Performance (2010–2019, $N=2,231$ Supervised Pairs)
To assess in-sample explanatory power vs. out-of-sample generalization:
* Model $B0$ (Unconditional Gaussian): $\text{NLL} = -3.3035$ nats
* Model $B1$ (Trailing RV Student-$t$): $\text{NLL} = -3.4379$ nats
* Model $B3$ ($X$-Only Student-$t$): $\text{NLL} = -3.4817$ nats
* Model $B2$ ($Q$-Only Student-$t$): $\text{NLL} = -3.4854$ nats
* Model $B4$ (Combined Baseline): $\text{NLL} = -3.4735$ nats
* Model $R1$ (Regime Challenger): $\text{NLL} = -3.4790$ nats
* **In-Sample Differential:** $\bar{d}_{\text{dev}} = +0.005501$ nats ($\text{DM} = 1.9165, p = 0.0277$).
* **Observation:** In-sample, adding regimes yielded a statistically detectable but modest $+0.0055$ nats edge. However, out-of-sample on Validation, this edge failed to achieve statistical significance.

### 5.4 Student-$t$ CRPS Audit, Validation & Closed-Form Correction
1. **Audit of Truncated Numerical Quadrature:**
   The initial implementation in `src/models/evaluation_metrics.py` utilized a 30-node Gauss-Legendre quadrature split over $[\mu - 12\sigma, y]$ and $[y, \mu + 12\sigma]$, asserting $10^{-8}$ accuracy. An audit against double-precision numerical integration over $(-\infty, \infty)$ revealed:
   - For extreme standardized returns (such as $|z| = 8.79$ on Model $B3$ and $|z| = 8.63$ on Model $R1$), polynomial node density across wide asymmetric intervals produced an observed maximum absolute error of $1.8891 \times 10^{-6}$ (relative error $3.27 \times 10^{-5}$) in sensitivity Model $B3$, and $1.2316 \times 10^{-6}$ in primary Model $B3$, failing the claimed $10^{-8}$ bound.
   - Truncation to $\pm 12\sigma$ would additionally fail if extreme market outliers exceeded $|z| > 12$.
2. **Adoption of Analytical Closed-Form Formula:**
   To guarantee exact precision across the entire real line without numerical truncation, `src/models/evaluation_metrics.py` was updated to implement the exact closed-form analytical expression for Student-$t$ CRPS from Jordan, Krüger, and Lerch (2019):
   $$\text{CRPS}(F_{\nu, \mu, \sigma}, y) = \sigma \left[ z \big(2F_\nu(z) - 1\big) + 2f_\nu(z)\left(\frac{\nu + z^2}{\nu - 1}\right) - \frac{2\sqrt{\nu}}{\nu - 1}\frac{B\left(\frac{1}{2}, \nu - \frac{1}{2}\right)}{B\left(\frac{1}{2}, \frac{\nu}{2}\right)^2}\right]$$
   where $z = (y - \mu)/\sigma$.
   This closed form is valid for all $\nu > 1$. Benchmark verification against `scipy.integrate.quad` with $10^{-12}$ tolerance confirmed that the formula is accurate to machine precision ($< 10^{-14}$) across all degrees of freedom ($\nu \in [2.1, 100]$) and standardized returns ($z \in [-15, +25]$).
3. **Recomputation Impact:**
   Recomputing all validation scores with the exact analytical formula produced a mean absolute difference of $< 3.8 \times 10^{-9}$ across all models; rounded to 6 decimal places, the reported table values ($B0: 0.007778, B1: 0.007332, B2: 0.007501, B3: 0.010774, B4: 0.007732, R1: 0.007935$) are fully invariant. Negative Log-Likelihood, Diebold-Mariano test statistics, and bootstrap intervals are independent of CRPS and remain identically unchanged.

### 5.5 Per-Refit HMM Diagnostics & Regime Stability Verification
To verify the latent regime persistence and non-degeneracy constraints specified in the protocol, complete diagnostics for each of the 25 walk-forward refit blocks were persisted to:
* `output/stage7_models/hmm_refit_diagnostics_primary.json`
* `output/stage7_models/hmm_refit_diagnostics_sensitivity.json`

Across all 25 refit blocks, the following protocol constraints were verified **without forcing any model parameters**:
1. **Expected Dwell Time ($\mathbb{E}[D_k] = 1 / (1 - A_{kk}) \ge 5.0$ sessions):**
   - **Primary Run:** State 0 dwell times range from $74.74$ to $114.97$ sessions; State 1 dwell times range from $40.96$ to $48.01$ sessions. Overall minimum observed dwell time is $40.96$ sessions, passing the $\ge 5.0$ threshold at **25 of 25 refits (100%)**.
   - **Mid-2012 Sensitivity Run:** State 0 dwell times range from $54.78$ to $125.60$ sessions; State 1 dwell times range from $31.98$ to $39.59$ sessions. Overall minimum observed dwell time is $31.98$ sessions, passing the $\ge 5.0$ threshold at **25 of 25 refits (100%)**.
2. **Empirical State Occupancy ($\text{Occupancy}(k) \ge 5.0\%$):**
   - **Primary Run:** Training argmax occupancies range from $26.38\%$ to $73.62\%$ across all refits (validation argmax occupancy: $54.66\%$ / $45.34\%$). Passing the $\ge 5.0\%$ threshold at **25 of 25 refits (100%)**.
   - **Mid-2012 Sensitivity Run:** Training argmax occupancies range from $21.87\%$ to $78.13\%$ across all refits. Passing the $\ge 5.0\%$ threshold at **25 of 25 refits (100%)**.

---

## 6. Mid-2012 Sensitivity Benchmark Analysis

### 6.1 Rationale & Experimental Setup
As documented in the Gate B audit, the early development sample (2010–2011) was characterized by a severe structural strike depth deficit due to monthly-only option expiries (~70% missing 30-day bracketing). Cboe's introduction of weekly options in mid-2012 established a rich, continuous volatility surface. To test whether the early data quality deficit distorted model estimation, the pre-specified sensitivity analysis was executed starting strictly on **`2012-07-02`**:
* **Training Period:** `2012-07-02` to `2019-12-31` ($1,887$ sessions; $1,846$ feature-complete rows; **$1,844$ usable supervised training pairs**).
* **Evaluation Period:** Exact same 494 validation scoring rows (2020–2021).

### 6.2 Empirical Findings & Comparison with Full Sample

```
+---------------------------------------------------------------------------------------------------------------------+
|                     Full Sample vs. Mid-2012 Sensitivity Benchmark Comparison (Validation N=494)                    |
+---------------------------------------------------------------------------------------------------------------------+
| Metric / Model                 | Full Sample (2010–2019 Start) | Mid-2012 Start (2012-07-02 Start) | Net Shift      |
+--------------------------------+-------------------------------+-----------------------------------+----------------+
| Baseline B4 Val NLL (nats)     | -3.1120                       | **-3.1146**                       | -0.0026 (Impr) |
| Challenger R1 Val NLL (nats)   | **-3.1176**                   | -3.1094                           | +0.0082 (Worse)|
| **Mean Differential d (nats)** | **+0.005573**                 | **-0.005240**                     | **-0.010813**  |
| Diebold-Mariano Statistic      | +0.7234                       | **-0.5455**                       | -1.2689        |
| DM One-Sided p-value           | 0.2347                        | **0.7073**                        | +0.4726        |
| Bootstrap 95% CI Lower         | -0.009480                     | **-0.026132**                     | --             |
| Bootstrap 95% CI Upper         | +0.019914                     | **+0.012317**                     | --             |
| Bootstrap Excludes Zero?       | FALSE                         | **FALSE**                         | Unchanged      |
+---------------------------------------------------------------------------------------------------------------------+
```

### 6.3 Interpretation & Theoretical Implications
1. **Sign Reversal:** Under the mid-2012 training window, the estimated $R1$-$B4$ differential changes from $+0.0056$ to $-0.0052$ nats/session; both estimates are statistically inconclusive and both bootstrap intervals include zero.
2. **Substantive Interpretation:** These results demonstrate empirical sensitivity to the estimation window. However, they do not definitively establish that $Q_t$ subsumes all regime information, that adding $\pi_t$ harms forecasting, or that the full-sample estimate is an artifact of early option-data gaps. Such explanations remain competing hypotheses to be tested during final Held-Out evaluation.

---

## 7. Gate Status Updates & Test Partition Protection

### 7.1 Status of Decision Gates

```
+-------------------------------------------------------------------------------------------------------------------------+
|                                               Project Gate Status Matrix                                                |
+-------------------------------------------------------------------------------------------------------------------------+
| Gate   | Name                                | Current Status                           | Evidence / Justification      |
+--------+-------------------------------------+------------------------------------------+-------------------------------+
| Gate A | Local Data Feasibility Gate         | QUALIFIED PASS                           | Stage 3 pilot verification    |
| Gate B | Calendar & Feature Construction Gate| QUALIFIED PASS (UD)                      | Resolved by UD-1 to UD-5      |
| Gate C | Baseline & Density Stability Gate   | **QUALIFIED PASS / PASSED WITH CAVEATS** | Stability verified; caveats doc|
| Gate D | Final Held-Out Test Evaluation Gate | **PENDING / BLOCKED**                    | Held-Out 2022–2023 partition  |
+-------------------------------------------------------------------------------------------------------------------------+
```

### 7.2 Strict Protection of Held-Out Test Partition
1. **Raw Option Bundles Unopened:** The 24 raw OptionsDX monthly bundles for 2022–2023 in `Data/SPX Options Chain/` remain **strictly unopened and uninspected**.
2. **Pre-Registered Test Exclusion:** The Jan 3 and Jan 4, 2022 cash closes and 2021-12-31 validation return retained in Git history commit `cee01a1` are formally pre-registered for exclusion from any eventual test scoring.
3. **Stage 6 Candidate CSV Hash Preservation:**
   - `spx_features_development_2010_2019.csv`: `138FA68AF7F8F21DA257F5D41332E583E73F32E358C6B2242A5D783DD5B2978E` (**VERIFIED INVARIANT**)
   - `spx_features_validation_2020_2021.csv`: `8BEDC8B4E3AE3CF42A99C8AB8477950AB69244EB8E052C7AFACEF8AC9E7C19D7` (**VERIFIED INVARIANT**)
   - `spx_daily_closes_2009_2021.csv`: `4F300DD58572EF986114E15BB35047449BA1E59B2A6678257AB34A3F1F5EBB1A` (**VERIFIED INVARIANT**)

---

## 8. Reproducibility Manifest

### 8.1 Generated Artifacts
All Stage 7 modeling artifacts have been generated and archived in `output/stage7_models/`:
* `output/stage7_models/validation_predictions_primary.csv` (Date-level forecasts for all models across 494 validation sessions).
* `output/stage7_models/validation_predictions_sensitivity_2012.csv` (Date-level forecasts for mid-2012 sensitivity benchmark).
* `output/stage7_models/validation_metrics_summary.json` (Full validation metrics, DM tests, and bootstrap CIs).
* `output/stage7_models/hmm_refit_diagnostics_primary.json` (Per-refit HMM transition matrices, dwell times, and occupancies for primary run).
* `output/stage7_models/hmm_refit_diagnostics_sensitivity.json` (Per-refit HMM diagnostics for mid-2012 sensitivity run).
* `output/stage7_models/sensitivity_analysis_summary.json` (Comparison of full sample vs. mid-2012 benchmark).
* `output/stage7_models/insample_metrics_summary.json` (In-sample development performance).
* `output/stage7_models/hyperparameter_tuning_results.json` (Grid search results for $K \in \{2, 3\}, \lambda \in \{10^{-4}, 10^{-3}, 10^{-2}\}$).
* `output/stage7_models/density_integration_checks.json` (Numerical integration verification).

### 8.2 Execution Scripts
* [`src/models/density_models.py`](file:///D:/IE612_Project/src/models/density_models.py): Implements $B0, B1, B2, B3, B4, R1$, and 2-component MDN.
* [`src/models/hmm_filter.py`](file:///D:/IE612_Project/src/models/hmm_filter.py): Causal Gaussian HMM with Baum-Welch EM and causal forward recursion.
* [`src/models/evaluation_metrics.py`](file:///D:/IE612_Project/src/models/evaluation_metrics.py): Exact analytical Student-$t$ CRPS (Jordan et al., 2019), Gaussian CRPS, NLL, PIT, coverage, pinball, Diebold-Mariano, and block bootstrap.
* [`src/models/walk_forward_pipeline.py`](file:///D:/IE612_Project/src/models/walk_forward_pipeline.py): Monthly expanding walk-forward engine with per-refit diagnostic collection.
* [`scratch/run_stage7_experiments.py`](file:///D:/IE612_Project/scratch/run_stage7_experiments.py): End-to-end experiment driver.

---
*End of Gate C Model Validation Report.*
