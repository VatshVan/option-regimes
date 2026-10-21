# Gate B Audit Report: Calendar Continuity, Early Strike Breadth, Quote Timing, Rate Ingestion, and Candidate Feature Datasets

**Document Status:** Working Audit Report & Quality Review (Stage 6 / Gate B Deliverable)  
**Date:** 21 October 2026 (Revised & Corrected)  
**Author:** Antigravity (Advanced Agentic Coding Pair Programmer)  
**Governing Documents:** [research_protocol.md](file:///D:/IE612_Project/research_protocol.md), [stage5_modeling_specification.md](file:///D:/IE612_Project/stage5_modeling_specification.md), [stage4_feature_pipeline.md](file:///D:/IE612_Project/stage4_feature_pipeline.md), [data_feasibility_audit.md](file:///D:/IE612_Project/data_feasibility_audit.md), [implementation.md](file:///D:/IE612_Project/implementation.md)

---

## 1. Executive Summary & Gate B Determination

### 1.1 Gate B Determination: **BLOCKED / QUALIFIED (CANNOT BE CLAIMED FULLY PASSED)**
In accordance with project governance, empirical audit findings, and anti-leakage disciplines:
1. **Test Partition Boundary Crossing & Disclosure:** While the 24 raw OptionsDX monthly bundles for 2022–2023 remained unopened and unparsed, the cash index close dataset (`^GSPC`) was initially downloaded through January 2022, thereby accessing the **2022-01-03 closing price (`4796.56`)** across the test boundary to compute the terminal validation return $r_{t+1}$. Therefore, **the test partition seal cannot be claimed as intact or untouched**. In the corrected datasets, the terminal validation return on `2021-12-31` has been set strictly to `NaN` (`UNOBSERVED_WITHOUT_TEST_CLOSE`), and cached cash closes have been truncated to $\le \text{2021-12-31}$.
2. **Datasets are Candidate Outputs, NOT Permanently Frozen:** Neither the Development nor Validation feature datasets are treated as permanently frozen. They serve as audit-stage candidate datasets pending resolution of the information cutoff, rate ingestion policy, and test boundary rules.
3. **Information Cutoff Gate (OD-6) Unresolved:** While vendor readtimes uniformly report `'16:00'`, OptionsDX documentation does not establish whether quotes reflect 16:00:00 ET instantaneous snapshots or 16:15:00 ET closing quotes. Put-call parity guarantees internal surface consistency, but does not prove synchronization with the 16:00:00 ET cash equity close $S_t$. Operational model training remains **strictly gated**.
4. **Early-Sample Structural Deficit (2010–2012):** Due to standard monthly expiration cycles prior to mid-2012, 30-day constant-maturity bracketing fails on **76.4% of sessions in 2010** and **68.6% of sessions in 2011**. Complete 5-feature option vectors ($Q_t \in \mathbb{R}^5$) are missing on **283 sessions (11.25%)** in the Development partition. Furthermore, call-wing liquidity truncates at $1.08–1.12 \times S$, failing the $K_{\max}/S \ge 1.15$ span on $>93\%$ of early sessions.
5. **Session Continuity Fails Annual 1.0% Threshold in 5 Years:** While aggregate 12-year missingness is $0.993\%$, annual missingness exceeds the 1.0% tolerance in five separate calendar years (2011, 2014, 2019, 2020, 2021). Continuity cannot be described as a clean pass across every year.

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

## 4. Check 3: Quote Timestamps and Cash Synchronization

* **Uniform Vendor Readtime:** Across all 3,021 sessions in 2010–2021, `QUOTE_READTIME` is stamped `'16:00'`.
* **Absence of Early Close Timestamps:** Scheduled half-days (e.g. Black Friday, Christmas Eve) never report `'13:00'`.
* **The 16:00 vs. 16:15 ET Lookahead Wedge:** S&P 500 cash equity closes strictly at 16:00:00 ET ($S_t$). SPX options historically traded until 16:15:00 ET. If option quotes reflect 16:15 ET trading, $Q_t$ incorporates 15 minutes of post-close news, leaking forward-looking information into the target return denominator $r_{t+1} = \ln(S_{t+1}/S_t)$. Put-call parity alone proves internal quote consistency, not cash synchronization.
* **Status:** Operational model training remains **strictly gated** until quote timing is empirically verified or an alternative cutoff is formally pre-specified.

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
   - The next exchange session was `2022-01-03`, which resides in the sealed test partition.
   - To prevent test data persistence, $S_{\text{next}}$ and $r_{t+1}$ on `2021-12-31` are set strictly to `NaN` and flagged `UNOBSERVED_WITHOUT_TEST_CLOSE`.
2. **Development Terminal Row (`2019-12-31`):**
   - The next exchange session was `2020-01-02`, which resides in the validation partition.
   - Flagged explicitly as `CROSS_PARTITION_LABEL (calculated using validation close 2020-01-02)`.
3. **Cash Close Dataset Truncation:**
   - [`output/stage6_features/spx_daily_closes_2009_2021.csv`](file:///D:/IE612_Project/output/stage6_features/spx_daily_closes_2009_2021.csv) was truncated to remove all 2022 dates, terminating strictly on `2021-12-31` (3,063 closes from 2009-11-02 to 2021-12-31).

### 6.3 Candidate Dataset Manifest & Hashes

```
+--------------------------------------------------------------------------------------------------------------------+
|                                Corrected Candidate Feature Datasets (Stage 6 Deliverable)                          |
+--------------------------------------------------------------------------------------------------------------------+
| Partition   | Filename                               | Date Range               | Rows  | Valid Q_t | Valid X_t | SHA-256 Hash                                                     |
+-------------+----------------------------------------+--------------------------+-------+-----------+-----------+------------------------------------------------------------------+
| Development | spx_features_development_2010_2019.csv | 2010-01-04 to 2019-12-31 | 2,516 |   2,233   |   2,516   | 201679a93c387507d6766283b44036f736e40920088feebbf5afb3dad6a96f11 |
| Validation  | spx_features_validation_2020_2021.csv  | 2020-01-02 to 2021-12-31 |   505 |     496   |     505   | 8bedc8b4e3ae3cf42a99c8ab8477950ab69244eb8e052c7afacef8ac9e7c19d7 |
| Test        | SEALED (2022-2023)                     | 2022-01-01 to 2023-12-31 |   --  |    --     |    --     | UNPARSED / SEALED                                                |
+--------------------------------------------------------------------------------------------------------------------+
```

---

## 7. Gate B Final Recommendation & Required Conditions Before Modeling

Work may not proceed to forecasting model fitting (Stage 7) until the following open conditions are formally resolved:
1. **Resolution of Information Cutoff Gate (OD-6):** Empirically verify whether OptionsDX `'16:00'` quotes reflect 16:00:00 ET instantaneous snapshots or 16:15:00 ET closing quotes, or specify a defensible cutoff adjustment.
2. **Administrative Decision on Test Calendar Audit:** Confirm whether test partition continuity should be formally audited at Gate D or if an administrative waiver applies.
3. **Handling of 2010–2011 Structural Missingness:** Approve whether walk-forward training will omit the 283 incomplete sessions in 2010–2011 or start expanding walk-forward training in mid-2012 following the weekly option expansion.
