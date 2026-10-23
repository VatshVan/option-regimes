# Gate D Final Test Report: Physical Return Density Forecasting

**Project Title:** Empirical Evaluation of Latent Market Regimes in Physical Return Density Forecasting  
**Author:** Antigravity (Advanced Agentic Coding Pair Programmer)  
**Date:** 24 October 2026  
**Document Status:** Formal Stage 8 Deliverable & Gate D Final Held-Out Evaluation Report  
**Authoritative References:** [research_protocol.md](file:///D:/IE612_Project/research_protocol.md), [stage5_modeling_specification.md](file:///D:/IE612_Project/stage5_modeling_specification.md), [gate_b_audit_report.md](file:///D:/IE612_Project/gate_b_audit_report.md), [gate_c_model_validation_report.md](file:///D:/IE612_Project/gate_c_model_validation_report.md), [implementation.md](file:///D:/IE612_Project/implementation.md)  
**Frozen Pre-Execution Git Commit:** `66924f36d55a1c829f8a4c8657935735ee177b81`

---

## 1. Executive Summary & Gate D Final Determination

### 1.1 Gate D Status: **COMPLETE / EVALUATION INCONCLUSIVE (NO STATISTICALLY SIGNIFICANT R1 ADVANTAGE)**
This report documents the completion of **Stage 8: Final Held-Out Test Evaluation** for the IE 612 research project, evaluating whether forward-looking option-implied risk-neutral moments ($Q_t \in \mathbb{R}^5$) and trailing historical market state ($X_t \in \mathbb{R}^6$) augmented with causally filtered latent market regime probabilities ($\pi_t \in \Delta^{K-1}$) produce superior out-of-sample physical density forecasts compared to a matched non-regime comparator:

$$\text{Hypothesis Test: } \quad H_0: \mathbb{E}\big[\ln p(y_t \mid Q_t, X_t, \pi_t) - \ln p(y_t \mid Q_t, X_t)\big] \le 0 \quad \text{vs.} \quad H_1: \mathbb{E}\big[\ln p(y_t \mid Q_t, X_t, \pi_t) - \ln p(y_t \mid Q_t, X_t)\big] > 0$$

Under the frozen Stage 7 configuration (Proposal A timing $y_t \equiv \ln(S_{t+2}/S_{t+1})$, complete-case filtering, $K=2$ regimes, $\lambda=0.01$ $\ell_2$ shrinkage, 21-session expanding walk-forward refits, exact analytical Student-$t$ CRPS), all models ($B0$ through $B4$ and challenger $R1$) were evaluated on the held-out 2022–2023 test partition across 24 sequential walk-forward refit blocks.

```
+-------------------------------------------------------------------------------------------------------------------------------+
|                                  Gate D Held-Out Test Evaluation Performance Matrix                                           |
+-------------------------------------------------------------------------------------------------------------------------------+
| Evaluation Sample Trajectory       | Metric                         | Challenger (R1) | Baseline (B4)   | Net Differential    |
+------------------------------------+--------------------------------+-----------------+-----------------+---------------------+
| **Primary Prequential Run**        | Negative Log-Likelihood (nats) | **-3.0608**     | **-3.0553**     | **+0.005417**       |
| (Jan 3-Origin-Score-Excluded,      | CRPS (Analytical Exact)        | **0.006609**    | **0.006616**    | -0.000007           |
|  N = 500 Sessions, Matured Jan 3   | Newey-West HAC SE (L=5 lags)   | --              | --              | 0.003731            |
|  Target in Later Refits)           | Diebold-Mariano Stat (DM)      | --              | --              | **+1.4521**         |
|                                    | One-Sided p-value (H_1: d > 0) | --              | --              | **0.0732**          |
|                                    | Two-Sided p-value              | --              | --              | **0.1465**          |
|                                    | Stationary Bootstrap 95% CI    | [-0.001979, +0.013837]            | Spans Zero: TRUE    |
+------------------------------------+--------------------------------+-----------------+-----------------+---------------------+
| **Strictly Isolated Trajectory**   | Negative Log-Likelihood (nats) | **-3.0611**     | **-3.0556**     | **+0.005506**       |
| (Jan 3 Origin Excluded from Both   | CRPS (Analytical Exact)        | **0.006610**    | **0.006617**    | -0.000007           |
|  Scoring AND Supervised Refits,    | Newey-West HAC SE (L=5 lags)   | --              | --              | 0.003642            |
|  N = 500 Sessions)                 | Diebold-Mariano Stat (DM)      | --              | --              | **+1.5118**         |
|                                    | One-Sided p-value (H_1: d > 0) | --              | --              | **0.0653**          |
|                                    | Two-Sided p-value              | --              | --              | **0.1306**          |
|                                    | Stationary Bootstrap 95% CI    | [-0.002074, +0.013873]            | Spans Zero: TRUE    |
+------------------------------------+--------------------------------+-----------------+-----------------+---------------------+
| **Full Test Set (Secondary)**      | Negative Log-Likelihood (nats) | **-3.0542**     | **-3.0469**     | **+0.007257**       |
| (N = 501 Sessions,                 | Diebold-Mariano Stat (DM)      | --              | --              | **+1.8240**         |
|  Including Compromised 2022-01-03) | One-Sided p-value              | --              | --              | 0.0341              |
|                                    | Two-Sided p-value              | --              | --              | 0.0682              |
|                                    | Stationary Bootstrap 95% CI    | [-0.000509, +0.015382]            | Spans Zero: TRUE    |
+------------------------------------+--------------------------------+-----------------+-----------------+---------------------+
| **Actual-Quote Scoring Subset**    | Negative Log-Likelihood (nats) | **-3.0645**     | **-3.0591**     | **+0.005426**       |
| (N = 495 Sessions, Live Quotes     | Diebold-Mariano Stat (DM)      | --              | --              | **+1.4389**         |
|  Only, Refits Include Gaps)        | One-Sided p-value              | --              | --              | 0.0751              |
|                                    | Two-Sided p-value              | --              | --              | 0.1502              |
|                                    | Stationary Bootstrap 95% CI    | [-0.002097, +0.013343]            | Spans Zero: TRUE    |
+-------------------------------------------------------------------------------------------------------------------------------+
```

### 1.2 Core Scientific Findings & Verdict
1. **Evaluation Complete but Inconclusive:**
   On the primary Jan 3-origin-score-excluded test sample ($N=500$ sessions), challenger $R1$ achieves an average log-score differential of $\bar{d} = \mathbf{+0.005417\text{ nats/session}}$ over baseline $B4$. The Newey-West HAC Diebold-Mariano statistic is $\text{DM} = 1.4521$, with a one-sided $p$-value of **$0.0732$** and a two-sided $p$-value of **$0.1465$**. At the pre-registered significance level ($\alpha = 0.05$), the test **does not establish a statistically significant advantage for $R1$**.
2. **Confidence Interval Spans Zero and Extends Above Practical Threshold:**
   The Politis & Romano (1994) stationary block bootstrap 95% confidence interval ($B=2,000$ replications, average block length $b=5$ sessions) is **$[-0.001979, +0.013837]$** (primary prequential) and **$[-0.002074, +0.013873]$** (strictly isolated trajectory). Because each interval contains zero, no statistically significant effect is confirmed. However, because the upper bound ($+0.0138$) extends above the $+0.010$ practical threshold, the data does not rule out an incremental effect of that magnitude either.
3. **Observed Mean Estimate Below Project Threshold:**
   The observed point estimate ($\bar{d} \approx +0.0054$ nats/session, equivalent to $\approx +1.37$ nats annualized) lies below the project's pre-registered practical significance threshold ($\bar{d} \ge 0.010$ nats/session). This indicates that the point estimate obtained within this sample falls short of the project's practical benchmark, rather than constituting definitive proof of zero benefit in a broader universe.
4. **Model Comparison & Parsimony:**
   Challenger $R1$ produces the numerically lower out-of-sample NLL ($-3.0608$ vs $-3.0553$ in primary run; $-3.0611$ vs $-3.0556$ in strict isolation). However, this difference is not statistically significant, while baseline $B4$ achieves comparable density accuracy with lower model complexity ($11$ features vs $13$), eliminating latent regime transition uncertainty and estimation overhead.
5. **Secondary Status of Compromised Full Test Set:**
   In the full test set ($N=501$, including origin `2022-01-03`), the one-sided $p$-value is $0.0341$, but the two-sided $p$-value is $0.0682$ and the bootstrap confidence interval ($[-0.000509, +0.015382]$) continues to span zero. Because origin `2022-01-03` is historically compromise-exposed via commit `cee01a1`, it is maintained strictly as secondary context.
6. **No Unsupported or Investor-Value Claims:**
   Because no portfolio translation, execution model, or economic backtest was conducted, conclusions are strictly restricted to statistical density forecasting performance (NLL, CRPS, PIT uniformity, pinball loss).

---

## 2. Frozen Configuration & Pre-Execution Freeze

All modeling architectures, estimation routines, and evaluation metrics were frozen prior to test execution based on Stage 7 outcomes:

| Component | Specification | Governing Rationale & Justification |
|---|---|---|
| **Target Estimand** | Proposal A: $y_t \equiv \ln(S_{t+2} / S_{t+1})$ | Eliminates 16:00 cash close vs 16:15 option quote timestamp ambiguity (UD-1). |
| **Primary Comparison** | $R1$ (Challenger, $d=13$) vs $B4$ (Baseline, $d=11$) | Pre-registered primary hypothesis test ($p(y \mid Q, X, \pi)$ vs $p(y \mid Q, X)$). |
| **Latent Regimes ($K$)** | $K = 2$ (Low Volatility / High Volatility) | Parsimony default; $K=3$ failed validation improvement threshold in Stage 7. |
| **Shrinkage Penalty ($\lambda$)** | $\lambda = 0.01$ ($\ell_2$ ridge regularization) | Minimized validation NLL for both $B4$ and $R1$ during Stage 7 grid search. |
| **Density Family** | Location-Scale Student-$t$ regression | Primary parametric family with $\nu \ge 2.1, \sigma \ge 10^{-4}$ constraints. |
| **Refit Schedule** | 21-session expanding walk-forward | 24 blocks across 501 test sessions; contemporaneous HMM ($t \le \tau_m$). |
| **Label Maturity Rule** | Supervised training pairs strictly $t \le \tau_m - 2$ | Prevents future return targets from entering supervised estimation. |
| **HMM Filtering Rule** | Causal forward recursion only | Strict anti-leakage: zero Viterbi paths, zero backward smoothing. |
| **CRPS Evaluation** | Exact closed-form formula (Jordan et al., 2019) | Machine-precision ($< 10^{-14}$) analytical integration over $(-\infty, \infty)$. |

---

## 3. Data Inventory, Coverage Audit & Gap Reconciliation

### 3.1 Raw Option Bundle Inventory & Schema Audit
The complete data audit was executed and persisted to [`output/stage8_test/raw_data_audit_2022_2023.json`](file:///D:/IE612_Project/output/stage8_test/raw_data_audit_2022_2023.json):
* **File Inventory:** Exactly 24 monthly OptionsDX SPX option bundles present across 8 quarterly directories, representing each month (`202201` through `202212` and `202301` through `202312`) exactly once.
* **Volume:** 4,100,693 contract-level records, 1.38 GB uncompressed.
* **Header & Type Checks:** 100% column header conformity (all 33 columns matching schema). Structural numeric columns (`[UNDERLYING_LAST]`, `[DTE]`, `[STRIKE]`) parsed with zero missing or invalid values. Quote bid/ask columns had $712$ blank quotes ($0.017\%$ of records), handled by standard $0.05$ minimum bid filtering.
* **Timestamp Rule Verification:** Every single quote date across all 24 files was verified to have **exactly one distinct timestamp** (`len(ts) == 1`), and that timestamp uniformly reflects the `16:00` EOD snapshot. Zero multiple-timestamp dates exist.
* **Date Uniqueness:** Zero date overlap across monthly files confirmed.

### 3.2 Calendar Reconciliation & Missing Session Rate
Official S&P 500 cash trading sessions from `^GSPC` were reconciled against observed option bundle dates:
* **Expected Cash Trading Sessions:**
  - 2022: 251 sessions (2022-01-03 to 2022-12-30)
  - 2023: 250 sessions (2023-01-03 to 2023-12-29)
  - **Total Expected Exchange Sessions:** **501 sessions**.
* **Observed Option Sessions:** 496 matching exchange sessions (plus 9 vendor snapshot dumps on official 2022 market holidays: MLK Day, Presidents Day, Good Friday, Memorial Day, Juneteenth, Independence Day, Labor Day, Thanksgiving, Christmas).
* **Missing Option Sessions in Raw Bundles:** Exactly 5 sessions:
  1. `2022-05-11` (Wednesday) — Isolated 1-session gap (prior: 05-10, next: 05-12).
  2. `2022-06-17` (Friday) — Isolated 1-session gap (prior: 06-16, next trading: 06-21).
  3. `2022-06-24` (Friday) — Isolated 1-session gap (prior: 06-23, next: 06-27).
  4. `2022-12-16` (Friday) — Isolated 1-session gap (prior: 12-15, next: 12-19).
  5. `2023-01-03` (Tuesday) — Isolated 1-session gap (prior: 2022-12-30, next: 2023-01-04).
* **Missing Session Rate:** $\frac{5}{501} = \mathbf{0.9980\%} \le 1.000\%$. Passes the Gate B/D protocol threshold ($\le 1.0\%$).
* **Gap Rule Execution:**
  - In strict compliance with `research_protocol.md`, all 5 gaps were confirmed to be **isolated single-session gaps** ($\le 1$ trading day).
  - Option features $Q_t$ were causally forward-filled from the prior active trading session ($Q_t \leftarrow Q_{t-1}$) and explicitly logged with `q_is_fallback = True`.
  - Historical cash features $X_t \in \mathbb{R}^6$ were computed from actual traded cash closes on date $t$ without imputation.
  - Multi-session gaps: **Zero**.

### 3.3 Data-Access Scope Reconciliation (2024 Closes)
* **Target Maturity Requirements:** Proposal A requires two future trading-session closes to mature target $y_t = \ln(S_{t+2} / S_{t+1})$. For the final 2023 test origins:
  - Origin `2023-12-28`: Requires $S_{\text{2023-12-29}} = 4769.83$ and $S_{\text{2024-01-02}} = 4742.83$ ($y_t = -0.005677$).
  - Origin `2023-12-29`: Requires $S_{\text{2024-01-02}} = 4742.83$ and $S_{\text{2024-01-03}} = 4704.81$ ($y_t = -0.008047$).
* **Access Scope & Truncation Disclosure:** Closes for `2024-01-02` ($4742.83$) and `2024-01-03` ($4704.81$) were retrieved strictly to mature these final two return labels. Additional cash closes for `2024-01-04` through `2024-01-09` were initially fetched during initial data download and have been explicitly truncated. [`output/stage8_test/spx_daily_closes_2009_2024.csv`](file:///D:/IE612_Project/output/stage8_test/spx_daily_closes_2009_2024.csv) strictly terminates on `2024-01-03`.
* **Integrity Confirmation:** Zero 2024 forecast origins exist, zero 2024 option files were accessed, and no post-maturity closes enter any feature or label.

### 3.4 Breach-Origin Reconciliation & Trajectory Definitions
* **Historical Compromise Context:** S&P 500 cash closes for `2022-01-03` ($4796.56$) and `2022-01-04` ($4793.54$), and the derived return $\ln(4793.54 / 4796.56) = -0.000630$, were committed in Git history (`cee01a1`).
* **Interval Exclusion:** Under Proposal A ($y_t = \ln(S_{t+2} / S_{t+1})$), the return from Jan 3 close to Jan 4 close corresponds to origin `2021-12-31`, which was part of the Validation dataset and was nulled (`NaN`) in Stage 7.
* **Origin `2022-01-03` Handling:**
  - Origin `2022-01-03` features were observed on `2022-01-03`; its Proposal A target is $\ln(S_{\text{2022-01-05}} / S_{\text{2022-01-04}})$.
  - **Primary Prequential Run:** Origin `2022-01-03` is excluded from out-of-sample scoring ($N=500$) as a conservative safeguard. Under standard prequential walk-forward rules, after $t \le \tau_m - 2$ matures, its target enters the expanding training set at refit blocks $\tau_1$ through $\tau_{23}$.
  - **Strictly Isolated Trajectory (Sensitivity):** Origin `2022-01-03` is excluded from **both** out-of-sample scoring AND supervised model refits at all 24 blocks ($N=500$). Both trajectories yield statistically and practically identical results ($\bar{d} = +0.005417$ vs $+0.005506$, neither statistically significant).

---

## 4. Comprehensive Test Performance & Model Ladder Evaluation

Evaluated across all 24 expanding walk-forward refit blocks on the held-out test partition:

```
+----------------------------------------------------------------------------------------------------------------------------+
|                                  Comprehensive Held-Out Test Evaluation Performance Table                                  |
+----------------------------------------------------------------------------------------------------------------------------+
| Metric / Diagnostic            | B0 (Uncond) | B1 (RV-t)   | B2 (Q-Only) | B3 (X-Only) | B4 (Combined) | R1 (Regime)   |
+--------------------------------+-------------+-------------+-------------+-------------+---------------+---------------+
| **Negative Log-Likelihood**    | -2.9648     | -3.0301     | -3.0547     | -3.0365     | **-3.0553**   | **-3.0608**   |
| **CRPS (Analytical Exact)**    | 0.006743    | 0.006678    | 0.006629    | 0.006687    | **0.006616**   | **0.006609**   |
| **Mean Predictive Scale**      | 0.010186    | 0.008365    | 0.008759    | 0.008969    | 0.009109      | 0.009244      |
| **Mean Degrees of Freedom**    | -- (Gauss)  | 5.013       | 5.016       | 5.017       | 5.015         | 5.012         |
+--------------------------------+-------------+-------------+-------------+-------------+---------------+---------------+
| **PIT KS-Test Statistic**      | 0.0424      | 0.0603      | 0.0762      | 0.0733      | 0.0604        | 0.0628        |
| **PIT KS-Test p-value**        | 0.3211      | 0.0507      | 0.0057      | 0.0088      | 0.0500        | 0.0371        |
+--------------------------------+-------------+-------------+-------------+-------------+---------------+---------------+
| **50% Central Coverage (0.50)**| 0.5080      | 0.4140      | 0.4120      | 0.4360      | 0.4380        | 0.4360        |
| **80% Central Coverage (0.80)**| 0.7860      | 0.7220      | 0.7420      | 0.7360      | 0.7500        | 0.7480        |
| **95% Central Coverage (0.95)**| 0.9160      | 0.9320      | 0.9400      | 0.9380      | 0.9400        | 0.9400        |
+--------------------------------+-------------+-------------+-------------+-------------+---------------+---------------+
| **Pinball Loss alpha=0.01**    | 0.000492    | 0.000364    | 0.000341    | 0.000366    | 0.000358      | 0.000342      |
| **Pinball Loss alpha=0.05**    | 0.001445    | 0.001391    | 0.001390    | 0.001387    | 0.001359      | 0.001330      |
| **Pinball Loss alpha=0.10**    | 0.002262    | 0.002252    | 0.002275    | 0.002273    | 0.002243      | 0.002228      |
| **Pinball Loss alpha=0.90**    | 0.002166    | 0.002069    | 0.001888    | 0.002033    | 0.001943      | 0.001944      |
| **Pinball Loss alpha=0.95**    | 0.001307    | 0.001183    | 0.001143    | 0.001223    | 0.001171      | 0.001187      |
| **Pinball Loss alpha=0.99**    | 0.000351    | 0.000326    | 0.000338    | 0.000360    | 0.000348      | 0.000352      |
+----------------------------------------------------------------------------------------------------------------------------+
```

### 4.1 Paired Statistical Comparison ($R1$ versus $B4$)
* **Daily Paired Differential:** $d_t \equiv \ln \widehat{p}^{(R1)}(y_t) - \ln \widehat{p}^{(B4)}(y_t) = \ell_t^{(B4)} - \ell_t^{(R1)}$.
* **Sample Size:** $N = 500$ active trading sessions.
* **Mean Loss Differential ($\bar{d}$):** $\mathbf{+0.005417\text{ nats/session}}$ (Strict isolation: $+0.005506$ nats/session).
* **Newey-West HAC Standard Error ($L=5$ lags):** $0.003731$ (Strict isolation: $0.003642$).
* **Diebold-Mariano Statistic:** $\text{DM} = \mathbf{1.4521}$ (Strict isolation: $\mathbf{1.5118}$).
* **$p$-values:** $p_{\text{one-sided}} = \mathbf{0.0732}$; $p_{\text{two-sided}} = \mathbf{0.1465}$ (Strict isolation: $p_{\text{one-sided}} = 0.0653, p_{\text{two-sided}} = 0.1306$).
* **Stationary Block Bootstrap ($B = 2,000$ replications, mean block length $b=5$):**
  - Primary Prequential 95% CI: $[\mathbf{-0.001979}, \mathbf{+0.013837}]$
  - Strict Isolation 95% CI: $[\mathbf{-0.002074}, \mathbf{+0.013873}]$
  - **Spans Zero:** **TRUE in both runs**.
  - **Extends Above $+0.010$:** **TRUE in both runs**.

---

## 5. Per-Refit Latent Regime Diagnostics on Test Partition

Diagnostics were recorded at all 24 test refit blocks and persisted to [`output/stage8_test/hmm_refit_diagnostics_test.json`](file:///D:/IE612_Project/output/stage8_test/hmm_refit_diagnostics_test.json):
1. **Expected Dwell Time ($\mathbb{E}[D_k] = 1 / (1 - A_{kk}) \ge 5.0$ sessions):**
   - State 0 (Low Volatility) dwell times range from $98.0$ to $116.7$ sessions.
   - State 1 (High Volatility) dwell times range from $45.2$ to $64.0$ sessions.
   - Minimum observed dwell time: **$45.19$ sessions** ($\ge 5.0$). **Passes at 24 of 24 refits (100%)**.
2. **State Occupancy ($\text{Occupancy}(k) \ge 5.0\%$):**
   - Training argmax occupancies range from $29.26\%$ to $70.74\%$ across all refits.
   - Test partition causal forward-filtered argmax occupancies: **$36.4\%$ (Low Vol) / $63.6\%$ (High Vol)**.
   - Minimum observed occupancy: **$29.26\%$** ($\ge 5.0\%$). **Passes at 24 of 24 refits (100%)**.
3. **Parameter Forcing:** Zero parameter forcing or artificial constraints applied.

---

## 6. Cross-Partition Synthesis & Scientific Evaluation

Across the entire 14-year data lifecycle of the IE 612 project, the performance differential between the latent regime challenger ($R1$) and the matched non-regime option baseline ($B4$) is summarized below:

```
+-------------------------------------------------------------------------------------------------------------------------+
|                                Comprehensive Cross-Partition Evaluation Synthesis                                      |
+-------------------------------------------------------------------------------------------------------------------------+
| Partition / Trajectory             | Sample Size (Sessions) | Mean Diff d (nats) | DM Stat (p-value) | Bootstrap 95% CI     |
+------------------------------------+------------------------+--------------------+-------------------+----------------------+
| In-Sample Development              | N = 2,231 pairs        | +0.005501          | 1.9165 (0.0277*)  | --                   |
| Prequential Validation             | N = 494 sessions       | +0.005573          | 0.7234 (0.2347)   | [-0.009480, +0.019914]
| Mid-2012 Sensitivity Benchmark     | N = 494 sessions       | -0.005240          | -0.5455 (0.7073)  | [-0.026132, +0.012317]
| **Primary Prequential Test**       | **N = 500 sessions**   | **+0.005417**      | **1.4521 (0.0732)**| **[-0.001979, +0.013837]**
| **Strictly Isolated Trajectory**   | **N = 500 sessions**   | **+0.005506**      | **1.5118 (0.0653)**| **[-0.002074, +0.013873]**
| Full Test Set (Secondary)          | N = 501 sessions       | +0.007257          | 1.8240 (0.0341*)  | [-0.000509, +0.015382]
| Actual-Quote Scoring Subset        | N = 495 sessions       | +0.005426          | 1.4389 (0.0751)   | [-0.002097, +0.013343]
+-------------------------------------------------------------------------------------------------------------------------+
*Note: In Full Test Set (N=501), the one-sided p-value is 0.0341, but the two-sided p-value is 0.0682 and the 95%
 bootstrap interval includes zero. In the Primary Unbreached Set (N=500), both tests fail to reject at 5%.
```

### Substantive Scientific Interpretation
1. **Inconclusive Out-of-Sample Result:**
   While adding causally filtered latent market regimes produces a persistent positive point estimate ($\bar{d} \approx +0.0054$ to $+0.0055$ nats/session), this difference is **statistically insignificant** on held-out test data ($p = 0.0732$ and $p = 0.0653 > 0.05$).
2. **Confidence Bounds Span Practical Threshold:**
   The observed mean differential ($\bar{d} \approx +0.0054$ nats/session) lies below the pre-registered $+0.010$ practical threshold, indicating that the sample point estimate did not attain the targeted magnitude. However, the upper confidence limit ($+0.0138$) extends above $+0.010$, meaning the evaluation cannot definitively rule out an effect of that size.
3. **Parsimonious Baseline Viability:**
   Baseline $B4$ achieves comparable predictive accuracy with lower model complexity, avoiding latent state filtering and regime transition parameter estimation.

---

## 7. Gate Status Updates

```
+-------------------------------------------------------------------------------------------------------------------------+
|                                               Project Gate Status Matrix                                                |
+-------------------------------------------------------------------------------------------------------------------------+
| Gate   | Name                                | Final Status             | Evidence / Justification                      |
+--------+-------------------------------------+--------------------------+-----------------------------------------------+
| Gate A | Local Data Feasibility Gate         | QUALIFIED PASS           | Stage 3 pilot verification                    |
| Gate B | Calendar & Feature Construction Gate| QUALIFIED PASS (UD)      | Resolved by User Decisions UD-1 to UD-5       |
| Gate C | Baseline & Density Stability Gate   | QUALIFIED PASS (CAVEATS) | Stability verified across 25 refits           |
| Gate D | Final Held-Out Test Evaluation Gate | **PASSED / COMPLETE**    | **Evaluation complete; inconclusive R1 edge**  |
+-------------------------------------------------------------------------------------------------------------------------+
```

---

## 8. Reproducibility Manifest

### 8.1 Generated Test Artifacts
All Gate D artifacts are archived in [`output/stage8_test/`](file:///D:/IE612_Project/output/stage8_test/):
* [`output/stage8_test/spx_features_test_2022_2023.csv`](file:///D:/IE612_Project/output/stage8_test/spx_features_test_2022_2023.csv) (`SHA-256: 8A4BF13AF38F5FA8D4681B746B2D162D5A02F7711A04564F704CA2CDE2BC5C0E`)
* [`output/stage8_test/test_dataset_metadata.json`](file:///D:/IE612_Project/output/stage8_test/test_dataset_metadata.json) (`SHA-256: 7977B436345DCE990F4E662E7B934E8B3DAE89A0F5AAB282E912A281AD30D7C9`)
* [`output/stage8_test/test_predictions.csv`](file:///D:/IE612_Project/output/stage8_test/test_predictions.csv) (`SHA-256: 3097CE28BE9484D7D0A429B620BE886A8643086CED8E961A5615982DAE61E600`)
* [`output/stage8_test/test_predictions_strict_isolation.csv`](file:///D:/IE612_Project/output/stage8_test/test_predictions_strict_isolation.csv) (`SHA-256: 3C98FD166CBAF68E167BEDA9A5EBE64B6B70BB68D30BF546ECBE28892D3D5EEC`)
* [`output/stage8_test/test_metrics_summary.json`](file:///D:/IE612_Project/output/stage8_test/test_metrics_summary.json) (`SHA-256: CE29FEB51D4E5BCE70A1EA948A872CDA0FEF19EFD96E9D96173A12FAD1620A14`)
* [`output/stage8_test/hmm_refit_diagnostics_test.json`](file:///D:/IE612_Project/output/stage8_test/hmm_refit_diagnostics_test.json) (`SHA-256: EC6F4E489BD3A2D260CA684F3C2DA7685E8BA02836BF308151DF2B2F27ADD968`)
* [`output/stage8_test/raw_data_audit_2022_2023.json`](file:///D:/IE612_Project/output/stage8_test/raw_data_audit_2022_2023.json) (`SHA-256: F165B3D93061773F7677F0FF40E1F13C00EF629E2D82FEC2B488DF4056B31849`)
* [`output/stage8_test/density_integration_checks.json`](file:///D:/IE612_Project/output/stage8_test/density_integration_checks.json) (`SHA-256: 07F39D708FE0F934AE1BE1DC94003AF78A6FCD1CDB19EDC4B8F32B26468D39F0`)
* [`output/stage8_test/spx_daily_closes_2009_2024.csv`](file:///D:/IE612_Project/output/stage8_test/spx_daily_closes_2009_2024.csv) (`SHA-256: 32EDF5D44533F399C919DD7B4303D4408E8DC4E7FCD1E32A3A3E1A9615B56852`)

### 8.2 Invariant Historical Checksums
* `output/stage6_features/spx_features_development_2010_2019.csv`: `138FA68AF7F8F21DA257F5D41332E583E73F32E358C6B2242A5D783DD5B2978E` (**VERIFIED INVARIANT**)
* `output/stage6_features/spx_features_validation_2020_2021.csv`: `8BEDC8B4E3AE3CF42A99C8AB8477950AB69244EB8E052C7AFACEF8AC9E7C19D7` (**VERIFIED INVARIANT**)
* `output/stage6_features/spx_daily_closes_2009_2021.csv`: `4F300DD58572EF986114E15BB35047449BA1E59B2A6678257AB34A3F1F5EBB1A` (**VERIFIED INVARIANT**)

### 8.3 Execution Scripts
* [`scratch/audit_2022_2023_test_data.py`](file:///D:/IE612_Project/scratch/audit_2022_2023_test_data.py): Full raw options bundle inventory, schema verification, timestamp checks, and calendar reconciliation.
* [`scratch/extract_stage8_test_features.py`](file:///D:/IE612_Project/scratch/extract_stage8_test_features.py): Test feature extraction, moment calculation, Proposal A target alignment, and truncated cash closes generation.
* [`scratch/run_stage8_test_evaluation.py`](file:///D:/IE612_Project/scratch/run_stage8_test_evaluation.py): Dual walk-forward test evaluation, scoring, paired Diebold-Mariano tests, and block bootstrap.

---
*End of Gate D Final Test Report.*
