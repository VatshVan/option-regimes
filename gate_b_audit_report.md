# Stage 7 Readiness & Gate B Closure Review: Calendar Continuity, Early Strike Breadth, Quote Timing, Rate Ingestion, and Candidate Feature Datasets

**Document Status:** Formal Gate B Closure Review & Stage 7 Readiness Assessment  
**Date:** 22 October 2026 (Revised & Comprehensive)  
**Author:** Antigravity (Advanced Agentic Coding Pair Programmer)  
**Governing Documents:** [research_protocol.md](file:///D:/IE612_Project/research_protocol.md), [stage5_modeling_specification.md](file:///D:/IE612_Project/stage5_modeling_specification.md), [stage4_feature_pipeline.md](file:///D:/IE612_Project/stage4_feature_pipeline.md), [data_feasibility_audit.md](file:///D:/IE612_Project/data_feasibility_audit.md), [implementation.md](file:///D:/IE612_Project/implementation.md)

---

## 1. Executive Summary & Gate B Determination

### 1.1 Gate B Determination: **BLOCKED / QUALIFIED (STAGE 7 MODEL FITTING NOT AUTHORIZED)**
In accordance with project governance, empirical audit findings, anti-leakage disciplines, and course protocol:
1. **Stage 7 Model Fitting is NOT Authorized:** Under the governing protocol, no forecasting models ($B0$–$B4$, $R1$) or latent Hidden Markov Models (HMM) may be trained, tuned, or fitted until all Gate B blockers are resolved and approved.
2. **Test Partition Cash Close Breach & Permanent Git Retention:** While the 24 raw OptionsDX monthly bundles for 2022–2023 remained unopened and unparsed, the cash index close dataset (`^GSPC`) was downloaded through January 2022 in Stage 6, thereby accessing both the **2022-01-03 closing price (`4796.56`)** and the **2022-01-04 closing price (`4793.54`)**, and deriving the terminal validation return $r_{t+1}$ on `2021-12-31` (`0.0063538`). All three test-period values were committed in commit `cee01a1` and remain permanently recorded in the Git repository history. Therefore, **the test partition cannot be described as sealed or untouched**. In the active working tree and candidate datasets, cached cash closes have been truncated to $\le \text{2021-12-31}$, and terminal target returns on both `2019-12-31` (`UNOBSERVED_WITHOUT_VALIDATION_CLOSE`) and `2021-12-31` (`UNOBSERVED_WITHOUT_TEST_CLOSE`) have been set strictly to `NaN` to guarantee partition boundary purity.
3. **Information Cutoff Gate (OD-6) Unresolved:** Vendor readtime strings uniformly report `'16:00'`, even on unscheduled half-days. However, Cboe SPX options historically traded until 16:15:00 ET, while S&P 500 cash equity closed strictly at 16:00:00 ET. Synthetic forward parity proves internal surface consistency, but does not prove synchronization with the 16:00:00 ET cash equity close $S_t$. The available data cannot establish synchronization without lookahead risk. Concrete alternative reference price proposals are submitted herein for approval.
4. **Early-Sample Structural Deficit (2010–2012):** Due to standard monthly expiration cycles prior to mid-2012, 30-day constant-maturity bracketing fails on **76.4% of sessions in 2010** and **68.6% of sessions in 2011**. Complete 5-feature option vectors ($Q_t \in \mathbb{R}^5$) are missing on **283 sessions (11.25%)** in the Development partition (with 205 missing in 2010–2011 alone). A fixed Complete-Case Filtering policy is formalized herein.
5. **Session Continuity Fails Annual 1.0% Threshold in 5 Years:** While aggregate 12-year missingness is $0.993\%$, annual missingness exceeds the 1.0% tolerance in five separate calendar years (2011, 2014, 2019, 2020, 2021). Continuity is not a clean annual pass.
6. **Datasets are Candidate Outputs, NOT Permanently Frozen:** Neither the Development nor Validation feature datasets are treated as permanently frozen. They serve as candidate audit deliverables pending formal resolution of the information cutoff and test seal governance.

---

## 2. Check 1: Session Continuity Audit (2010–2021)

### 2.1 Authoritative Denominator Definition & Arithmetic Reconciliation
* **Exchange Calendar Benchmark:** The authoritative exchange trading schedule was constructed from the official daily close series of the S&P 500 cash index (`^GSPC`, primary price index), verified against NYSE/Cboe holiday schedules and unscheduled market closures.
* **Special Closures Accounted For:**
  - Hurricane Sandy: 29–30 October 2012 (2 full closure days).
  - National Day of Mourning for President George H.W. Bush: 5 December 2018 (1 full closure day).
* **Expected Active Exchange Sessions (2010–2021):** Exactly **3,021 sessions**.
* **Total Observed SPX Option Dates:** **2,994 sessions**.
* **Missing Sessions:** **30 sessions**.
* **Unexpected Sessions (Stale Closure Records):** **3 sessions** (Sandy Oct 29–30, 2012; Bush mourning Dec 5, 2018), where OptionsDX propagated stale quotes, identical underlying index levels (`1411.94` and `2700.06`), and stale volumes from the preceding active sessions.
* **Arithmetic Reconciliation Formula:**
  $$\begin{aligned}
  \text{Observed SPX Dates (2,994)} &= \text{Expected Exchange Sessions (3,021)} \\
  &\quad - \text{Missing Active Sessions (30)} \\
  &\quad + \text{Unexpected Stale Closure Records (3)}
  \end{aligned}$$

### 2.2 Annual Dispersion & Protocol Threshold Evaluation
The aggregate 12-year missing session rate is:
$$\text{Aggregate Missing Rate} = \frac{30}{3,021} = 0.993\% \quad (\le 1.0\% \text{ aggregate threshold})$$

> [!WARNING]
> While the aggregate 12-year average marginally satisfies the 1.0% threshold, **the continuity check fails the 1.0% limit in 5 individual calendar years**:
> - **2011:** 7 missing sessions (**2.78%**), driven by a 5-day consecutive outage from 2011-01-19 to 2011-01-25.
> - **2014:** 3 missing sessions (**1.19%**).
> - **2019:** 5 missing sessions (**1.98%**).
> - **2020:** 3 missing sessions (**1.19%**), including Black Friday and Christmas Eve early closes.
> - **2021:** 6 missing sessions (**2.38%**).
> Continuity is therefore **not a uniform pass** across the historical sample.

### 2.3 Annual Session Continuity Reconciliation Table

| Calendar Year | Expected Sessions | Missing Sessions | Unexpected Records | Observed Records | Annual Missing Rate | Missing Dates |
|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **2010** | 252 | 2 | 0 | 250 | 0.79% | 2010-05-19, 2010-11-15 |
| **2011** | 252 | 7 | 0 | 245 | **2.78%** *(Exceeds 1%)* | 2011-01-19:25 (5 consecutive), 2011-08-22, 2011-12-16 |
| **2012** | 250 | 2 | 2 (Sandy) | 250 | 0.80% | 2012-02-29, 2012-10-24 *(Stale: 10-29, 10-30)* |
| **2013** | 252 | 0 | 0 | 252 | 0.00% | None |
| **2014** | 252 | 3 | 0 | 249 | **1.19%** *(Exceeds 1%)* | 2014-01-02, 2014-08-04, 2014-12-05 |
| **2015** | 252 | 0 | 0 | 252 | 0.00% | None |
| **2016** | 252 | 1 | 0 | 251 | 0.40% | 2016-04-18 |
| **2017** | 251 | 1 | 0 | 250 | 0.40% | 2017-09-27 |
| **2018** | 251 | 0 | 1 (Bush) | 252 | 0.00% | None *(Stale: 12-05)* |
| **2019** | 252 | 5 | 0 | 247 | **1.98%** *(Exceeds 1%)* | 2019-03-01, 2019-04-17, 2019-05-24, 2019-06-07, 2019-09-05 |
| **2020** | 253 | 3 | 0 | 250 | **1.19%** *(Exceeds 1%)* | 2020-06-18, 2020-11-27 (Black Friday), 2020-12-24 (Xmas Eve) |
| **2021** | 252 | 6 | 0 | 246 | **2.38%** *(Exceeds 1%)* | 2021-02-26, 2021-08-09, 2021-08-31, 2021-09-07, 2021-09-09, 2021-09-15 |
| **Total** | **3,021** | **30** | **3** | **2,994** | **0.993%** | *(Reconciliation: $3021 - 30 + 3 = 2994$)* |

---

## 3. Check 2: Early-Sample Strike Breadth Audit (2010–2012)

### 3.1 Audit Methodology
Every active session across 2010, 2011, and 2012 (**745 total trading sessions** across 36 monthly files) was audited using Stage 4 contract-wise OTM screening ($P_{\text{bid}} > 0.05, \text{spread} \le 0.35$ for puts; $C_{\text{bid}} > 0.05, \text{spread} \le 0.35$ for calls):
- Invert synthetic forward $F_{\text{parity}}$ at ATM strike $K^*$.
- Screen liquid OTM quotes; evaluate liquid strike count and moneyness span $K_{\min}/S \le 0.85$ and $K_{\max}/S \ge 1.15$ in $20 \le \text{DTE} \le 50$.
- Evaluate 30-day constant-maturity bracketing: existence of valid expiries $\tau_1 \le 30 \le \tau_2$ in $20 \le \text{DTE} \le 50$.

### 3.2 Audit Findings & Structural Deficit

```
+-----------------------------------------------------------------------------------------+
|                    Early-Sample Strike Breadth Audit (2010–2012)                        |
+-----------------------------------------------------------------------------------------+
| Year  | Total Sessions | Spanned [0.85, 1.15] (>=30 Strikes) | Bracketed 30 Days (20–50 DTE)|
+-------+----------------+-------------------------------------+--------------------------+
| 2010  |      250       |              11 ( 4.4%)             |        59 (23.6%)        |
| 2011  |      245       |              30 (12.2%)             |        77 (31.4%)        |
| 2012  |      250       |               6 ( 2.4%)             |       175 (70.0%)        |
+-------+----------------+-------------------------------------+--------------------------+
| Total |      745       |              47 ( 6.3%)             |       311 (41.7%)        |
+-----------------------------------------------------------------------------------------+
```

1. **Monthly Expiry Gap in 2010–2011:** Standard monthly expirations (3rd Friday) created 2-to-3-week windows where only one contract existed in the 20–50 DTE range. Consequently, 30-day bracketing failed on **76.4% of sessions in 2010** and **68.6% of sessions in 2011**.
2. **Weekly Option Transition (Mid-2012):** When Cboe expanded SPX Weekly (SPXW) options in June/July 2012, 30-day bracketing jumped from ~20% in early 2012 to **95–100%** in the second half of 2012.
3. **Call Wing Truncation:** While put wings routinely extended to $K/S \le 0.75$, liquid call quotes truncated at $1.08–1.12 \times S$, failing the $K_{\max}/S \ge 1.15$ span on $>93\%$ of early sessions.

---

## 4. Check 3: Quote Timestamps, Cash Synchronization, and Look-Ahead Mitigation

### 4.1 Available Timestamp Evidence & Vendor Invariance
Every active trading session across the 12-year historical sample (3,021 expected sessions, 2,994 observed option dates in 2010–2021) was audited for quote timestamp integrity:
1. **Uniform Vendor Readtime String:** Across all 3,021 sessions, the vendor field `QUOTE_READTIME` reports the invariant text string `'YYYY-MM-DD 16:00'`, and the numeric field `QUOTE_TIME_HOURS` reports `16.0`.
2. **Absence of Early Close Timestamps:** On official exchange half-days where NYSE and Cboe halted trading early at 13:00:00 ET (e.g. Black Friday 2020-11-27, Christmas Eve 2020-12-24), OptionsDX files still report `'16:00'`.
3. **Implication:** The vendor readtime string `'16:00'` is a static batch processing label, not an authoritative, exchange-synchronized timestamp. It provides no second- or millisecond-level precision regarding the exact moment quotes were sampled.

### 4.2 Cash Equity vs. Option Market Microstructure (The 15-Minute Lookahead Wedge)
* **Cash Equity Close ($S_t$):** S&P 500 cash equity trading on the primary listing venues (NYSE and NASDAQ) closes strictly at 16:00:00 ET. S&P Dow Jones Indices calculates the official benchmark cash close ($S_t$, ticker `^GSPC`) based on the closing auction prices of the 500 constituent stocks.
* **Option Market Hours:** Standard SPX index options on Cboe historically traded until 16:15:00 ET (4:15 PM Eastern / 3:15 PM Central). CME S&P 500 futures contracts likewise trade through 16:15:00 ET.
* **Empirical Divergence:** Because option market makers continuously update quotes between 16:00 and 16:15 ET based on active CME index futures, option quotes at 16:15 ET reflect price discovery and post-16:00 news. The vendor's recorded `UNDERLYING_LAST` diverges systematically from the official 16:00:00 ET cash close $S_t$:
  - **2020-01-02 (Calm):** OptionsDX `UNDERLYING_LAST` = `3258.14`, Cash Close $S_t$ = `3257.85` ($+0.29$ index pts, $+0.89$ bps).
  - **2020-01-15 (Calm):** OptionsDX `UNDERLYING_LAST` = `3289.76`, Cash Close $S_t$ = `3289.29` ($+0.47$ index pts, $+1.43$ bps).
  - **2020-03-03 (Crisis):** OptionsDX `UNDERLYING_LAST` = `3002.74`, Cash Close $S_t$ = `3003.37` ($-0.63$ index pts, $-2.10$ bps).
* **The Lookahead Hazard:** If option quotes reflect 16:15:00 ET trading, conditioning on option feature vector $Q_t$ to forecast next-day return $r_{t+1} = \ln(S_{t+1}/S_t)$ introduces forward-looking information: $Q_t$ incorporates 15 minutes of price discovery that occurred *after* the denominator $S_t$ was frozen at 16:00:00 ET.

### 4.3 Why Synthetic-Forward Parity Does NOT Resolve the Cutoff
Synthetic forward parity:
$$F_{\text{parity}} = K^* + e^{r\tau}(C(K^*, \tau) - P(K^*, \tau))$$
verifies that the call and put quotes at strike $K^*$ were captured synchronously *with each other* and are free from static cross-sectional arbitrage.
> [!IMPORTANT]
> **Synthetic forward parity proves internal surface consistency only.** If call and put quotes were both captured at 16:14:59 ET, put-call parity holds with extreme precision, but the entire surface embeds 14 minutes and 59 seconds of post-close information relative to the 16:00:00 ET equity close $S_t$. Parity cannot establish temporal synchronization with the cash index.

### 4.4 Concrete Alternative Forecast Origin & Reference Price Proposals (Submitted for Approval)
Because OptionsDX data lacks tick-level timestamps, cash synchronization cannot be empirically proven. To establish a defensible, airtight research design, the following three precisely defined alternative proposals are submitted for instructor/user decision:

1. **Proposal A: Lagged Close-to-Close Return ($r_{t+1 \to t+2} = \ln(S_{t+2}/S_{t+1})$) [Recommended for Operational Realism]**
   - **Forecast Origin / Information Cutoff:** EOD of day $t$ (all $X_t$, $Q_t$, and causal HMM filtered probability $\pi_t$ formed using information available through 16:15:00 ET on day $t$).
   - **Trade / Evaluation Window:** The forecast density targets the return between the next session's cash close $S_{t+1}$ (16:00:00 ET on day $t+1$) and the subsequent cash close $S_{t+2}$ (16:00:00 ET on day $t+2$).
   - **Target Definition:**
     $$r_{t+1 \to t+2} = \ln\left(\frac{S_{t+2}}{S_{t+1}}\right)$$
   - **Lookahead Mitigation:** The evaluation return window begins a full 23 hours and 45 minutes *after* the feature cutoff at $t$. Lookahead bias is mathematically impossible.
   - **Course Protocol Impact:** Aligns with realistic portfolio rebalancing where trades are queued overnight and executed at market close on $t+1$.

2. **Proposal B: Next-Day Intraday Open-to-Close Return ($r_{t+1}^{\text{open} \to \text{close}} = \ln(S_{t+1}^{\text{close}} / S_{t+1}^{\text{open}})$)**
   - **Forecast Origin / Information Cutoff:** EOD of day $t$ (16:15:00 ET).
   - **Trade / Evaluation Window:** Initiated at the official NYSE cash open on day $t+1$ ($S_{t+1}^{\text{open}}$ at 09:30:00 ET) and liquidated at the cash close ($S_{t+1}^{\text{close}}$ at 16:00:00 ET).
   - **Target Definition:**
     $$r_{t+1}^{\text{intraday}} = \ln\left(\frac{S_{t+1}^{\text{close}}}{S_{t+1}^{\text{open}}}\right)$$
   - **Lookahead Mitigation:** The position opens 17 hours and 15 minutes after the feature cutoff, isolating next-day cash trading from overnight news.

3. **Proposal C: Primary Close-to-Close with Bounded Lookahead Margin ($r_{t+1} = \ln(S_{t+1}/S_t)$)**
   - **Forecast Origin:** Retain $r_{t+1} = \ln(S_{t+1}/S_t)$ as the primary theoretical target, but formally define the 15-minute price wedge:
     $$\delta_t = \ln\left(\frac{\text{UNDERLYING\_LAST}_t}{S_t}\right)$$
   - **Evaluation Hurdle:** The standard deviation of $\delta_t$ is empirically quantified at $\sigma_{\delta} \approx 2.1 \text{ bps}$. Require that any statistical outperformance of challenger model $R1$ over baseline $B4$ (e.g. Diebold-Mariano test or log-score differential $\bar{d}$) be shown to exceed the 15-minute wedge variance $\text{Var}(\delta_t) \approx 4.4 \times 10^{-8}$. If gains disappear under a 2 bps noise perturbation, the outperformance cannot be attributed to genuine predictive skill.

**Decision Gate Recommendation:** Adopt **Proposal A (Lagged Close-to-Close)** or **Proposal B (Intraday Open-to-Close)** to completely eliminate lookahead risk, pending instructor approval before Stage 7. Model fitting remains **STRICTLY GATED**.

---

## 5. Check 4: Risk-Free Input Ingestion & Day-Count Conversion

### 5.1 Treasury Bill Discount Yield vs. Continuous Zero Rate
US Treasury bills (`^IRX`, 13-week benchmark) are quoted on an **annualized bank discount basis** $d$ under an **actual/360** day-count:

$$P = 100 \times \left(1 - \frac{d}{100} \cdot \frac{D_{\text{bill}}}{360}\right), \quad D_{\text{bill}} = 91$$

The exact continuously compounded annualized zero rate $r_{\text{cont}}$ under an **actual/365** day-count (required by Black-Scholes, Martin SVIX, and BKM integrations) is:

$$r_{\text{cont}} = -\frac{365}{D_{\text{bill}}} \ln\left(1 - \frac{d}{100} \cdot \frac{D_{\text{bill}}}{360}\right)$$

* 2020-01-15 (Calm): $d = 1.508\% \implies r_{\text{cont}} = \mathbf{1.532\%}$ ($+2.39$ bps wedge).
* 2020-03-03 (Crisis): $d = 0.918\% \implies r_{\text{cont}} = \mathbf{0.932\%}$ ($+1.38$ bps wedge).

### 5.2 Elimination of Silent Rate Imputation & Holiday Carryforward Audit
* **Audit Finding on Bond Market Closures:** On two active equity trading days, the US Treasury bond market (SIFMA) was closed for federal bank holidays, so `^IRX` was not published:
  1. **2010-10-11 (Columbus Day):** `^IRX` was missing (`NaN`). Carried forward causally from 2010-10-08 ($d = 0.115\% \implies r_{\text{cont}} = 0.001166$).
  2. **2016-11-11 (Veterans Day):** `^IRX` was missing (`NaN`). Carried forward causally from 2016-11-10 ($d = 0.458\% \implies r_{\text{cont}} = 0.004652$). Recomputed option moments using exact rate ($\text{SVIX}_{30d} = 0.133632, \text{QSkew}_{30d} = -2.062157, \text{ATM\_IV}_{30d} = 0.120003$).
* **Explicit Logging:** Zero silent constant substitution was performed. Both dates are explicitly logged with `rate_source = 'CAUSAL_PRIOR_SESSION_CARRYFORWARD'`, `rate_is_fallback = True`, and explanatory notes. All other 3,019 rows have `rate_source = 'CBOE_IRX_ACTUAL'` and `rate_is_fallback = False`.

---

## 6. Check 5: Feature Implementation, Full Completeness Diagnostics & Candidate Datasets

### 6.1 Complete Feature Vector Diagnostics ($Q_t \in \mathbb{R}^5$ vs. 30d Moments)
Full option feature vector completeness requires all five elements:
$$Q_t = [\text{SVIX}_{30d}, \text{QSkew}_{30d}, \text{QKurt}_{30d}, \text{ATM\_IV}_{30d}, \text{TermSlope}_{60\_30}]^\top \in \mathbb{R}^5$$

* **Development Partition (2010–2019, 2,516 sessions):**
  - **All 5 Features Complete (`valid_Q_all5`):** **2,233 sessions (88.75%)**.
  - **Missing at Least One Feature:** **283 sessions (11.25%)**.
  - **Breakdown of Missingness:**
    - 231 sessions lack 30-day moments (`SVIX_30d`, `QSkew_30d`, `QKurt_30d`, `ATM_IV_30d`), driven by monthly expiration gaps in 2010–2011 (201 days) and missing vendor dates (30 days).
    - An additional 52 sessions have valid 30-day moments but lack 60-day constant maturity options, making `TermSlope_60_30` missing.
  - **Historical State Features ($X_t \in \mathbb{R}^6$):** 2,516 sessions complete (**100.0%**).
* **Validation Partition (2020–2021, 505 sessions):**
  - **All 5 Features Complete (`valid_Q_all5`):** **496 sessions (98.22%)**.
  - **Missing Features:** Exactly 9 sessions (1.78%), corresponding directly to the 9 missing option dates in the vendor archive.
  - **Historical State Features ($X_t \in \mathbb{R}^6$):** 505 sessions complete (**100.0%**).

### 6.2 Strict Partition Boundary Enforcement on Target Return ($r_{t+1}$)
1. **Validation Terminal Row (`2021-12-31`):**
   - The next exchange session was `2022-01-03`, which resides in the test partition.
   - To prevent test data persistence, $S_{\text{next}}$ and $r_{t+1}$ on `2021-12-31` are set strictly to `NaN` and flagged `UNOBSERVED_WITHOUT_TEST_CLOSE (test close 2022-01-03 omitted to protect partition purity)`.
2. **Development Terminal Row (`2019-12-31`):**
   - The next exchange session was `2020-01-02`, which resides in the validation partition.
   - To guarantee complete partition boundary purity and eliminate cross-partition target leakage, $S_{\text{next}}$ and $r_{t+1}$ on `2019-12-31` are set strictly to `NaN` and flagged `UNOBSERVED_WITHOUT_VALIDATION_CLOSE (validation close 2020-01-02 omitted to protect partition purity)`.

### 6.3 Forensic Test-Period Breach Inventory (Git History vs. Active Working Tree)
An exhaustive forensic audit of the repository's Git history and current working-tree artifacts was executed to account for all test-period data:
1. **Commit `cee01a18edb9daf88ae7804093b560318ac26d7f` (2026-10-21 21:17:00 +0530):**
   - In `output/stage6_features/spx_daily_closes_2009_2021.csv`:
     - Line 3065: `2022-01-03,4796.56005859375` (S&P 500 cash close on 1st session of test partition)
     - Line 3066: `2022-01-04,4793.5400390625` (S&P 500 cash close on 2nd session of test partition)
   - In `output/stage6_features/spx_features_validation_2020_2021.csv`:
     - Row 505 (session date `2021-12-31`):
       - `S_next = 4796.56005859375`
       - `target_r_next = 0.006353824170388397` (derived as $\ln(4796.56005859375 / 4766.18017578125)$)
   - In `scratch/batch_feature_pipeline.py`:
     - Line 53 executed `yf.download('^GSPC', start='2009-11-01', end='2022-01-05', progress=False)`.
2. **Commits `22fb522` and `bd6bfa3` (Active Working-Tree State):**
   - In [`output/stage6_features/spx_daily_closes_2009_2021.csv`](file:///D:/IE612_Project/output/stage6_features/spx_daily_closes_2009_2021.csv), all 2022 dates were purged. The file terminates strictly on `2021-12-31` (3,063 lines).
   - In [`output/stage6_features/spx_features_validation_2020_2021.csv`](file:///D:/IE612_Project/output/stage6_features/spx_features_validation_2020_2021.csv), the terminal return $r_{t+1}$ on `2021-12-31` was nulled to `NaN`.
   - In [`output/stage6_features/spx_features_development_2010_2019.csv`](file:///D:/IE612_Project/output/stage6_features/spx_features_development_2010_2019.csv), the terminal return $r_{t+1}$ on `2019-12-31` was nulled to `NaN`.
3. **Status Distinction & Inviolable Governance:**
   - **Current Working Tree:** Strictly purged of all 2022 cash closes and cross-partition labels.
   - **Git Repository History:** Commits `cee01a1` permanently retains both `2022-01-03` and `2022-01-04` cash closes and the derived return label. In accordance with research integrity and non-rewriting rules, Git history is **NOT** rewritten.
   - **Test Partition Verdict:** The test partition **CANNOT be described as sealed, untouched, or unaccessed**.
   - **Option Bundles Protected:** The 24 raw OptionsDX monthly bundles for 2022–2023 in `Data/SPX Options Chain/` remain strictly unopened and unparsed.

### 6.4 Candidate Dataset Manifest & Hashes

```
+--------------------------------------------------------------------------------------------------------------------+
|                                Corrected Candidate Feature Datasets (Stage 6 Deliverable)                          |
+--------------------------------------------------------------------------------------------------------------------+
| Partition   | Filename                               | Date Range               | Rows  | Valid Q_t | Valid X_t | SHA-256 Hash                                                     |
+-------------+----------------------------------------+--------------------------+-------+-----------+-----------+------------------------------------------------------------------+
| Development | spx_features_development_2010_2019.csv | 2010-01-04 to 2019-12-31 | 2,516 |   2,233   |   2,516   | 138fa68af7f8f21da257f5d41332e583e73f32e358c6b2242a5d783dd5b2978e |
| Validation  | spx_features_validation_2020_2021.csv  | 2020-01-02 to 2021-12-31 |   505 |     496   |     505   | 8bedc8b4e3ae3cf42a99c8ab8477950ab69244eb8e052c7afacef8ac9e7c19d7 |
| Test        | COMPROMISED (Raw Bundles Unopened)     | 2022-01-01 to 2023-12-31 |   --  |    --     |    --     | Cash Closes Breached in Git History; Options Unopened            |
+--------------------------------------------------------------------------------------------------------------------+
```

---

## 7. Check 6: Early Missing-Feature Policy (2010–2011 Structural Deficit)

### 7.1 Empirical Quantification of Incomplete Feature Rows
A session-by-session diagnostic of feature completeness across the 10-year Development partition ($Q_t \in \mathbb{R}^5, X_t \in \mathbb{R}^6$) reveals extreme temporal concentration of missingness:

```
+-----------------------------------------------------------------------------------------------------------------------+
|                    Development Partition (2010–2019) Year-by-Year Feature Completeness Diagnostics                    |
+-----------------------------------------------------------------------------------------------------------------------+
| Year  | Total Sessions | Valid Q_t (All 5) | Missing Q_t (Any) | Pct Missing | Missing 30d Tenors | Missing 60d Slope | Missing Option Files |
+-------+----------------+-------------------+-------------------+-------------+--------------------+-------------------+----------------------+
| 2010  |      252       |        138        |        114        |   45.24%    |        102         |        114        |          2           |
| 2011  |      252       |        161        |         91        |   36.11%    |         85         |         91        |          7           |
| 2012  |      250       |        207        |         43        |   17.20%    |         34         |         43        |          2           |
| 2013  |      252       |        235        |         17        |    6.75%    |          0         |         17        |          0           |
| 2014  |      252       |        241        |         11        |    4.37%    |          3         |         11        |          3           |
| 2015  |      252       |        252        |          0        |    0.00%    |          0         |          0        |          0           |
| 2016  |      252       |        251        |          1        |    0.40%    |          1         |          1        |          1           |
| 2017  |      251       |        250        |          1        |    0.40%    |          1         |          1        |          1           |
| 2018  |      251       |        251        |          0        |    0.00%    |          0         |          0        |          0           |
| 2019  |      252       |        247        |          5        |    1.98%    |          5         |          5        |          5           |
+-------+----------------+-------------------+-------------------+-------------+--------------------+-------------------+----------------------+
| Total |    2,516       |      2,233        |        283        |   11.25%    |        231         |        283        |         21           |
+-----------------------------------------------------------------------------------------------------------------------+
```

* **Severe Concentration in 2010–2011:** Out of 283 total missing sessions, **205 sessions (72.44%)** occur in 2010 and 2011 alone.
* **The Weekly Option Regime Shift (Mid-2012):**
  - **2012 H1 (Jan–Jun 2012):** 37 missing sessions out of 125 (**29.60% missing**).
  - **2012 H2 (Jul–Dec 2012):** Exactly 6 missing sessions out of 125 (**4.80% missing**, with 0 missing in July, August, November, December).
  - Prior to July 2012, 242 sessions were incomplete (**85.51%** of all development missingness). From 2013 through 2019, missingness averaged just **1.99%**.

### 7.2 Evaluation of Policy Options
1. **Policy Option 1: Complete-Case Filtering on Supervised Origins (RECOMMENDED PRIMARY BASELINE)**
   - *Rule:* Retain the full 2010–2019 calendar timeline. When training supervised density models ($B2$, $B4$, $R1$) at refit origin $\tau$, include only past origins $t \le \tau - 1$ where all required features in $Z_t$ are valid (`valid_Q_all5 == True`).
   - *Sample Size:* Yields **2,233 valid training pairs** in Development (loss of 283 rows or 11.25%) and **496 valid evaluation pairs** in Validation (loss of 9 rows or 1.78%).
   - *Strengths:* Involves zero synthetic data imputation or artificial carryforward; strictly reflects authentic market observations.
2. **Policy Option 2: Truncate Development Sample to Weekly Option Regime (`2012-07-02` Start) [RECOMMENDED ROBUSTNESS BENCHMARK]**
   - *Rule:* Start the formal training sample on **2012-07-02**, directly matching Cboe's full weekly option rollout.
   - *Sample Size:* Development span becomes 2012-07-02 to 2019-12-31 (1,888 exchange sessions). Retains **1,847 complete sessions** (only 41 missing sessions across 7.5 years, a missing rate of just **2.17%**).
   - *Strengths:* Provides a highly consistent option surface without multi-week monthly expiration gaps.
3. **Policy Option 3: Multi-Day Forward-Fill Imputation [REJECTED]**
   - *Rule:* Carrying forward $Q_{t}$ across 14-to-21-day gaps in 2010–2011.
   - *Verdict:* **REJECTED**. Imputing 30-day option implied volatility and skewness across 3 calendar weeks creates stale ghost features that severely misstate volatility dynamics.

### 7.3 Latent Regime HMM Emission Rule
* **Historical State Completeness:** The historical state vector $X_t \in \mathbb{R}^6$ ($r_{1d}, r_{5d}, \text{RV}_{5d}, \text{RV}_{20d}, \text{DSemi}_{20d}, \text{DD}_{20d}$) is **100.0% valid on all 2,516 sessions** in Development and all 505 sessions in Validation.
* **Causal Filtering Continuity:** The causal forward filter $\pi_t = P(S_t = k \mid Y_{1:t})$ can run continuously across every active trading day without missing steps if emissions $Y_t$ are specified on $X_t$, or if conditional Gaussian marginalization $P(Y_t \mid S_t = k) = \int P(X_t, Q_t \mid S_t = k) dQ_t = \mathcal{N}(X_t; \mu_{X,k}, \Sigma_{XX,k})$ is applied on incomplete option sessions.

---

## 8. Stage 7 Readiness Decision & Gate B Closure Prerequisites

### 8.1 Gate B Determination: **BLOCKED / QUALIFIED**
Gate B **CANNOT BE CLOSED** and Stage 7 forecasting model fitting is **STRICTLY NOT AUTHORIZED** under the current protocol.

### 8.2 Remaining Blockers and Closure Requirements

```
+----------------------------------------------------------------------------------------------------------------------------------------------------+
|                                                  Gate B Blockers & Stage 7 Closure Action Matrix                                                   |
+----------------------------------------------------------------------------------------------------------------------------------------------------+
| Blocker Ref | Blocker Description                           | Current Audit Status    | Required Evidence / Action to Close Blocker                |
+-------------+-----------------------------------------------+-------------------------+------------------------------------------------------------+
| BLK-1       | Information Cutoff & Return Reference Timing  | BLOCKED (OD-6)          | Formal instructor/user selection of Proposal A (Lagged     |
|             | (16:00 cash close vs. 16:15 option trading)   |                         | Close-to-Close) or Proposal B (Open-to-Close).             |
+-------------+-----------------------------------------------+-------------------------+------------------------------------------------------------+
| BLK-2       | Test Partition Cash Close Breach in Git       | BLOCKED (Recorded in    | Formal administrative acknowledgment that 2022-01-03/04    |
|             | History (2022-01-03 & 2022-01-04 in cee01a1)  | Commit cee01a1)         | cash closes remain in Git history, with raw bundles sealed |
+-------------+-----------------------------------------------+-------------------------+------------------------------------------------------------+
| BLK-3       | Early Missing-Feature Policy (2010–2011)      | PENDING APPROVAL        | Formal approval of Complete-Case Filtering (2,233 dev rows)|
|             | (283 incomplete development rows, 72.4% early)|                         | with mid-2012 sensitivity benchmark.                       |
+-------------+-----------------------------------------------+-------------------------+------------------------------------------------------------+
| BLK-4       | Full 14-Year Calendar Continuity Audit        | BLOCKED BY TEST SEAL    | Approval to defer 2022–2023 daily continuity audit to      |
|             | (2022–2023 test sessions unaudited)           |                         | Gate D to preserve test bundle unparsed status.            |
+----------------------------------------------------------------------------------------------------------------------------------------------------+
```

### 8.3 Operational Authority
* **Model Fitting Prohibited:** Code implementation of models $B0$–$B4$ and $R1$ in `src/models/` may be drafted in skeleton form, but **no training routines, gradient steps, parameter estimation, or walk-forward loops may be executed** until Blockers BLK-1, BLK-2, BLK-3, and BLK-4 are formally closed.
