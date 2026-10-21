# Stage 5 Modeling Specification: Regime-Conditioned Physical Return Density Forecasting

**Document Status:** Working Engineering Specification (Stage 5 Deliverable)  
**Date:** 21 October 2026  
**Author:** Antigravity (Advanced Agentic Coding Pair Programmer)  
**Authoritative Reference:** [research_protocol.md](file:///D:/IE612_Project/research_protocol.md) (Frozen Stage 1 Protocol)  
**Supporting Documents:** [implementation.md](file:///D:/IE612_Project/implementation.md), [data_feasibility_audit.md](file:///D:/IE612_Project/data_feasibility_audit.md), [stage4_feature_pipeline.md](file:///D:/IE612_Project/stage4_feature_pipeline.md)

---

## 1. Executive Summary & Document Role

### 1.1 Scope and Objective
This document formalizes the complete mathematical, algorithmic, and evaluation specification for Stage 5 of the IE 612 course project. The central research question investigates whether augmenting forward-looking option-implied risk-neutral moments ($Q_t \in \mathbb{R}^5$) and trailing historical market state ($X_t \in \mathbb{R}^6$) with causally filtered latent market regime probabilities ($\pi_t \in \Delta^{K-1}$) produces superior out-of-sample physical return density forecasts for the next trading day compared to a matched non-regime density model:

$$\text{Predictive Comparison: } \quad p(r_{t+1} \mid Q_t, X_t, \pi_t) \quad \text{versus} \quad p(r_{t+1} \mid Q_t, X_t)$$

### 1.2 Strict Stage 5 Operational Constraints
Stage 5 is **strictly a specification and protocol finalization stage**. In compliance with project governance and anti-leakage disciplines:
1. **No Model Training or Fitting:** No baseline, MDN, or HMM parameters are estimated or fitted during this stage.
2. **No Walk-Forward Execution:** No rolling out-of-sample predictions are generated.
3. **No Test Partition Processing:** The untouched 2022–2023 test data remains strictly uninspected, unparsed, and unaccessed.
4. **Preservation of Limitations:** The qualified status of Gate A, the discrete finite-grid nature of option-moment quadrature (without tail extrapolation), the unverified full 14-year calendar session continuity, the unverified early-sample strike depth (2010–2012), and the illustrative status of demonstration interest rates are preserved without alteration.

---

## 2. Target Variable, Information Cutoff & Temporal Alignment

### 2.1 Target Return Definition
* **Return Definition:** The forecast target is the physical close-to-close log return of the S&P 500 index over session $t+1$:
  $$r_{t+1} \equiv \ln\left(\frac{S_{t+1}}{S_t}\right)$$
  where $S_t$ is the official closing price level of the S&P 500 cash index on trading day $t$, recorded in **Index points**.
* **One-Day Non-Overlapping Horizon:** The primary forecast horizon is strictly one trading day. Consecutive forecast targets $r_{t+1}$ and $r_{t+2}$ are non-overlapping, eliminating moving-average forecast error structures.
* **Price Return vs. Total Return:** Options are traded directly on the price index ($S_t$, `^GSPC`), which defines the contract boundary, moneyness, and forward parity levels. Forecast target $r_{t+1}$ is computed on the price index to match contract mechanics.

### 2.2 Information Cutoff & Synchronization (Unresolved Cutoff & Gate B Prerequisite)
* **Forecast Origin ($t$):** Established at the end of the trading session on date $t$.
* **Information Set ($\mathcal{I}_t$):** Contains only data observable at or prior to the declared cutoff on date $t$:
  $$\mathcal{I}_t = \sigma\big(\{S_s, Q_s, X_s\}_{s=1}^t\big)$$
* **Unresolved Cutoff Status & 16:00 vs. 16:15 ET Lookahead Risk:**
  - Official S&P 500 cash equity trading ceases strictly at **16:00:00 ET** ($S_t$).
  - However, Cboe SPX index options historically traded until **16:15:00 ET** (15 minutes after equity market close). Although OptionsDX raw files report a `16:00` quote readtime string, whether these quotes reflect a 16:00:00 ET snapshot, a 16:15:00 ET closing settlement snapshot, or an unrecorded timestamp remains empirically unverified across product vintages.
  - If option quotes reflect price discovery through 16:15 ET while the cash index close $S_t$ was frozen at 16:00 ET, option-implied features $Q_t$ incorporate 15 minutes of post-close information, inducing lookahead leakage into the target return $r_{t+1} = \ln(S_{t+1}/S_t)$.
  - **Strict Gate Rule:** The forecast information cutoff is explicitly treated as **UNRESOLVED**. Any operational use of option features ($Q_t$) in predictive models is **strictly gated** until quote timing and cash synchronization are empirically verified in Gate B, or a defensible alternative cutoff (e.g., synchronizing via 16:15 ET index futures/level or advancing the forecast origin) is formally specified and approved.

### 2.3 Handling Missing Sessions and Feature Gaps
To prevent lookahead leakage and preserve causal evaluation integrity:
1. **Trading Calendar Alignment:** Cash index returns $r_{t+1}$ are computed across consecutive active exchange trading days. Weekends and NYSE holidays advance to the next active trading session.
2. **Isolated Option Data Gap ($\le 1$ Trading Day):** If the option chain at date $t$ is missing but the underlying cash index traded, option features are causally carried forward from the previous valid session ($Q_t \leftarrow Q_{t-1}$).
3. **Multi-Day Option Gap ($> 1$ Consecutive Trading Days):** If option chain data is unavailable for $>1$ consecutive session, forecast origin $t$ is omitted from out-of-sample loss aggregation and flagged with diagnostic code `ERR_CONSECUTIVE_OPTION_GAP`. Backward-filling or forward interpolation utilizing future data is strictly barred.
4. **Missing Underlying Close:** If $S_t$ or $S_{t+1}$ is missing, the session is excluded from scoring and flagged `ERR_MISSING_CASH_CLOSE`.

---

## 3. Feature Vectors & Preprocessing Discipline

### 3.1 Option-Implied Risk-Neutral Features ($Q_t \in \mathbb{R}^5$)
Standardized to a constant 30-day tenor via linear interpolation across the two nearest monthly/weekly expiries $\tau_1 < 30 < \tau_2$ ($20 \le \text{DTE} \le 50$):

| Feature Name | Symbol | Mathematical Formulation | Description / Theoretical Anchor |
|---|---|---|---|
| **Simple Variance Swap Index** | $\text{SVIX}_{30d}$ | $\text{SVIX}_{t,\tau}^2 = \frac{2 e^{r\tau}}{\tau F_{t,\tau}^2} \left[ \int_0^{F_{t,\tau}} P(K) dK + \int_{F_{t,\tau}}^\infty C(K) dK \right]$ | Martin (2017) simple return variance; lower bound on equity risk premium. |
| **Risk-Neutral Skewness** | $\text{QSkew}_{30d}$ | $S_t^Q(\tau) = \frac{e^{r\tau} W_t - 3\mu_t^Q e^{r\tau} V_t + 2(\mu_t^Q)^3}{\big(e^{r\tau} V_t - (\mu_t^Q)^2\big)^{3/2}}$ | Bakshi, Kapadia & Madan (2003) centered, standardized 3rd risk-neutral moment. |
| **Risk-Neutral Kurtosis** | $\text{QKurt}_{30d}$ | $K_t^Q(\tau) = \frac{e^{r\tau} X_t - 4\mu_t^Q e^{r\tau} W_t + 6(\mu_t^Q)^2 e^{r\tau} V_t - 3(\mu_t^Q)^4}{\big(e^{r\tau} V_t - (\mu_t^Q)^2\big)^2}$ | BKM (2003) centered, standardized non-excess 4th risk-neutral moment (Gaussian = 3.0). |
| **ATM Implied Volatility** | $\text{ATM\_IV}_{30d}$ | $\sigma_{\text{BS}}(K^*, \tau; F_{t,\tau}, M(K^*))$ | Inverted Black-Scholes volatility for strike $K^*$ closest to $F_{t,\tau}$. |
| **Term-Structure Slope** | $\text{TermSlope}_{60\_30}$ | $\text{ATM\_IV}_{60d} - \text{ATM\_IV}_{30d}$ | Slope of the implied volatility term structure between 60 and 30 calendar days. |

### 3.2 Historical Market State Features ($X_t \in \mathbb{R}^6$)
Constructed strictly from trailing daily cash index closes $\{S_{t-i}\}_{i=0}^{19}$:

| Feature Name | Symbol | Mathematical Formulation | Economic Rationale |
|---|---|---|---|
| **1-Day Return** | $r_{1d}$ | $\ln(S_t / S_{t-1})$ | Short-term momentum / price shock. |
| **5-Day Return** | $r_{5d}$ | $\sum_{i=0}^4 \ln(S_{t-i} / S_{t-i-1})$ | Weekly return momentum. |
| **5-Day Realized Volatility** | $\text{RV}_{5d}$ | $\sqrt{\frac{252}{5} \sum_{i=0}^4 r_{t-i}^2}$ | Short-term physical volatility spike. |
| **20-Day Realized Volatility** | $\text{RV}_{20d}$ | $\sqrt{\frac{252}{20} \sum_{i=0}^{19} r_{t-i}^2}$ | Monthly baseline physical volatility. |
| **20-Day Downside Semi-Vol** | $\text{DSemi}_{20d}$ | $\sqrt{\frac{252}{20} \sum_{i=0}^{19} \min(r_{t-i}, 0)^2}$ | Asymmetric downside volatility / tail risk. |
| **20-Day Maximum Drawdown** | $\text{DD}_{20d}$ | $\frac{S_t - \max_{0 \le i \le 19} S_{t-i}}{\max_{0 \le i \le 19} S_{t-i}}$ | Trailing stress / drawdown depth. |

### 3.3 Training-Only Preprocessing & Scaling Discipline
1. **Fit-Transform Separation:** All feature transformations (centering, scaling, winsorizing) are fit **strictly on the expanding in-sample training window** $\mathcal{T}_{\tau} = \{s \le \tau\}$.
2. **Scaler Parameters:** Feature scaling parameters (e.g., median and interquartile range for robust scaling: $z_{t,j} = (f_{t,j} - \text{med}_{\tau,j}) / \text{IQR}_{\tau,j}$) are frozen at each refit origin $\tau$ and applied causally to all out-of-sample dates $t \in (\tau, \tau + 21]$.
3. **No Lookahead in Imputation:** If any historical input feature is undefined (e.g., during the initial 20-day burn-in period of 2010), it is imputed using training-set medians. Test-period values never inform scalers.

---

## 4. Model Comparison Ladder ($B0$ to $B4$ and $R1$)

To rigorously evaluate whether latent market regimes add predictive density value, the project establishes a strict 6-model comparison ladder:

```
+-----------------------------------------------------------------------------------------+
|                                Model Comparison Ladder                                  |
+-----------------------------------------------------------------------------------------+
| [B0] Unconditional Gaussian Benchmark                                                   |
|      - Unconditioned expanding historical density N(mu_train, sigma_train^2)             |
+-----------------------------------------------------------------------------------------+
| [B1] Trailing Realized Volatility Benchmark                                             |
|      - Location-scale Student-t conditioned strictly on RV_20d                           |
+-----------------------------------------------------------------------------------------+
| [B2] Q-Only Distribution Model                                                          |
|      - Conditional density conditioned strictly on option-implied features Q_t           |
+-----------------------------------------------------------------------------------------+
| [B3] X-Only Distribution Model                                                          |
|      - Conditional density conditioned strictly on historical state features X_t         |
+-----------------------------------------------------------------------------------------+
| [B4] Combined Non-Regime Density Baseline (PRIMARY COMPARATOR)                          |
|      - Student-t location-scale / compact MDN conditioned on [Q_t, X_t] in R^11         |
+-----------------------------------------------------------------------------------------+
| [R1] Matched Latent Regime Density Challenger (PRIMARY HYPOTHESIS TEST)                 |
|      - Identical B4 architecture conditioned on [Q_t, X_t, \pi_t] in R^{11+K}            |
|      - \pi_t in Delta^{K-1} is forward-filtered causal regime probability vector         |
+-----------------------------------------------------------------------------------------+
```

### 4.1 Detailed Mathematical Formulations

#### 4.1.1 Model B0: Unconditional Gaussian Benchmark
A static historical benchmark representing the unconditional distribution of daily returns:
$$\widehat{p}_{t+1}^{(B0)}(r) = \frac{1}{\sqrt{2\pi \sigma_{\tau}^2}} \exp\left(-\frac{(r - \mu_{\tau})^2}{2\sigma_{\tau}^2}\right)$$
where $\mu_{\tau} = \frac{1}{|\mathcal{T}_{\tau}|} \sum_{s \in \mathcal{T}_{\tau}} r_s$ and $\sigma_{\tau}^2 = \frac{1}{|\mathcal{T}_{\tau}|-1} \sum_{s \in \mathcal{T}_{\tau}} (r_s - \mu_{\tau})^2$ are estimated over the expanding in-sample window.

#### 4.1.2 Model B1: Trailing Volatility Location-Scale Benchmark
A conditional distribution model where dispersion scales with trailing 20-day realized volatility:
$$\widehat{p}_{t+1}^{(B1)}(r) = \frac{1}{\sigma_t} f_\nu\left(\frac{r - \mu}{\sigma_t}\right)$$
$$\sigma_t = \alpha_0 + \alpha_1 \text{RV}_{20d,t}$$
where $f_\nu(z) = \frac{\Gamma((\nu+1)/2)}{\Gamma(\nu/2)\sqrt{\pi \nu}} (1 + z^2/\nu)^{-(\nu+1)/2}$ is the standard Student-$t$ density. Parameters $\boldsymbol{\theta}_{B1} = (\mu, \alpha_0, \alpha_1, \nu)$ are estimated via maximum likelihood on $\mathcal{T}_{\tau}$ with constraints $\alpha_0 > 0, \alpha_1 \ge 0, \nu > 2.1$.

#### 4.1.3 Model B2: Option-Implied ($Q$-Only) Density Model
Tests the predictive signal of forward-looking option moments in isolation:
* **Input:** $Q_t \in \mathbb{R}^5$.
* **Formulation:** Location-scale Student-$t$ regression:
  $$\mu_t = \mathbf{w}_\mu^\top Q_t + b_\mu, \quad \sigma_t = \text{softplus}(\mathbf{w}_\sigma^\top Q_t + b_\sigma) + \sigma_{\min}, \quad \nu = \text{softplus}(w_\nu) + 2.1$$
  with $\sigma_{\min} = 10^{-4}$ and $\text{softplus}(x) = \ln(1 + e^x)$.

#### 4.1.4 Model B3: Historical State ($X$-Only) Density Model
Tests the predictive signal of trailing physical momentum and volatility in isolation:
* **Input:** $X_t \in \mathbb{R}^6$.
* **Formulation:** Identical location-scale Student-$t$ structure as $B2$:
  $$\mu_t = \mathbf{w}_\mu^\top X_t + b_\mu, \quad \sigma_t = \text{softplus}(\mathbf{w}_\sigma^\top X_t + b_\sigma) + \sigma_{\min}, \quad \nu = \text{softplus}(w_\nu) + 2.1$$

#### 4.1.5 Model B4: Primary Non-Regime Density Comparator
The primary benchmark mapping combined option and historical features to the next-day physical return density:
* **Input Vector:** $\mathbf{u}_t = [Q_t, X_t] \in \mathbb{R}^{11}$.
* **Primary Architecture (Student-$t$ Location-Scale Regression):**
  $$\mu_t = \mathbf{w}_\mu^\top \mathbf{u}_t + b_\mu$$
  $$\sigma_t = \text{softplus}(\mathbf{w}_\sigma^\top \mathbf{u}_t + b_\sigma) + \sigma_{\min}$$
  $$\nu = \text{softplus}(w_\nu) + 2.1$$
* **Fallback Architecture (Compact 2-Component Mixture Density Network - MDN):**
  If validation data indicates multi-modality, a 2-component MDN ($M=2$) is evaluated:
  $$\widehat{p}_{t+1}^{(B4)}(r \mid \mathbf{u}_t) = \sum_{m=1}^M w_m(\mathbf{u}_t) \, \frac{1}{\sigma_m(\mathbf{u}_t)} f_{\nu_m}\left(\frac{r - \mu_m(\mathbf{u}_t)}{\sigma_m(\mathbf{u}_t)}\right)$$
  where mixing weights satisfy the simplex constraint via Softmax: $w_m(\mathbf{u}_t) = \frac{\exp(a_m(\mathbf{u}_t))}{\sum_{j=1}^M \exp(a_j(\mathbf{u}_t))}$.
* **Loss Function and Optimization:**
  Trained by minimizing regularized Negative Log-Likelihood (NLL) on $\mathcal{T}_{\tau}$:
  $$\mathcal{L}_{B4}(\boldsymbol{\theta}) = -\sum_{s \in \mathcal{T}_{\tau}} \ln \widehat{p}_{s+1}^{(B4)}(r_{s+1} \mid \mathbf{u}_s) + \lambda \|\boldsymbol{\theta}\|_2^2$$
  where $\lambda \ge 0$ is an $\ell_2$ penalty parameter tuned on validation data.

#### 4.1.6 Model R1: Matched Latent Regime Density Challenger
The primary experimental challenger testing the incremental value of latent market regimes:
* **Input Vector:** $\mathbf{v}_t = [Q_t, X_t, \pi_t] \in \mathbb{R}^{11 + K}$, where $\pi_t \in \Delta^{K-1}$ is the forward-filtered regime probability vector.
* **Architecture and Regularization Discipline:**
  * **Strict Matching:** $R1$ employs the **exact identical functional form**, hidden units, activation functions, and parameter constraints as $B4$.
  * **Identical Optimization Budget:** Uses the identical optimizer (Adam / L-BFGS), learning rate schedule, early stopping rules, and $\ell_2$ regularization grid ($\lambda \in \{10^{-4}, 10^{-3}, 10^{-2}\}$).
  * **Isolation of Treatment Effect:** The sole structural difference between $B4$ and $R1$ is the concatenation of $\pi_t$. Any out-of-sample performance wedge is strictly attributable to regime information.

---

## 5. Causal Hidden Markov Model (HMM) Specification

### 5.1 Latent State Formulation
* **Discrete State Space:** $z_t \in \{1, \dots, K\}$, where $K \in \{2, 3\}$.
* **Markov Transition Dynamics:** First-order homogeneous Markov chain with transition probability matrix $\mathbf{A} \in \mathbb{R}^{K \times K}$:
  $$A_{jk} \equiv P(z_t = k \mid z_{t-1} = j), \quad \sum_{k=1}^K A_{jk} = 1, \quad A_{jk} \ge 0$$
* **Initial State Distribution:** $\boldsymbol{\rho} \in \Delta^{K-1}$, $\rho_k = P(z_1 = k)$.

### 5.2 Emission Distribution
To prevent overfitting and preserve economic interpretability, the HMM emission variables are restricted to a low-dimensional bivariate vector $\mathbf{y}_t \in \mathbb{R}^2$:
$$\mathbf{y}_t = \begin{bmatrix} \widetilde{r}_t \\ \widetilde{\text{RV}}_{20d,t} \end{bmatrix} = \begin{bmatrix} (r_t - \bar{r}_\tau) / s_{r,\tau} \\ (\text{RV}_{20d,t} - \overline{\text{RV}}_\tau) / s_{\text{RV},\tau} \end{bmatrix}$$
Conditional on state $z_t = k$, emissions follow a bivariate Gaussian distribution:
$$\mathbf{y}_t \mid z_t = k \sim \mathcal{N}\big(\boldsymbol{\mu}_k, \boldsymbol{\Sigma}_k\big)$$
with diagonal covariance $\boldsymbol{\Sigma}_k = \text{diag}(\sigma_{k,1}^2, \sigma_{k,2}^2)$ to enforce parameter parsimony.

### 5.3 In-Sample Estimation (Baum-Welch EM)
All HMM parameters $\boldsymbol{\theta}_{\text{HMM}} = (\boldsymbol{\rho}, \mathbf{A}, \{\boldsymbol{\mu}_k, \boldsymbol{\Sigma}_k\}_{k=1}^K)$ are estimated **strictly on the expanding in-sample training window** $\mathcal{T}_{\tau}$ using the Baum-Welch (Expectation-Maximization) algorithm.

### 5.4 Causal Forward Filter Recursion ($\pi_t$)
At every out-of-sample date $t$, the regime state vector $\pi_t = [\pi_{t,1}, \dots, \pi_{t,K}]^\top$ is computed causally using the standard forward algorithm:

1. **Initialization (at $t=1$ of the expanding period):**
   $$\alpha_1(k) = \rho_k \, \mathcal{N}\big(\mathbf{y}_1; \boldsymbol{\mu}_k, \boldsymbol{\Sigma}_k\big)$$
2. **Forward Step (for $s = 2, \dots, t$):**
   $$\alpha_s(k) = \mathcal{N}\big(\mathbf{y}_s; \boldsymbol{\mu}_k, \boldsymbol{\Sigma}_k\big) \sum_{j=1}^K A_{jk} \, \alpha_{s-1}(j)$$
3. **Causal Filtered State Probability:**
   $$\pi_{t,k} \equiv P(z_t = k \mid \mathbf{y}_1, \dots, \mathbf{y}_t) = \frac{\alpha_t(k)}{\sum_{j=1}^K \alpha_t(j)}$$
4. **Numerical Underflow Prevention:** Normalization scale factor $c_s = \sum_{k=1}^K \alpha_s(k)$ is computed at each step, and scaled forward variables $\widehat{\alpha}_s(k) = \alpha_s(k) / c_s$ are propagated.

### 5.5 Strict Anti-Leakage Prohibitions
> [!CAUTION]
> The following estimators utilize future observations $s > t$ and are **strictly prohibited** from feature construction, baseline conditioning, or model evaluation:
> 1. **Smoothed Posteriors Barred:** $\gamma_{t,k} \equiv P(z_t = k \mid \mathbf{y}_1, \dots, \mathbf{y}_T)$ incorporates the backward pass from terminal date $T$. Using smoothed probabilities constitutes severe lookahead leakage.
> 2. **Full-Sample Viterbi Paths Barred:** $\mathbf{z}^* = \arg\max_{\mathbf{z}} P(\mathbf{z} \mid \mathbf{y}_{1:T})$ decodes the global optimal trajectory across the full sample. It is strictly barred.
> 3. **Frozen HMM Parameters Between Refits:** Between scheduled refit dates, HMM parameters $\boldsymbol{\theta}_{\text{HMM}}$ remain fixed; only the forward recursion advances.

### 5.6 Selection of Regime Count $K$ and Occupancy Constraints
The number of latent regimes $K \in \{2, 3\}$ is determined strictly on the **validation partition (2020–2021)**:
* **Occupancy Threshold:** Every latent regime $k \in \{1, \dots, K\}$ must maintain an empirical sample occupancy of at least $5.0\%$:
  $$\text{Occupancy}(k) = \frac{1}{|\mathcal{T}_{\text{val}}|} \sum_{t \in \mathcal{T}_{\text{val}}} \mathbb{I}\left(\arg\max_{j} \pi_{t,j} = k\right) \ge 0.05$$
* **Persistence / Dwell-Time Threshold:** Regimes must represent persistent market states rather than high-frequency noise. The expected dwell time $\mathbb{E}[D_k] = \frac{1}{1 - A_{kk}}$ must be $\ge 5$ trading sessions (1 calendar week) for all $k$.
* **Parsimony Tie-Breaker:** Default to $K=2$ (Low Volatility / High Volatility). $K=3$ is adopted if and only if all 3 states satisfy the occupancy and persistence criteria, and $K=3$ reduces validation NLL by $\Delta \text{NLL}_{\text{val}} \ge 0.020$ nats over $K=2$.

---

## 6. Walk-Forward Refit Cadence & Tuning Protocol

### 6.1 Chronological Partition Boundaries
The sample spans 14 calendar years (2010–2023, 168 monthly files) partitioned cleanly by calendar-year spans to respect annual macroeconomic regimes:

```
+-------------------------------------------------------------------+--------------------+--------------------+
|                Training Partition (~71.4% Span)                   | Validation (~14%)  | Untouched Test(~14%)|
|                   2010-01-01 to 2019-12-31                        | 2020-01-01:2021-12 | 2022-01-01:2023-12 |
|                   10 Full Calendar Years                          |  2 Calendar Years  |  2 Calendar Years  |
+-------------------------------------------------------------------+--------------------+--------------------+
  - Pipeline debugging & unit tests                                   - Tuning lambda, K   - SCORED ONCE
  - Initial parameter estimation                                      - MDN vs Student-t   - Sealed and frozen
```

### 6.2 Expanding-Window Walk-Forward Protocol
* **Refit Cadence:** Monthly, executed **every 21 active trading sessions**.
* **Supervised Training vs. HMM Information Sets at Refit Origin $\tau_m$:**
  > [!IMPORTANT]
  > At refit origin $\tau_m$ (close of trading day $\tau_m$), the next-day target return $r_{\tau_m + 1} = \ln(S_{\tau_m + 1} / S_{\tau_m})$ has **not yet occurred**. Including origin $\tau_m$ in supervised model training would leak unobserved future return $r_{\tau_m + 1}$. The training partitions must strictly distinguish supervised label availability from unsupervised emission availability:
  > 1. **Supervised Model Training Set ($\mathcal{T}_{\text{sup},\tau_m}$):** Restricted strictly to origins whose target label $r_{t+1}$ has already been fully observed by session close $\tau_m$:
  >    $$\mathcal{T}_{\text{sup},\tau_m} \equiv \{t : 1 \le t \le \tau_m - 1\}$$
  >    For every origin $t \in \mathcal{T}_{\text{sup},\tau_m}$, the realized return $r_{t+1}$ was observed on or before session close $\tau_m$ (since $t \le \tau_m - 1 \implies t+1 \le \tau_m$).
  > 2. **HMM Estimation & Feature Scaler Set ($\mathcal{T}_{\text{HMM},\tau_m}$):**
  >    $$\mathcal{T}_{\text{HMM},\tau_m} \equiv \{t : 1 \le t \le \tau_m\}$$
  >    Because emission vector $\mathbf{y}_t = [\widetilde{r}_t, \widetilde{\text{RV}}_{20d,t}]^\top$ and feature inputs $[Q_t, X_t]$ are contemporaneous to date $t$, the realization at $t = \tau_m$ is fully observed at session close $\tau_m$ (since $r_{\tau_m} = \ln(S_{\tau_m} / S_{\tau_m - 1})$ is already realized).
* **Execution Sequence at Refit Date $\tau_m$:**
  1. Fit feature scaling statistics (medians, IQRs) strictly on $\mathcal{T}_{\text{HMM},\tau_m} = \{t \le \tau_m\}$.
  2. Estimate HMM transition and emission parameters $\boldsymbol{\theta}_{\text{HMM}}$ strictly on $\mathcal{T}_{\text{HMM},\tau_m} = \{t \le \tau_m\}$.
  3. Fit predictive density models $B0, B1, B2, B3, B4,$ and $R1$ **strictly on supervised pairs $\{(\mathbf{z}_t, r_{t+1})\}_{t=1}^{\tau_m - 1}$** ($\mathcal{T}_{\text{sup},\tau_m}$), with features scaled by statistics frozen at $\tau_m$.
  4. **Out-of-Sample Forecasting for Block $t \in [\tau_m, \tau_m + 20]$ (21 Trading Days):**
     - For origin $t = \tau_m$: scale features $[Q_{\tau_m}, X_{\tau_m}]$, compute causal forward-filtered probability $\pi_{\tau_m}$, and generate one-step predictive density $\widehat{p}_{\tau_m + 1}(r)$. Observe realized return $r_{\tau_m + 1}$ after session $\tau_m + 1$ close and record out-of-sample log-likelihood.
     - Advance sequentially to $t = \tau_m + 1, \dots, \tau_m + 20$: compute causal forward filter $\pi_t$ using frozen HMM parameters $\boldsymbol{\theta}_{\text{HMM}}$, scale features using frozen scalers from $\tau_m$, generate 1-day forecast $\widehat{p}_{t+1}(r)$ using frozen predictive models, observe $r_{t+1}$ after session $t+1$ close, and record log-likelihood.
     - At $t = \tau_m + 21$, advance to the next refit origin $\tau_{m+1}$ and repeat the sequence.

---

## 7. Statistical Evaluation, Inference & Multiple Testing Protocol

### 7.1 Primary Metric: Out-of-Sample Negative Log-Likelihood (NLL)
Evaluated on the untouched test partition $\mathcal{T}_{\text{test}}$ (2022–2023):
$$\mathcal{L}(M) = -\frac{1}{N_{\text{test}}} \sum_{t \in \mathcal{T}_{\text{test}}} \ln \widehat{p}_{t+1}^{(M)}(r_{t+1})$$

### 7.2 Paired Loss Differential and Diebold-Mariano Test
For each out-of-sample date $t$, the paired differential is:
$$d_t = \ln \widehat{p}_{t+1}^{(R1)}(r_{t+1}) - \ln \widehat{p}_{t+1}^{(B4)}(r_{t+1}) = \ell_{t+1}^{(B4)} - \ell_{t+1}^{(R1)}$$
where $\ell_t = -\ln \widehat{p}_t(r_t)$. A positive mean differential ($\bar{d} = \frac{1}{N_{\text{test}}}\sum_{t=1}^{N_{\text{test}}} d_t > 0$) indicates $R1$ assigns higher likelihood (lower log loss) to realized returns.

* **Diebold-Mariano Test Statistic:**
  $$\text{DM} = \frac{\bar{d}}{\sqrt{\widehat{\text{LRV}}(\bar{d}) / N_{\text{test}}}} \xrightarrow{d} \mathcal{N}(0, 1) \quad \text{under } H_0: \mathbb{E}[d_t] \le 0$$
* **Newey-West HAC Variance Estimation:**
  Long-Run Variance $\widehat{\text{LRV}}(\bar{d})$ is estimated using the Newey-West (1987) estimator with Bartlett kernel:
  $$\widehat{\text{LRV}}(\bar{d}) = \widehat{\gamma}_0 + 2 \sum_{j=1}^L \left(1 - \frac{j}{L+1}\right) \widehat{\gamma}_j, \quad \widehat{\gamma}_j = \frac{1}{N_{\text{test}}} \sum_{t=j+1}^{N_{\text{test}}} (d_t - \bar{d})(d_{t-j} - \bar{d})$$
  with automatic bandwidth selection $L = \lfloor 4 (N_{\text{test}} / 100)^{2/9} \rfloor$ (Newey & West, 1994).

### 7.3 Stationary Block Bootstrap Confidence Intervals
To account for potential conditional heteroskedasticity and non-Gaussian dependence in daily loss differentials:
1. **Resampling Unit:** Paired loss differential series $\{d_t\}_{t=1}^{N_{\text{test}}}$.
2. **Resampling Mechanism:** Politis and Romano (1994) stationary bootstrap with pseudo-series generated by blocks of random length drawn from a geometric distribution with mean block length $b = \mathbb{E}[B]$.
3. **Automatic Block Length Selection:** $b$ is selected via the data-dependent algorithm of Politis and White (2004) with correction by Patton, Politis, and White (2009).
4. **Replications and Output:** $B_{\text{boot}} = 2,000$ bootstrap replications. Report $95\%$ studentized and percentile confidence intervals for $\bar{d}$.

### 7.4 Secondary Forecast Diagnostics
1. **Continuous Ranked Probability Score (CRPS):**
   $$\text{CRPS}(\widehat{F}_{t+1}, r_{t+1}) = \int_{-\infty}^\infty \Big(\widehat{F}_{t+1}(u) - \mathbb{I}(r_{t+1} \le u)\Big)^2 du$$
2. **Probability Integral Transform (PIT) Calibration:**
   $$u_t = \widehat{F}_{t+1}(r_{t+1}) = \int_{-\infty}^{r_{t+1}} \widehat{p}_{t+1}(s) \, ds$$
   Evaluated via 10-bin histogram uniformity, Kolmogorov-Smirnov test, and Berkowitz (2001) likelihood ratio test of normality on $z_t = \Phi^{-1}(u_t)$.
3. **Central Interval Coverage & Sharpness:** Empirical coverage rates and average interval widths for $50\%, 80\%$, and $95\%$ central prediction intervals.
4. **Tail Quantile Pinball Loss:** Evaluated at left-tail ($\alpha \in \{0.01, 0.05, 0.10\}$) and right-tail ($\alpha \in \{0.90, 0.95, 0.99\}$) crash boundaries.

### 7.5 Multiple Testing Control and Significance Criteria
* **False Discovery Rate (FDR):** To guard against false positive discoveries across multiple secondary metrics (CRPS, PIT, interval coverage, quantiles), the Benjamini-Hochberg (1995) FDR procedure is applied at nominal rate $q = 0.05$.
* **Statistical vs. Practical Significance:**
  * *Statistical Significance:* Achieved if one-sided Diebold-Mariano $p < 0.05$ and $95\%$ stationary block bootstrap CI strictly excludes zero.
  * *Practical Significance:* Requires an average log predictive density improvement $\bar{d} \ge 0.010$ nats per day (~2.5 nats per year). An outcome with $p < 0.05$ but $\bar{d} < 0.010$ is reported as statistically detectable but economically negligible.

---

## 8. Open Operational Decisions & Recommended Defaults

The following operational choices are explicitly documented as **OPEN DECISIONS** requiring empirical validation or administrative confirmation:

| Decision ID | Description | Governing Constraint | Recommended Default | Approval Status |
|---|---|---|---|---|
| **OD-1** | **Risk-Free Rate Ingestion** | Dynamic daily curve vs. fixed benchmark | Ingest continuous daily 13-week T-Bill (`^IRX`) via $r = -\frac{365}{91} \ln(1 - d \frac{91}{360})$ or FRED 3M CMT matching date $t$. | **Conversion Formula Implemented in Gate B Interim Datasets**; multi-tenor curve matching remains open. |
| **OD-2** | **Density Architecture** | Student-$t$ Location-Scale vs. 2-component MDN | Default to single-component Student-$t$ location-scale. MDN retained only if validation NLL improves with zero mode collapse. | **Provisional Default Fixed** (Student-$t$ location-scale prioritized for numerical robustness). |
| **OD-3** | **Regime Count ($K$)** | $K=2$ vs. $K=3$ | Default to $K=2$ (Calm/Stress) unless $K=3$ passes $>5\%$ occupancy on validation and lowers NLL by $>0.02$. | **Provisional Default Fixed** ($K=2$ default). |
| **OD-4** | **Consecutive Missing Data Rule** | Drop date vs. causal carry-forward | Forward-fill $Q_t = Q_{t-1}$ for $\le 1$ day; drop date from scoring for $>1$ day gap. | **Empirically Audited in Gate B** (Reduces validation missingness from 1.78% to 0.00%; leaves 7.27% missingness in development due to 2010–2011 monthly gaps). |
| **OD-5** | **Portfolio Translation Inclusion** | Inclusion of cash/index volatility-targeted backtest | Strictly optional secondary deliverable. Cannot rescue a failed density hypothesis. | **Provisional Default Fixed** (Confirmed as secondary/optional). |
| **OD-6** | **Information Cutoff & Quote Synchronization** | 16:00 vs. 16:15 ET lookahead risk; cash close $S_t$ frozen at 16:00 while options traded until 16:15 ET. | **Unresolved Cutoff Gate:** Gate all option feature use in predictive models until synchronization is confirmed or a defensible cutoff is specified. | **Open & Strictly Gated** (Vendor string `'16:00'` audited in Gate B, but does not prove synchronization with 16:00 ET cash close). |

---

## 9. Pre-Fitting Prerequisites & Stop/Go Decision Gates

Before any model training, HMM estimation, or full-sample evaluation may begin, the project must satisfy four sequential gates:

```
+-----------------------------------------------------------------------------------------+
|                                Stage-by-Stage Decision Gates                            |
+-----------------------------------------------------------------------------------------+
  [Gate A: Local Data Feasibility & Quality Gate] -> STATUS: QUALIFIED PASS (Stage 3/4)
  - Verified 168 monthly bundles (2010–2023, 5.28 GB).
  - Verified schema, 16:00 timestamp, forward parity, and Martin SVIX on 2 pilot dates.
  - Demonstrated QSkew, QKurt, ATM IV, and X_t algorithms on the 2 pilot dates.
                        |
                        v
  [Gate B: Calendar Audit & Feature Construction Gate] -> STATUS: BLOCKED / QUALIFIED
  - Audited 2010–2021 session continuity & reconciliation: 3,021 expected - 30 missing + 3 unexpected
    stale closure records = 2,994 observed. Aggregate missing rate 0.993% <= 1.0%, but annual missingness
    exceeds 1.0% in 5 calendar years (2011, 2014, 2019, 2020, 2021). Not a clean annual pass.
  - Audited early strike breadth (2010–2012): identified monthly-only expiry deficit in 2010–2011
    (~70% missing 30d bracketing) and weekly option regime shift in mid-2012.
  - Quote timestamps audited: uniform '16:00' vendor string, zero '13:00' early close stamps.
  - Converted T-bill discount yield to continuous rate: r = -(365/91)*ln(1-d*91/360). Causal carryforward
    on Columbus Day 2010 and Veterans Day 2016 explicitly logged (zero silent imputation).
  - Candidate feature datasets generated: Development (2,516 rows, 2,233 all-5 valid [88.75%],
    283 missing [11.25%], SHA-256: 138fa68a...) and Validation (505 rows, 496 all-5 valid [98.22%],
    9 missing [1.78%], SHA-256: 8bedc8b4...). NOT permanently frozen.
  - TEST BOUNDARY DISCLOSURE: ^GSPC closes for 2022-01-03 and 2022-01-04 accessed during download
    and committed in commit cee01a1 along with the 2021-12-31 target return (retained in Git history).
    The test partition cannot be claimed as intact or sealed. Terminal boundary labels on 2019-12-31
    and 2021-12-31 are set strictly to NaN to guarantee partition purity. Raw option bundles remain unopened.
  - BLOCKERS: 14-year calendar audit incomplete; 16:00 vs 16:15 ET cutoff remains unverified.
    Model training remains strictly gated. Cannot claim Gate B passed.
                        |
                        v
  [Gate C: Baseline & Density Stability Gate] -> MODELING PREREQUISITE
  - Fit models B0–B4 on supervised development pairs {t <= tau - 1} (2010–2019).
  - Verify density validity on validation split (2020–2021): all densities integrate to 1.0,
    scales sigma_t > 10^-4, degrees of freedom nu_t >= 2.1, zero NaN/Inf losses.
  - Verify HMM regime persistence on emissions {t <= tau}: dwell time >= 5 days, occupancy >= 5%.
                        |
                        v
  [Gate D: Final Test Evaluation & Integrity Gate] -> EVALUATION PREREQUISITE
  - Score frozen B4 and R1 models on the untouched 2022–2023 test partition EXACTLY ONCE.
  - Execute paired Diebold-Mariano test and stationary block bootstrap.
  - Report findings transparently, regardless of whether H1 is supported or refuted.
+-----------------------------------------------------------------------------------------+
```
  - Fit models B0–B4 on supervised development pairs {t <= tau - 1} (2010–2019).
  - Verify density validity on validation split (2020–2021): all densities integrate to 1.0,
    scales sigma_t > 10^-4, degrees of freedom nu_t >= 2.1, zero NaN/Inf losses.
  - Verify HMM regime persistence on emissions {t <= tau}: dwell time >= 5 days, occupancy >= 5%.
                        |
                        v
  [Gate D: Final Test Evaluation & Integrity Gate] -> EVALUATION PREREQUISITE
  - Score frozen B4 and R1 models on the untouched 2022–2023 test partition EXACTLY ONCE.
  - Execute paired Diebold-Mariano test and stationary block bootstrap.
  - Report findings transparently, regardless of whether H1 is supported or refuted.
+-----------------------------------------------------------------------------------------+
```

---

*End of Stage 5 Modeling Specification. This document serves as the governing architecture for all model implementation in subsequent stages.*