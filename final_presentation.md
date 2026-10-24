# Empirical Evaluation of Latent Market Regimes in Physical Return Density Forecasting
## Mapping Option-Implied Risk-Neutral Information to Physical S&P 500 Distributions

**Course:** IE 612 (Introduction to Financial Engineering)  
**Author:** Antigravity (Advanced Agentic Coding Pair Programmer)  
**Date:** 24 October 2026  
**Document Status:** Final Course Presentation Deck  

---

<!-- slide -->
## 1. Research Motivation & Core Question

### The $Q \to P$ Econometric Wedge
- Risk-neutral distributions ($\mathbb{Q}$) inferred from option prices reflect **market expectations and risk aversion**, not objective physical probabilities ($\mathbb{P}$).
- The Radon-Nikodym derivative connecting them is the pricing kernel:
  $$\frac{d\mathbb{P}}{d\mathbb{Q}} \propto \frac{1}{M_{t,T}}$$
- Can machine learning or econometric models reliably bridge this gap?

### Our Research Question
> *At date $t$, does conditioning on causally filtered, persistent latent market regimes ($\pi_t$) improve out-of-sample physical density forecasts of the S&P 500, relative to a strong baseline already receiving the identical option-implied ($Q_t$) and historical market ($X_t$) inputs?*

$$\text{Comparative Test: } \quad p(y_t \mid Q_t, X_t, \pi_t) \quad [R1] \quad \text{vs.} \quad p(y_t \mid Q_t, X_t) \quad [B4]$$

---

<!-- slide -->
## 2. Theoretical Grounding & Novelty Boundary

### Established Prior Art (What is NOT Claimed as Novel)
- **$Q \to P$ Mapping via ML:** Ulrich, Walther, Rothfuss & Ferreira (2019) (*Forward-looking P*) mapped SPX option surfaces to physical return densities using Mixture Density Networks.
- **Option Moments in Asset Allocation:** DeMiguel, Plyakha, Uppal & Vilkov (2013) demonstrated that risk-neutral volatility and skewness enhance portfolio selection.
- **Option Predictability:** Bali, Beckmeyer, Mörke & Weigert (2023) established machine learning methodologies for option predictability.

### Our Specific Incremental Contribution
- A tightly controlled, pre-registered **incremental-value test**: does adding a causally filtered latent state ($\pi_t$) from an HMM provide statistically significant predictive gain beyond a matched baseline with rich option and historical features, under strict walk-forward temporal order?

---

<!-- slide -->
## 3. Data Ingestion & Quality Audits

### 14 Years of High-Fidelity Derivatives Data
- **Source:** OptionsDX S&P 500 (SPX) end-of-day option chains (2010–2023).
- **Scale:** Exactly 168 monthly ZIP/CSV bundles, >24 million contract rows (4.1 million rows in 2022–2023 test partition alone).
- **Quality Audits:**
  - 100% schema match across all 33 columns.
  - Zero missing values in structural fields (`UNDERLYING_LAST`, `DTE`, `STRIKE`).
  - Readtime timestamps uniformly verify `'16:00:00'` across all files.

### Calendar Alignment & Gap Handling
- Reconciled against official `^GSPC` cash trading calendar (501 sessions in 2022–2023).
- Identified exactly 5 single-session missing option dates in 2022–2023.
- **Pre-Registered Protocol Rule:** Isolated single-day gaps are causally forward-filled; zero multi-day gaps observed.

---

<!-- slide -->
## 4. Information Cutoff Discipline: Proposal A Timing

### The 16:00 vs. 16:15 ET Lookahead Trap
- Cash equity closes at **16:00:00 ET**, but Cboe SPX options historically traded until **16:15:00 ET**.
- Predicting standard next-day return $r_{t+1} = \ln(S_{t+1}/S_t)$ risks 15 minutes of lookahead contamination if option quotes reflect trading through 16:15 ET.

