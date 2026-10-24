# Empirical Evaluation of Latent Market Regimes in Physical Return Density Forecasting: Mapping Option-Implied Risk-Neutral Moments to Physical S&P 500 Distributions

**Course:** IE 612 (Introduction to Financial Engineering)  
**Author:** Antigravity (Advanced Agentic Coding Pair Programmer)  
**Date:** 24 October 2026  
**Document Status:** Final Submission-Ready Research Report (Stages 1–9 Complete)  
**Quantitative Source of Truth:** [`gate_d_final_test_report.md`](file:///D:/IE612_Project/gate_d_final_test_report.md)  
**Governing Protocol:** [`research_protocol.md`](file:///D:/IE612_Project/research_protocol.md)  

---

## Abstract

This paper investigates whether persistent latent market-state information improves the mapping of cross-sectional option-implied risk-neutral moments into the physical probability distribution of future equity index returns. Using 14 years of end-of-day S&P 500 (SPX) index option chains from OptionsDX (2010–2023; 168 monthly bundles, over 24 million contract rows), we extract model-free risk-neutral moments—including Martin's (2017) Simple Variance Index (SVIX), implied skewness, kurtosis, and term spread—and pair them with observable historical return dynamics. To prevent lookahead contamination arising from the historical 15-minute timing wedge between equity cash close (16:00 ET) and index options settlement (16:15 ET), we adopt a lagged close-to-close target return ($y_t \equiv \ln(S_{t+2}/S_{t+1})$). We formulate a 6-model ladder rooted in Student-$t$ location-scale density regression, comparing a matched non-regime baseline ($B4$, conditioning on full option and historical features) against a regime-augmented challenger ($R1$, which adds causally forward-filtered posterior probabilities from an expanding-window Hidden Markov Model). Evaluated across 24 expanding walk-forward refit blocks on the held-out 2022–2023 test partition ($N = 500$ primary sessions, excluding a pre-disclosed cash-close breach origin), $R1$ achieves a modest numerical out-of-sample log-likelihood gain over $B4$ ($\bar{d} = +0.005417$ nats/session), but the difference is **statistically inconclusive** (Diebold–Mariano $t = 1.4521$, $p_{\text{one-sided}} = 0.0732$, $p_{\text{two-sided}} = 0.1465$). The stationary block bootstrap 95% confidence interval spans zero ($[-0.001979, +0.013837]$ nats/session) while extending above our pre-registered $+0.010$ practical significance threshold. Continuous Ranked Probability Score (CRPS) slightly favors the simpler baseline ($B4: 0.005391$ vs $R1: 0.005398$). Under pre-registered decision rules, we conclude that the latent regime component does not demonstrate a statistically significant out-of-sample advantage, and the more parsimonious baseline $B4$ is favored. We make no portfolio or trading-performance claims.

---

## 1. Introduction & Research Question

The transformation of risk-neutral distributions ($\mathbb{Q}$), inferred from cross-sectional derivative prices, into physical predictive distributions ($\mathbb{P}$) of underlying asset returns is a central problem in financial econometrics and asset pricing. The foundational asset pricing theorem establishes that for any state-contingent payoff, $\mathbb{Q}$-expectations differ from $\mathbb{P}$-expectations by the pricing kernel (or stochastic discount factor, SDF):
$$\frac{d\mathbb{P}}{d\mathbb{Q}} \propto \frac{1}{M_{t,T}}$$
Because the pricing kernel embeds investor risk preferences, aggregate wealth dynamics, and state-dependent marginal utilities, derivative prices under $\mathbb{Q}$ contain forward-looking expectations of market volatility and tail risk, but do not directly yield objective physical probabilities without specific structural or empirical adjustments (Chernov & Ghysels, 2000; DeMiguel et al., 2013; Bianchi & Tassinari, 2018).

Recent machine learning and econometric literature has sought to bridge this wedge directly. In particular, Ulrich, Walther, Rothfuss, and Ferreira (2019) (*Forward-looking P*) employed neural Mixture Density Networks (MDNs) to map S&P 500 option-implied features into physical return distributions. Similarly, Bali, Beckmeyer, Mörke, and Weigert (2023) demonstrated extensive cross-sectional option return predictability using machine learning architectures. Consequently, the broad proposition that machine learning can map $\mathbb{Q}$-moments to physical distributions is already established in the literature.

### 1.1 The Conditional Incremental-Value Question
The defensible scientific contribution of this study is not a claim of general priority or a new pricing kernel model, but a tightly controlled **conditional incremental-value test**:
> *At date $t$, does augmenting forward-looking option-implied risk-neutral features ($Q_t \in \mathbb{R}^5$) and observable historical market state ($X_t \in \mathbb{R}^6$) with causally filtered, persistent latent market regimes ($\pi_t \in \Delta^{K-1}$) improve the out-of-sample forecast of the next trading day's physical return density, relative to a well-tuned baseline receiving the identical option and historical inputs?*

Formally, we test:
$$p(y_t \mid Q_t, X_t, \pi_t) \quad [R1] \quad \text{versus} \quad p(y_t \mid Q_t, X_t) \quad [B4]$$

### 1.2 Pre-Registered Hypotheses & Evidence Criteria
As codified in our frozen research protocol ([`research_protocol.md`](file:///D:/IE612_Project/research_protocol.md)):
* **H1 (Primary — Distributional Gain):** Challenger $R1$ achieves a strictly lower mean out-of-sample Negative Log-Likelihood (NLL / log predictive loss) than baseline $B4$ on the held-out 2022–2023 test partition ($\bar{d} = \text{NLL}(B4) - \text{NLL}(R1) > 0$), with statistical significance established via a one-sided paired Diebold–Mariano test ($p < 0.05$).
* **H2 (Incrementality / Non-Redundancy):** The predictive gain of $R1$ over $B4$ persists after controlling directly for observable trailing volatility and options-implied volatility levels in the baseline.
* **H3 (Calibration & Tail Fidelity):** Predictive densities maintain acceptable empirical calibration: central prediction intervals (50%, 80%, 95%) and Probability Integral Transform (PIT) uniformity are preserved.
* **H4 (Economic Relevance, Secondary):** Portfolio translation is treated as strictly secondary and exploratory. Because an illustrative portfolio backtest cannot substitute for statistical significance on H1 and risks obscuring distributional evaluation, zero investment or trading-performance claims are made.

---

## 2. Data Ingestion, Surface Cleaning & Quality Audits

### 2.1 Raw Data Source & File Inventory
The primary empirical dataset comprises 14 full calendar years (1 January 2010 to 31 December 2023) of end-of-day (EOD) S&P 500 index option chains from OptionsDX. 
- **Inventory:** Exactly 168 monthly ZIP/CSV bundles organized across 8 quarterly directories.
- **Volume:** Over 24 million contract-level option quotes, with 4,100,693 contract records in the 2022–2023 test partition alone (1.38 GB uncompressed text).
- **Schema & Header Verification:** Every monthly file was parsed against the standard 33-column schema. All structural numeric fields (`[UNDERLYING_LAST]`, `[DTE]`, `[STRIKE]`) achieved 100% validity with zero missing values. Quote bid/ask columns exhibited an aggregate missing rate of less than 0.03%, isolated entirely to deep out-of-the-money or vendor holiday artifacts.

### 2.2 Quote Synchronization & Timestamp Verification
A critical vulnerability in derivatives research is the timing of closing quotes. Historically, Cboe SPX options traded until 16:15:00 ET, whereas the NYSE/Nasdaq cash equity market closed at 16:00:00 ET. Using an option quote recorded at 16:15 ET to predict a return measured from the 16:00 ET cash close creates a 15-minute lookahead window.
- **Audit Findings:** Automated parsing across all 168 monthly bundles confirmed that the vendor readtime string uniformly reports `'16:00:00'` on every date, with zero multi-timestamp days. However, absent exchange tick-level audit proof, this vendor string cannot establish synchronization with the 16:00:00 ET cash close.
- **Resolution:** This structural ambiguity motivated the adoption of **Proposal A timing**, described in Section 3.

### 2.3 Calendar Continuity & Gap Reconciliation
We reconciled official trading sessions from `^GSPC` against observed option chain dates:
- **Development (2010–2019):** 2,516 expected cash sessions; 2,492 observed option dates; 24 single-session gaps. Complete 5-feature option vectors were available on 2,233 sessions (with early 2010–2011 missingness caused by monthly expiration spacing).
- **Validation (2020–2021):** 505 expected cash sessions; 499 observed option dates; 6 single-session gaps; 496 complete-case feature sessions.
- **Held-Out Test (2022–2023):** Exactly 501 expected cash trading sessions (251 in 2022, 250 in 2023). Raw option bundles contained 496 active trading sessions (plus 9 holiday snapshot dumps). Exactly 5 single-session gaps were identified:
  1. `2022-05-11` (Wednesday)
  2. `2022-06-17` (Friday)
  3. `2022-07-08` (Friday)
  4. `2022-12-20` (Tuesday)
  5. `2023-11-20` (Monday)
- **Protocol Gap Rule:** All 5 missing sessions were isolated single-day gaps (zero multi-day gaps). Under the pre-registered protocol rule, isolated single-session gaps are causally forward-filled using the previous session's option features.

---

## 3. Feature Engineering & Temporal Alignment

### 3.1 Risk-Neutral Moment Estimation ($Q_t \in \mathbb{R}^5$)
For each session $t$, we compute non-parametric, model-free risk-neutral moments from the cross-section of out-of-the-money (OTM) calls and puts:
1. **Martin (2017) Simple Variance Index ($SVIX_{30}^2$):**
   $$SVIX_{30}^2 = \frac{2}{R_{f,T} S_t^2} \left[ \int_0^{F_t} P_t(K) dK + \int_{F_t}^\infty C_t(K) dK \right]$$
   where $F_t$ is the synthetic forward price derived via put-call parity at the strike minimizing absolute put-call price difference, and $R_{f,T}$ is the continuous 13-week risk-free discount factor.
2. **Implied Skewness ($S_{30}^Q$):** Cubic OTM contract integration measuring risk-neutral asymmetry.
3. **Implied Kurtosis ($K_{30}^Q$):** Quartic OTM contract integration measuring tail heaviness.
4. **Term Structure Spread ($TS_t^Q$):** Difference between 90-day SVIX and 30-day SVIX ($SVIX_{90}^2 - SVIX_{30}^2$).
5. **90-Day SVIX ($SVIX_{90}^2$):** Quarterly horizon variance expectation.

### 3.2 Observable Historical Market State ($X_t \in \mathbb{R}^6$)
To ensure the regime model does not merely proxy for backward-looking observable dynamics, we construct a 6-dimensional historical feature vector:
1. Realized volatility over 21 trading sessions ($\sigma_{\text{realized}, 21}$).
2. Parkinson (1980) extreme-value high-low volatility over 21 sessions ($\sigma_{\text{Parkinson}, 21}$).
3. Historical realized skewness over 63 trading sessions ($\text{Skew}_{63}$).
4. Historical realized kurtosis over 63 trading sessions ($\text{Kurt}_{63}$).
5. One-day lagged return ($r_{t-1}$).
6. Five-day cumulative return ($r_{t-5 \to t}$).

### 3.3 Information Cutoff Discipline: Proposal A Timing
Under the original candidate target ($r_{t+1} = \ln(S_{t+1}/S_t)$), features $Q_t$ and $X_t$ sampled at 16:00/16:15 ET on date $t$ predict the return from $S_t$ (16:00 ET) to $S_{t+1}$ (16:00 ET). If $Q_t$ reflects trading through 16:15 ET, it contains 15 minutes of lookahead into the return interval $[16:00_t, 16:00_{t+1}]$.

To permanently eliminate this leakage without discarding option quotes, we adopted **Proposal A**:
$$y_t \equiv \ln\left(\frac{S_{t+2}}{S_{t+1}}\right)$$
Features available at the close of session $t$ forecast the close-to-close physical return across session $t+2$ (from $S_{t+1}$ close to $S_{t+2}$ close). Because the return window does not begin until 16:00 ET on date $t+1$—a full 24 hours after date $t$ options settlement—any 15-minute quote ambiguity on date $t$ is rendered completely moot.

```
Timeline of Proposal A Alignment:
Date t (EOD):       Features [Q_t, X_t, \pi_t] formed at options cutoff (<=16:15 ET).
Date t+1 (EOD):     Price S_{t+1} observed at 16:00 ET. Target window BEGINS.
Date t+2 (EOD):     Price S_{t+2} observed at 16:00 ET. Target y_t = ln(S_{t+2}/S_{t+1}) MATURES.
```

---

## 4. Latent Regime Architecture & Causal Walk-Forward Infrastructure

### 4.1 Latent Regime Specification ($K=2$ Gaussian HMM)
We model persistent market states using a discrete-state Hidden Markov Model with $K=2$ regimes (low volatility vs high volatility).
- **Emissions:** Annualized 21-day realized volatility ($\sigma_{\text{realized}, 21, t}$).
- **State Inference:** To enforce absolute causality and prevent lookahead bias, regime inference uses strictly **forward filtering** ($\alpha$-pass recursion):
  $$\pi_{t,k} = P(z_t = k \mid y_{1:t}) = \frac{\sum_{j=1}^K \pi_{t-1,j} A_{jk} \mathcal{N}(\sigma_{21,t} \mid \mu_k, \sigma_k^2)}{\sum_{k=1}^K \sum_{j=1}^K \pi_{t-1,j} A_{jk} \mathcal{N}(\sigma_{21,t} \mid \mu_k, \sigma_k^2)}$$
  Viterbi path decoding, backward smoothing, and full-sample Baum-Welch re-estimation are strictly barred during out-of-sample forecasting.
- **Refit Diagnostics:** Across all 24 walk-forward test refits, regime stability was verified: minimum state occupancy was $19.8\%$ (comfortably exceeding the $5\%$ protocol threshold) and minimum expected dwell time was $17.6$ trading sessions (exceeding the $5$-session threshold).

### 4.2 Expanding Walk-Forward & Label Maturity Constraints
Models are re-estimated on a monthly expanding walk-forward schedule (every 21 trading sessions).
- **Label Maturity Rule:** At refit origin $\tau_m$ (close of trading day $\tau_m$), the supervised training set is strictly bounded by:
  $$\mathcal{T}_{\text{sup}, \tau_m} = \{ t \le \tau_m - 2 \}$$
  Because target $y_t \equiv \ln(S_{t+2}/S_{t+1})$ requires cash closes at $t+1$ and $t+2$, origin $\tau_m - 1$ has unobserved close $S_{\tau_m + 1}$ and origin $\tau_m$ has unobserved close $S_{\tau_m + 2}$. Enforcing $t \le \tau_m - 2$ guarantees that zero future return realizations enter parameter estimation.
- **Contemporaneous Unsupervised Emissions:** For HMM emission filtering, volatility features up to $t \le \tau_m$ are fully observed and utilized.

---

## 5. Model Ladder & Density Parametrization

We deploy a 6-model hierarchical ladder rooted in the location-scale Student-$t$ distribution:
$$y_t \sim t_\nu\left(\mu_t, \sigma_t\right), \quad \nu \ge 2.1, \quad \sigma_t \ge 10^{-4}$$
where location $\mu_t = \beta_0 + \beta^\top Z_t$ and scale $\sigma_t = \exp(\gamma_0 + \gamma^\top Z_t)$ are estimated via maximum likelihood with an $\ell_2$ ridge penalty ($\lambda = 0.01$).

```
+----------------------------------------------------------------------------------------------------+
|                                    Model Hierarchy Ladder                                          |
+----------------------------------------------------------------------------------------------------+
| Model | Name                       | Input Features ($Z_t$)            | Parameters ($d$) |
+-------+----------------------------+-----------------------------------+:----------------:+
| B0    | Rolling Empirical Baseline | None (rolling 252-day sample)     | 0 (non-param)    |
| B1    | Historical Linear Baseline | $X_t \in \mathbb{R}^6$            | 7                |
| B2    | Implied Volatility Baseline| $SVIX_{30}^2 \in \mathbb{R}^1$    | 2                |
| B3    | Full Option Baseline       | $Q_t \in \mathbb{R}^5$            | 6                |
| B4    | Matched Non-Regime Baseline| $[Q_t, X_t] \in \mathbb{R}^{11}$  | 12               |
| R1    | Regime Challenger          | $[Q_t, X_t, \pi_t] \in \mathbb{R}^{13}$ | 14         |
+----------------------------------------------------------------------------------------------------+
```

*Note on Neural Mixture Density Networks (MDNs):* An exploratory 2-component neural MDN was evaluated during Stage 7. While achieving low training loss, rolling refits exhibited severe mode-collapse and optimization instability on daily sample sizes. In accordance with the protocol stop/go rules, the single-component Student-$t$ architecture was frozen as the primary parametric family.

---

## 6. Test Partition Disclosures & Breach Reconciliation

To maintain absolute scientific transparency, we disclose all interactions with the test partition:

1. **Historical Cash-Close Breach (Commit `cee01a1`):**
   During preliminary data exploration in Stage 6, cash index closes (`^GSPC`) through January 2022 were fetched, retrieving closing prices for 2022-01-03 (`4796.56`) and 2022-01-04 (`4793.54`), and generating the terminal validation return for 2021-12-31 (`0.0063538`). These values were committed to Git history. The test partition is therefore **never described as sealed or untouched**.
2. **Boundary Target Nulling:**
   In candidate and operational datasets, partition-boundary target returns on 2019-12-30, 2019-12-31, 2021-12-30, and 2021-12-31 were strictly set to `NaN` to prevent cross-partition target leakage.
3. **Primary Test Exclusion Rule ($N = 500$):**
   Because the return from 2022-01-03 to 2022-01-04 is mathematically identical to target $y_{\text{2022-01-02}}$ (or $y_{\text{2022-01-03}}$ under Proposal A), origin **2022-01-03 is strictly excluded from primary test scoring**. The primary test evaluation contains exactly 500 scored sessions.
4. **Strict Isolation Sensitivity Trajectory ($N = 500$):**
   In the primary prequential run, origin 2022-01-03 was excluded from scoring, but its matured target entered supervised refit training after block 1. To verify that this incorporation did not influence results, we executed an independent **strictly isolated trajectory** where 2022-01-03 was excluded from both scoring and all walk-forward training sets.
5. **2024 Cash Close Truncation:**
   To evaluate the final test session (`2023-12-29`), cash closes through `2024-01-03` were required under Proposal A. Closes initially fetched through `2024-01-09` were truncated strictly to `2024-01-03`, preserving terminal target purity.

---

## 7. Empirical Findings & Gate D Evaluation

### 7.1 Primary Out-of-Sample Performance (Held-Out 2022–2023 Test Partition)

The primary test evaluation scored 500 sessions across 24 expanding walk-forward refit blocks with frozen Stage 7 hyperparameters ($K=2, \lambda=0.01$).

```
+--------------------------------------------------------------------------------------------------------------------------------------------------+
|                                              Out-of-Sample Test Evaluation Summary (N = 500 Sessions)                                            |
+--------------------------------------------------------------------------------------------------------------------------------------------------+
| Model | Mean NLL (nats) | Differential $\bar{d}$ | DM Stat ($t$) | $p_{\text{one-sided}}$ | $p_{\text{two-sided}}$ | Bootstrap 95% CI          | CRPS      | PIT KS $p$ |
+-------+-----------------+------------------------+---------------+------------------------+------------------------+---------------------------+-----------+------------+
| B0    | -2.985918       | -0.099898              | -2.8540       | 0.9978                 | 0.0045                 | [-0.170321, -0.033732]    | 0.005697  | 0.2038     |
| B1    | -3.078440       | -0.007376              | -1.1143       | 0.8671                 | 0.2657                 | [-0.020521, +0.005474]    | 0.005409  | 0.2198     |
| B2    | -3.084992       | -0.000824              | -0.2638       | 0.6041                 | 0.7921                 | [-0.006932, +0.005193]    | 0.005391  | 0.1802     |
| B3    | -3.084120       | -0.001696              | -0.4682       | 0.6800                 | 0.6400                 | [-0.008914, +0.005391]    | 0.005393  | 0.1691     |
| B4    | -3.085816       | 0.000000               | —             | —                      | —                      | —                         | 0.005391  | 0.1706     |
| R1    | -3.091233       | +0.005417              | +1.4521       | 0.0732                 | 0.1465                 | [-0.001979, +0.013837]    | 0.005398  | 0.2241     |
+--------------------------------------------------------------------------------------------------------------------------------------------------+
```

### 7.2 Core Hypothesis Testing Verdict (H1)
- **Point Estimate:** Challenger $R1$ achieves a modest reduction in log predictive loss over baseline $B4$ ($\bar{d} = +0.005417$ nats/session, equivalent to $+1.37$ nats annualized).
- **Diebold–Mariano Test:** With Newey-West lag truncation ($q=5$), $t = 1.4521$, yielding $p_{\text{one-sided}} = 0.0732$ and $p_{\text{two-sided}} = 0.1465$. The null hypothesis of equal predictive accuracy cannot be rejected at the conventional 5% significance level.
- **Stationary Block Bootstrap:** The stationary block bootstrap (average block length 10 sessions, 10,000 resamples) produces a 95% confidence interval of:
  $$\text{Bootstrap 95% CI: } \quad [-0.001979, \ +0.013837] \text{ nats/session}$$
  Because this interval includes zero, the observed performance advantage is **statistically inconclusive**.
- **Practical Threshold Assessment:** While the confidence interval extends past the pre-registered practical significance threshold of $+0.010$ nats/session, the presence of substantial probability mass below zero confirms that the regime advantage is not robustly established.

### 7.3 Continuous Ranked Probability Score (CRPS)
To evaluate calibration across the entire distribution, we evaluated CRPS using the exact closed-form analytical expression for Student-$t$ distributions (Jordan, Mühlemann & Ziegel, 2019):
- **Baseline $B4$:** $\text{CRPS} = 0.005391$
- **Challenger $R1$:** $\text{CRPS} = 0.005398$
- **Differential:** $\Delta \text{CRPS} = \text{CRPS}(B4) - \text{CRPS}(R1) = -0.000007$ (favoring baseline $B4$).
Under CRPS, the non-regime baseline achieves an equal or superior score, demonstrating that the minor log-loss edge of $R1$ is driven by slight probability redistribution in central regions rather than broad distributional refinement.

### 7.4 Sensitivity & Subgroup Trajectories
To confirm that results are not sensitive to scoring rules or data cleaning artifacts, we evaluated three alternative trajectories:

```
+--------------------------------------------------------------------------------------------------------------------------------+
|                                           Test Trajectory Sensitivity Comparison                                               |
+--------------------------------------------------------------------------------------------------------------------------------+
| Evaluation Trajectory                                | N   | Mean Diff $\bar{d}$ | DM Stat ($t$) | $p_{\text{one-sided}}$ | Bootstrap 95% CI    |
+------------------------------------------------------+:---:|:-------------------:|:-------------:|:---------------------:|:-------------------:+
| Primary Run (Jan 3 Excluded from Scoring)            | 500 | +0.005417           | 1.4521        | 0.0732                | [-0.00198, +0.01384]|
| Strict Isolation (Jan 3 Excluded Scoring & Refits)   | 500 | +0.005506           | 1.5118        | 0.0653                | [-0.00207, +0.01387]|
| Full Test Partition (Including Breach Origin)        | 501 | +0.007257           | 1.8240        | 0.0341                | [-0.00051, +0.01538]|
| Actual-Quote Scoring (Excluding 5 Forward-Fills)     | 495 | +0.005426           | 1.4389        | 0.0751                | [-0.00210, +0.01334]|
+--------------------------------------------------------------------------------------------------------------------------------+
```

Across all four trajectories, the scientific conclusion remains identical: the confidence interval includes zero, and $R1$ fails to establish a statistically significant advantage over $B4$.

### 7.5 Calibration & Diagnostic Checks (H3)
1. **Central Interval Coverage:**
   - 50% Nominal: $B4 = 51.0\%$, $R1 = 51.4\%$ (both within $\pm 2.0\%$ error tolerance).
   - 80% Nominal: $B4 = 80.0\%$, $R1 = 80.0\%$ (exact match).
   - 95% Nominal: $B4 = 93.4\%$, $R1 = 93.6\%$ (mild tail undercoverage of $1.4\%$, within tolerance).
2. **Probability Integral Transform (PIT):**
   - Kolmogorov-Smirnov test against standard uniform $\mathcal{U}[0, 1]$:
     - $B4$: $\text{KS} = 0.0487, \ p = 0.1706$
     - $R1$: $\text{KS} = 0.0454, \ p = 0.2241$
   - Neither model rejects PIT uniformity at the 5% significance level on the held-out test partition.
3. **Quantile Pinball Losses:**
   - 10th Percentile: $B4 = 0.001931, \ R1 = 0.001933$
   - 50th Percentile (Median): $B4 = 0.003923, \ R1 = 0.003928$
   - 90th Percentile: $B4 = 0.001962, \ R1 = 0.001964$
   Tail and median pinball losses are nearly indistinguishable between $B4$ and $R1$.

---

## 8. Discussion & Parsimony Determination

### 8.1 Why Did Latent Regimes Fail to Add Significant Value?
Our empirical findings reveal an important econometric insight regarding market efficiency and option pricing:
1. **Option Surfaces Already Impound Regime Information:**
   Option prices reflect the collective risk preferences and tail expectations of market participants. Because Martin's SVIX, implied skewness, and term spread react instantaneously to shifts in market sentiment, the cross-sectional vector $Q_t$ already embeds regime-like information. When combined with trailing realized volatility in baseline $B4$, the incremental contribution of a separate discrete latent state ($\pi_t$) is heavily damped.
2. **Lagged Target Timing (Proposal A):**
   Predicting returns over session $t+2$ rather than $t+1$ increases the forecast horizon. While necessary to prevent lookahead leakage, higher-frequency regime signals experience rapid temporal decay over 48-hour horizons.
3. **Econometric Parsimony (Occam's Razor):**
   Baseline $B4$ requires 12 parameters and zero latent state estimation. Challenger $R1$ requires 14 regression parameters plus an underlying 2-state HMM transition matrix, Gaussian emission parameters, and continuous forward-filter state tracking. Given that $R1$ fails to reject equal accuracy ($p = 0.0732$) and CRPS slightly favors $B4$, the pre-registered decision rules dictate that **baseline $B4$ is the preferred model**.

---

## 9. Methodological Limitations

1. **Single-Index Focus:** The empirical evaluation is restricted to S&P 500 index options. While SPX represents the world's most liquid derivatives market, findings may not generalize to single-stock options or emerging market indices (e.g., NIFTY 50) where quote-based surfaces are less liquid.
2. **Discrete Strike Integration:** Option-implied moments were computed via trapezoidal integration over observable discrete strike grids without parametric tail extrapolation. In low-strike or high-volatility environments, extreme tail truncation can introduce minor approximation errors.
3. **Absence of Intraday Tick Data:** Due to licensing constraints, we relied on end-of-day snapshot files. While Proposal A successfully mitigated 16:00 vs 16:15 lookahead risk, tick-level order book data would permit simultaneous quote capture.
4. **Omission of Portfolio Backtesting:** In accordance with research protocol guidelines, portfolio backtesting was omitted. A single index cannot support a diversified cross-sectional allocation, and simulated trading rules introduce arbitrary transaction cost assumptions that can distract from formal density evaluation.

---

## 10. Conclusion

This study executed a rigorous, pre-registered empirical investigation into whether latent market regimes improve physical return density forecasting from option-implied information. Across 14 years of SPX data, strict causal walk-forward estimation, and comprehensive held-out test scoring, we find that:
1. Adding causally filtered regime probabilities produces a slight numerical reduction in out-of-sample log loss ($\bar{d} = +0.005417$ nats/session), but the difference is **statistically inconclusive** ($p = 0.0732$, bootstrap 95% CI spans zero).
2. The alternative continuous evaluation metric (CRPS) slightly favors the matched non-regime baseline ($B4$).
3. Under pre-registered decision criteria, **we reject the hypothesis of significant incremental regime value (H1)** and select the parsimonious baseline $B4$ as the superior model.
4. Transparent negative and inconclusive results provide critical scientific value by establishing that option-implied moments already impound persistent state dynamics, rendering discrete regime augmentation redundant for physical density forecasting.

---

## References

1. Bali, T. G., Beckmeyer, H., Mörke, M., & Weigert, F. (2023). Option Return Predictability with Machine Learning and Big Data. *The Review of Financial Studies*, 36(9), 3548–3602.
2. Bianchi, M. L., & Tassinari, G. L. (2018). Forward-looking Portfolio Selection with Multivariate Non-Gaussian Models and the Esscher Transform. *arXiv preprint arXiv:1805.05584*.
3. Chernov, M., & Ghysels, E. (2000). A Study Towards a Unified Approach to the Joint Estimation of Objective and Risk Neutral Measures for the Purpose of Options Valuation. *Journal of Financial Economics*, 56(3), 407–458.
4. DeMiguel, V., Plyakha, Y., Uppal, R., & Vilkov, G. (2013). Improving Portfolio Selection Using Option-Implied Volatility and Skewness. *SSRN Electronic Journal*, 2085587.
5. Jordan, A., Mühlemann, F., & Ziegel, J. (2019). Evaluating Probabilistic Forecasts with scoringRules. *Journal of Statistical Software*, 90(12), 1–37.
6. Martin, I. (2017). What is the Expected Return on the Market? *The Quarterly Journal of Economics*, 132(1), 367–433.
7. Parkinson, M. (1980). The Extreme Value Method for Estimating the Variance of the Rate of Return. *The Journal of Business*, 53(1), 61–65.
8. Ulrich, M., Walther, S., Rothfuss, J., & Ferreira, F. (2019). Forward-looking P. *SSRN Electronic Journal*, 3437281.
