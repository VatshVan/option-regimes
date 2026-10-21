# Frozen Research Protocol: SPX Options Physical Density Forecasting

**Project Title:** Regime-Conditioned Mapping from Option-Implied Risk-Neutral Information to Physical Return Distributions  
**Course & Scope:** IE 612 (Introduction to Financial Engineering), 1-Month Empirical Project  
**Document Status:** Stage 1 Frozen Protocol (Version 1.0, 21 October 2026)  
**Governing Source of Truth:** [`implementation.md`](file:///D:/IE612_Project/implementation.md)  
**Associated Documents:** [`project_implementation_idea.md`](file:///D:/IE612_Project/project_implementation_idea.md), [`SPX_data_research.md`](file:///D:/IE612_Project/SPX_data_research.md)  

---

## 1. Research Question, Estimand, Hypotheses, and Decision Rules

### 1.1 Primary Research Question
At trading date $t$, does conditioning on causally filtered, persistent latent market regimes ($\pi_t$) improve the out-of-sample forecast of the next trading day's physical return distribution, relative to a strong non-regime baseline that receives the identical option-implied risk-neutral features ($Q_t$) and historical market state ($X_t$)?

$$\text{Forecast Comparison: } \quad p(r_{t+1} \mid Q_t, X_t, \pi_t) \quad \text{versus} \quad p(r_{t+1} \mid Q_t, X_t)$$

where:
* $Q_t$ denotes summary features extracted from the cross-section of S&P 500 (SPX) index option prices under the risk-neutral measure ($\mathbb{Q}$).
* $X_t$ denotes observable historical market state variables available at or before the forecast cutoff.
* $\pi_t = \big[P(z_t=1 \mid \mathcal{F}_t), \dots, P(z_t=K \mid \mathcal{F}_t)\big]^\top$ is the vector of filtered posterior regime probabilities inferred causally from an in-sample Hidden Markov Model (HMM) using information $\mathcal{F}_t$.
* $r_{t+1} = \log(S_{t+1} / S_t)$ is the physical close-to-close log return of the underlying S&P 500 index over session $t+1$.

### 1.2 Formal Estimand & Primary Metric
The primary target of estimation is the conditional physical probability density function $\widehat{p}_{t+1}(r) \equiv p(r_{t+1} \mid \mathcal{I}_t)$.

The primary evaluation criterion is the **mean out-of-sample Negative Log-Likelihood (NLL)** (log predictive loss) evaluated on realized next-day physical returns across the held-out test evaluation window $\mathcal{T}_{\text{test}}$:

$$\mathcal{L}(M) = -\frac{1}{|\mathcal{T}_{\text{test}}|} \sum_{t \in \mathcal{T}_{\text{test}}} \log \widehat{p}^{(M)}_{t+1}(r_{t+1})$$

Lower loss represents superior predictive density performance.

### 1.3 Hypotheses
* **H1 (Primary — Distributional Gain):** The regime-augmented model ($R1$) achieves a strictly lower mean out-of-sample NLL than the primary non-regime comparator ($B4$) on the held-out 2022–2023 test period (whose raw option bundles remain unopened, acknowledging the 2022-01-03/04 cash close breach retained in commit cee01a1 Git history) ($\Delta \mathcal{L} = \mathcal{L}(B4) - \mathcal{L}(R1) > 0$), with statistical significance established via a paired test.
* **H2 (Incrementality / Non-Redundancy):** The predictive gain of $R1$ over $B4$ is not merely a proxy for current observable volatility or trend. The improvement persists after controlling directly for observable volatility state variables in the baseline.
* **H3 (Calibration & Tail Fidelity):** Predictive densities from $R1$ maintain acceptable calibration: Probability Integral Transform (PIT) values are approximately uniform, empirical coverage of 50%, 80%, and 95% central predictive intervals does not violate theoretical nominal rates by more than pre-specified tolerances, and tail-loss metrics are preserved.
* **H4 (Secondary — Economic Relevance):** When predictive densities are fed into a pre-specified, transparent single-index volatility-targeting rule, $R1$ achieves superior net Sharpe ratio or lower maximum drawdown relative to simple benchmarks after transaction costs (5 bps). *(This is strictly secondary and illustrative; it cannot override a failure on H1 or H3.)*

### 1.4 Decision Rules: What Counts as Evidence
1. **Evidence For Incremental Regime Value:**
   * $\Delta \mathcal{L} > 0$ on the held-out test period (raw option bundles unopened; test cash close breach recorded in commit cee01a1), with a one-sided paired Diebold–Mariano test rejecting the null of equal predictive accuracy at $p < 0.05$.
   * Stationary block bootstrap 95% confidence intervals for $\Delta \mathcal{L}$ exclude zero.
   * Model passes PIT uniformity diagnostics without exhibiting overconfidence (variance of PIT not collapsing).
   * Control ablations (shuffled regime probabilities, static volatility thresholding) underperform $R1$.

2. **Evidence Against Incremental Regime Value (Null Result):**
   * $\Delta \mathcal{L} \le 0$, or $\Delta \mathcal{L} > 0$ but fails to achieve statistical significance ($p \ge 0.05$).
   * A simpler baseline augmented only with observable trailing volatility matches or outperforms $R1$.
   * Filtered regime states degenerate (e.g., regime persistence collapses, occupancy is $<5\%$ for a state, or label switching renders states uninterpretable across rolling fits).
   * Apparent log-loss gains are accompanied by pathological calibration (severe undercoverage of tails or severe PIT clustering).

A null result is treated as a fully valid, reportable scientific finding. The project will report negative or null findings directly and will not conduct retrospective search on the test dataset to force a positive outcome.

---

## 2. Forecast Origin, Information Cutoff, and Alignment Rules

### 2.1 Forecast Origin and Cutoff Time
* **Observation Frequency:** Daily, End-of-Day (EOD).
* **Forecast Origin & Cutoff Status:** Established at the nominal trading close on date $t$. The precise information cutoff is explicitly treated as **UNRESOLVED** due to the structural risk of Cboe option closes at 16:15 ET post-dating the 16:00 ET cash equity close $S_t$. Any operational use of option features in predictive models is **strictly gated** until quote timing is empirically verified in Gate B or a defensible alternative cutoff is formally pre-specified.
* **Information Set $\mathcal{F}_t$:** Contains all underlying prices, trades, macro series, and option quotes recorded up to the declared session cutoff at date $t$. Absolutely no information timestamped after date $t$'s market close is permitted in feature construction or model conditioning.

### 2.2 Target Return Definition
* **Primary Target:** Close-to-close log return of the S&P 500 index:
  $$r_{t+1} = \log\left(\frac{S_{t+1}}{S_t}\right)$$
  where $S_t$ is the closing price of the S&P 500 index (`^GSPC`) on trading date $t$, and $S_{t+1}$ is the closing price on the subsequent trading date $t+1$.
* **Horizon:** Strictly 1 trading session (non-overlapping). This avoids overlapping-label autocorrelation, purge/embargo requirements, and rolling-label dependence artifacts in the primary study.
* **Total Return vs. Price Return:** The underlying index options are written on the price index ($S_t$), which defines the contract boundary and forward levels. Physical portfolio evaluation (secondary) may track total return (`^SP500TR`) to incorporate dividend reinvestment, but $r_{t+1}$ for density forecasting is defined uniformly on the price series matching the option underlying.

### 2.3 Trading Calendar and Holiday Alignment
* **Calendar Specification:** The official trading calendar is governed by the Cboe Index Options and NYSE calendars (via `pandas_market_calendars`).
* **Session Pairs $(t, t+1)$:** A valid observation pair requires that $t+1$ be the immediate next scheduled trading session following $t$. If an unscheduled exchange closure occurs (e.g., severe weather closure or national day of mourning), $t+1$ is the first resumed trading day, and the return is measured across that actual holding period.
* **Early-Close Sessions:** On scheduled early-close days (e.g., day after Thanksgiving, Christmas Eve with 13:00 ET close), timestamps must be verified against actual session hours. If quote timestamps in the raw data do not match the early close, that session must be flagged and audited during Gate A.

### 2.4 Unresolved Timing Choices & Alignment Protocols

> [!IMPORTANT]
> The presence of a `16:00:00` string in vendor text files does not prove synchronous recording with the underlying equity cash index close. The following structural timing discrepancies are recognized and must be handled via explicit protocol rules:

1. **The 16:00 vs. 16:15 ET Option Close Discrepancy:**
   * *The Problem:* Cboe historically traded SPX index options until 16:15 ET (15 minutes after the cash equity close at 16:00 ET). If an option snapshot taken at 16:15 ET is paired with a 16:00 ET cash index value $S_t$, any post-market macro announcements or index futures movement will distort apparent moneyness ($K/S_t$) and artificially violate put-call parity.
   * *Frozen Protocol Rule:* **Do not rely directly on reported cash index levels (`UNDERLYING_LAST`) for strike moneyness or pricing parity.** Instead, infer the synchronous synthetic forward price $F_{t,\tau}$ directly from at-the-money (ATM) call and put quote midpoints at each maturity:
     $$F_{t,\tau} = K^* + e^{r \tau} \big(C(K^*, \tau) - P(K^*, \tau)\big)$$
     where $K^*$ is the liquid strike minimizing $|C(K, \tau) - P(K, \tau)|$.
   * *Crucial Timing Clarification (Strict Cutoff Gate):* Inverting the synthetic forward $F_{t,\tau}$ via at-the-money put-call parity guarantees internal moneyness consistency across strikes within the option snapshot. However, **it does not by itself prove synchronization with the 16:00:00 ET cash equity close ($S_t$) or eliminate potential 15-minute look-ahead risk** if the options snapshot reflects 16:15:00 ET Cboe market closes while the physical return target denominator $S_t$ was frozen at 16:00:00 ET. Therefore, the forecast cutoff is explicitly classified as **UNRESOLVED**, and any operational use of option features in predictive models is strictly gated until quote timing and synchronization are empirically verified in Gate B or an alternative cutoff is formally approved.

2. **AM Settlement (`SPX`) vs. PM Settlement (`SPXW`) Ambiguity:**
   * *The Problem:* Standard monthly SPX options stop trading on Thursday afternoon and settle against the Friday morning Special Opening Quotation (`SET`), whereas weekly/end-of-month options (`SPXW`) trade until Friday 16:00 ET and settle against the 16:00 ET closing price. Raw OptionsDX files do not contain contract root identifiers (`SPX` vs. `SPXW`).
   * *Frozen Protocol Rule:*
     * Group contracts strictly by `(QUOTE_DATE, EXPIRE_DATE, STRIKE)`.
     * Exclude contracts with $DTE \le 1$ to remove settlement-day expiration noise.
     * Restrict primary feature extraction to intermediate monthly/weekly expiries satisfying $20 \le DTE \le 50$, where settlement timing differences have negligible impact on 30-day constant-maturity moments.
     * If duplicate strikes appear for the same date and maturity, select the quote with tighter relative spread and higher trading volume; log duplicate frequencies in the Gate A audit.

---

## 3. Option Features ($Q_t$), Historical Features ($X_t$), and Preprocessing

All features must be constructed using strictly causal information available at or before cutoff $t$.

```
                      Raw Input Streams at Date t
         +-------------------------------------------------+
         |  SPX Option Quotes (EOD)   |  SPX Index History |
         +----------------------------+--------------------+
                       |                         |
                       v                         v
              [Section 4 Cleaning]        [Lagged Return Calc]
                       |                         |
                       v                         v
         +----------------------------+--------------------+
         |   Risk-Neutral Vector Q_t  | Historical State   |
         |   - SVIX_30d               | Vector X_t         |
         |   - QSkew_30d              | - r_t, r_{t-4:t}   |
         |   - QKurt_30d              | - RV_5d, RV_20d    |
         |   - ATM_IV_30d             | - SemiVar_20d      |
         |   - Term_Slope (60d - 30d) | - Drawdown_20d     |
         +----------------------------+--------------------+
                       \                         /
                        \                       /
                         v                     v
                    +------------------------------+
                    |  Training-Only Normalization |
                    |  (StandardScaler fit on      |
                    |   training window only)      |
                    +--------------+---------------+
                                   |
                                   v
                    +------------------------------+
                    | Model Feature Input Vector   |
                    | z_t = [ Q_t , X_t ]          |
                    +------------------------------+
```

### 3.1 Option-Implied Risk-Neutral Feature Set ($Q_t$)
Rather than attempting full non-parametric Breeden–Litzenberger continuous density inversion (which is prone to butterfly arbitrage artifacts and numerical instability on discrete quotes), the project adopts the structured moment approach of [Ulrich et al. (2019)](file:///D:/IE612_Project/Papers/ssrn_id3437281_code3012080.pdf) and [DeMiguel et al. (2013)](file:///D:/IE612_Project/Papers/ssrn_id2085587_code417015.pdf).

The feature vector $Q_t$ contains 5 compact forward-looking moments standardized to a constant 30-day maturity:

1. **Martin (2017) Simple Variance Swap Index ($\text{SVIX}_t$):**
   $$\text{SVIX}^2_t(\tau) = \frac{2 e^{r \tau}}{\tau F_{t,\tau}^2} \left[ \int_0^{F_{t,\tau}} P(K, \tau) \, dK + \int_{F_{t,\tau}}^\infty C(K, \tau) \, dK \right]$$
   Evaluated via discrete standard composite trapezoidal quadrature over retained out-of-the-money liquid puts and calls without tail extrapolation. Martin (2017) establishes that $\text{SVIX}^2$ measures the risk-neutral variance of simple gross returns, normalized by the forward squared $F_{t,\tau}^2$ (unweighted by $1/K^2$), and acts as a model-free lower bound on the equity risk premium ($\mathbb{E}_t[R_{t+1}] - R_{f,t+1} \ge R_{f,t+1} \text{SVIX}_t^2$). Note that Martin's SVIX is distinct from Cboe VIX, which measures log-contract variance and weights options by $1/K^2$. If the risk-neutral distribution features negative skewness, Martin (2017) shows that theoretically $\text{VIX} > \text{SVIX}$. In our data check, the comparison serves as an approximate structural diagnostic, not an equivalence test.
2. **Bakshi, Kapadia, and Madan (2003) Risk-Neutral Skewness ($\text{QSkew}_t$):**
   $$S_t^Q(\tau) = \frac{e^{r \tau} W_t(\tau) - 3 \mu_t^Q(\tau) e^{r \tau} V_t(\tau) + 2 \big(\mu_t^Q(\tau)\big)^3}{\big(e^{r \tau} V_t(\tau) - (\mu_t^Q(\tau))^2\big)^{3/2}}$$
   where $V_t, W_t$ represent the fair prices of the volatility and cubic contracts (raw non-central option-implied contract moments), and $\mu_t^Q(\tau) \approx e^{r\tau} - 1 - \frac{e^{r\tau}}{2} V_t - \frac{e^{r\tau}}{6} W_t - \frac{e^{r\tau}}{24} X_t$ is the risk-neutral expected log return. $S_t^Q(\tau)$ is the centered, standardized 3rd central moment under $Q$.
3. **Bakshi, Kapadia, and Madan (2003) Risk-Neutral Kurtosis ($\text{QKurt}_t$):**
   $$K_t^Q(\tau) = \frac{e^{r \tau} X_t(\tau) - 4 \mu_t^Q(\tau) e^{r \tau} W_t(\tau) + 6 \big(\mu_t^Q(\tau)\big)^2 e^{r \tau} V_t(\tau) - 3 \big(\mu_t^Q(\tau)\big)^4}{\big(e^{r \tau} V_t(\tau) - (\mu_t^Q(\tau))^2\big)^2}$$
   where $X_t$ represents the fair price of the quartic contract (raw 4th power payoff contract). $K_t^Q(\tau)$ is the **centered, standardized 4th central moment** under $Q$ (non-excess kurtosis, where a Gaussian benchmark equals 3.0; excess kurtosis equals $K_t^Q - 3.0$).
4. **At-The-Money Implied Volatility ($\text{ATM\_IV}_t$):**
   Black–Scholes implied volatility inverted from the option midpoint whose strike is closest to $F_{t,\tau}$.
5. **Term-Structure Slope ($\text{TermSlope}_t$):**
   Difference between constant-maturity 60-day ATM IV and 30-day ATM IV ($\text{ATM\_IV}_{60} - \text{ATM\_IV}_{30}$).

**Constant-Maturity Standardization:** Features are computed on the two distinct expirations $\tau_1 < 30 < \tau_2$ nearest to 30 calendar days and linearly interpolated to a fixed 30-day tenor ($\tau = 30/365$), eliminating maturity-decay artifacts.

*(Risk-Free Rate Note: In the forward inversion and moment formulas above, $r$ represents the continuously compounded risk-free discount rate corresponding to expiration tenor $\tau$. For the Stage 3 and Stage 4 demonstration runs, illustrative benchmark rates based on Cboe 13-week T-Bill (`^IRX`) closes were utilized; automated continuous daily yield curve ingestion matching each option tenor has not been integrated into the repository and remains unverified for the full sample).*

### 3.2 Historical Market State Feature Set ($X_t$)
The vector $X_t$ captures observable recent return dynamics, realized volatility, and drawdown:

1. **Short-Term Return Momentum:** 1-day lagged return $r_t = \log(S_t / S_{t-1})$.
2. **Medium-Term Return Momentum:** 5-day cumulative log return $\sum_{i=0}^4 r_{t-i}$.
3. **Short-Term Realized Volatility ($\text{RV}_{5,t}$):**
   $$\text{RV}_{5,t} = \sqrt{\frac{252}{5} \sum_{i=0}^4 r_{t-i}^2}$$
4. **Medium-Term Realized Volatility ($\text{RV}_{20,t}$):**
   $$\text{RV}_{20,t} = \sqrt{\frac{252}{20} \sum_{i=0}^{19} r_{t-i}^2}$$
5. **Downside Semi-Variance ($\text{SemiVar}_{20,t}$):**
   Annualized volatility calculated strictly on negative daily returns over the preceding 20 trading days:
   $$\text{SemiVar}_{20,t} = \sqrt{\frac{252}{20} \sum_{i=0}^{19} \min(r_{t-i}, 0)^2}$$
6. **Trailing 20-Day Drawdown ($\text{DD}_{20,t}$):**
   $$\text{DD}_{20,t} = \frac{S_t - \max_{0 \le i \le 19} S_{t-i}}{\max_{0 \le i \le 19} S_{t-i}}$$

### 3.3 Training-Only Preprocessing Rules
* **No Global Scaling:** Under no circumstances may standard scalers, min-max normalizers, PCA transforms, or imputation routines be fit on the complete multi-year dataset.
* **Rolling/Expanding Pipeline:** At every refit date, feature transformers must be fit strictly on in-sample training observations $\mathcal{T}_{\text{train}}$. Test features are transformed using frozen training parameters:
  $$\mu_{\text{train}} = \frac{1}{|\mathcal{T}_{\text{train}}|} \sum_{s \in \mathcal{T}_{\text{train}}} x_s, \quad \sigma_{\text{train}} = \sqrt{\frac{1}{|\mathcal{T}_{\text{train}}|} \sum_{s \in \mathcal{T}_{\text{train}}} (x_s - \mu_{\text{train}})^2}$$
  $$x_t^{\text{scaled}} = \frac{x_t - \mu_{\text{train}}}{\sigma_{\text{train}} + \epsilon}$$
* **Missing Value Imputation:** If an option feature is missing on a specific date (e.g., due to sparse strike coverage during an extreme market disruption), missingness is carried forward causally from the previous valid trading day ($t-1$) only if missingness is isolated ($\le 1$ day). If more than 2 consecutive days lack liquid chains, those dates are dropped from out-of-sample evaluation with reason codes logged.

---

## 4. Provisional Quote-Quality and Maturity Screening Filters

All raw options data must pass explicit quality gates before entering numerical quadrature routines.

### 4.1 Field Distinctions: Open Interest vs. Volume and Sizes
* **Open Interest (`OPEN_INTEREST`):** **CONFIRMED MISSING** from the OptionsDX dataset schema. Illiquidity filtering cannot use an open interest cut (e.g., $OI \ge 100$).
* **Volume (`C_VOLUME`, `P_VOLUME`):** **PRESENT** in the schema as floating-point / integer trade counts for the session.
* **Quote Lot Sizes (`C_SIZE`, `P_SIZE`):** **PRESENT** in the schema as string representations (e.g., `"10 x 20"` for bid size $\times$ ask size). They represent instantaneous market depth at close, *not* open interest. They are retained for diagnostics but not parsed into numerical filters unless needed.

### 4.2 Provisional Filtering Thresholds

> [!NOTE]
> The thresholds below represent the Stage 1 baseline rules derived from literature precedents ([Bali et al., 2023](file:///D:/IE612_Project/Papers/hhad017.pdf); [Ulrich et al., 2019](file:///D:/IE612_Project/Papers/ssrn_id3437281_code3012080.pdf)). They are **provisional** and subject to confirmation during the Gate A empirical data audit.

```
       Raw Option Chain Record on Date t
                       |
                       v
         [Step 1: Invert Synthetic Forward F_t at ATM]
            Valid ATM pair (|C_MID - P_MID| min, C_BID>0.05, P_BID>0.05)
                       |
                       v
         [Step 2: Maturity Window Selection]
            20 <= DTE <= 50 calendar days ?    -----> No  --> [Exclude from Primary]
                       | Yes
                       v
         [Step 3: Contract-Wise OTM-Side Screening]
            If K < F_t (OTM Put):
               P_BID > 0.05, P_ASK > P_BID, (P_ASK - P_BID)/P_MID <= 0.35 ?
            If K >= F_t (OTM Call):
               C_BID > 0.05, C_ASK > C_BID, (C_ASK - C_BID)/C_MID <= 0.35 ?
                       | Yes
                       v
         [Retained for Feature Extraction Q_t]
```

1. **ATM Forward Inversion Pair:**
   At the single strike $K^*$ where $|C_{\text{mid}} - P_{\text{mid}}|$ is minimized, require both $C\_BID > \$0.05$, $P\_BID > \$0.05$, $C\_ASK > C\_BID$, and $P\_ASK > P\_BID$ to estimate $F_{t,\tau}$.
2. **Contract-Wise OTM-Side Screening (Confirmed in Stage 3):**
   Option quotes must be screened contract-wise on their own active out-of-the-money side, *not* row-wise:
   * **For Out-of-the-Money Puts ($K < F_{t,\tau}$):** Screen the put quote only: require $P\_BID > \$0.05$, $P\_ASK > P\_BID$, and relative spread $(P\_ASK - P\_BID)/P\_{\text{mid}} \le 0.35$. Disregard `C_BID` (deep in-the-money call quotes on the same row are not required to be liquid).
   * **For Out-of-the-Money Calls ($K \ge F_{t,\tau}$):** Screen the call quote only: require $C\_BID > \$0.05$, $C\_ASK > C\_BID$, and relative spread $(C\_ASK - C\_BID)/C\_{\text{mid}} \le 0.35$. Disregard `P_BID` (deep in-the-money put quotes on the same row are not required to be liquid).
   * Midpoint price $M(K) = (Bid + Ask)/2$ is used for all retained contracts.
3. **Primary Maturity Window:**
   $$20 \le \text{DTE} \le 50 \text{ calendar days}$$
   Focuses on the most liquid monthly/weekly contracts surrounding 30 days; excludes expiry-day contracts ($DTE \le 1$) and long-dated illiquid options ($DTE > 60$).
4. **No-Arbitrage Diagnostic Screening:**
   * Monotonicity check: Call midpoints must be strictly non-increasing in strike ($\frac{\partial C}{\partial K} \le 0$), and put midpoints strictly non-decreasing ($\frac{\partial P}{\partial K} \ge 0$).
   * Vertical and butterfly spread positivity checks ($\frac{\partial^2 C}{\partial K^2} \ge 0$).
5. **External Validation Gate Diagnostic (Cboe Benchmark Anchoring):**
   * Download official historical Cboe VIX (`VIX_History.csv`) and SKEW (`SKEW_History.csv`) daily series from the public Cboe CDN.
   * Extracted model-free $\text{SVIX}_t$ and $\text{QSkew}_t$ are benchmarked against official Cboe VIX and SKEW as a consistency diagnostic.
   * *Critical Theoretical Distinction:* SVIX (Martin, 2017) measures simple return variance (unweighted by $1/K^2$), while Cboe VIX measures log-contract variance (weighted by $1/K^2$). They are distinct theoretical measures. Martin (2017) proves that under negative risk-neutral skewness of simple returns, VIX exceeds SVIX theoretically ($\text{VIX} > \text{SVIX}$). The empirical comparison serves as an approximate structural diagnostic rather than an identity, and neither a 1-vol-point tolerance nor a 0.98-correlation threshold is imposed as an equivalence requirement.

---

## 5. Model Comparison Ladder and Estimation Specification

To isolate the incremental value of latent regimes without confounding from arbitrary model complexity, all predictive models are organized in a strict hierarchical ladder:

```
+-----------------------------------------------------------------------------------------+
|                                Model Comparison Ladder                                  |
+-----------------------------------------------------------------------------------------+
| [B0] Historical Unconditional Benchmark                                                 |
|      - Unconditioned expanding Gaussian density N(mu_train, sigma_train^2)              |
+-----------------------------------------------------------------------------------------+
| [B1] Trailing Volatility Location-Scale Benchmark                                       |
|      - Location-scale Student-t conditioned strictly on RV_20d                           |
+-----------------------------------------------------------------------------------------+
| [B2] Q-Only Distribution Model                                                          |
|      - Conditional density conditioned strictly on option-implied features Q_t          |
+-----------------------------------------------------------------------------------------+
| [B3] X-Only Distribution Model                                                          |
|      - Conditional density conditioned strictly on historical state features X_t        |
+-----------------------------------------------------------------------------------------+
| [B4] Combined Non-Regime Density Baseline (PRIMARY COMPARATOR)                          |
|      - Student-t location-scale / compact MDN conditioned on [Q_t, X_t] in R^11         |
+-----------------------------------------------------------------------------------------+
| [R1] Matched Latent Regime Density Challenger (PRIMARY HYPOTHESIS TEST)                 |
|      - Identical B4 architecture conditioned on [Q_t, X_t, \pi_t] in R^{11+K}            |
|      - \pi_t in Delta^{K-1} is forward-filtered causal regime probability vector         |
+-----------------------------------------------------------------------------------------+
```

### 5.1 Diagnostic Benchmarks
* **Model B0 (Historical Unconditional Benchmark):**
  A stationary benchmark representing the unconditional distribution of daily returns:
  $$\widehat{p}_{t+1}^{(B0)}(r) = \frac{1}{\sqrt{2\pi \sigma_{\tau}^2}} \exp\left(-\frac{(r - \mu_{\tau})^2}{2\sigma_{\tau}^2}\right)$$
  where $\mu_{\tau} = \frac{1}{|\mathcal{T}_{\tau}|} \sum_{s \in \mathcal{T}_{\tau}} r_s$ and $\sigma_{\tau}^2 = \frac{1}{|\mathcal{T}_{\tau}|-1} \sum_{s \in \mathcal{T}_{\tau}} (r_s - \mu_{\tau})^2$ are estimated over the expanding in-sample window.
* **Model B1 (Trailing Volatility Location-Scale Benchmark):**
  A conditional location-scale Student-$t$ model whose dispersion scales with recent 20-day realized volatility:
  $$\widehat{p}_{t+1}^{(B1)}(r) = \frac{1}{\sigma_t} f_{\nu}\left(\frac{r - \mu}{\sigma_t}\right), \quad \sigma_t = \alpha_0 + \alpha_1 \text{RV}_{20d,t}$$
  where $f_\nu(z) = \frac{\Gamma((\nu+1)/2)}{\Gamma(\nu/2)\sqrt{\pi \nu}} (1 + z^2/\nu)^{-(\nu+1)/2}$ is the standard Student-$t$ density. Degrees of freedom $\nu$, intercept $\alpha_0$, and coefficient $\alpha_1$ are estimated via maximum likelihood on $\mathcal{T}_{\tau}$ with constraints $\alpha_0 > 0, \alpha_1 \ge 0, \nu > 2.1$.
* **Model B2 ($Q$-Only Diagnostic):**
  Distribution model mapping $Q_t \to \widehat{p}_{t+1}(r)$ via location-scale Student-$t$ regression:
  $$\mu_t = \mathbf{w}_\mu^\top Q_t + b_\mu, \quad \sigma_t = \text{softplus}(\mathbf{w}_\sigma^\top Q_t + b_\sigma) + \sigma_{\min}, \quad \nu = \text{softplus}(w_\nu) + 2.1$$
  Verifies whether option moments alone contain sufficient predictive signal.
* **Model B3 ($X$-Only Diagnostic):**
  Distribution model mapping $X_t \to \widehat{p}_{t+1}(r)$ via location-scale Student-$t$ regression:
  $$\mu_t = \mathbf{w}_\mu^\top X_t + b_\mu, \quad \sigma_t = \text{softplus}(\mathbf{w}_\sigma^\top X_t + b_\sigma) + \sigma_{\min}, \quad \nu = \text{softplus}(w_\nu) + 2.1$$
  Verifies the predictive power of trailing historical returns and volatility in isolation.

### 5.2 Primary Comparator: Combined Non-Regime Baseline ($B4$)
* **Architecture:** Parametric Student-$t$ location-scale regression (primary) or compact Mixture Density Network (MDN) with a small number of components ($M \in \{2, 3\}$):
  * **Primary Formulation (Student-$t$ Location-Scale):**
    $$\mu_t = \mathbf{w}_\mu^\top [Q_t, X_t] + b_\mu$$
    $$\sigma_t = \text{softplus}(\mathbf{w}_\sigma^\top [Q_t, X_t] + b_\sigma) + \sigma_{\min}$$
    $$\nu = \text{softplus}(w_\nu) + 2.1$$
  * **Fallback Formulation (Compact 2-Component MDN):**
    $$\widehat{p}_{t+1}^{(B4)}(r \mid Q_t, X_t) = \sum_{m=1}^M w_m(Q_t, X_t) \, \frac{1}{\sigma_m(Q_t, X_t)} f_{\nu_m}\left(\frac{r - \mu_m(Q_t, X_t)}{\sigma_m(Q_t, X_t)}\right)$$
* **Input Vector:** Concatenated vector $\mathbf{u}_t = [Q_t, X_t] \in \mathbb{R}^{11}$.
* **Parameter Constraints:**
  * Component weights satisfy simplex constraint: $\sum_{m=1}^M w_m = 1, w_m > 0$ (enforced via Softmax).
  * Scale parameters are strictly positive: $\sigma_m > 0$ (enforced via Softplus activation with numerical floor $\sigma_{\min} = 10^{-4}$).
  * Degrees of freedom constrained: $\nu_m \ge 2.1$ to guarantee finite second moments.
* **Objective Function and Tuning:** Trained by minimizing regularized Negative Log-Likelihood (NLL) on $\mathcal{T}_{\tau}$:
  $$\mathcal{L}_{B4}(\boldsymbol{\theta}) = -\sum_{s \in \mathcal{T}_{\tau}} \ln \widehat{p}_{s+1}^{(B4)}(r_{s+1} \mid \mathbf{u}_s) + \lambda \|\boldsymbol{\theta}\|_2^2$$
  where $\lambda \ge 0$ is tuned strictly via chronological cross-validation on the development/validation window.

### 5.3 Primary Challenger: Regime-Augmented Model ($R1$)
* **Regime Inference Model (HMM):**
  * Continuous Gaussian Hidden Markov Model with $K \in \{2, 3\}$ latent regimes.
  * *Emission Variables:* Low-dimensional historical state: standardized 1-day return $\widetilde{r}_t$ and realized volatility $\widetilde{\text{RV}}_{20d,t}$:
    $$\mathbf{y}_t = \begin{bmatrix} (r_t - \bar{r}_\tau) / s_{r,\tau} \\ (\text{RV}_{20d,t} - \overline{\text{RV}}_\tau) / s_{\text{RV},\tau} \end{bmatrix} \in \mathbb{R}^2, \quad \mathbf{y}_t \mid z_t = k \sim \mathcal{N}\big(\boldsymbol{\mu}_k, \boldsymbol{\Sigma}_k\big)$$
    with diagonal covariance $\boldsymbol{\Sigma}_k = \text{diag}(\sigma_{k,1}^2, \sigma_{k,2}^2)$.
  * *In-Sample Estimation:* Parameters (transition matrix $\mathbf{A}$, initial state probabilities $\boldsymbol{\rho}$, and emission parameters $\boldsymbol{\mu}_k, \boldsymbol{\Sigma}_k$) are estimated strictly within the in-sample training window $\mathcal{T}_{\tau}$ via Baum–Welch Expectation-Maximization.
* **Causal Forward Filtered Posterior Probabilities ($\pi_t$):**
  For each out-of-sample date $t$, the forward filter computes the posterior probability of being in regime $k$ using only information available through date $t$:
  $$\alpha_1(k) = \rho_k \, \mathcal{N}\big(\mathbf{y}_1; \boldsymbol{\mu}_k, \boldsymbol{\Sigma}_k\big)$$
  $$\alpha_t(k) = \mathcal{N}\big(\mathbf{y}_t; \boldsymbol{\mu}_k, \boldsymbol{\Sigma}_k\big) \sum_{j=1}^K A_{jk} \, \alpha_{t-1}(j)$$
  $$\pi_{t,k} \equiv P(z_t = k \mid \mathbf{y}_1, \dots, \mathbf{y}_t) = \frac{\alpha_t(k)}{\sum_{j=1}^K \alpha_t(j)}$$
  **STRICT ANTI-LEAKAGE RULE:** Never use smoothed probabilities $\gamma_{t,k} \equiv P(z_t = k \mid \mathbf{y}_1, \dots, \mathbf{y}_T)$ or full-sample Viterbi paths that utilize future observations $s > t$.
* **Regime Count ($K$) Selection Criteria:**
  Evaluated on validation split (2020–2021). Every regime $k$ must exhibit empirical occupancy $\ge 5.0\%$ and expected dwell time $\mathbb{E}[D_k] = 1/(1 - A_{kk}) \ge 5$ trading sessions. Default to parsimonious $K=2$; $K=3$ selected only if all states satisfy occupancy/persistence and validation NLL improves by $\Delta \text{NLL}_{\text{val}} \ge 0.020$ nats.
* **Challenger Specification ($R1$):**
  The filtered probability vector $\pi_t \in \Delta^{K-1}$ is appended to the feature vector of model $B4$:
  $$\text{Input to } R1: \quad \mathbf{v}_t = \big[ Q_t, X_t, \pi_t \big] \in \mathbb{R}^{11 + K}$$
  $R1$ shares the **identical functional form, parameter constraints, optimization algorithm, and regularization budget** as $B4$. This ensures that any measured performance difference is strictly attributable to the incremental information content of $\pi_t$.

---

## 6. Chronological Experimental Design and Evaluation Protocol

```
Timeline: 2010 to 2023 (14 Full Calendar Years: 168 Monthly Bundles)
+----------------------------------------------------+------------------+-------------------+
|               Training Window (~71.4%)             | Validation (~14%)| Held-Out Test (~14%)|
|                    2010 - 2019                     |   2020 - 2021    |    2022 - 2023    |
|                (10 full calendar years)            | (2 calendar yrs) | (2 calendar yrs)  |
+----------------------------------------------------+------------------+-------------------+
  ^                                                    ^                  ^
  |                                                    |                  |
  +-- In-sample parameter estimation                   +-- Tuning only    +-- SCORED ONCE
  +-- HMM Baum-Welch training                          +-- Model selection+-- Absolutely frozen
```

### 6.1 Split Architecture
* **Strict Chronological Ordering:** Random shuffling, k-fold cross-validation, or any non-chronological sampling is strictly barred.
* **Partition Ratios by Calendar Span (~71.4% / 14.3% / 14.3%):**
  The sample comprises exactly 14 full calendar years (168 monthly bundles). The partition boundaries are aligned cleanly with complete calendar years to avoid cutting through intra-year macro regimes:
  * **Development / Initial Training Segment (2010–2019, 10 years, ~71.4%):** Used for pipeline calibration, baseline stability tests, and initial in-sample parameter estimation across multiple market cycles.
  * **Validation Segment (2020–2021, 2 years, ~14.3%):** Spans the 2020 Covid shock and recovery. Used exclusively for hyperparameter tuning (number of HMM regimes $K \in \{2, 3\}$, regularization penalties, neural network layer width).
  * **Held-Out Test Segment (2022–2023, 2 years, ~14.3%):** Spans the 2022 rate-hiking cycle / bear market and 2023 disinflation rally. Scored only once at Gate D. Raw 2022–2023 option bundles remain unopened. (Note: January 3 and 4, 2022 cash closes and derived validation return were retrieved in Stage 6 commit `cee01a1` and remain in Git history; the test partition cannot be described as sealed or untouched).
  *(Note on Calendar Partitioning vs. Nominal Counts: This partition is strictly defined by complete calendar-year spans: 2010–2019 [Train, 10 years, ~71.4%], 2020–2021 [Val, 2 years, ~14.3%], and 2022–2023 [Test, 2 years, ~14.3%]. This preserves complete annual macro regimes. Exact session counts will be computed directly from the full calendar audit without assuming nominal totals in advance).*
* **Freezing Rule:** The test segment raw option bundles remain unopened and must not be processed, evaluated, or scored until all model architectures, hyperparameters, data cleaning rules, and calibration thresholds are permanently frozen.

### 6.2 Refit Cadence and Walk-Forward Protocol
* **Walk-Forward Refit:** Expanding window design. Models are refit periodically on an established cadence.
* **Cadence Default:** **Monthly (every 21 trading sessions)**.
* **Supervised Training vs. HMM Information Sets at Refit Origin $\tau$:**
  > [!IMPORTANT]
  > At refit origin $\tau$ (close of trading day $\tau$), the next-day target return $r_{\tau + 1} = \ln(S_{\tau + 1} / S_{\tau})$ has **not yet occurred**. Including origin $\tau$ in supervised model training would leak unobserved future return $r_{\tau + 1}$. The training partitions must strictly distinguish supervised label availability from unsupervised emission availability:
  > 1. **Supervised Model Training Set ($\mathcal{T}_{\text{sup},\tau}$):** Restricted strictly to origins whose target label $r_{s+1}$ has already been fully observed by session close $\tau$:
  >    $$\mathcal{T}_{\text{sup},\tau} \equiv \{s : 1 \le s \le \tau - 1\}$$
  >    For every origin $s \in \mathcal{T}_{\text{sup},\tau}$, the realized return $r_{s+1}$ was observed on or before session close $\tau$ (since $s \le \tau - 1 \implies s+1 \le \tau$).
  > 2. **HMM Estimation & Feature Scaler Set ($\mathcal{T}_{\text{HMM},\tau}$):**
  >    $$\mathcal{T}_{\text{HMM},\tau} \equiv \{s : 1 \le s \le \tau\}$$
  >    Because emission vector $\mathbf{y}_s = [\widetilde{r}_s, \widetilde{\text{RV}}_{20d,s}]^\top$ and feature inputs $[Q_s, X_s]$ are contemporaneous to date $s$, the realization at $s = \tau$ is fully observed at session close $\tau$ (since $r_{\tau} = \ln(S_{\tau} / S_{\tau - 1})$ is already realized).
* **Execution Rules per Refit Date $\tau$:**
  1. Fit feature scalers (medians, IQRs) strictly on $\mathcal{T}_{\text{HMM},\tau} = \{s \le \tau\}$.
  2. Estimate HMM transition and emission parameters $\boldsymbol{\theta}_{\text{HMM}}$ strictly on $\mathcal{T}_{\text{HMM},\tau} = \{s \le \tau\}$.
  3. Re-fit predictive density models $B0, B1, B2, B3, B4,$ and $R1$ **strictly on supervised pairs $\{(\mathbf{z}_s, r_{s+1})\}_{s=1}^{\tau - 1}$** ($\mathcal{T}_{\text{sup},\tau}$), with features scaled by statistics frozen at $\tau$.
  4. For the subsequent 21 sessions $t \in [\tau, \tau + 20]$:
     - For origin $t = \tau$: scale features $[Q_\tau, X_\tau]$, compute forward-filtered probability $\pi_\tau$, and generate forecast $\widehat{p}_{\tau+1}(r)$. Observe realized return $r_{\tau+1}$ after session $\tau+1$ close and record log-likelihood.
     - Advance sequentially through $t = \tau + 1, \dots, \tau + 20$: apply frozen scalers from date $\tau$ to features $Q_t, X_t$; compute causal forward filtered probabilities $\pi_t$ using frozen HMM parameters; generate 1-day density forecasts $\widehat{p}_{t+1}(r)$ using frozen predictive models; observe realized return $r_{t+1}$ after session $t+1$ close and record out-of-sample log-likelihood.
  5. Store forecast distributions, loss scores, and computation logs permanently.

### 6.3 Missing Sessions and Missing Feature Handling
* **Trading Day Alignment:** Target $r_{t+1} = \ln(S_{t+1}/S_t)$ is evaluated across consecutive active exchange trading sessions.
* **Isolated Option Gap ($\le 1$ Trading Day):** If the option chain at date $t$ is missing but the cash market traded, option features are causally forward-filled ($Q_t \leftarrow Q_{t-1}$).
* **Multi-Session Gap ($> 1$ Consecutive Trading Days):** If option chain data is unavailable for $>1$ consecutive session, forecast origin $t$ is omitted from out-of-sample loss aggregation and flagged `ERR_CONSECUTIVE_OPTION_GAP`. No backward-filling or interpolation using future data is permitted.
* **Missing Cash Close:** If $S_t$ or $S_{t+1}$ is missing, the session is excluded from scoring and flagged `ERR_MISSING_CASH_CLOSE`.

### 6.4 Performance Metrics

#### Primary Metric
* **Out-of-Sample Negative Log-Likelihood (NLL):**
  $$\mathcal{L}(M) = -\frac{1}{N_{\text{test}}} \sum_{t=1}^{N_{\text{test}}} \ln \widehat{p}_{t+1}^{(M)}(r_{t+1})$$
  Paired loss differential: $d_t = \ln \widehat{p}_{t+1}^{(R1)}(r_{t+1}) - \ln \widehat{p}_{t+1}^{(B4)}(r_{t+1})$. A positive mean differential ($\bar{d} > 0$) signifies that $R1$ assigns higher likelihood (lower log loss) to realized physical returns.

#### Secondary Forecast Metrics
1. **Continuous Ranked Probability Score (CRPS):**
   $$\text{CRPS}(\widehat{F}_{t+1}, r_{t+1}) = \int_{-\infty}^\infty \Big(\widehat{F}_{t+1}(u) - \mathbb{I}(r_{t+1} \le u)\Big)^2 du$$
   Evaluates distributional calibration and sharpness with lower sensitivity to extreme outlier points than NLL.
2. **Probability Integral Transform (PIT) Diagnostics:**
   $$u_t = \widehat{F}_{t+1}(r_{t+1}) = \int_{-\infty}^{r_{t+1}} \widehat{p}_{t+1}(s) \, ds$$
   Under perfect calibration, $u_t \sim \text{Uniform}[0, 1]$. Evaluated via:
   * Visual inspection of 10-bin PIT histogram.
   * Kolmogorov–Smirnov test and Berkowitz (2001) likelihood ratio test of normality on $z_t = \Phi^{-1}(u_t)$.
3. **Empirical Coverage & Interval Width:**
   Evaluate coverage of central predictive intervals: $50\%, 80\%$, and $95\%$. Compute empirical violation rates and mean interval width (sharpness).
4. **Quantile / Pinball Loss at Tails:**
   Quantile loss evaluated at $\alpha \in \{0.01, 0.05, 0.10, 0.90, 0.95, 0.99\}$ to verify left-tail (crash) and right-tail calibration.

### 6.5 Statistical Uncertainty and Hypothesis Testing
* **Paired Diebold–Mariano Test:**
  Compute the DM test statistic on the loss differential series $d_t$:
  $$\text{DM} = \frac{\bar{d}}{\sqrt{\widehat{\text{LRV}}(\bar{d}) / N_{\text{test}}}} \xrightarrow{d} \mathcal{N}(0, 1) \quad \text{under } H_0: \mathbb{E}[d_t] \le 0$$
  Because the target return is 1-day non-overlapping, autocorrelation at lag $>0$ is theoretically negligible. However, to guard against conditional heteroskedasticity and clustering, $\widehat{\text{LRV}}(\bar{d})$ is estimated using a Newey–West (1987) heteroskedasticity-and-autocorrelation-consistent (HAC) estimator with Bartlett kernel and automatic bandwidth $L = \lfloor 4 (N_{\text{test}} / 100)^{2/9} \rfloor$ (Newey & West, 1994).
* **Stationary Block Bootstrap:**
  Compute 95% bootstrap confidence intervals for $\bar{d}$ using a stationary block bootstrap (Politis & Romano, 1994) on the paired differential series $\{d_t\}$. Mean block length $b = \mathbb{E}[B]$ is selected via the data-dependent algorithm of Politis and White (2004) as corrected by Patton, Politis, and White (2009). Generate 2,000 bootstrap pseudo-series to construct 95% studentized and percentile confidence intervals.
* **Multiple Testing Correction:**
  To control false discovery rates across secondary diagnostic metrics (CRPS, PIT, interval coverage, quantiles), the Benjamini-Hochberg (1995) FDR procedure is applied at nominal level $q = 0.05$.
* **Statistical vs. Practical Significance:**
  * *Statistical Significance:* Achieved if one-sided Diebold-Mariano $p < 0.05$ and 95% stationary block bootstrap CI strictly excludes zero.
  * *Practical Significance:* Requires an average log predictive density improvement $\bar{d} \ge 0.010$ nats per day (~2.5 nats per year). If $\bar{d} < 0.010$, findings are documented as economically trivial despite potential statistical significance.

### 6.6 Optional Secondary Portfolio Translation
If time permits after forecast evaluation is complete, predictive distributions will be converted into an illustrative 1-asset volatility-targeting strategy (cash vs. index):
* **Exposure Rule:**
  $$w_t = \text{clip}\left(\frac{\sigma_{\text{target}}}{\widehat{\sigma}_{t+1}}, 0.0, 1.0\right)$$
  where $\sigma_{\text{target}} = 15\%$ annualized, and $\widehat{\sigma}_{t+1} = \big(\int (r - \widehat{\mu}_{t+1})^2 \widehat{p}_{t+1}(r) dr\big)^{1/2}$.
* **Execution Rules:** Long-only, no leverage ($w_t \in [0, 1]$), rebalanced daily or when $|w_t - w_{t-1}| > 0.05$.
* **Transaction Costs:** Flat 5 basis points ($0.05\%$) deducted on every unit of turnover:
  $$r_{t+1}^{\text{net}} = w_t \, r_{t+1}^{\text{total}} - 0.0005 \cdot |w_t - w_{t-1}|$$
* **Benchmarks:** Buy-and-hold SPX, static $15\%$ volatility target using trailing $\text{RV}_{20,t}$, and non-regime option volatility target ($B4$).
* **Reporting:** Net annualized return, realized volatility, Sharpe ratio, maximum drawdown, and total portfolio turnover.
* **Secondary Status:** The portfolio backtest is strictly secondary and illustrative; it cannot rescue or substitute for a failed density-forecast hypothesis.

---

## 7. Leakage Controls, Ablations, Falsification, and Novelty Delimitation

### 7.1 Strict Leakage Controls
1. **Target Leakage:** The target return $r_{t+1}$ is computed strictly using index closes after date $t$ ($S_{t+1}$). It must never enter any feature calculation, scaling parameter, or regime inference at date $t$.
2. **HMM Filtering vs. Smoothing:** Full-sample Viterbi paths or smoothed Baum–Welch probabilities ($P(z_t = k \mid r_1, \dots, r_T)$) incorporate future observations $s > t$ and are **strictly banned** from all model pipelines. Only causal forward-filtered probabilities $\pi_t$ may be generated.
3. **Information Cutoff Discipline:** The vector $[Q_t, X_t]$ must use only data available by 16:00 ET on date $t$. Any series updated after close (e.g., late macro announcements or overnight futures) is barred.

### 7.2 Controlled Ablations & Falsification Checks
To prove that $R1$ captures genuine persistent latent dynamics rather than incidental artifacts, the following falsification tests are pre-specified:

| Ablation / Falsification Test | Mechanism / Modification | What it Tests |
|---|---|---|
| **Ablation 1: Observable Volatility Control** | Add current $\text{RV}_{20,t}$ and $\text{SVIX}_t$ as direct interaction terms to $B4$. | Tests whether $R1$'s gain is merely a trivial proxy for observable volatility level. |
| **Ablation 2: Regime Probability Shuffling** | Randomly permute the vector $\pi_t$ chronologically across dates in the test set. | If the shuffled model matches $R1$, the timing of regime assignments has no genuine predictive power. |
| **Ablation 3: Static Volatility Thresholding** | Replace $\pi_t$ with a simple indicator $\mathbb{I}(\text{RV}_{20,t} > \text{Median})$. | Tests whether the Markov transition dynamics add value over simple two-state thresholding. |
| **Ablation 4: Component Removal** | Progressively remove $Q_t$ (yielding $X_t + \pi_t$), then remove $X_t$ (yielding $Q_t + \pi_t$). | Isolates whether option-implied features and historical state features are mutually complementary. |
| **Ablation 5: Regime Occupancy Check** | Monitor HMM stationary probabilities and state dwell times during rolling refits. | Rejects regime model if occupancy collapses ($<5\%$) or state switching occurs every single day (lack of persistence). |

### 7.3 Gate-Based Stop / Go Criteria

```
+-----------------------------------------------------------------------------------+
|                           Stage-by-Stage Stop / Go Gates                          |
+-----------------------------------------------------------------------------------+
  [Gate A: Data Quality & Coverage Gate] -> STATUS: QUALIFIED PASS (Stage 3/4)
  - Verify presence of contiguous monthly EOD SPX chains (2010–2023, 168 files).
  - Targeted two-date quality audit confirmed schema, 16:00 timestamp, forward parity,
    and Martin SVIX integration.
  - Benchmarked SVIX against Cboe VIX as an empirical observation (accounting for
    theoretical VIX > SVIX wedge).
  - Confirmed contract-wise OTM screening retains adequate strikes across 20–50 DTE.
  - Feature extraction algorithms for Q_t and X_t demonstrated on the two pilot dates.
                        |
                        v
  [Gate B: Calendar Audit & Feature Construction Gate] -> STATUS: BLOCKED / QUALIFIED
  - Audited 2010-2021 session continuity & reconciliation: 3,021 expected - 30 missing + 3 unexpected
    stale closure records = 2,994 observed. Aggregate missing rate 0.993% <= 1.0%, but annual missingness
    exceeds 1.0% in 5 calendar years (2011, 2014, 2019, 2020, 2021). Not a clean annual pass.
  - Audited early strike breadth (2010-2012): identified monthly-only expiry deficit in 2010-2011
    (~70% missing 30d bracketing) and weekly option regime shift in mid-2012.
  - Quote timestamps audited: uniform '16:00' vendor string, zero '13:00' early close stamps.
  - Converted T-bill discount yield to continuous rate: r = -(365/91)*ln(1-d*91/360). Causal carryforward
    on Columbus Day 2010 and Veterans Day 2016 explicitly logged (zero silent imputation).
  - Candidate feature datasets generated: Development (2,516 sessions, 2,233 feature-complete rows yielding 2,232 usable supervised training pairs [283 missing/incomplete, terminal row 2019-12-31 target nulled], SHA-256: 138fa68a...) and Validation (505 sessions, 496 feature-complete rows yielding 495 usable validation scoring rows [9 missing/incomplete, terminal row 2021-12-31 target nulled], SHA-256: 8bedc8b4...). NOT permanently frozen.
  - TEST BOUNDARY DISCLOSURE: ^GSPC closes for 2022-01-03 and 2022-01-04 accessed during download and committed in commit cee01a1 along with the 2021-12-31 target return (retained in Git history). The test partition cannot be claimed as intact or sealed. Terminal boundary labels on 2019-12-31 and 2021-12-31 set strictly to NaN to guarantee partition purity. Raw 2022–2023 option bundles remain unopened.
  - BLOCKERS: 2022–2023 test period daily continuity unaudited to avoid opening raw test bundles (deferral to Gate C / Gate D pending approval); 16:00 vs 16:15 ET cutoff unresolved (Proposals A & B pending approval; Proposal C withdrawn); complete-case filtering policy pending approval. Model training is NOT authorized. Gate B cannot be claimed as passed or closed.

                        |
                        v
  [Gate C: Baseline Stability Gate] -> MODELING PREREQUISITE
  - Fit models B0–B4 on development split (2010–2019).
  - Verify density validity on validation split (2020–2021): all densities integrate to 1.0,
    scales sigma_t > 10^-4, degrees of freedom nu_t >= 2.1, zero NaN/Inf losses.
  - Verify HMM regime persistence: dwell time >= 5 days, occupancy >= 5% in each state.
  - If MDN unstable: Simplify to single-component Student-t location-scale model.
                        |
                        v
  [Gate D: Final Evaluation & Novelty Integrity Gate] -> EVALUATION PREREQUISITE
  - Score held-out 2022–2023 test set ONCE (raw option bundles unopened; test cash close breach recorded in commit cee01a1).
  - Execute paired Diebold-Mariano test and stationary block bootstrap.
  - Report findings honestly (positive or null); freeze final write-up.
+-----------------------------------------------------------------------------------+
```

### 7.4 Explicit Limits on Novelty Claims
The project acknowledges the established literature and explicitly circumscribes its candidate scientific contribution:
1. **Prior Art Acknowledgement:**
   * [Ulrich, Walther, Rothfuss & Ferreira (2019)](file:///D:/IE612_Project/Papers/ssrn_id3437281_code3012080.pdf) (*Forward-looking P*) already demonstrated the mapping of S&P 500 option-implied features to physical return distributions using neural mixture density networks. **The use of ML to map $Q \to P$ is not claimed as novel.**
   * [DeMiguel et al. (2013)](file:///D:/IE612_Project/Papers/ssrn_id2085587_code417015.pdf) already established that option-implied volatility and skewness improve out-of-sample portfolio selection.
   * [Chernov & Ghysels (2000)](file:///D:/IE612_Project/Papers/main.pdf) established the econometric wedge between objective and risk-neutral dynamics.
   * [Bali et al. (2023)](file:///D:/IE612_Project/Papers/hhad017.pdf) established machine-learning methodologies for option predictability.
2. **Provisional Novelty Boundary:**
   The project's sole candidate contribution is:
   > Testing whether conditioning on **causally filtered, persistent latent market regimes ($\pi_t$)** provides incremental out-of-sample predictive density accuracy when mapping risk-neutral option moments and historical market state into the physical distribution of next-day returns, evaluated against a matched non-regime baseline under strict time-ordered evaluation.
3. **No Exaggerated Priority Claims:** The project makes no claim to have solved the general physical-to-risk-neutral change of measure, discovered a new arbitrage-free pricing model, or developed an investable trading system.

---

## 8. Unresolved Decisions Requiring Confirmation Post-Audit

The following operational choices are explicitly labeled as **UNRESOLVED** and must be resolved based on the empirical findings of the Stage 2 data audit and course administrative directives:

| Unresolved Decision | Governing Constraints | Provisional Default | Action Required in Stage 2 Audit |
|---|---|---|---|
| **1. Exact Historical Sample Range** | Must have contiguous daily EOD coverage and multiple market cycles (stress and calm). | **2010-01-01 to 2023-12-31** (14 full calendar years, 168 monthly bundles) | **Gate B Status:** 2010–2021 daily session continuity audited (3,021 expected, 2,994 observed, 30 missing, 0.993% aggregate missing rate). 2022–2023 test period daily continuity unaudited to avoid opening raw test option bundles; January 3 and 4, 2022 cash closes and derived label were committed in cee01a1 and remain in Git history. |
| **2. Exact Split Boundary Dates** | Train/Val/Test calendar span aligned with macro regimes. | **Train:** 2010-2019 (~71.4%) <br>**Val:** 2020-2021 (~14.3%) <br>**Test:** 2022-2023 (~14.3%) | **Provisional Default Fixed:** Calendar-year partition (~71.4% / 14.3% / 14.3% by year span) approved; exact usable session counts will be computed from the full calendar audit without assuming nominal totals. |
| **3. Risk-Free Rate Source & Curve** | Forward inversion requires reliable daily risk-free rates matching contract DTE. | **Daily 13-week T-Bill (^IRX) or FRED 1M/3M CMT** | **Gate B Status (Stage 6):** Continuous day-count conversion derived and implemented in interim datasets ({\\text{cont}} = -\\frac{365}{91} \\ln(1 - d \\frac{91}{360})$). Multi-tenor curve matching remains open. Stage 4 demonstration rates (.508\\%$ and .918\\%$) preserved as illustrative benchmarks. |
| **4. Density Architecture Selection** | Balance between flexible multi-modality and numerical training stability on daily series. | **Student-$ Location-Scale Regression** (Primary fallback: 2-component MDN) | Evaluate MDN log-likelihood stability on validation split. If loss divergence or mode collapse occurs, freeze Student-$. |
| **5. Number of Latent Regimes ($)** | Must maintain distinct, economically interpretable state separation without overfitting. | ** = 2$ (Low Vol / High Vol)** (Test =3$ on validation only) | Inspect state occupancy in validation refits. If any state has $<5\\%$ dwell time, freeze =2$. |
| **6. Inclusion of Secondary Portfolio Backtest** | Depends on course rubric requirements and remaining time in the 1-month timeline. | **Optional secondary deliverable** | Confirm with course instructor/rubric whether portfolio allocation is required or purely illustrative. |
| **7. OptionsDX Raw Redistribution Compliance** | OptionsDX terms prohibit public redistribution of raw CSV files. | **Local gitignore of Data/** | Ensure .gitignore permanently excludes raw files; include only processed features or code in final hand-in. |
| **8. Information Cutoff & Quote Synchronization** | Cash equity closes at 16:00 ET; SPX options historically traded until 16:15 ET. 15-minute lookahead must be prevented. | **Unresolved Cutoff Gate** | **Gate B Status (Stage 6):** Empirical audit verified uniform '16:00' vendor string, but absence of exchange timestamp proof leaves 16:15 ET lookahead risk active. Operational model fitting remains strictly gated. |

---

*End of Research Protocol. This document is frozen and serves as the benchmark against which all subsequent stages will be validated.*