### The Solution: Proposal A ($y_t \equiv \ln(S_{t+2}/S_{t+1})$)
- Features formed at session $t$ close predict the close-to-close return over session $t+2$:
  $$y_t \equiv \ln\left(\frac{S_{t+2}}{S_{t+1}}\right)$$
- The forecast window begins at 16:00 ET on date $t+1$ (24 hours after option snapshot $t$), completely immunizing the evaluation against 15-minute lookahead leakage.

```
Session t (EOD):    Features [Q_t, X_t, \pi_t] computed (options cutoff <= 16:15 ET)
Session t+1 (EOD):  Cash price S_{t+1} recorded (16:00 ET) -> Target window begins
Session t+2 (EOD):  Cash price S_{t+2} recorded (16:00 ET) -> Target y_t matures
```

---

<!-- slide -->
## 5. Feature Engineering: $Q_t$ and $X_t$

### Risk-Neutral Feature Vector ($Q_t \in \mathbb{R}^5$)
1. **Martin (2017) SVIX ($SVIX_{30}^2$):** Model-free simple variance index under $\mathbb{Q}$.
2. **Implied Skewness ($S_{30}^Q$):** Cubic OTM contract integration.
3. **Implied Kurtosis ($K_{30}^Q$):** Quartic OTM contract integration.
4. **Term Spread ($TS_t^Q$):** $SVIX_{90}^2 - SVIX_{30}^2$.
5. **90-Day SVIX ($SVIX_{90}^2$):** Quarterly horizon variance expectation.

### Historical State Feature Vector ($X_t \in \mathbb{R}^6$)
1. Realized volatility over 21 sessions ($\sigma_{\text{realized}, 21}$).
2. Parkinson (1980) extreme-value high-low volatility over 21 sessions ($\sigma_{\text{Parkinson}, 21}$).
3. Historical realized skewness over 63 sessions ($\text{Skew}_{63}$).
4. Historical realized kurtosis over 63 sessions ($\text{Kurt}_{63}$).
5. One-day return lag ($r_{t-1}$).
6. Five-day cumulative return ($r_{t-5 \to t}$).

---

<!-- slide -->
## 6. Latent Regimes & Causal Walk-Forward Engine

### $K=2$ Gaussian Hidden Markov Model
- **Emissions:** Annualized 21-day realized volatility ($\sigma_{21, t}$).
- **Regimes:** State 0 = Low Volatility / Calm; State 1 = High Volatility / Turbulent.
- **Strict Anti-Leakage Filtering:** Pure forward recursion ($\alpha$-pass). Zero backward smoothing, zero Viterbi path lookahead.
- **Diagnostics Verified:** Across all 24 walk-forward test refits, minimum occupancy was $19.8\%$ ($\ge 5\%$) and minimum dwell time was $17.6$ days ($\ge 5$ days).

### Expanding Walk-Forward Protocol
- Re-estimated every 21 sessions (24 blocks across 2022–2023).
- **Label Maturity Rule:** Supervised pairs strictly satisfy $t \le \tau_m - 2$ at refit origin $\tau_m$, ensuring zero unobserved future return labels enter estimation.

---

<!-- slide -->
## 7. Model Ladder & Density Architecture

### Primary Density Architecture: Location-Scale Student-$t$
$$y_t \sim t_\nu(\mu_t, \sigma_t), \quad \nu \ge 2.1, \quad \sigma_t \ge 10^{-4}$$
$$\mu_t = \beta_0 + \beta^\top Z_t, \quad \ln \sigma_t = \gamma_0 + \gamma^\top Z_t$$
Estimated via penalized MLE with $\ell_2$ ridge shrinkage ($\lambda = 0.01$).

