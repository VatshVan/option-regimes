# Data Feasibility Audit: Stage 2 Assessment for SPX Options Study

**Project Title:** Regime-Conditioned Mapping from Option-Implied Risk-Neutral Information to Physical Return Distributions  
**Course & Scope:** IE 612 (Introduction to Financial Engineering), 1-Month Empirical Project  
**Document Status:** Stage 2 Data Feasibility Audit (Version 1.0, 21 October 2026)  
**Governing Documents:** [`implementation.md`](file:///D:/IE612_Project/implementation.md), [`research_protocol.md`](file:///D:/IE612_Project/research_protocol.md)  
**Inspection Mode:** Metadata, file sizes, folder names, and representative sample findings only (no new raw data files opened; no full-dataset row scanning).

---

## 1. Executive Summary & Gate A Recommendation

### Gate A Recommendation: **QUALIFIED PASS (Pilot Quality Check Completed; Conditional Approval for Feature Pipeline Specification)**

The local data inventory confirms that the project possesses a complete 14-year calendar inventory of monthly End-of-Day (EOD) options files for the S&P 500 index (SPX), covering **January 2010 through December 2023** (168 contiguous monthly files, totaling 5.28 GB).

A targeted empirical audit on two representative dates from 2020 (calm session `2020-01-15` and crisis session `2020-03-03`) confirms that:
1. **Schema & Timestamps:** The 33-column schema trims cleanly and quotes uniformly report a `16:00` timestamp on these two dates.
2. **Contract-Wise OTM Screening:** Screening puts on the put side ($K < F_t$) and calls on the call side ($K \ge F_t$) preserves 99 to 278 liquid strikes across the 20–50 DTE range, avoiding the over-pruning flaw of row-level filtering.
3. **Maturity Support:** Available tenors cleanly bracket a constant 30-day horizon on both dates.
4. **Martin (2017) SVIX Computation:** Implemented using Martin's forward-normalized formula (unweighted by $1/K^2$, normalized by $F_{t,T}^2$ with standard composite trapezoidal weights). Because the retained quotes span a finite strike range without tail extrapolation, the values are discrete finite-grid estimates (yielding 30-day SVIX of **12.00%** on the calm date vs. official VIX 12.42%, and **34.88%** on the stress date vs. official VIX 36.82%). The numerical gaps ($-0.42$ vol pts and $-1.94$ vol pts) are documented strictly as empirical observations on these two dates, without asserting an unverified causal link to skewness or crisis put demand or implying full integral coverage or equivalence with Cboe VIX.
5. **Cost-of-Carry Forward Check:** Inferred synthetic forwards match theoretical cost-of-carry $S_t e^{(r-q)T}$ within $+0.91$ pts (implied $q = 1.41\%$) on the calm date and $-0.34$ pts (implied $q = 2.08\%$) on the stress date. Differences between vendor `UNDERLYING_LAST` and cash closes are $+0.47$ pts and $-0.63$ pts.

**Scope of Approval & Remaining Unknowns:**
This pass is strictly **qualified**. The Stage 3 audit verified parsing mechanics, synthetic forward parity, and Martin SVIX integration on the two pilot dates only. While feature extraction algorithms for QSkew, QKurt, ATM IV, term-structure slope, and historical features $X_t$ were subsequently implemented and demonstrated in Stage 4 for these same two dates, full-sample surface extraction across 2010–2021, full 14-year session continuity, early-sample strike density (2010–2012), and historical quote timestamps (16:00 vs. 16:15 ET) remain unverified. Full-sample model estimation remains strictly conditioned on completing these remaining audit checks.

---

## 2. Complete Inventory of Downloaded Data

An audit of directory hierarchies, file counts, naming conventions, and file sizes was performed across the `Data/` subfolders without opening or reading raw data rows.

### 2.1 Inventory Summary Table

| Folder Name | Underlying Asset | Subdirectory Structure | File Count | Apparent Date Span | Total Size | File Size Range |
|---|---|---|---|---|---|---|
| **`SPX Options Chain/`** | S&P 500 Index (`SPX`) | 22 subdirectories: <br>• 11 annual bundles (2010–2020)<br>• 11 quarterly bundles (2021Q1–2023Q4) | **168 `.txt` files** | **2010-01 to 2023-12** (168 / 168 months) | **5,280.99 MB** (~5.28 GB) | **5.04 MB** (2010-02) to **72.10 MB** (2023-11) |
| **`SPY Options Chain/`** | SPDR S&P 500 ETF (`SPY`) | 20 subdirectories: <br>• 12 annual bundles (2010–2021)<br>• 8 quarterly bundles (2022Q1–2023Q4) | **168 `.txt` files** | **2010-01 to 2023-12** (168 / 168 months) | **3,203.50 MB** (~3.20 GB) | **5.56 MB** (2010-08) to **40.25 MB** (2023-11) |
| **`VIX/`** | Cboe Volatility Index Options | 22 subdirectories: <br>• 11 annual bundles (2010–2020)<br>• 11 quarterly bundles (2021Q1–2023Q4) | **168 `.txt` files** | **2010-01 to 2023-12** (168 / 168 months) | **395.53 MB** (~0.40 GB) | **0.78 MB** (2010-08) to **5.40 MB** (2023-10) |
| **TOTAL** | — | **64 subdirectories** | **504 `.txt` files** | **14 full calendar years** | **8,880.02 MB** (~8.88 GB) | — |

### 2.2 Apparent Date Coverage and Gap Assessment
* **Completeness by Filename:** Comparing extracted filenames against the expected sequence of months $\{YYYYMM : 2010 \le YYYY \le 2023, 1 \le MM \le 12\}$ reveals **zero missing calendar months**. Every year contains exactly 12 monthly files (`01` through `12`).
* **Packaging Evolution:** Earlier years (2010 through 2020/2021) are stored in single annual archive folders with random hash suffixes (e.g., `spx_eod_2010-hixkhi`), each containing all 12 monthly files. Starting in 2021/2022, OptionsDX transitioned to quarterly delivery folders (e.g., `spx_eod_2022q1-ff0r18`), each containing 3 monthly files.
* **File Size Progression:** In `SPX Options Chain`, monthly file size increases by more than 14-fold over the sample:
  * 2010: ~5.0 MB to ~6.5 MB per month.
  * 2015: ~18.0 MB to ~24.0 MB per month.
  * 2019: ~39.0 MB to ~46.0 MB per month.
  * 2023: ~60.0 MB to ~72.1 MB per month.
  This reflects the massive real-world expansion of Cboe option listings, including the introduction of weekly contracts, Wednesday/Monday expiries, and Tuesday/Thursday daily expiries, rather than data corruption.
* **Essential Caveat:** Filename presence and non-zero byte size establish only that archive files were successfully downloaded and unpacked. **Filename coverage does not prove that every trading session is present, that quotes are synchronous, or that valid, liquid strike grids exist within each file.**

---

## 3. Assessment of SPX Date Span for Train / Validation / Test Periods

### 3.1 Feasibility of the Proposed ~71.4% / 14.3% / 14.3% Calendar Split
The 14-year span (168 monthly bundles) supports the calendar-aligned split design specified in [`research_protocol.md`](file:///D:/IE612_Project/research_protocol.md):

```
                                SPX Sample Timeline (2010 - 2023)
+-------------------------------------------------------------+--------------------+--------------------+
|                Training Window (~71.4%)                     | Validation (~14.3%)| Held-Out Test (~14%)|
|                   2010-01-01 to 2019-12-31                  |2020-01-01to2021-12 |2022-01-01to2023-12 |
|                     (120 monthly files)                     | (24 monthly files) | (24 monthly files) |
+-------------------------------------------------------------+--------------------+--------------------+
  Market Regimes:                                               Market Regimes:      Market Regimes:
  - 2010 Flash Crash & Euro Debt                                - 2020 Covid Crash   - 2022 Rate Shock
  - 2011 US Debt Downgrade                                      - 2020-21 Recovery     & Bear Market
  - 2015-16 Oil Shock / China Deval                             - Low-rate Tech Bull - 2023 Disinflation
  - 2017 Historic Volatility Low                                                       & AI Rally
  - 2018 Volmageddon (Feb) & Q4 Crash
```

1. **In-Sample Training Window (2010–2019, 10 Full Calendar Years, 120 Months, ~71.4% of Span):**
   * Spans multiple distinct macroeconomic and volatility regimes: acute sovereign/market stress (2010, 2011, late 2018), sustained low-volatility grinding bull markets (2012–2014, 2017), and volatility spikes (February 2018).
   * Provides substantial multi-cycle depth to estimate HMM transition dynamics and train baseline density models without overfitting.
2. **Validation Window (2020–2021, 2 Full Calendar Years, 24 Months, ~14.3% of Span):**
   * Spans extreme crisis dynamics (March 2020 Covid shock: VIX reaching 82.69) and the subsequent high-momentum recovery.
   * Provides an ideal stress-testing environment for hyperparameter tuning ($K=2$ vs. $K=3$ regimes, regularization, neural layer capacity) without touching the test set.
3. **Held-Out Test Window (2022–2023, 2 Full Calendar Years, 24 Months, ~14.3% of Span):**
   * Spans the 2022 aggressive Federal Reserve interest-rate hiking cycle / equity bear market, followed by the 2023 disinflationary expansion.
   * Completely held out until all model architectures and cleaning thresholds are frozen. *(Historical Stage 2 Context: At the time of Stage 2 audit, the test partition was designed as untouched. Note: In Stage 6, January 3 and 4, 2022 cash closes were accessed and committed in commit `cee01a1` Git history; raw 2022–2023 option bundles remain unopened).*

*Note on Calendar Partitioning vs. Exact Session Counts:* This partition is aligned with complete calendar years: 2010–2019 (10 years, ~71.4%), 2020–2021 (2 years, ~14.3%), and 2022–2023 (2 years, ~14.3% of the calendar-year span). It avoids cutting across annual macroeconomic boundaries. Exact trading session counts will be computed directly from the full calendar audit without assuming nominal session totals in advance.

### 3.2 Gaps and Limitations Unresolved by Metadata
While the macro calendar span is ideal, metadata alone cannot resolve:
1. **Intra-Month Date Missingness:** Metadata cannot confirm whether all ~252 exchange trading days per year are present without gaps exceeding the protocol's 1.0% tolerance.
2. **Early Sample Strike Breadth (2010–2012):** Monthly files in 2010 are ~5 MB, compared to ~70 MB in 2023. We cannot verify from file size alone whether 2010 contains the minimum liquid strike coverage (at least 30 liquid strikes spanning $0.85 \le K/S \le 1.15$ in the 20–50 DTE bucket) required to compute Bakshi et al. (2003) skewness and Martin (2017) SVIX without quadrature discretization breakdown.
3. **Internal File Corruption:** File size proves bytes exist on disk, but cannot detect internal parsing anomalies (e.g., malformed lines, mid-file null bytes, or truncated headers).

---

## 4. Timing Reconciliation, Information Cutoff, and Look-Ahead Risk

### 4.1 The 16:00 ET Quote Timestamp Assumption
* **Inspected Sample Finding:** The representative October 2023 files inspected in [`implementation.md`](file:///D:/IE612_Project/implementation.md#L88-L94) show a `16:00` quote timestamp (`QUOTE_READTIME = '2023-10-02 16:00'`).
* **Hazard of Generalization:** It is an unverified assumption that all 168 files from 2010 to 2023 adhere to a 16:00 ET snapshot convention. OptionsDX capture scripts, vendor upstream sources, or Cboe exchange reporting conventions may have varied across product vintages (especially across the pre-2015 and post-2020 eras).
* **Early-Close Sessions:** On scheduled half-days (e.g., 13:00 ET closes on Thanksgiving Friday or Christmas Eve), if vendor files report 16:00 ET or stale morning quotes, timestamps must be audited.

### 4.2 Target Alignment with Information Cutoff $\mathcal{F}_t$
The primary target return is the next-day close-to-close log return:
$$r_{t+1} = \log\left(\frac{S_{t+1}}{S_t}\right)$$
where $S_t$ and $S_{t+1}$ are the official closing values of the underlying S&P 500 cash equity index (`^GSPC`) recorded at the 16:00:00 ET equity market close.

For the forecasting pipeline to remain strictly causal, the feature set $[Q_t, X_t, \pi_t]$ must belong strictly to $\mathcal{F}_t$, the information filtration generated up to the close of date $t$.

### 4.3 Why Put-Call Parity Synthetic Forward Does NOT Eliminate Alignment/Leakage Risk

> [!CAUTION]
> Section 2.4 of [`research_protocol.md`](file:///D:/IE612_Project/research_protocol.md#L97-L108) asserts that inferring a synthetic forward $F_{t,\tau} = K^* + e^{r\tau}(C - P)$ directly from ATM call and put quotes "guarantees that the underlying reference level is internally consistent with the option quotes." 
> 
> While mathematically true for relative strike moneyness *within the option chain*, **estimating a synthetic forward does not prove quote/index synchronization and does not remove look-ahead risk relative to the physical return target.**

There are three distinct failure modes that put-call parity cannot resolve:
1. **The 15-Minute Information Leakage Problem:**
   Cboe SPX options historically traded until 16:15:00 ET (15 minutes after the cash equity market closed at 16:00:00 ET). If an OptionsDX snapshot reflects quotes traded between 16:00 and 16:15 ET:
   * The synthetic forward $F_t$ correctly reflects market expectations at **16:15 ET**.
   * However, the physical return target $r_{t+1} = \log(S_{t+1}/S_t)$ has its denominator $S_t$ frozen at **16:00 ET**.
   * Any market-moving news occurring between 16:00 and 16:15 ET is embedded in $Q_t$ (via $F_t$ and option midpoints), but is *not yet reflected* in $S_t$.
   * This generates an artificial, un-tradable predictive signal for $r_{t+1}$—a form of look-ahead leakage.
2. **Dependence on Discount Factor $e^{-r\tau}$:**
   The parity formula $F_{t,\tau} = K^* + e^{r\tau}(C - P)$ requires an exogenous risk-free interest rate $r$. If the interest rate input is mis-specified, stale, or does not reflect institutional funding rates (e.g., SOFR vs. CMT), the inverted forward is shifted, distorting the implied cost-of-carry.
3. **Bid-Ask Bounce in Wide Spreads:**
   At ATM strikes, if bid-ask spreads are wide or dealer quotes are asynchronous, $(C - P)$ fluctuates due to quote bounce rather than true shifts in forward expectations.

**Conclusion for Protocol:** The protocol must explicitly state that put-call parity ensures internal surface consistency across strikes, but external synchronization with the cash index close $S_t$ must be empirically verified by comparing the implied forward with cash close $S_t$ across normal dates.

---

## 5. Quote Filters and Maturity Rules vs. Sample Evidence

A critical examination of the representative October 2023 sample findings recorded in [`implementation.md`](file:///D:/IE612_Project/implementation.md#L88-L94) validates several design choices while exposing an operational flaw in the protocol:

### 5.1 Supported Design Choices
1. **Exclusion of Very Short Maturities ($DTE \le 1$):**
   The sample contains expiry-day contracts ($DTE = 0$) where time decay ($\Theta$) explodes, bid-ask spreads widen dramatically, and quotes reflect immediate settlement payoff rather than continuous distribution dynamics. The protocol’s provisional exclusion of $DTE \le 1$ and focus on $20 \le DTE \le 50$ is strongly supported.
2. **Discarding Vendor Greeks and Precomputed IV:**
   The inspected sample shows blank values (`' '`) in `C_IV`, `P_IV`, and delta columns on out-of-the-money strikes, with completely undocumented interest rate and dividend assumptions. The protocol's rule to discard vendor calculations and independently recompute midpoints, forward levels, and model-free moments is mandatory.
3. **Absence of Open Interest:**
   `OPEN_INTEREST` is confirmed absent. The protocol's strategy of substituting relative spread bounds ($(Ask - Bid)/Mid \le 0.35$) and non-zero bid constraints for open interest filtering is validated as the only feasible mechanism in this dataset.

### 5.2 Protocol Filter Flaw: Row-Level vs. Contract-Level Screening

> [!WARNING]
> **Identified Protocol Conflict:** Section 4.2 of [`research_protocol.md`](file:///D:/IE612_Project/research_protocol.md#L162-L177) specifies:
> `Rule 1: Non-Zero Positive Bid Filter: C_BID > 0.05 and P_BID > 0.05`
> 
> Because OptionsDX stores quotes in a **wide format** (pairing Call and Put quotes for identical strikes on the same row):
> * For deep out-of-the-money puts ($K \ll F_t$), the put is actively traded with a liquid bid, but the corresponding deep in-the-money call on that strike frequently has a zero bid ($C\_BID = 0.00$).
> * Conversely, for deep out-of-the-money calls ($K \gg F_t$), the call has a liquid bid, but the corresponding deep in-the-money put has a zero bid ($P\_BID = 0.00$).
> 
> If Rule 1 requires **both** `C_BID > 0.05` **and** `P_BID > 0.05` on that row, **the pipeline would drop all deep OTM puts and deep OTM calls!** This would truncate the option wings, severely underestimating risk-neutral kurtosis and skewness.

**Required Protocol Correction:** Bid and spread filtering must be evaluated **contract-wise by moneyness** after reshaping to long format:
* For OTM Puts ($K < F_t$): Enforce $P\_BID > 0.05$ and $(P\_ASK - P\_BID)/P\_MID \le 0.35$. Ignore `C_BID`.
* For OTM Calls ($K \ge F_t$): Enforce $C\_BID > 0.05$ and $(C\_ASK - C\_BID)/C\_MID \le 0.35$. Ignore `P_BID`.
* Only the single ATM strike ($K \approx F_t$) used for parity forward inversion requires *both* valid Call and Put quotes.

---

## 6. Primary MVP Scope: Distinguishing SPX, SPY, and VIX

### 6.1 VIX Options vs. VIX Index History
* **The Reality in `Data/VIX`:** Metadata and sample inspection confirm that `Data/VIX/` contains **options written on the VIX index** (`UNDERLYING_LAST = 23.17`, strikes from 10 to 80+, DTE, call/put bids).
* **Critical Finding:** It does **NOT** contain the daily closing historical time series of the VIX cash index.
* **MVP Role:** VIX options are completely irrelevant for the primary SPX physical return forecasting model. To obtain daily VIX closing levels for observable state conditioning ($X_t$) or external validation anchoring, the project must download the free, official Cboe VIX history file directly from the Cboe CDN:
  `https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv`
  VIX options in `Data/VIX` must be formally excluded from the primary pipeline.

### 6.2 SPY Options Chain vs. SPX Options Chain
* **The Reality in `Data/SPY Options Chain`:** Contains 168 monthly EOD option files for the SPDR S&P 500 ETF (`SPY`), sharing the 33-column wide schema.
* **Critical Distinction:** SPY options are **American-style options** written on an exchange-traded fund. They feature:
  1. Early-exercise risk (particularly for dividend capture on high-delta calls or deep ITM puts).
  2. Cash dividend payments that cause discrete price drops on ex-dividend dates.
  3. Black–Scholes / European model-free moment formulas do not strictly hold without complex early-exercise adjustments (e.g., Bjerksund-Stensland or binomial trees).
* **MVP Role:** In contrast, SPX options are **European-style, cash-settled index options** with no early exercise. SPX is the universal academic benchmark for risk-neutral density research ([Ulrich et al., 2019](file:///D:/IE612_Project/Papers/ssrn_id3437281_code3012080.pdf); [Martin, 2017](file:///D:/IE612_Project/SPX_data_research.md#L196)).
* **Verdict:** SPY options must be **strictly excluded from the primary MVP**. They are reserved exclusively as an optional, secondary robustness universe if required by course supervisors.

---

## 7. Operational Feasibility of Splits, Rates, and Portfolio Simulation

1. **Chronological Splits:** **Feasible in Principle.** The presence of 168 contiguous monthly files permits an approximate 71.4% / 14.3% / 14.3% partition by calendar-year span (2010–2019 [10 full calendar years], 2020–2021 [2 full calendar years], 2022–2023 [2 full calendar years]). Exact session counts will be computed directly from the full calendar audit without assuming nominal totals.
2. **Interest-Rate Inputs:** **Feasible via Public St. Louis FRED / Market T-Bills.** Daily US Treasury bill rates (`^IRX` or FRED `DTB3`, `DGS1MO`, `DGS3MO`) are free and accessible. Linearly interpolating between available tenors provides the required discount rate $r$.
3. **Optional Portfolio Step:** **Feasible as a Simple Index/Cash Rule.** A 1-asset volatility-targeting strategy (allocating $w_t \in [0, 1]$ between cash and the S&P 500 with 5 bps transaction costs) requires no complex optimizer and can be computed in seconds from predicted physical variances $\widehat{\sigma}_{t+1}^2$. It remains strictly secondary.
4. **Unresolved Factors to Monitor:**
   * *Licensing & Redistribution:* OptionsDX terms bar redistribution of raw CSV files. `.gitignore` must permanently exclude `Data/` from version control.
   * *Course Rubric:* The course instructor must confirm whether portfolio backtesting is mandatory for the course grade or purely illustrative.
   * *Compute Budget:* Re-fitting an HMM and neural mixture density model every 21 sessions over a 14-year walk-forward backtest involves ~168 refits. A lightweight Student-$t$ location-scale model runs in minutes; a multi-component neural MDN could require several hours and should be scoped conservatively.

---

## 8. Protocol Discrepancies and Proposed Replacement Wording

To maintain scientific integrity without silently rewriting [`research_protocol.md`](file:///D:/IE612_Project/research_protocol.md), the following conflicts and exact replacement wordings are identified:

### Conflict 1: Row-Wise vs. Contract-Wise Bid Filtering
* **Current Protocol Text ([`research_protocol.md`, Section 4.2](file:///D:/IE612_Project/research_protocol.md#L162-L177)):**
  > `Rule 1: Non-Zero Positive Bid Filter: C_BID > 0.05 and P_BID > 0.05`
* **Identified Problem:** Drops wide-format rows where the OTM contract is valid but the opposite-side ITM contract has a zero bid, truncating the option wings.
* **Proposed Exact Replacement Wording for Section 4.2:**
  > *"Rule 1 (Contract-Wise Positive Bid Filter): Option screening must be executed contract-wise according to moneyness after identifying the synthetic forward $F_{t,\tau}$. For out-of-the-money puts ($K < F_{t,\tau}$), require $P\_BID > \$0.05$ and relative spread $(P\_ASK - P\_BID)/P\_MID \le 0.35$, regardless of $C\_BID$. For out-of-the-money calls ($K \ge F_{t,\tau}$), require $C\_BID > \$0.05$ and relative spread $(C\_ASK - C\_BID)/C\_MID \le 0.35$, regardless of $P\_BID$. The simultaneous requirement $C\_BID > \$0.05$ and $P\_BID > \$0.05$ is enforced solely for the single at-the-money strike ($K \approx F_{t,\tau}$) utilized for put-call parity forward inversion."*

### Conflict 2: Put-Call Parity and Timestamp Synchronization
* **Current Protocol Text ([`research_protocol.md`, Section 2.4](file:///D:/IE612_Project/research_protocol.md#L97-L108)):**
  > *"This guarantees that the underlying reference level is internally consistent with the option quotes."*
* **Identified Problem:** Overstates what parity achieves. It synchronizes strikes internally to an implied forward, but does not prove synchronization with the external cash index close $S_t$ or remove 15-minute look-ahead if quotes were recorded at 16:15 ET.
* **Proposed Exact Replacement Wording for Section 2.4:**
  > *"Inverting the synthetic forward $F_{t,\tau}$ via at-the-money put-call parity guarantees internal moneyness consistency across strikes within the option snapshot. However, it does not by itself prove synchronization with the 16:00:00 ET cash equity close ($S_t$) or eliminate potential 15-minute look-ahead if the options snapshot reflects 16:15:00 ET Cboe market closes. Therefore, Gate A must audit the empirical difference $|F_{t,\tau} - S_t e^{(r-q)\tau}|$ against theoretical cost-of-carry bounds and verify quote timestamps across sample dates."*

### Conflict 3: Clarification of Universe Scope (Exclusion of VIX and SPY)
* **Current Protocol Text ([`research_protocol.md`, Section 1.1](file:///D:/IE612_Project/research_protocol.md#L15)):**
  > Mentions SPX index options, but does not explicitly document the status of the local `Data/VIX` and `Data/SPY Options Chain` folders.
* **Proposed Addition to Section 1.1:**
  > *"Scope Delimitation on Local Data Folders: The local `Data/SPY Options Chain` folder contains American-style ETF options and is strictly excluded from the primary MVP. The `Data/VIX` folder contains options written on the VIX, not historical cash VIX index levels; it is excluded from the MVP. Daily cash VIX and SKEW benchmarks must be obtained from official public Cboe CDN time series."*

---

## 9. Concluding Summary

### 9.1 What Metadata and Sample Evidence Supports
1. **Macro Calendar Completeness:** Exactly 168 monthly files exist for SPX, covering every calendar month from January 2010 through December 2023 without a single missing month.
2. **Sample Depth for ~71.4% / 14.3% / 14.3% Calendar Partition:** The 14 full calendar years provide substantial historical coverage across training (2010–2019, 10 yrs), validation (2020–2021, 2 yrs), and held-out test (2022–2023, 2 yrs; raw option bundles unopened; test cash close breach recorded in commit cee01a1) windows, spanning diverse market cycles.
3. **Appropriate Wide Schema for European Parity:** Contract-level bid and ask quotes exist on paired call/put rows with underlying levels, enabling synthetic forward extraction and midpoint quadrature.
4. **Need to Discard Vendor Calculations:** Precomputed IV and Greeks display gaps and opaque modeling, confirming that moments must be computed independently from clean quotes.
5. **Volume and Spread as Open Interest Proxy:** Missing open interest is confirmed; relative bid-ask spread and non-zero bid constraints are supported as feasible proxies.

### 9.2 What Remains Unverified
1. **Intra-Month Trading Session Continuity:** Whether any calendar month suffers from dropped trading sessions exceeding the 1.0% protocol tolerance.
2. **Early-Year Strike Density (2010–2012):** Whether 2010–2012 monthly files (~5 MB) contain sufficient liquid OTM strikes across $0.85 \le K/S \le 1.15$ to avoid quadrature discretization failure.
3. **Timestamp Consistency Across Eras:** Whether all historical files adhere to the 16:00 ET snapshot convention observed in the October 2023 sample, or if earlier vintages reflect 16:15 ET option closes.
4. **External Cash Synchronization:** Whether the inferred synthetic forward $F_{t,\tau}$ matches the theoretical cost-of-carry band around cash close $S_t$ on normal dates.
5. **External Benchmark Behavior Across Time:** How extracted SVIX behaves relative to Cboe volatility series across the full sample, recognizing that SVIX (simple variance swap) and VIX (log-contract variance) are distinct theoretical quantities.

### 9.3 The Smallest Next Authorized Data Check Needed
Before coding model pipelines or constructing full 14-year feature matrices, execute a **strictly bounded Gate A Data-Quality Audit** limited to **exactly two dates from a single calendar year** (e.g., 2020):
1. **Select Two Fixed Dates:** One calm/normal trading day (VIX $\le 20$) and one volatile/stress trading day (VIX $> 30$).
2. **Execute Targeted Checks on Those Two Dates Only:**
   * Verify header string trimming (`df.columns.str.strip()`) and row schema.
   * Confirm exact quote timestamp in `QUOTE_READTIME`.
   * Apply contract-wise OTM bid and spread filtering; verify that $>30$ liquid strikes remain in the $20 \le \text{DTE} \le 50$ bucket.
   * Invert synthetic forward $F_t$ at ATM strike; compare against cash close $S_t$.
   * Compute 30-day trapezoidal Martin (2017) SVIX using forward normalization and evaluate finite-strike coverage.

Passing these pilot checks provides qualified confirmation of parsing mechanics on these two dates, but does not certify the full 14-year dataset or remaining feature definitions.

---

## 10. Stage 3 Narrowly Scoped Two-Date Quality Audit (Corrected Results)

As authorized in Stage 2, a targeted empirical verification was executed on **exactly two dates from calendar year 2020**, selected from official Cboe VIX history:
* **Calm / Low-Volatility Session:** **2020-01-15** (Official Cboe VIX Close: **12.42%** $\le 20$; SPX Cash Close: **3,289.29**).
* **Crisis / Stress Session:** **2020-03-03** (Official Cboe VIX Close: **36.82%** $> 30$; SPX Cash Close: **3,003.37**; emergency 50 bps Federal Reserve rate cut).

### 10.1 Data Sources, Rates, and Dividend Inputs
* **SPX Options Data:** Streamed chunk-by-chunk from `Data/SPX Options Chain/spx_eod_2020-wh6jt7/spx_eod_202001.txt` and `spx_eod_202003.txt`. All non-target date rows were immediately dropped from memory.
* **Risk-Free Interest Rate ($r$):** Hardcoded illustrative benchmark rates based on the 13-week US Treasury Bill rate (`^IRX`): $1.508\%$ annualized ($r = 0.01508$) on 2020-01-15; $0.918\%$ annualized ($r = 0.00918$) on 2020-03-03. *(Note: These values are illustrative benchmark inputs for pilot demonstration; dynamic daily yield curve ingestion matching each option tenor remains deferred).*
* **Illustrative Benchmark Dividend Yield ($q_{\text{bench}}$):** Trailing 12-month S&P 500 dividend yield from standard macro benchmark series (Robert Shiller / S&P indices): $1.75\%$ ($q = 0.0175$) in January 2020; $1.95\%$ ($q = 0.0195$) in March 2020. *(Note: These values are illustrative external macro benchmarks, not dynamically observed options-implied dividend curves).*
* **Cash Index Close ($S_t$):** S&P 500 official closing index (`^GSPC`) from verified market close records.

### 10.2 Empirical Audit Findings by Target Date

#### Date 1: 2020-01-15 (Calm Regime)
1. **Schema & Timestamps:**
   * Raw rows extracted: **6,726 rows**.
   * Schema: Exactly **33 columns** confirmed after stripping header whitespace and brackets.
   * Timestamp: `QUOTE_READTIME = '2020-01-15 16:00'` uniformly across all rows.
   * Underlying price: Vendor reports `UNDERLYING_LAST = 3289.76` vs. official cash close `3289.29` ($\Delta = +0.47$ points, $+0.014\%$).
2. **Maturity Coverage in Primary 20–50 DTE Band:**
   * Available expiries: **9 distinct maturities** ($DTE \in \{21.0, 23.0, 26.0, 28.0, 30.0, 34.0, 35.0, 37.0, 44.0\}$).
   * Exact 30-day tenor ($DTE = 30.0$) is present; maturities cleanly bracket 30 days.
3. **Synthetic Forward & Cost-of-Carry Plausibility Check:**
   * At $DTE = 30.0$ ($T = 0.0822$), ATM strike $K^* = 3290.0$, call midpoint $C^* = 28.50$, put midpoint $P^* = 28.95$.
   * Parity synthetic forward: $F_{\text{parity}} = K^* + e^{rT}(C^* - P^*) = \mathbf{3,289.55}$.
   * Theoretical carry forward: $F_{\text{theo}} = S_t e^{(r - q_{\text{bench}})T} = 3289.29 \cdot e^{(0.01508 - 0.0175) \cdot 0.0822} = \mathbf{3,288.64}$.
   * Difference: $F_{\text{parity}} - F_{\text{theo}} = +0.91$ index points ($+0.028\%$).
   * Implied continuous dividend yield from parity: $q_{\text{implied}} = r - \frac{1}{T} \ln(F_{\text{parity}} / S_t) = \mathbf{1.41\%}$.
4. **Contract-Wise OTM Strikes & Finite-Strike Bounds:**
   * Retained liquid OTM strikes: **99 to 222 usable strikes per maturity** (167 strikes spanning $2525.0$ to $3460.0$ at $DTE = 30.0$).
   * Strike grid boundary at $DTE = 30.0$: $K_{\min} = 2525.0$ ($K_{\min}/F = 0.768$), $K_{\max} = 3460.0$ ($K_{\max}/F = 1.052$). Outside this range, the integral is truncated without tail extrapolation.
5. **Martin (2017) Forward-Normalized Formula (Finite-Strike Truncated Estimate) vs. Cboe VIX Diagnostic:**
   * **Martin (2017) Formula & Truncated-Grid Estimate:** The continuous formula normalizes by the forward squared $F_{\text{parity}}^2$. Evaluated across the discrete, finite strike grid with standard composite trapezoidal weights ($\Delta K_0 = 0.5(K_1 - K_0), \Delta K_N = 0.5(K_N - K_{N-1})$) without tail extrapolation:
     $$\widehat{\text{SVIX}}_{\text{ann}}^2 = \frac{2 e^{rT}}{T F_{\text{parity}}^2} \left[ \sum_{K_{\min} \le K_i < F} P(K_i) \Delta K_i + \sum_{F \le K_j \le K_{\max}} C(K_j) \Delta K_j \right]$$
     Yields 30-day finite-strike Martin SVIX estimate = **12.00%** (11.9964%).
   * **Cboe VIX Heuristic Diagnostic (Log Contract):** Weighted by $1/K^2$ on sampled quotes:
     $$\text{VIX}_{\text{approx}}^2 = \frac{2 e^{rT}}{T} \left[ \sum_{K_i < F} \frac{P(K_i)}{K_i^2} \Delta K_i + \sum_{K_j \ge F} \frac{C(K_j)}{K_j^2} \Delta K_j \right]$$
     Yields 30-day Cboe approximation = **12.37%** (vs. official Cboe VIX **12.42%**, diff: $-0.05$ vol pts).
   * **Observed Numerical Gap:** The finite-strike Martin SVIX estimate (12.00%) is **0.42 vol points below** official VIX (12.42%). This gap is an empirical observation on this date; it does not imply full continuum integral coverage or equivalence with Cboe VIX.

#### Date 2: 2020-03-03 (Crisis/Stress Regime)
1. **Schema & Timestamps:**
   * Raw rows extracted: **7,681 rows**.
   * Schema: Exactly **33 columns** confirmed.
   * Timestamp: `QUOTE_READTIME = '2020-03-03 16:00'` uniformly across all rows.
   * Underlying price: Vendor reports `UNDERLYING_LAST = 3002.74` vs. official cash close `3003.37` ($\Delta = -0.63$ points, $-0.021\%$).
2. **Maturity Coverage in Primary 20–50 DTE Band:**
   * Available expiries: **10 distinct maturities** ($DTE \in \{21.96, 23.96, 26.96, 27.96, 28.96, 30.96, 33.96, 35.96, 36.96, 44.96\}$).
   * Matched maturities bracket 30 days ($DTE = 28.96$ and $DTE = 30.96$).
3. **Synthetic Forward & Cost-of-Carry Plausibility Check:**
   * At $DTE = 30.96$ ($T = 0.0848$), ATM strike $K^* = 3000.0$, call midpoint $C^* = 94.75$, put midpoint $P^* = 94.35$.
   * Parity synthetic forward: $F_{\text{parity}} = K^* + e^{rT}(C^* - P^*) = \mathbf{3,000.41}$.
   * Theoretical carry forward: $F_{\text{theo}} = S_t e^{(r - q_{\text{bench}})T} = 3003.37 \cdot e^{(0.00918 - 0.0195) \cdot 0.0848} = \mathbf{3,000.74}$.
   * Difference: $F_{\text{parity}} - F_{\text{theo}} = -0.34$ index points ($-0.011\%$).
   * Implied continuous dividend yield from parity: $q_{\text{implied}} = r - \frac{1}{T} \ln(F_{\text{parity}} / S_t) = \mathbf{2.08\%}$.
4. **Contract-Wise OTM Strikes & Finite-Strike Bounds:**
   * Retained liquid OTM strikes: **107 to 278 usable strikes per maturity** (208 strikes spanning $1700.0$ to $3460.0$ at $DTE = 30.96$).
   * Strike grid boundary at $DTE = 30.96$: $K_{\min} = 1700.0$ ($K_{\min}/F = 0.567$), $K_{\max} = 3460.0$ ($K_{\max}/F = 1.153$). Outside this range, the integral is truncated without tail extrapolation.
5. **Martin (2017) Forward-Normalized Formula (Finite-Strike Truncated Estimate) vs. Cboe VIX Diagnostic:**
   * **Martin (2017) Truncated-Grid Estimate:** Yields 30-day finite-strike Martin SVIX estimate = **34.88%** (linearly interpolated between DTE 28.96 [34.88%] and DTE 30.96 [34.87%]).
   * **Cboe VIX Heuristic Diagnostic (Log Contract):** Yields 30-day Cboe approximation = **37.16%** (vs. official Cboe VIX **36.82%**, diff: $+0.34$ vol pts).
   * **Observed Numerical Gap:** The finite-strike Martin SVIX estimate (34.88%) is **1.94 vol points below** official VIX (36.82%). This gap is an empirical observation on this date; it does not imply full continuum integral coverage or equivalence with Cboe VIX.

### 10.3 Methodological Clarifications & Audit Trail of Corrections

1. **Forward Normalization vs. Spot Normalization (Corrected):**
   * *The Prior Flaw:* The previous revision normalized option integrals by the spot price squared ($S_t^2$) scaled by $e^{-rT}$. As Martin (2017) demonstrates, that simplification holds only under a zero-dividend assumption ($F = S e^{rT}$). Under non-zero dividends, the exact formula normalizes by the forward squared:
     $$\text{SVIX}^2 = \frac{2 e^{rT}}{T F_{t,T}^2} \left[ \int_0^{F_{t,T}} P(K) \, dK + \int_{F_{t,T}}^\infty C(K) \, dK \right]$$
   * *The Correction:* The calculation was recomputed using exact forward normalization ($F_{\text{parity}}^2$ with $e^{rT}$).
2. **Standard Composite Trapezoidal Weights & Boundary Truncation (Corrected):**
   * *The Prior Flaw:* The previous script assigned full adjacent intervals ($\Delta K = K_1 - K_0$) to the endpoint strikes, inflating boundary weights.
   * *The Correction:* Endpoints are now correctly weighted with half-intervals ($\Delta K_0 = 0.5(K_1 - K_0)$ and $\Delta K_N = 0.5(K_N - K_{N-1})$). The resulting integration is explicitly documented as a finite-strike discrete quadrature over $[K_{\min}, K_{\max}]$ without tail extrapolation.
3. **Cboe VIX Comparison as an Approximate Diagnostic:**
   * The script's $1/K^2$ calculation omits full operational Cboe rulebook adjustments (e.g. $K_0$ truncation term, near/next term 30-day weighting across maturities with min 8 days DTE). It relies on the same sampled quotes and is an illustrative reference, not an independent validation of the surface.
4. **Numerical Gap as an Observation, Not Causal Proof:**
   * The numerical gap between Martin SVIX and official Cboe VIX ($-0.42$ vol pts on 2020-01-15; $-1.94$ vol pts on 2020-03-03) is reported strictly as an **empirical observation on these two dates**. While QSkew was not calculated during the Stage 3 quality audit and was subsequently computed in Stage 4 ($-2.8405$ on 2020-01-15 and $-1.9537$ on 2020-03-03), the observed SVIX–VIX difference is an empirical observation on these two dates and does not establish an econometric causal explanation or proof of crisis put demand.
5. **Forward Parity and Cost-of-Carry Plausibility Check:**
   * Parity forwards align closely with theoretical cost-of-carry under illustrative trailing dividend benchmarks ($+0.91$ pts in calm, $-0.34$ pts in stress), yielding realistic implied yields ($1.41\%$ and $2.08\%$).
   * However, estimating $F_{\text{parity}}$ from option quotes guarantees internal surface consistency only; **it does not prove synchronization with the 16:00 ET cash equity close $S_t$ or eliminate 15-minute look-ahead risk if option quotes closed at 16:15 ET**.
6. **What the Stage 3 Audit Did NOT Validate:**
   * In Stage 3, the empirical check was strictly scoped to parsing, forward parity, and Martin SVIX; it did not calculate QSkew, QKurt, ATM IV, or the 60-day term-structure slope. (Note: These feature algorithms were subsequently implemented and demonstrated in Stage 4 for these same two dates only; full-sample batch extraction across 2010–2021 remains outstanding).
   * Does not verify 14-year intra-month session continuity or confirm $<1.0\%$ missing sessions.
   * Does not verify early-period strike depth (2010–2012 files, ~5 MB).
   * Does not verify timestamp consistency across earlier product vintages (2010–2015).

### 10.4 Revised Gate A Decision: **QUALIFIED PASS (CONDITIONAL APPROVAL)**

The pilot data-quality check is approved on the two authorized dates. Work may proceed to Stage 4 (Feature Pipeline Specification). However, **full-sample model estimation remains conditioned on completing the audit checks during pipeline construction**:
1. Scan the SPX calendar to verify that missing trading sessions do not exceed $1.0\%$.
2. Verify that 2010–2012 monthly chains contain at least 30 liquid strikes spanning $0.85 \le K/S \le 1.15$ in the 20–50 DTE band.
3. Complete implementation and unit testing of the remaining $Q_t$ moments (QSkew, QKurt, ATM IV, Term Slope) and $X_t$ historical features (*Feature algorithms implemented and demonstrated in Stage 4 for the two pilot dates; batch extraction executed across 2010–2021 in Gate B*).
4. Confirm exact training/validation/test session cutoffs based on verified calendar dates.

---

## 11. Post-Audit Resolution: Stage 6 / Gate B Empirical Audit (21 October 2026, Revised)

In Stage 6, the authorized Gate B empirical data audit was conducted across the 2010–2021 Development and Validation periods. Complete details and full numerical distributions are documented in [gate_b_audit_report.md](file:///D:/IE612_Project/gate_b_audit_report.md).

### 11.1 Session Continuity Findings & Reconciliation (2010–2021)
* **Authoritative Denominator:** 3,021 active exchange trading sessions (`^GSPC` benchmark, accounting for Hurricane Sandy closures on 2012-10-29/30 and Bush mourning closure on 2018-12-05).
* **Observed Option Sessions:** 2,994 sessions.
* **Missing Sessions:** 30 sessions.
* **Unexpected Sessions:** 3 market closure dates where OptionsDX propagated stale quotes, identical underlyings (`1411.94` and `2700.06`), and stale volumes (Sandy Oct 29–30, 2012; Bush mourning Dec 5, 2018).
* **Arithmetic Reconciliation:**
  $$\text{Observed SPX Dates (2,994)} = \text{Expected Exchange Sessions (3,021)} - \text{Missing Active Sessions (30)} + \text{Unexpected Stale Records (3)}$$
* **Non-Uniform Annual Missingness:** While aggregate 12-year missingness is $0.993\% \le 1.0\%$, annual missingness exceeds the 1.0% limit in 5 separate years: 2011 (**2.78%**, 5-day consecutive outage), 2014 (**1.19%**), 2019 (**1.98%**), 2020 (**1.19%**), and 2021 (**2.38%**). Continuity is not a uniform annual pass.
* **Audit Scope Distinction (2010–2021 Audited vs. 2022–2023 Unaudited):** The 14-year file inventory (168 monthly bundles) is 100% verified. Daily session continuity across option records has been audited for 2010–2021 (3,021 expected sessions, 2,994 observed, 30 missing, 3 unexpected; 0.993% aggregate missing rate). The 2022–2023 test period daily continuity remains unaudited to avoid opening or parsing the raw test option bundles prior to Gate D.

### 11.2 Early-Sample Strike Breadth Findings (2010–2012)
* **Audit Scope:** 745 trading sessions across 36 monthly files.
* **Monthly Expiration Cycle Deficit:** Prior to mid-2012, standard monthly expirations left long gaps between expiries. 30-day constant-maturity bracketing failed on **76.4% of sessions in 2010** and **68.6% of sessions in 2011**.
* **Weekly Option Shift (Mid-2012):** Introduction of weekly options in June/July 2012 caused 30-day bracketing to jump to **95–100%**.
* **Call Wing Truncation:** Liquid call quotes truncated at $1.08–1.12 \times S$, failing the $K_{\max}/S \ge 1.15$ span on $>93\%$ of early sessions.

### 11.3 Quote Timestamps & Cash Synchronization (Gate B Prerequisite)
* Vendor readtime strings uniformly report `'16:00'`, but do not document whether quotes reflect instantaneous 16:00:00 ET NBBO or 16:15:00 ET Cboe option settlement.
* Put-call parity guarantees internal surface consistency, but does not prove synchronization with the 16:00:00 ET cash equity close $S_t$.
* **Information Cutoff Gate Status:** Remains **UNRESOLVED**. Operational model fitting remains strictly gated.

### 11.4 Rate Fallback Audit & Elimination of Silent Imputation
* On two federal bank holidays where US bond markets were closed but equity markets traded (2010-10-11 Columbus Day and 2016-11-11 Veterans Day), `^IRX` was missing (`NaN`).
* Rates were causally carried forward from the prior active trading day with explicit logging (`rate_source = 'CAUSAL_PRIOR_SESSION_CARRYFORWARD'`, `rate_is_fallback = True`). Zero silent constant substitution was performed. Moments on 2016-11-11 were recomputed at the exact causal rate ($0.004652$).

### 11.5 Test Boundary Disclosure, Target Label Corrections & Candidate Datasets
* **Test Boundary Disclosure:** Downloading `^GSPC` through January 2022 accessed both the `2022-01-03` close (`4796.56`) and `2022-01-04` close (`4793.54`), and derived the `2021-12-31` validation target return (`0.0063538`). All three values were committed in commit `cee01a1` and remain permanently recorded in Git repository history. Although raw 2022–2023 option bundles remained unopened, cash close access breached the test seal. Cached cash closes in the active working tree were truncated to $\le \text{2021-12-31}$.
* **Partition Target Corrections:** To guarantee strict partition boundary purity, boundary target returns on both `2019-12-31` in Development (`UNOBSERVED_WITHOUT_VALIDATION_CLOSE`) and `2021-12-31` in Validation (`UNOBSERVED_WITHOUT_TEST_CLOSE`) are set strictly to `NaN`.
* **Complete 5-Feature Completeness:** $Q_t \in \mathbb{R}^5$ is valid on **2,233 rows (88.75%)** and missing on **283 rows (11.25%)** in Development (due to 2010–2011 monthly gaps and 60d slope gaps); valid on **496 rows (98.22%)** and missing on **9 rows (1.78%)** in Validation.
* **Dataset Status:** Candidate feature datasets for Development (2,516 rows, SHA-256: `138fa68af7f8f21da257f5d41332e583e73f32e358c6b2242a5d783dd5b2978e`) and Validation (505 rows, SHA-256: `8bedc8b4e3ae3cf42a99c8ab8477950ab69244eb8e052c7afacef8ac9e7c19d7`) are candidate audit outputs, **not permanently frozen**.
* **Gate B Status:** **BLOCKED / QUALIFIED**. Stage 7 forecasting model fitting is NOT permitted or authorized until the information cutoff, test breach acknowledgment, proposed early missing-feature policy, and test continuity audit deferral decisions are formally resolved.

---
*End of Data Feasibility Audit (Updated Stage 6 Version).*
