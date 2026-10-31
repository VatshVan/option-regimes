# Reproducibility & Demonstration Guide: Empirical Evaluation of Latent Market Regimes in Physical Return Density Forecasting

**Course:** IE 612 (Introduction to Financial Engineering)  
**Author:** Antigravity (Advanced Agentic Coding Pair Programmer)  
**Date:** 24 October 2026  
**Document Status:** Project reproduction guide; course submission requirements remain to be confirmed
**Governing Documents:**
- [`research_protocol.md`](file:///D:/IE612_Project/research_protocol.md)
- [`gate_d_final_test_report.md`](file:///D:/IE612_Project/gate_d_final_test_report.md)
- [`final_research_report.md`](file:///D:/IE612_Project/final_research_report.md)

---

## 1. Executive Summary & Verification Guarantee

This guide describes read-only artifact verification and the commands used to rerun selected audit/model stages. Rerun commands can read local raw data and may overwrite generated outputs; verify hashes first and use a clean copy if preserving the archived run matters.
1. **Local Vendor Data:** Raw OptionsDX bundles are intended to remain local and are excluded by the repository `.gitignore`; verify repository tracking status before any distribution. Reproduction requires lawful local access to those vendor files.
2. **Artifact Integrity:** SHA-256 values are recorded for selected datasets, predictions, diagnostics, and summaries. A matching hash verifies byte identity, not correctness of the method.
3. **Walk-Forward Re-Execution:** The Stage 8 script re-estimates the 24-block expanding walk-forward run from saved feature CSVs. Runtime and bit-for-bit determinism depend on the local software environment and are not guaranteed here.

---

## 2. Environment Setup & Dependencies

### 2.1 Software Prerequisites
- **Operating System:** Windows, macOS, or Linux.
- **Python Version:** Python 3.10 or higher.
- **Shell:** PowerShell or Bash.

### 2.2 Python Dependencies
The project relies exclusively on standard scientific computing libraries. Install dependencies via pip:
```powershell
pip install numpy scipy pandas yfinance torch
```
The model code imports PyTorch; CPU use is sufficient. Exact package versions and environment locking are not recorded, so results should be checked against the saved artifacts and hashes.

---

## 3. Repository Architecture & Key Artifact Locations

```text
IE612_Project/
├── README.md                                 # Project overview and top-level execution summary
├── implementation.md                         # Detailed project specification & audit trail
├── research_protocol.md                      # Frozen research protocol (version 1.0)
├── stage5_modeling_specification.md          # Formal model ladder & inference specification
├── gate_b_audit_report.md                    # Gate B calendar & feature construction report
├── gate_c_model_validation_report.md         # Gate C baseline & density stability report
├── gate_d_final_test_report.md               # Gate D final held-out test evaluation report
├── final_research_report.md                  # Comprehensive academic research report
├── final_presentation.md                     # Markdown presentation slide deck
├── reproducibility_guide.md                  # This guide
│
├── src/                                      # Core library modules
│   ├── data/
│   │   ├── audit_calendar.py                 # Exchange session calendar & missing session audit
│   │   ├── check_optionsdx_sample.py         # Schema parser, timestamp verification & forward parity
│   │   └── build_dataset.py                  # End-to-end dataset builder
│   ├── features/
│   │   ├── svix.py                           # Martin (2017) SVIX integration engine
│   │   ├── moments.py                        # Risk-neutral skewness and kurtosis computation
│   │   └── historical_state.py               # Historical return, realized volatility, downside semivariance, drawdown
│   └── models/
│       ├── hmm_filter.py                     # Causal forward-filtered HMM implementation
│       ├── density_models.py                 # Student-t location-scale regression architecture
│       ├── walk_forward_pipeline.py          # Expanding walk-forward engine with 21-session refits
│       └── evaluation_metrics.py             # Analytical Student-t CRPS, NLL, DM test, and bootstrap
│
├── scratch/                                  # Execution and audit scripts
│   ├── batch_feature_pipeline.py             # Feature pipeline for Stage 6 candidate generation
│   ├── run_stage7_experiments.py             # Stage 7 Development and Validation execution
│   ├── audit_2022_2023_test_data.py          # Stage 8 raw data coverage and contract schema audit
│   └── run_stage8_test_evaluation.py         # Stage 8 Gate D walk-forward test evaluation
│
└── output/                                   # Archived datasets, predictions & metrics
    ├── stage6_features/                      # Candidate feature datasets (Development & Validation)
    │   ├── spx_features_development_2010_2019.csv
    │   ├── spx_features_validation_2020_2021.csv
    │   ├── spx_daily_closes_2009_2021.csv
    │   └── feature_datasets_metadata.json
    ├── stage7_models/                        # Stage 7 validation outputs & refit diagnostics
    │   ├── validation_predictions_primary.csv
    │   ├── validation_metrics_summary.json
    │   ├── hmm_refit_diagnostics_primary.json
    │   └── sensitivity_analysis_summary.json
    └── stage8_test/                          # Stage 8 test outputs, predictions & metadata
        ├── raw_data_audit_2022_2023.json
        ├── test_dataset_metadata.json
        ├── spx_features_test_2022_2023.csv
        ├── spx_daily_closes_2009_2024.csv
        ├── test_predictions.csv
        ├── test_predictions_strict_isolation.csv
        ├── test_metrics_summary.json
        ├── hmm_refit_diagnostics_test.json
        └── density_integration_checks.json
```

---

## 4. Invariant Cryptographic Checksums (SHA-256)

To guarantee scientific reproducibility without data drift, verify that local files match these exact hashes:

### 4.1 Stage 6 Candidate Datasets (Frozen Invariants)
```powershell
Get-FileHash output/stage6_features/spx_features_development_2010_2019.csv -Algorithm SHA256
# Expected: 138FA68AF7F8F21DA257F5D41332E583E73F32E358C6B2242A5D783DD5B2978E

Get-FileHash output/stage6_features/spx_features_validation_2020_2021.csv -Algorithm SHA256
# Expected: 8BEDC8B4E3AE3CF42A99C8AB8477950AB69244EB8E052C7AFACEF8AC9E7C19D7

Get-FileHash output/stage6_features/spx_daily_closes_2009_2021.csv -Algorithm SHA256
# Expected: 4F300DD58572EF986114E15BB35047449BA1E59B2A6678257AB34A3F1F5EBB1A
```

### 4.2 Stage 8 Test Evaluation Outputs
```powershell
Get-FileHash output/stage8_test/spx_features_test_2022_2023.csv -Algorithm SHA256
# Expected: 8A4BF13AF38F5FA8D4681B746B2D162D5A02F7711A04564F704CA2CDE2BC5C0E

Get-FileHash output/stage8_test/test_predictions.csv -Algorithm SHA256
# Expected: 3097CE28BE9484D7D0A429B620BE886A8643086CED8E961A5615982DAE61E600

Get-FileHash output/stage8_test/test_predictions_strict_isolation.csv -Algorithm SHA256
# Expected: 3C98FD166CBAF68E167BEDA9A5EBE64B6B70BB68D30BF546ECBE28892D3D5EEC

Get-FileHash output/stage8_test/test_metrics_summary.json -Algorithm SHA256
# Expected: CE29FEB51D4E5BCE70A1EA948A872CDA0FEF19EFD96E9D96173A12FAD1620A14

Get-FileHash output/stage8_test/raw_data_audit_2022_2023.json -Algorithm SHA256
# Expected: F165B3D93061773F7677F0FF40E1F13C00EF629E2D82FEC2B488DF4056B31849

Get-FileHash output/stage8_test/hmm_refit_diagnostics_test.json -Algorithm SHA256
# Expected: EC6F4E489BD3A2D260CA684F3C2DA7685E8BA02836BF308151DF2B2F27ADD968
```

---

## 5. Step-by-Step Reproduction Walkthrough

### Step 1: Verify Stage 8 Raw Data Coverage (Test Partition Audit)
This command reads all local 2022–2023 raw OptionsDX bundles and downloads the ^GSPC calendar through `yfinance`; it requires lawful local data access and network availability. It rewrites the audit JSON. To preserve the committed audit, first copy the repository or use the saved JSON for read-only review.
```powershell
python scratch/audit_2022_2023_test_data.py
```
**Expected Output:**
- 24 monthly option bundles audited.
- Exactly 4,100,693 contract records scanned.
- 100% schema match (33/33 columns).
- Uniform 16:00 vendor read-time strings verified on all observed dates; this does not prove exchange-level synchronization.
- Exactly 5 single-session gaps detected and reconciled against exchange calendar.
- Audit report written to `output/stage8_test/raw_data_audit_2022_2023.json`.

---

### Step 2: Reproduce Stage 7 Validation Models & Sensitivity Analyses
This command re-estimates models $B0$–$B4$ and $R1$ across the saved development/validation datasets, including the mid-2012 sensitivity benchmark. It rewrites Stage 7 outputs; use a copy if you need to preserve the archived run.
```powershell
python scratch/run_stage7_experiments.py
```
**Expected Output:**
- Fits $B0$–$B4$ and $R1$ on Development split ($N = 2,231$ pairs).
- Generates 494 out-of-sample validation predictions across 25 rolling refits.
- Verifies density validity (all integrals $= 1.0000$, $\sigma_t > 10^{-4}$, $\nu \ge 2.1$).
- Calculates analytical Student-$t$ CRPS.
- Generates mid-2012 sensitivity benchmark predictions ($N = 1,844$ pairs).
- Saves predictions and summaries to `output/stage7_models/`.

---

### Step 3: Reproduce Stage 8 Gate D Final Test Evaluation
This command re-estimates the frozen-configuration walk-forward pipeline from saved operational development, validation, and test feature datasets. It does not need to parse raw 2022–2023 option bundles, but it rewrites Stage 8 predictions and metrics; use a copy if preserving the committed results.
```powershell
python scratch/run_stage8_test_evaluation.py
```
**Expected Output:**
- Re-fits models across 24 expanding walk-forward blocks on the held-out test partition.
- Evaluates both the primary Jan 3-origin-score-excluded trajectory ($N=500$) and the strictly isolated trajectory ($N=500$).
- Computes out-of-sample NLL, CRPS, empirical central interval coverage (50%, 80%, 95%), quantile pinball losses (10th, 50th, 90th), and PIT Kolmogorov-Smirnov tests.
- Executes paired Diebold–Mariano tests with Newey-West lag truncation ($q=5$).
- Executes stationary block bootstrap (2,000 resamples, mean block length 5 sessions).
- Confirms:
  - $\bar{d} = +0.005417$ nats/session
  - $\text{DM} = 1.4521, \ p_{\text{one-sided}} = 0.0732$
  - Bootstrap 95% CI: $[-0.001979, +0.013837]$
  - $B4$ CRPS $= 0.006616$, $R1$ CRPS $= 0.006609$
- Saves all artifacts to `output/stage8_test/`.

---

## 6. OptionsDX Licensing & Data Protection Disciplines

In strict accordance with the OptionsDX terms of service:
1. **No Source CSV Redistribution:** Raw contract-level ZIP and CSV files located in `Data/` are strictly excluded from version control via `.gitignore`.
2. **Derivatives & Summaries Only:** Only derived scalar features ($Q_t, X_t$), date-level model predictions, and statistical metrics are checked into the repository.
3. **Local Ingestion Only:** Anyone replicating the pipeline from raw files must obtain lawful access to the OptionsDX SPX historical package and place files into the local `Data/SPX Options Chain/` directory structure.

---

## 7. Unresolved Administrative Requirements

The repository contains all theoretical, empirical, econometric, and code artifacts necessary for the scientific evaluation. However, an exhaustive search of the project repository confirms that **no formal course syllabus, rubric, or submission specification file is present**.

The following administrative items are formally classified as **Unresolved Administrative Requirements**:

```
+-------------------------------------------------------------------------------------------------------------------------+
|                                           Unresolved Administrative Items                                               |
+-------------------------------------------------------------------------------------------------------------------------+
| Item | Requirement Description                   | Current Project Status        | Action Required for Final Submission |
+------+-------------------------------------------+-------------------------------+--------------------------------------+
| AD-1 | Course Grading Rubric                     | Not present in repository     | Verify with instructor whether a     |
|      |                                           |                               | formal rubric or scoring sheet applies|
+------+-------------------------------------------+-------------------------------+--------------------------------------+
| AD-2 | Portfolio Backtest Requirement            | Omitted from final report to  | Confirm whether course requires an   |
|      |                                           | prevent overclaiming          | illustrative portfolio backtest      |
+------+-------------------------------------------+-------------------------------+--------------------------------------+
| AD-3 | Final Report Format & Page Constraints    | Authored as standard Markdown | Confirm whether PDF, LaTeX, or Word  |
|      |                                           | (`final_research_report.md`)  | conversion with page limits is needed|
+------+-------------------------------------------+-------------------------------+--------------------------------------+
| AD-4 | Presentation Slide Format                 | Authored as Markdown deck     | Confirm whether PowerPoint (.pptx) or|
|      |                                           | (`final_presentation.md`)     | PDF export is required for class     |
+------+-------------------------------------------+-------------------------------+--------------------------------------+
| AD-5 | Submission Portal & Archive Scope         | Git repository clean          | Confirm submission channel (Moodle,  |
|      |                                           |                               | GitHub, or ZIP archive without Data/)|
+-------------------------------------------------------------------------------------------------------------------------+
```

---

## 8. Summary of Scientific Determination

For academic assessment, the quantitative findings of this study are summarized as follows:
1. **Primary Null Result:** The regime-augmented challenger ($R1$) does not demonstrate a statistically significant out-of-sample log-likelihood gain over the matched non-regime baseline ($B4$) ($p = 0.0732 > 0.05$; bootstrap 95% CI spans zero).
2. **Secondary Metric:** Mean CRPS is numerically slightly lower for $R1$ (0.006609) than for $B4$ (0.006616); this does not establish an inferential advantage.
3. **Parsimony Ruling:** In accordance with pre-registered econometric decision criteria, **the non-regime baseline $B4$ is favored on grounds of parsimony**.
4. **Economic Integrity:** No trading, investment, or live-portfolio claims are made.