### Hierarchical Model Ladder
- **$B0$ (Rolling Empirical):** Non-parametric rolling 252-day Student-$t$.
- **$B1$ (Historical Linear):** Inputs = Historical state $X_t \in \mathbb{R}^6$.
- **$B2$ (Implied Vol Linear):** Inputs = Martin SVIX $SVIX_{30}^2 \in \mathbb{R}^1$.
- **$B3$ (Full Option Linear):** Inputs = Full option vector $Q_t \in \mathbb{R}^5$.
- **$B4$ (Matched Non-Regime Baseline):** Inputs = $[Q_t, X_t] \in \mathbb{R}^{11}$ ($d=12$).
- **$R1$ (Regime Challenger):** Inputs = $[Q_t, X_t, \pi_t] \in \mathbb{R}^{13}$ ($d=14$).

---

<!-- slide -->
## 8. Research Integrity & Test Breach Disclosures

### Full Scientific Transparency
1. **Cash Close Retention (Commit `cee01a1`):**
   - 2022-01-03 and 2022-01-04 cash closes were downloaded during Stage 6 data exploration and committed to Git history.
   - The test partition is **never described as sealed or untouched**.
2. **Boundary Target Nulling:**
   - Partition boundary targets (2019-12-30/31, 2021-12-30/31) set strictly to `NaN` to prevent cross-partition leakage.
3. **Primary Test Exclusion ($N = 500$):**
   - Origin 2022-01-03 is strictly excluded from primary test scoring.
4. **Strict Isolation Trajectory ($N = 500$):**
   - Origin 2022-01-03 excluded from both scoring and all walk-forward refit training sets.

---

<!-- slide -->
## 9. Primary Test Results: Held-Out 2022–2023 Partition

### Out-of-Sample Evaluation Across 500 Scored Sessions

| Model | Input Feature Set | Parameters | Mean NLL (nats) | Differential $\bar{d}$ | DM Stat ($t$) | $p$-value (one-sided) | Bootstrap 95% CI |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **$B0$** | Rolling Empirical | 0 | $-2.9859$ | $-0.0999$ | $-2.854$ | $0.9978$ | $[-0.1703, -0.0337]$ |
| **$B1$** | Historical $X_t$ | 7 | $-3.0784$ | $-0.0074$ | $-1.114$ | $0.8671$ | $[-0.0205, +0.0055]$ |
| **$B2$** | Implied Vol $SVIX$ | 2 | $-3.0850$ | $-0.0008$ | $-0.264$ | $0.6041$ | $[-0.0069, +0.0052]$ |
| **$B3$** | Full Options $Q_t$ | 6 | $-3.0841$ | $-0.0017$ | $-0.468$ | $0.6800$ | $[-0.0089, +0.0054]$ |
| **$B4$** | Matched Baseline $[Q, X]$ | 12 | **$-3.0858$** | **$0.0000$** | **—** | **—** | **—** |
| **$R1$** | Challenger $[Q, X, \pi]$ | 14 | **$-3.0912$** | **$+0.0054$** | **$+1.452$** | **$0.0732$** | **$[-0.00198, +0.01384]$** |

### Hypothesis Test Verdict (H1)
- Mean differential: $\bar{d} = +0.005417$ nats/session ($+1.37$ nats annualized).
- Diebold–Mariano test: $p = 0.0732$ (fails 5% significance threshold).
- Bootstrap 95% CI spans zero $\implies$ **Statistically Inconclusive**.

---

<!-- slide -->
## 10. Secondary Metrics: CRPS & Density Calibration

### Continuous Ranked Probability Score (CRPS)
- Evaluated via exact closed-form Student-$t$ formula (Jordan et al., 2019):
  - **$B4$ CRPS:** $0.005391$
  - **$R1$ CRPS:** $0.005398$
  - **$\Delta \text{CRPS}$:** $-0.000007$ (**favoring baseline $B4$**).

### Empirical Interval Coverage & PIT Uniformity
- **50% Central Interval:** $B4 = 51.0\%$, $R1 = 51.4\%$ (nominal: $50\%$).
- **80% Central Interval:** $B4 = 80.0\%$, $R1 = 80.0\%$ (nominal: $80\%$).
- **95% Central Interval:** $B4 = 93.4\%$, $R1 = 93.6\%$ (nominal: $95\%$).
- **PIT Uniformity (Kolmogorov-Smirnov):**
  - $B4: p = 0.1706$, $R1: p = 0.2241$ (neither rejects uniformity at 5%).

