# Empirical Evaluation of Latent Market Regimes in Physical Return Density Forecasting

**Course:** IE 612 (Introduction to Financial Engineering), 1-Month Empirical Project  
**Author:** Antigravity (Advanced Agentic Coding Pair Programmer)  
**Date:** 24 October 2026  
**Document Status:** Complete Final Research Package (Stages 1–9)  
**Governing Documents:**
- [`research_protocol.md`](file:///D:/IE612_Project/research_protocol.md) (Frozen Research Protocol)
- [`implementation.md`](file:///D:/IE612_Project/implementation.md) (Implementation Plan & Audit Log)
- [`gate_b_audit_report.md`](file:///D:/IE612_Project/gate_b_audit_report.md) (Gate B Calendar, Breadth & Feature Audit)
- [`gate_c_model_validation_report.md`](file:///D:/IE612_Project/gate_c_model_validation_report.md) (Gate C Modeling & Validation Report)
- [`gate_d_final_test_report.md`](file:///D:/IE612_Project/gate_d_final_test_report.md) (Gate D Final Held-Out Evaluation Report)
- [`final_research_report.md`](file:///D:/IE612_Project/final_research_report.md) (Submission-Ready Research Report)
- [`final_presentation.md`](file:///D:/IE612_Project/final_presentation.md) (Course Presentation Slide Deck)
- [`reproducibility_guide.md`](file:///D:/IE612_Project/reproducibility_guide.md) (Replication & Verification Guide)

---

## 1. Executive Summary & Research Question

This study investigates whether persistent, causally filtered market-state information improves the mapping of cross-sectional option-implied risk-neutral moments into the physical probability distribution of future index returns.

### Formal Hypothesis Test
At trading date $t$, given option-implied risk-neutral features $Q_t \in \mathbb{R}^5$ (Martin SVIX, 30-day skewness, kurtosis, term spread, and 90-day SVIX) and observable historical market state $X_t \in \mathbb{R}^6$ (realized volatility, Parkinson volatility, historical skewness, kurtosis, and return lags), does augmenting the feature space with a causally filtered posterior regime vector $\pi_t \in \Delta^{K-1}$ from an in-sample Hidden Markov Model (HMM) improve out-of-sample physical density forecasts over a matched non-regime comparator receiving identical inputs?

$$\text{Forecast Comparison: } \quad p(y_t \mid Q_t, X_t, \pi_t) \quad [R1] \quad \text{versus} \quad p(y_t \mid Q_t, X_t) \quad [B4]$$

### Primary Empirical Outcome
- **Test Metric:** Out-of-sample Negative Log-Likelihood (NLL / log predictive loss).
- **Mean Differential:** $\bar{d} = \text{NLL}(B4) - \text{NLL}(R1) = +0.005417$ nats/session ($N = 500$ primary sessions).
- **Inference:** Diebold–Mariano $t = 1.4521$, $p_{\text{one-sided}} = 0.0732$, $p_{\text{two-sided}} = 0.1465$.
- **Stationary Block Bootstrap 95% CI:** $[-0.001979, +0.013837]$ nats/session.
- **Scientific Determination:** The primary hypothesis test is **statistically inconclusive** ($p \ge 0.05$; bootstrap 95% confidence interval spans zero, although extending above the $+0.010$ practical significance threshold). In accordance with pre-registered econometric decision rules, the simpler non-regime baseline $B4$ is favored on grounds of parsimony.
- **Economic / Portfolio Claims:** Zero portfolio, trading, or investment-performance claims are made.

---

## 2. Core Methodological Disciplines

1. **Information Cutoff Discipline (Proposal A Timing):**
   Cboe SPX options historically closed at 16:15 ET, while the underlying cash index equity closed at 16:00 ET. To completely prevent lookahead contamination across this 15-minute gap, Proposal A was adopted: features computed at session close $t$ forecast the close-to-close return over session $t+2$:
   $$y_t \equiv \ln\left(\frac{S_{t+2}}{S_{t+1}}\right)$$
2. **Strict Chronological Expanding Walk-Forward:**
   Models are refit on a fixed 21-session expanding cadence (24 refit blocks across the 2-year test partition). At refit origin $\tau_m$, supervised training labels are strictly constrained to $t \le \tau_m - 2$ to guarantee that no unobserved future return enters model fitting.
3. **Causal Forward Filtering:**
   Regime state probabilities $\pi_t$ are generated via pure forward filtering ($\alpha$-pass). Viterbi path decoding, backward smoothing, and full-sample Baum-Welch passes are strictly prohibited in out-of-sample periods.
4. **Transparent Test Partition Disclosures:**
   - Cash index closes for 2022-01-03 and 2022-01-04 and the derived 2021-12-31 validation return were retrieved during Stage 6 data exploration and committed in Git commit `cee01a1`. The test partition is never described as untouched or sealed.
   - The primary test score excludes the 2022-01-03 origin ($N=500$ sessions scored out of 501). A strictly isolated sensitivity trajectory ($N=500$) that removes 2022-01-03 from both scoring and supervised refits yields identical scientific conclusions ($\bar{d} = +0.005506, p = 0.0653$).
   - Cash closes retrieved through 2024-01-09 were truncated to 2024-01-03 to observe the 2023-12-29 test target without incorporating subsequent 2024 market movements.
5. **OptionsDX Data Licensing Compliance:**
   Raw OptionsDX CSV bundles in `Data/` are excluded from Git tracking via `.gitignore` to adhere strictly to non-redistribution terms. All feature generation, model weights, date-level predictions, and evaluation scripts are fully reproducible from local files.

---

## 3. Four-Gate Governance Progression

```
+--------------------------------------------------------------------------------------------------------------------------+
|                                              Project Governance Gate Summary                                             |
+--------------------------------------------------------------------------------------------------------------------------+
| Gate   | Name                                | Scope / Focus                           | Status                          |
+--------+-------------------------------------+-----------------------------------------+---------------------------------+
| Gate A | Local Data Feasibility Gate         | OptionsDX 2010–2023 file inventory;     | QUALIFIED PASS                  |
|        |                                     | pilot parser & forward parity check     |                                 |
+--------+-------------------------------------+-----------------------------------------+---------------------------------+
| Gate B | Calendar Continuity & Feature Gate  | 2010–2021 continuity audit; early strike| QUALIFIED PASS                  |
|        |                                     | breadth check; Proposal A timing adopted| (User Decisions UD-1 to UD-5)   |
+--------+-------------------------------------+-----------------------------------------+---------------------------------+
| Gate C | Baseline & Density Stability Gate   | B0–B4 & R1 walk-forward validation on   | QUALIFIED PASS WITH CAVEATS     |
|        |                                     | 2020–2021; analytical CRPS verification;| (Density stability established; |
|        |                                     | per-refit HMM dwell/occupancy checks    | R1 gain inconclusive)           |
+--------+-------------------------------------+-----------------------------------------+---------------------------------+
| Gate D | Final Held-Out Evaluation Gate      | 2022–2023 test audit & 24 walk-forward  | COMPLETED                       |
|        |                                     | refit blocks; dual prequential /        | (Evaluation complete;           |
|        |                                     | strict-isolation evaluations            | primary test inconclusive)      |
+--------------------------------------------------------------------------------------------------------------------------+
```

---

## 4. Key Quantitative Results

### Out-of-Sample Test Evaluation (2022–2023 Held-Out Partition)

| Model | Architecture & Feature Inputs | Parameters ($d$) | NLL (nats) | $\bar{d} = \text{NLL}_{B4} - \text{NLL}_M$ | DM Stat ($t$) | $p_{\text{one-sided}}$ | Bootstrap 95% CI | CRPS | PIT KS $p$ |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **$B0$** | Rolling Empirical Student-$t$ ($y_t$) | 0 (rolling) | $-2.9859$ | $-0.0999$ | $-2.854$ | $0.9978$ | $[-0.1703, -0.0337]$ | $0.005697$ | $0.2038$ |
| **$B1$** | Linear Student-$t$ on Historical $X_t$ | 7 | $-3.0784$ | $-0.0074$ | $-1.114$ | $0.8671$ | $[-0.0205, +0.0055]$ | $0.005409$ | $0.2198$ |
| **$B2$** | Linear Student-$t$ on Implied Vol $Q_{\text{SVIX}}$ | 2 | $-3.0850$ | $-0.0008$ | $-0.264$ | $0.6041$ | $[-0.0069, +0.0052]$ | $0.005391$ | $0.1802$ |
| **$B3$** | Linear Student-$t$ on Full Options $Q_t$ | 6 | $-3.0841$ | $-0.0017$ | $-0.468$ | $0.6800$ | $[-0.0089, +0.0054]$ | $0.005393$ | $0.1691$ |
| **$B4$** | Matched Baseline: Student-$t$ on $[Q_t, X_t]$ | 12 | **$-3.0858$** | **$0.0000$** | **—** | **—** | **—** | **$0.005391$** | $0.1706$ |
| **$R1$** | Challenger: Student-$t$ on $[Q_t, X_t, \pi_t]$ | 14 | **$-3.0912$** | **$+0.0054$** | **$+1.452$** | **$0.0732$** | **$[-0.00198, +0.01384]$** | **$0.005398$** | $0.2241$ |

### Sensitivity & Subgroup Trajectories

| Evaluation Trajectory | Sample Size ($N$) | Mean Differential $\bar{d}$ | DM Stat ($t$) | $p_{\text{one-sided}}$ | $p_{\text{two-sided}}$ | Stationary Bootstrap 95% CI |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Primary (Jan 3 Origin Excluded)** | 500 | $+0.005417$ | $1.4521$ | $0.0732$ | $0.1465$ | $[-0.001979, +0.013837]$ |
| **Strict Isolation (Jan 3 Excluded Scoring & Refits)** | 500 | $+0.005506$ | $1.5118$ | $0.0653$ | $0.1306$ | $[-0.002074, +0.013873]$ |
| **Full Compromised Test Partition** | 501 | $+0.007257$ | $1.8240$ | $0.0341$ | $0.0682$ | $[-0.000509, +0.015382]$ |
| **Actual-Quote Scoring Subset (No Forward-Fills)** | 495 | $+0.005426$ | $1.4389$ | $0.0751$ | $0.1502$ | $[-0.002097, +0.013343]$ |

---

## 5. Repository Directory Layout

```text
IE612_Project/
├── README.md                                 # Top-level repository overview and execution manifest
├── implementation.md                         # Detailed project specification, protocol log & gate records
├── research_protocol.md                      # Frozen pre-registered research protocol
├── stage5_modeling_specification.md          # Formal model definitions, ladder, tuning & walk-forward design
├── gate_b_audit_report.md                    # Gate B audit report (calendar continuity & feature extraction)
├── gate_c_model_validation_report.md         # Gate C model validation report (2020–2021 validation outcomes)
├── gate_d_final_test_report.md               # Gate D final evaluation report (2022–2023 test outcomes)
├── final_research_report.md                  # Comprehensive academic research report
├── final_presentation.md                     # Markdown course slide presentation
├── reproducibility_guide.md                  # Step-by-step reproduction instructions and command guide
├── src/
│   ├── data/
│   │   ├── audit_calendar.py                 # Exchange session calendar & missing session audit
│   │   ├── check_optionsdx_sample.py         # Schema parser, timestamp verification & forward parity
│   │   └── build_dataset.py                  # End-to-end dataset builder
│   ├── features/
│   │   ├── svix.py                           # Martin (2017) SVIX integration engine
│   │   ├── moments.py                        # Risk-neutral skewness and kurtosis computation
│   │   └── physical_features.py              # Realized volatility, Parkinson, and return lag calculation
│   └── models/
│       ├── hmm_filter.py                     # Causal forward-filtered HMM implementation
│       ├── density_models.py                 # Student-t location-scale regression architecture
│       ├── walk_forward_pipeline.py          # Expanding walk-forward engine with 21-session refits
│       └── evaluation_metrics.py             # Analytical Student-t CRPS, NLL, DM test, and bootstrap
├── scratch/
│   ├── batch_feature_pipeline.py             # Feature pipeline for Stage 6 candidate generation
│   ├── run_stage7_experiments.py             # Stage 7 Development and Validation execution
│   ├── audit_2022_2023_test_data.py          # Stage 8 raw data coverage and contract schema audit
│   └── run_stage8_test_evaluation.py         # Stage 8 Gate D walk-forward test evaluation
└── output/
    ├── stage6_features/                      # Candidate feature datasets (Development & Validation)
    │   ├── spx_features_development_2010_2019.csv  (SHA-256: 138fa68a...)
    │   ├── spx_features_validation_2020_2021.csv   (SHA-256: 8bedc8b4...)
    │   ├── spx_daily_closes_2009_2021.csv          (SHA-256: 4f300dd5...)
    │   └── feature_datasets_metadata.json
    ├── stage7_models/                        # Stage 7 validation outputs, predictions & refit diagnostics
    │   ├── validation_predictions_primary.csv
    │   ├── validation_metrics_summary.json
    │   └── hmm_refit_diagnostics_primary.json
    └── stage8_test/                          # Stage 8 test outputs, predictions, diagnostics & metadata
        ├── raw_data_audit_2022_2023.json           (SHA-256: f165b3d9...)
        ├── test_dataset_metadata.json              (SHA-256: 7977b436...)
        ├── spx_features_test_2022_2023.csv         (SHA-256: 8a4bf13a...)
        ├── spx_daily_closes_2009_2024.csv          (SHA-256: 32edf5d4...)
        ├── test_predictions.csv                    (SHA-256: 3097ce28...)
        ├── test_predictions_strict_isolation.csv   (SHA-256: 3c98fd16...)
        ├── test_metrics_summary.json               (SHA-256: ce29feb5...)
        ├── hmm_refit_diagnostics_test.json         (SHA-256: ec6f4e48...)
        └── density_integration_checks.json         (SHA-256: 07f39d70...)
```

---

## 6. Reproducibility & Execution Instructions

To inspect and reproduce the completed pipeline from saved features and scripts:

### Prerequisites
- Python 3.10+ with standard scientific libraries: `numpy`, `scipy`, `pandas`, `yfinance`.
- Git.

### Step 1: Feature Extraction Verification (Stage 6)
```powershell
python scratch/batch_feature_pipeline.py
```
*Note: The candidate feature CSVs (`output/stage6_features/`) are pre-generated. Re-running is not required unless validating raw data extraction.*

### Step 2: Model Validation & Sensitivity Analysis (Stage 7)
```powershell
python scratch/run_stage7_experiments.py
```
*Fits models B0–B4 and R1 across 2010–2019 Development pairs, executes 21-session walk-forward validation across 2020–2021, recomputes analytical CRPS, and exports validation metrics to `output/stage7_models/`.*

### Step 3: Raw Data Audit for Test Partition (Stage 8)
```powershell
python scratch/audit_2022_2023_test_data.py
```
*Scans 24 raw OptionsDX monthly bundles, verifies 4,100,693 contract records, confirms 100% schema match, audits 16:00 ET timestamps, and checks exchange trading session alignment.*

### Step 4: Final Test Evaluation & Statistical Inference (Stage 8)
```powershell
python scratch/run_stage8_test_evaluation.py
```
*Executes the frozen walk-forward refit pipeline on held-out 2022–2023 test data across 24 expanding blocks, computes both primary and strict-isolation trajectories, runs Diebold–Mariano paired tests and block bootstrap, and archives results to `output/stage8_test/`.*

### Step 5: Independent Verification of Checksums
```powershell
Get-FileHash output/stage8_test/test_predictions.csv -Algorithm SHA256
Get-FileHash output/stage8_test/test_metrics_summary.json -Algorithm SHA256
```

---

## 7. Research Boundaries & Course Disclosures

1. **Course Context:** This study was conducted for **IE 612 (Introduction to Financial Engineering)** at IIT Bombay.
2. **Administrative Requirements Status:** Formal course submission guidelines (such as page limits, required slide format, or whether an illustrative portfolio backtest is mandatory) are not formally codified in the repository. They are documented as **Unresolved Administrative Requirements** in [`reproducibility_guide.md`](file:///D:/IE612_Project/reproducibility_guide.md).
3. **No Commercial or Trading Claims:** Predictive density superiority is strictly evaluated using econometric scoring rules (log loss and CRPS). No claim is made regarding live trading profitability, transaction cost feasibility under high-frequency rebalancing, or investment returns.
