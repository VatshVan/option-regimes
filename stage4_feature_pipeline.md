# Stage 4 Implementation Note: SPX Feature Construction Pipeline

**Project Title:** Regime-Conditioned Mapping from Option-Implied Risk-Neutral Information to Physical Return Distributions  
**Course & Scope:** IE 612 (Introduction to Financial Engineering), 1-Month Empirical Project  
**Document Status:** Stage 4 Feature Pipeline Specification & Bounded Demonstration (Version 1.0, 21 October 2026)  
**Governing Documents:** [`research_protocol.md`](file:///D:/IE612_Project/research_protocol.md), [`data_feasibility_audit.md`](file:///D:/IE612_Project/data_feasibility_audit.md), [`implementation.md`](file:///D:/IE612_Project/implementation.md)  
**Output Location:** [`output/stage4_features/`](file:///D:/IE612_Project/output/stage4_features/)  

---

## 1. Executive Summary & Deliverable Status

This document defines the mathematical, algorithmic, and engineering architecture of the feature-construction pipeline for the primary SPX Minimum Viable Product (MVP). The module extracts:
1. **Option-Implied Risk-Neutral Feature Vector ($Q_t \in \mathbb{R}^5$):** 30-day Martin (2017) Simple Variance Swap Index ($\text{SVIX}_{30d}$), Bakshi, Kapadia, and Madan (2003) risk-neutral skewness ($\text{QSkew}_{30d}$), Bakshi et al. centered, standardized risk-neutral kurtosis ($\text{QKurt}_{30d}$; non-excess kurtosis, Gaussian benchmark = 3.0), At-The-Money implied volatility ($\text{ATM\_IV}_{30d}$), and the 60-day minus 30-day term structure slope ($\text{TermSlope}_{60\_30}$).
2. **Historical Market State Feature Vector ($X_t \in \mathbb{R}^6$):** 1-day lagged return ($r_{1d}$), 5-day cumulative return ($r_{5d}$), 5-day annualized realized volatility ($\text{RV}_{5d}$), 20-day annualized realized volatility ($\text{RV}_{20d}$), 20-day annualized downside semivariance ($\text{DSemi}_{20d}$), and trailing 20-day drawdown ($\text{DD}_{20d}$).

In accordance with Stage 4 boundaries:
* **No Predictive Models Fit:** No forecasting models, HMM filters, or density estimators have been estimated.
* **No Test Period Contamination:** The untouched 2022–2023 test partition remains strictly sealed and unread.
* **Bounded Demonstration Only:** Code execution was restricted to the two Stage 3 authorized demonstration dates (`2020-01-15` and `2020-03-03`). No full multi-year matrix has been constructed.

---

## 2. Software Architecture and Module Layout

The feature construction pipeline is implemented in the `src/features/` package:

```
src/
  __init__.py
  features/
    __init__.py
    options_cleaning.py     # Header whitespace stripping, contract-wise OTM screening, synthetic forward inversion
    options_moments.py      # Martin SVIX, BKM moments, Black-76 ATM IV inversion, constant-maturity interpolation
    historical_state.py     # Point-in-time trailing returns, realized vol, downside semivariance, drawdown
    pipeline.py             # FeaturePipeline orchestrator class with schema validation and diagnostic auditing
run_stage4_feature_pipeline.py # Bounded execution runner with unit tests and output serialization
output/
  stage4_features/
    spx_daily_closes.csv    # Cached official historical SPX daily closes (^GSPC)
    spx_features_stage4_demonstration.csv # Extracted features for the two demonstration dates
    spx_features_stage4_diagnostics.json  # Comprehensive per-tenor and per-date diagnostic audit logs
```

### Key Software Principles
1. **Raw Input Immutability:** The raw option chains in `Data/` are opened in read-only streaming mode (`chunksize=10000`). Only records for the target demonstration dates are extracted; no raw files are modified or overwritten.
2. **Deterministic & Modular:** All components are broken into isolated, testable pure functions.
3. **Explicit Handling of Missingness:** Functions return `None` or `NaN` with explicit diagnostic failure codes rather than falling back to implicit zero or forward-fill heuristics.

---

## 3. Mathematical Formulations and Computational Rules

### 3.1 Option-Implied Feature Vector ($Q_t$)

#### Step 1: Synthetic Forward Inversion ($F_{t,\tau}$)
At each available maturity tenor $\tau = \text{DTE} / 365.0$:
Locate the strike $K^*$ where $|C_{\text{mid}} - P_{\text{mid}}|$ is minimized, subject to:
$$C_{\text{bid}} > \$0.05, \quad P_{\text{bid}} > \$0.05, \quad C_{\text{ask}} > C_{\text{bid}}, \quad P_{\text{ask}} > P_{\text{bid}}$$
Invert synthetic forward price via put-call parity:
$$F_{t,\tau} = K^* + e^{r \tau} [ C_{\text{mid}}(K^*) - P_{\text{mid}}(K^*) ]$$

#### Step 2: Contract-Wise OTM Screening
Quotes are screened contract-wise on their own out-of-the-money side:
* **For $K < F_{t,\tau}$ (OTM Put):** Require $P_{\text{bid}} > \$0.05$, $P_{\text{ask}} > P_{\text{bid}}$, and relative spread $\frac{P_{\text{ask}} - P_{\text{bid}}}{P_{\text{mid}}} \le 0.35$. Disregard in-the-money call quotes. Midpoint retained: $M(K) = P_{\text{mid}}(K)$.
* **For $K \ge F_{t,\tau}$ (OTM Call):** Require $C_{\text{bid}} > \$0.05$, $C_{\text{ask}} > C_{\text{bid}}$, and relative spread $\frac{C_{\text{ask}} - C_{\text{bid}}}{C_{\text{mid}}} \le 0.35$. Disregard in-the-money put quotes. Midpoint retained: $M(K) = C_{\text{mid}}(K)$.

#### Step 3: Discrete Numerical Quadrature
Over sorted retained strikes $K_0 < K_1 < \dots < K_N$, standard composite trapezoidal weights are assigned:
$$\Delta K_0 = \frac{K_1 - K_0}{2}, \quad \Delta K_N = \frac{K_N - K_{N-1}}{2}, \quad \Delta K_i = \frac{K_{i+1} - K_{i-1}}{2} \quad (1 \le i \le N-1)$$

#### Step 4: Martin (2017) Simple Variance Swap Index ($\text{SVIX}$)
Normalized by the forward squared $F_{t,\tau}^2$ with gross compounding factor $e^{r\tau}$:
$$\text{SVIX}_{\tau}^2 = \frac{2 e^{r \tau}}{\tau F_{t,\tau}^2} \sum_{i=0}^N M(K_i) \Delta K_i, \quad \text{SVIX}_{\tau} = \sqrt{\max(\text{SVIX}_{\tau}^2, 0)}$$
*(Note: Evaluated strictly over the finite grid $[K_{\min}, K_{\max}]$ without tail extrapolation).*

#### Step 5: Bakshi, Kapadia, and Madan (2003) Risk-Neutral Moments
Let reference price be $F_{t,\tau}$. For calls ($K \ge F_{t,\tau}$):
$$H_V(K) = \frac{2(1 - \ln(K / F_{t,\tau}))}{K^2}, \quad H_W(K) = \frac{6 \ln(K / F_{t,\tau}) - 3(\ln(K / F_{t,\tau}))^2}{K^2}, \quad H_X(K) = \frac{12(\ln(K / F_{t,\tau}))^2 - 4(\ln(K / F_{t,\tau}))^3}{K^2}$$
For puts ($K < F_{t,\tau}$):
$$H_V(K) = \frac{2(1 + \ln(F_{t,\tau} / K))}{K^2}, \quad H_W(K) = -\frac{6 \ln(F_{t,\tau} / K) + 3(\ln(F_{t,\tau} / K))^2}{K^2}, \quad H_X(K) = \frac{12(\ln(F_{t,\tau} / K))^2 + 4(\ln(F_{t,\tau} / K))^3}{K^2}$$
Contract fair values (raw non-central option-implied power payoff moments):
$$V(\tau) = \sum_{i=0}^N H_V(K_i) M(K_i) \Delta K_i, \quad W(\tau) = \sum_{i=0}^N H_W(K_i) M(K_i) \Delta K_i, \quad X(\tau) = \sum_{i=0}^N H_X(K_i) M(K_i) \Delta K_i$$
Undiscounted raw moments: $\mathbb{E}^Q[R^2] = e^{r\tau} V(\tau)$, $\mathbb{E}^Q[R^3] = e^{r\tau} W(\tau)$, $\mathbb{E}^Q[R^4] = e^{r\tau} X(\tau)$.

Risk-neutral log-return mean ($\mu_t^Q$) and central moments:
$$\mu_t^Q(\tau) = e^{r\tau} - 1 - \frac{e^{r\tau}}{2} V(\tau) - \frac{e^{r\tau}}{6} W(\tau) - \frac{e^{r\tau}}{24} X(\tau)$$
$$\text{Var}_t^Q(\tau) = \mathbb{E}_t^Q[(R - \mu_t^Q)^2] = e^{r\tau} V(\tau) - (\mu_t^Q(\tau))^2$$
$$\mu_{3,t}^Q(\tau) = \mathbb{E}_t^Q[(R - \mu_t^Q)^3] = e^{r\tau} W(\tau) - 3 \mu_t^Q(\tau) e^{r\tau} V(\tau) + 2 (\mu_t^Q(\tau))^3$$
$$\mu_{4,t}^Q(\tau) = \mathbb{E}_t^Q[(R - \mu_t^Q)^4] = e^{r\tau} X(\tau) - 4 \mu_t^Q(\tau) e^{r\tau} W(\tau) + 6 (\mu_t^Q(\tau))^2 e^{r\tau} V(\tau) - 3 (\mu_t^Q(\tau))^4$$

Standardized dimensionless shape parameters:
$$\text{QSkew}(\tau) = \frac{\mu_{3,t}^Q(\tau)}{\big(\text{Var}_t^Q(\tau)\big)^{3/2}} \quad \text{[Centered, standardized 3rd central moment]}$$
$$\text{QKurt}(\tau) = \frac{\mu_{4,t}^Q(\tau)}{\big(\text{Var}_t^Q(\tau)\big)^2} \quad \text{[Centered, standardized 4th central moment (non-excess; normal = 3.0)]}$$
*(Note: $\text{QKurt}$ is the standardized 4th central moment, centering about $\mu_t^Q$ via the binomial expansion of $(R - \mu_t^Q)^4$. It measures total/non-excess kurtosis, where a Gaussian benchmark equals 3.0; excess kurtosis equals $\text{QKurt} - 3.0$).*

#### Step 6: Black-76 ATM Implied Volatility Inversion
At the ATM strike $K^*(\tau)$ closest to $F_{t,\tau}$, invert $\sigma_{\text{ATM}}(\tau)$ numerically via root-finding:
$$C_{\text{Black76}}(F_{t,\tau}, K^*(\tau), r, \tau, \sigma) = C_{\text{mid}}(K^*(\tau))$$
where:
$$C_{\text{Black76}} = e^{-r\tau} [ F \Phi(d_1) - K \Phi(d_2) ], \quad d_1 = \frac{\ln(F/K) + \frac{1}{2}\sigma^2 \tau}{\sigma \sqrt{\tau}}, \quad d_2 = d_1 - \sigma \sqrt{\tau}$$

#### Step 7: Constant-Maturity Standardization & Term Slope
* **30-Day Tenor:** Interpolate $\text{SVIX}_{30d}, \text{QSkew}_{30d}, \text{QKurt}_{30d}, \text{ATM\_IV}_{30d}$ from the two nearest tenors $\tau_1 \le 30 \le \tau_2$ with weight $w = \frac{30 - \text{DTE}_1}{\text{DTE}_2 - \text{DTE}_1}$.
* **60-Day Tenor:** Interpolate $\text{ATM\_IV}_{60d}$ from the two nearest tenors $\tau_3 \le 60 \le \tau_4$.
* **Term Structure Slope:**
  $$\text{TermSlope}_{60\_30} = \text{ATM\_IV}_{60d} - \text{ATM\_IV}_{30d}$$

---

### 3.2 Historical Market State Feature Vector ($X_t$)

Using the strictly trailing daily S&P 500 cash closing index series $S_t$ up to observation session $t$ ($s \le t$):
1. **1-Day Return:** $r_{1d,t} = \ln(S_t / S_{t-1})$.
2. **5-Day Return:** $r_{5d,t} = \ln(S_t / S_{t-5}) = \sum_{i=0}^4 r_{t-i}$.
3. **5-Day Realized Volatility:** $\text{RV}_{5d,t} = \sqrt{\frac{252}{5} \sum_{i=0}^4 r_{t-i}^2}$.
4. **20-Day Realized Volatility:** $\text{RV}_{20d,t} = \sqrt{\frac{252}{20} \sum_{i=0}^{19} r_{t-i}^2}$.
5. **20-Day Downside Semivariance:** $\text{DSemi}_{20d,t} = \sqrt{\frac{252}{20} \sum_{i=0}^{19} \min(r_{t-i}, 0)^2}$.
6. **Trailing 20-Day Drawdown:** $\text{DD}_{20d,t} = \frac{S_t - \max_{0 \le i \le 19} S_{t-i}}{\max_{0 \le i \le 19} S_{t-i}}$.

---

## 4. Verification and Empirical Demonstration Results

The pipeline was executed on the two authorized Stage 3 sample dates. Output artifacts are persisted at:
* [`spx_features_stage4_demonstration.csv`](file:///D:/IE612_Project/output/stage4_features/spx_features_stage4_demonstration.csv)
* [`spx_features_stage4_diagnostics.json`](file:///D:/IE612_Project/output/stage4_features/spx_features_stage4_diagnostics.json)

### Comparison Table: Calm vs. Crisis Regime

| Feature / Metric | Calm Session (`2020-01-15`) | Stress Session (`2020-03-03`) | Economic Interpretation |
|---|---|---|---|
| **Macro / Market Regime** | Low-volatility grinding bull market | Acute Covid pandemic shock & Fed 50 bps cut | High-contrast macro states |
| **Official Cboe VIX Close** | **12.42%** | **36.82%** | External diagnostic reference |
| **Official SPX Cash Close ($S_t$)**| **3,289.29** | **3,003.37** | Official market close (^GSPC) |
| **Observed Quote Readtime** | `2020-01-15 16:00` | `2020-03-03 16:00` | OptionsDX quote timestamp |
| **13-Week T-Bill Rate ($r$)** | $1.508\%$ | $0.918\%$ | Illustrative benchmark input (dynamic yield curve deferred) |
| **Eligible OTM Strikes (30d tenor)**| **167 strikes** ($[2525, 3460]$) | **208 strikes** ($[1700, 3460]$) | Liquid strike coverage |
| **30-Day Martin SVIX ($\text{SVIX}_{30d}$)** | **12.00%** (0.11996) | **34.88%** (0.34875) | Finite-grid discrete estimate |
| **BKM Risk-Neutral Skewness ($\text{QSkew}_{30d}$)**| **-2.8405** | **-1.9537** | Centered, standardized 3rd central moment |
| **BKM Risk-Neutral Kurtosis ($\text{QKurt}_{30d}$)**| **17.4973** | **8.1583** | Centered, standardized 4th central moment (non-excess; normal = 3.0) |
| **30-Day ATM Implied Vol ($\text{ATM\_IV}_{30d}$)** | **10.19%** | **33.78%** | Inverted independently via Black-76 |
| **60-Day ATM Implied Vol ($\text{ATM\_IV}_{60d}$)** | **11.33%** | **29.58%** | Inverted from bracketed 60d tenors |
| **Term Structure Slope ($\text{TermSlope}_{60\_30}$)**| **+1.14%** (+0.0114) | **-4.20%** (-0.0420) | **Normal upward vs. inverted term structure** |
| **1-Day Trailing Return ($r_{1d}$)** | **+0.19%** | **-2.85%** | Short-term momentum |
| **5-Day Trailing Return ($r_{5d}$)** | **+1.11%** | **-4.07%** | Medium-term momentum |
| **5-Day Realized Vol ($\text{RV}_{5d}$)** | **7.32%** | **50.01%** | Severe short-term vol spike |
| **20-Day Realized Vol ($\text{RV}_{20d}$)** | **6.96%** | **31.18%** | Trailing monthly vol |
| **20-Day Downside Semivar ($\text{DSemi}_{20d}$)**| **3.59%** | **25.62%** | Asymmetric downside volatility |
| **Trailing 20-Day Drawdown ($\text{DD}_{20d}$)** | **0.00%** (At 20d peak) | **-11.30%** | Peak-to-trough decline |

---

## 5. Input Provenance, Conventions, and Reproducibility

To ensure scientific transparency and independent reproducibility:

1. **Daily SPX Cash Closes ($S_t$):**
   * **Source & Endpoint:** Yahoo Finance chart endpoint for index ticker `^GSPC`.
   * **Local Cache Path:** [`output/stage4_features/spx_daily_closes.csv`](file:///D:/IE612_Project/output/stage4_features/spx_daily_closes.csv) (retrieved 2026-10-21).
   * **Field & Units:** `close` in index points.
   * **Values Used in Demo:** `2020-01-15` (close = $3,289.290039$) and `2020-03-03` (close = $3,003.370117$).
   * **Transformations:** Trailing log returns $r_t = \ln(S_t / S_{t-1})$ computed strictly point-in-time over the preceding 20 trading sessions ($s \le t$, zero future leakage).
   * **Verification Status:** Illustrative market close aggregator series matching Cboe published closing levels.
2. **Risk-Free Interest Rates ($r$):**
   * **Values:** $1.508\%$ annualized ($0.01508$) on `2020-01-15`; $0.918\%$ annualized ($0.00918$) on `2020-03-03`.
   * **Origin:** Hardcoded benchmark rates corresponding to the closing levels of the Cboe 13-week Treasury Bill Index (`^IRX`).
   * **Convention:** Continuously compounded rate ($e^{rT}$ / $e^{-rT}$) with day count $T = \text{DTE} / 365.0$.
   * **Verification Status:** **Illustrative benchmark inputs for demonstration**. A full dynamic risk-free yield curve matching each option tenor has not been ingested into the repository; these rates must not be described as independently verified continuous yield curves.
3. **Options Chain Data:**
   * **Source Files:** Monthly EOD bundles from OptionsDX (`Data/SPX Options Chain/spx_eod_2020-wh6jt7/spx_eod_202001.txt` and `spx_eod_202003.txt`).
   * **Timestamps:** Uniformly `16:00` ET on both demonstration dates.
   * **Verification Status:** Verified raw source streaming with input immutability.
4. **Metadata Serialization:**
   * All input provenance records, cache paths, and run parameters are serialized to [`output/stage4_features/input_provenance_metadata.json`](file:///D:/IE612_Project/output/stage4_features/input_provenance_metadata.json) and embedded within [`output/stage4_features/spx_features_stage4_diagnostics.json`](file:///D:/IE612_Project/output/stage4_features/spx_features_stage4_diagnostics.json).

---

## 6. Unit Testing and Edge-Case Safeguards

The runner script [`run_stage4_feature_pipeline.py`](file:///D:/IE612_Project/run_stage4_feature_pipeline.py) incorporates 4 explicit edge-case checks:
1. **Sparse Strike Rejection:** Grids with $<15$ strikes trigger `failure_reason = "Insufficient strikes"` and return `None` (preventing severe quadrature discretization errors).
2. **Contract-Wise Quote Cleaning:** Correctly filters zero bids ($P_{\text{bid}} \le 0.05$), crossed markets ($P_{\text{ask}} \le P_{\text{bid}}$), and wide relative spreads ($>0.35$), while preserving valid quotes on the active OTM side regardless of ITM quote quality.
3. **Black-76 Intrinsic Boundary Guard:** Guarantees that option prices violating lower arbitrage bounds ($C_{\text{mid}} \le \max(0, e^{-rT}(F-K))$) fail safely to `None` rather than triggering solver divergence.
4. **Historical Lookback Leakage Guard:** Verifies that trailing return and volatility computations strictly truncate at $s \le t$, preventing future session leakage.

---

## 7. Documented Limitations, Unresolved Data Decisions, and Gate B Audit Status

To maintain scientific rigor, the following decisions and empirical audit findings are explicitly documented:
1. **16:00 vs. 16:15 Quote Timestamp Ambiguity (Gate B Check 3):** Across all 3,021 sessions in 2010–2021, OptionsDX `QUOTE_READTIME` uniformly reports `'16:00'`. However, standard SPX index options historically traded until 16:15 ET. Synthetic forward parity ensures internal surface consistency across simultaneous quotes, but does not prove synchronization with the 16:00:00 ET cash equity close $S_t$ or eliminate potential 15-minute look-ahead risk. The information cutoff remains an **unresolved decision gate (OD-6)**.
2. **Finite-Strike Quadrature vs. Continuum Integrals:** SVIX, QSkew, and QKurt are computed over the discrete retained strike range $[K_{\min}, K_{\max}]$ with standard composite trapezoidal weights without tail extrapolation. They are finite-grid numerical estimates, not continuum integrals over $[0, \infty)$.
3. **Early-Sample Strike Density & Expiration Gaps (2010–2012 Audit):** Auditing 745 trading sessions across 2010–2012 revealed that prior to the mid-2012 introduction of weekly options, Cboe listed SPX options primarily on standard monthly cycles. Consequently, 30-day constant-maturity bracketing failed on **76.4% of sessions in 2010** and **68.6% of sessions in 2011**, inducing a 9.18% raw missingness rate in $Q_t$ across the 2010–2019 development period. Furthermore, call wings routinely truncated at $1.08–1.12 \times S$, failing the $K_{\max}/S \ge 1.15$ span on $>93\%$ of sessions.
4. **Intra-Month Session Continuity Audit & Reconciliation (2010–2021):** Out of 3,021 expected exchange sessions, 2,994 option sessions were observed (30 missing, 3 unexpected stale closure dates from Sandy and Bush mourning: $3021 - 30 + 3 = 2994$). While the 12-year aggregate missing rate is $0.993\% \le 1.0\%$, annual missingness exceeds 1% in 5 calendar years (2011 at 2.78%, 2014 at 1.19%, 2019 at 1.98%, 2020 at 1.19%, 2021 at 2.38%).
5. **Candidate Feature Datasets & Test Boundary Disclosure (Stage 6 Deliverable):** Candidate datasets for Development (2010–2019, 2,516 rows, SHA-256: `201679a93c387507d6766283b44036f736e40920088feebbf5afb3dad6a96f11`) and Validation (2020–2021, 505 rows, SHA-256: `8bedc8b4e3ae3cf42a99c8ab8477950ab69244eb8e052c7afacef8ac9e7c19d7`) have been generated in `output/stage6_features/`. **They are candidate audit outputs, not permanently frozen.**
   * *Test Boundary Disclosure:* Downloading `^GSPC` through January 2022 accessed the `2022-01-03` close across the test boundary, compromising the test seal. The test partition cannot be described as intact. The terminal validation row on `2021-12-31` has its target label set strictly to `NaN` (`UNOBSERVED_WITHOUT_TEST_CLOSE`).
   * *5-Feature Vector Completeness:* Complete vectors ($Q_t \in \mathbb{R}^5$) exist on **2,233 rows (88.75%)** in Development (283 missing [11.25%]) and **496 rows (98.22%)** in Validation (9 missing [1.78%]).
   * *Rate Fallbacks:* On Columbus Day 2010 and Veterans Day 2016, rates were causally carried forward from the prior session with explicit audit flags, eliminating silent imputation.

---
*End of Stage 4 Implementation Note (Updated Post-Gate B Audit).*