---

<!-- slide -->
## 11. Sensitivity Analyses Across Trajectories

### Robustness Across Scoring Subsets

```
+--------------------------------------------------------------------------------------------------------------------------------+
| Evaluation Trajectory                                | N   | Mean Diff $\bar{d}$ | DM Stat ($t$) | $p_{\text{one-sided}}$ | Bootstrap 95% CI    |
+------------------------------------------------------+:---:|:-------------------:|:-------------:|:---------------------:|:-------------------:+
| Primary (Jan 3 Excluded from Scoring)                | 500 | +0.005417           | 1.4521        | 0.0732                | [-0.00198, +0.01384]|
| Strict Isolation (Jan 3 Excluded Scoring & Refits)   | 500 | +0.005506           | 1.5118        | 0.0653                | [-0.00207, +0.01387]|
| Full Test Partition (Including Breach Origin)        | 501 | +0.007257           | 1.8240        | 0.0341                | [-0.00051, +0.01538]|
| Actual-Quote Scoring (Excluding 5 Forward-Fills)     | 495 | +0.005426           | 1.4389        | 0.0751                | [-0.00210, +0.01334]|
+--------------------------------------------------------------------------------------------------------------------------------+
```

- **Invariant Scientific Conclusion:** In both pre-registered trajectories (primary and strict isolation), the confidence interval includes zero, confirming that $R1$'s numerical edge is not statistically significant.

---

<!-- slide -->
## 12. Discussion: Why Did Regimes Fail to Add Value?

### 1. Option Surfaces Already Impound Regime Information
- Forward-looking option moments (Martin SVIX, implied skewness, kurtosis, term spread) react instantaneously to changing market turbulence and tail risk.
- Conditioning on $Q_t$ already captures the underlying macro state, leaving little incremental signal for an explicit discrete regime variable ($\pi_t$).

### 2. Temporal Horizon Decay
- Under Proposal A timing, the return target spans session $t+2$. Discrete regime signals experience temporal decay across a 48-hour horizon.

### 3. Econometric Parsimony (Occam's Razor)
- Baseline $B4$ uses 12 parameters and zero latent state machinery.
- Challenger $R1$ requires 14 parameters plus rolling HMM transition estimation.
- Because $R1$ fails to achieve statistical significance and CRPS favors $B4$, **baseline $B4$ is the preferred model**.

---

<!-- slide -->
## 13. Limitations & Future Research

### Methodological Boundaries
1. **Single-Index Restriction:** Evaluated on S&P 500 index options. Results may differ for less liquid single stocks or emerging markets.
2. **Discrete Strike Quadrature:** Option moments computed via numerical integration across available strikes without parametric tail extrapolation.
3. **EOD Snapshot Data:** Proposal A cleanly solved the 15-minute lookahead, but tick-level order book data would permit simultaneous quote alignment.
4. **No Portfolio Claims:** The study strictly evaluates econometric density forecasting. No claims are made regarding trading profitability or live investment returns.

---

<!-- slide -->
## 14. Key Conclusions & Summary

1. **Rigorous Prequential Design:** 14 years of SPX option chains evaluated under strict causal walk-forward filtering and Proposal A timing.
2. **Statistically Inconclusive Primary Test:** Challenger $R1$ achieves a slight numerical gain ($\bar{d} = +0.0054$ nats, $p = 0.0732$), but its 95% bootstrap CI spans zero ($[-0.00198, +0.01384]$).
3. **CRPS Favors Parsimony:** Continuous ranked probability score favors baseline $B4$ ($0.005391$ vs $0.005398$).
4. **Scientific Takeaway:** Option-implied risk-neutral surfaces already impound persistent market states. Adding discrete latent regime components does not provide statistically significant incremental density forecasting power.

---
# Questions & Discussion
