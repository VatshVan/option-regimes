# Implementation Plan

## Regime-conditioned physical return density forecasts from option-implied information

**Document status:** Final research specification and implementation record; all phases completed through Stage 8 Gate D (final test evaluation complete; empirical findings inconclusive, parsimonious baseline B4 favored; Stage 9 final package delivered); updated 24 October 2026  
**Course scope:** IE 612, one-month empirical project  
**Decision status:** Completed single-index forecasting study using SPX EOD files from OptionsDX (2010–2023). All stages executed under strict prequential protocol; test evaluation completed at Gate D with Jan 3-origin score exclusion; primary hypothesis test inconclusive. Broad multi-stock portfolio version omitted as planned.

## 1. Executive decision

The project asks whether persistent market-state information improves the conversion of option-implied risk-neutral information into a forecast of the realized, physical distribution of future returns. This is a valid empirical question and fits the subject's mix of options, distributions, forecasting and portfolio decisions.

The five supplied papers establish that the ingredients are not individually new: option-implied moments have been used in portfolio selection (DeMiguel et al.); joint modelling of physical returns and option prices has a long econometric history (Chernov & Ghysels); flexible non-Gaussian distributions and a P/Q change of measure have been used for portfolio risk (Bianchi & Tassinari); ML already predicts option returns from rich characteristics (Bali et al.); and, most critically, an MDN already maps option-implied information into a physical return density (Ulrich et al.). The defensible contribution is therefore a *conditional incremental-value test*: does a causally filtered, persistent latent state improve physical density forecasts beyond a well-tuned non-regime model that already receives the same option and historical inputs?

### Feasibility verdict

- **Research question:** Feasible and precise after narrowing to one underlying, one forecast horizon and a small model ladder.
- **Data:** Main risk, but a plausible free US route exists. OptionsDX lists SPX full-chain products for 2010–2023 and describes EOD data with bid/ask/last, underlying, IV and Greeks; its variants range from $0 to $50. Confirm the selected EOD years check out at $0 and terms permit course research. NSE's public historical-report interface exposes F&O contract-wise price-volume CSV by date; official format specifications include option OHLC, OI and volume, but not bid/ask. This can support a lower-fidelity NIFTY prototype, not the preferred quote-based surface study. NSE separately lists historical EOD/order/trade products as subscription offerings. IIT Bombay LSEG/Capitaline remains another possible institutional route.
- **Methods:** Feasible if the first model uses compact option-surface summaries, a simple physical-density model, and only then a small filtered HMM extension. Full NTS/GH joint estimation, complex neural MDNs, multi-asset copulas, intraday execution, and a large universe are outside the one-month critical path.
- **Portfolio translation:** A single index cannot support a meaningful cross-sectional Markowitz experiment. Use an illustrative cash-versus-index exposure based on a pre-specified risk rule, or omit portfolio optimization if it distracts from forecast evaluation. Do not present this as a diversified portfolio-selection replication.
- **Novelty:** Unproven until the literature check is refreshed and the exact target, market, features, and baseline are fixed. The project should make no priority claim; report whether the regime feature adds value in this dataset and design.

## 2. Frozen research question and estimands

### Primary question

At date (t), do option-implied features (Q_t) and observable historical state (X_t), augmented with a filtered persistent regime probability π_t, improve the out-of-sample forecast of the next trading day's physical return density?

\[
p(r_{t+1}\mid Q_t,X_t,\mathcal F_t) \quad\text{versus}\quad
p(r_{t+1}\mid Q_t,X_t).
\]

Here (Q_t) is information inferred from observed option prices; it is under the risk-neutral measure and is **not** the physical expected return. (X_t) contains only information observable by the forecast cutoff. The realized return (r_{t+1}) is the physical outcome. No no-arbitrage identity by itself recovers the physical distribution without assumptions about the pricing kernel.

### Hypotheses

- **H1 (primary):** The regime-augmented model has lower mean out-of-sample log loss than the strongest non-regime model on the held-out 2022–2023 test period (historically unopened during development and validation; evaluated at Gate D in Stage 8 with Jan 3 origin excluded from primary scoring; test cash close breach acknowledged in commit cee01a1 Git history).
- **H2 (incrementality):** Any gain remains relative to a non-regime model with the same current volatility, return and option features; it is not just a disguised volatility-level effect.
- **H3 (calibration):** The regime model is not materially worse calibrated (PIT and interval coverage) and provides acceptable tail calibration.
- **H4 (economic relevance, secondary):** A pre-specified cash/index allocation using the forecasts improves net performance or risk relative to simple benchmarks. This is secondary and cannot substitute for H1.

Pre-register log score as the primary metric and a one-sided direction of improvement (lower is better) before looking at the final test period. Report negative results as valid results.

## 3. Unit of analysis and scope

### Recommended MVP

- **Underlying:** SPX index options from OptionsDX EOD, if a free yearly bundle, permitted use and sample validation pass the gate. If not, use licensed LSEG/Capitaline data or explicitly downscope to free NIFTY EOD price-derived features.
- **Frequency:** One end-of-day observation per trading date, using a fixed, reproducible cutoff and same-day option/underlying alignment.
- **Target:** Next trading day's close-to-close log return. This follows the daily density-forecast precedent in *Forward-looking P* and avoids overlapping 21-day labels in the primary study.
- **Universe:** One index only; no individual-stock cross section in MVP.
- **Models:** Historical distribution benchmark; option-only / historical-only feature checks; regularized or small MDN combined baseline; combined baseline plus filtered HMM probabilities. Keep model capacity modest relative to the sample.
- **Portfolio:** Secondary index/cash timing experiment only if time remains, with fixed exposure bounds, turnover reporting, costs and no test-period tuning.

### Explicit exclusions for the first delivery

No production trading, high-frequency data, stock-option universe, multi-asset Markowitz optimization, direct prediction of option prices, Black–Scholes expected-return inference, full NTS/GH or Esscher-transform implementation, deep/recurrent network sweep, reinforcement learning, or claim that the learned density is the unique true physical distribution.

## 4. Literature synthesis and implementation consequences

| Paper in folder | What it establishes | Consequence for this implementation |
|---|---|---|
| DeMiguel, Plyakha, Uppal & Vilkov, *Improving Portfolio Selection Using Option-Implied Volatility and Skewness* | Tests option-implied volatility, correlation, volatility-risk-premium and skewness in out-of-sample portfolio construction. Volatility can improve minimum-variance performance; correlation was not uniformly useful; return adjustments using implied measures improved Sharpe in their setting. | Treat portfolio performance as economic validation; include simple benchmarks, turnover and costs. Do not state that options mechanically give expected returns. |
| Bianchi & Tassinari, *Forward-looking Portfolio Selection with Multivariate Non-Gaussian Models and the Esscher Transform* | Fits multivariate NTS/GH models to return series and univariate option smiles, connecting (P) and (Q) through an Esscher transform; handles skew, tails and dependence. | Explain the measure distinction and tail-risk motivation. Use as conceptual benchmark; reproducing its joint calibration is too large for MVP. |
| Chernov & Ghysels (2000), *A Study Towards a Unified Approach to the Joint Estimation of Objective and Risk Neutral Measures for the Purpose of Options Valuation* | Jointly uses underlying prices and option-implied volatility in an EMM/Heston example with latent volatility; shows different data sources and measures need not agree. | Keep options-only, historical-only and combined models distinct. Avoid claiming model-free recovery of (P) from (Q). |
| Bali, Beckmeyer, Mörke & Weigert (2023), *Option Return Predictability with Machine Learning and Big Data* | Uses more than 12 million US option observations (1996–2020); nonlinear models improve out-of-sample option-return predictions; stock measures add information. The prediction target is option returns, not physical index density. | Use nonlinear non-regime baselines and strict time splits. Cite as ML-method precedent, not evidence for the project's density claim. |
| Ulrich, Walther, Rothfuss & Ferreira (2019), *Forward-looking P* | Uses a mixture-density network on S&P 500 option-implied measures to estimate the conditional physical return density; reports log-likelihood and calibration/predictive comparisons. This is the closest prior art. | Reproduce the core option-feature-to-density framing where data allow. The candidate extension is regime persistence beyond its flexible non-regime mapping, not MDN use or Q-to-P forecasting itself. |

### Required literature check before claims are finalized

The five supplied papers are a core pack, not proof of novelty. Before the final proposal/report, search forward citations and work on regime-dependent option-implied density forecasts, option-implied skewness regimes and state-dependent P/Q mappings. Add only directly relevant papers, record the search date and explain how this design differs. Avoid asserting “first” or “novel” without a documented search.

## 5. Data access and feasibility gate (do this before coding models)

### 5.1 Data-source finding (online check, 21 October 2026)

**NIFTY 50:** NSE's public Historical Reports page lists both *Contract-wise Price Volume Data* and *Archives of Daily / Monthly Reports (FO)*. The contract-wise interface exposes date-range and CSV download controls. NSE's published report specification defines contract-wise option records with expiry, strike, call/put, OHLC close, open interest, traded quantity, number of contracts/trades and premium value. These fields are useful, but do not include bid/ask quotes needed to screen spreads or compute quote midpoints. The official NSE EOD/historical-data page separately identifies subscription data products, including historical order/trade data. Therefore, the free official NIFTY route appears **downloadable in useful daily contract-level form, but does not meet the preferred quote-quality standard**. We have not retrieved a dated file to confirm the interface's practical historical range, bulk limits or exact research-use terms.

**SPX alternative:** OptionsDX lists full SPX chains for each year from 2010 through 2023 in monthly CSV files and includes end-of-day among the frequencies. Its product page says the chain includes all expiries/strikes, IV, Greeks, bid/ask/last and underlying price; variants range from $0 to $50. Its field definitions confirm quote time, underlying, expiry, strike, bid/ask and IV-related fields, but do not list open interest. This is substantially better suited to surface construction at zero acquisition cost for the free EOD variants, but it is a third-party dataset, not an exchange-certified archive. The data-generation and validation provenance is less transparent than an exchange or established academic vendor. Verify the selected years at checkout, inspect sample rows/terms, and compare sample dates and surface features with an independent source before treating it as research-grade.

**Recommendation:** Use SPX OptionsDX EOD as the first candidate because this study needs an option surface. If sample validation or permitted use fails, check IITB LSEG/Capitaline access. Use free NSE NIFTY contract reports only if the project explicitly downgrades to EOD-price-derived IV/surface-proxy features and describes missing bid/ask as a limitation; do not claim quote-quality Q moments.

### 5.1.1 Local data snapshot inspected

Only one representative monthly text file from each local product folder was inspected, as a schema/sample check; no file was read in full and no coverage or dataset-wide quality claim is implied:

| Local product | Representative file | What the sample shows | Interpretation |
|---|---|---|---|
| SPX options | `Data/SPX Options Chain/spx_eod_2023q4-ai4uc9/spx_eod_202310.txt` | OptionsDX wide schema with paired call/put fields, quote date/time, underlying, expiry, DTE, strike, bid/ask, volume, size, IV and Greeks. | Structurally suitable for the proposed SPX option-feature pipeline, subject to date coverage, timing, quote-quality, and permission gates. |
| SPY options | `Data/SPY Options Chain/spy_eod_2023q4-vzwoxb/spy_eod_202310.txt` | Same 33-column wide schema and quote fields. | Useful for a separate robustness study only. Do not pool with SPX: SPY is an ETF with different contract/early-exercise and dividend considerations. |
| VIX options | `Data/VIX/vix_eod_2023q4-9rnzlg/vix_eod_202310.txt` | Same option-chain schema, with VIX as the reported underlying and expiries/strikes for options. | This is a VIX options chain, not a daily VIX index history file. It is not required for the SPX MVP. If VIX level is used as an observable state feature or validation series, obtain a separate dated VIX index close series and align it to the forecast cutoff. |

The sampled files use a 16:00 quote timestamp and show some fields blank (including precomputed IV on some contracts), zero-bid options, and expiry-day contracts with `DTE = 0`. Therefore, do not assume vendor IV/Greeks are complete or reproducible. Recompute IV and Greeks from screened quotes with documented rates, forward/dividend inputs, and contract assumptions. The primary maturity selection must exclude expiry-day/very short-dated options; the existing 20–60 calendar-day band is a reasonable starting gate, not a validated final threshold. A single representative month establishes only that the columns and basic row layout are compatible; it does not establish sufficient liquid strikes, usable observations, continuous daily history, or a stable surface.

Before any model fitting, inventory filenames/dates and sizes without opening other raw files, then perform the planned audit on a preselected normal and stress date from the same source. Record usable dates, quote filters, strike/maturity coverage, missingness, and whether both dates pass the same predeclared criteria. Keep SPX as the sole primary universe unless the full audit fails; do not let the availability of SPY/VIX folders silently expand the research question.

*Stage 2 & 3 Update (21 October 2026):* The dataset inventory and targeted two-date quality audit were executed:
1. Inventory verified 168 contiguous monthly SPX files spanning 2010–2023 (14 full calendar years, ~5.28 GB) with zero missing calendar months. The calendar-year partition 2010–2019 / 2020–2021 / 2022–2023 represents an approximate 71.4% / 14.3% / 14.3% split by calendar-year span (10 years / 2 years / 2 years). Exact session counts will be computed directly from the full calendar audit without assuming nominal totals.
2. The two-date quality check was executed on 2020-01-15 (calm session, VIX = 12.42%, SPX cash close = 3289.29) and 2020-03-03 (crisis session, VIX = 36.82%, SPX cash close = 3003.37). Contract-wise OTM screening retained 99–278 usable strikes across 20–50 DTE, and maturities cleanly bracketed 30 days.
3. Theoretical cost-of-carry comparison: Synthetic forwards ($F_{\text{parity}} = 3289.55$ and $3000.41$) track theoretical forwards ($F_{\text{theo}} = S_t e^{(r-q)T} = 3288.64$ and $3000.74$) within $+0.91$ pts and $-0.34$ pts using 13-week T-Bill rates ($1.508\%, 0.918\%$) and benchmark dividend yields ($1.75\%, 1.95\%$), implying realistic dividend yields of $1.41\%$ and $2.08\%$. Observed differences between vendor `UNDERLYING_LAST` and cash closes are $+0.47$ pts ($+0.014\%$) and $-0.63$ pts ($-0.021\%$). Crucially, put-call parity guarantees internal surface consistency only; it does not prove quote/cash synchronization or remove 15-minute look-ahead risk if option quotes closed at 16:15 ET.
4. Martin (2017) SVIX calculation: Computed using Martin's forward-normalized formula (unweighted by $1/K^2$, normalized by $F_{t,T}^2$ with standard composite trapezoidal weights). Because retained quotes span a finite strike range without tail extrapolation, the values are discrete finite-grid estimates (yielding 30-day SVIX of **12.00%** on the calm date vs. official VIX 12.42%, and **34.88%** on the stress date vs. official VIX 36.82%). The numerical gaps ($-0.42$ vol pts and $-1.94$ vol pts) are documented strictly as empirical observations on these two dates, without asserting an unverified causal link to skewness or crisis put demand or implying equivalence with Cboe VIX.
5. **Gate A Verdict: Qualified Pass.** Pilot data-quality checks on the two authorized dates are approved. Work proceeded to Stage 4 (Feature Pipeline Specification). However, full-sample model estimation remains conditioned on completing full 14-year session continuity audits, early strike coverage (2010–2012) checks, and full-sample batch feature extraction across 2010–2021. `Data/SPY Options Chain` (American ETF) and `Data/VIX` (options on VIX) remain excluded from the primary MVP.
6. **Stage 4 Feature Pipeline Specification (21 October 2026):** Implemented the feature construction pipeline in `src/features/` extracting $Q_t \in \mathbb{R}^5$ ($\text{SVIX}_{30d}$, centered standardized $\text{QSkew}_{30d}$, centered standardized non-excess $\text{QKurt}_{30d}$, $\text{ATM\_IV}_{30d}$, $\text{TermSlope}_{60\_30}$) and $X_t \in \mathbb{R}^6$ ($r_{1d}, r_{5d}, \text{RV}_{5d}, \text{RV}_{20d}, \text{DSemi}_{20d}, \text{DD}_{20d}$). Validated via 4 unit tests and demonstrated on the two authorized dates (`2020-01-15` and `2020-03-03`). Risk-free rates and cash closes are documented as illustrative benchmark inputs with local caching. Output datasets, diagnostics, and provenance metadata are persisted in `output/stage4_features/`. (Historical Stage 4 context: At the completion of Stage 4, raw 2022–2023 option bundles remained unopened and no models were fit. Note: As disclosed in Stage 6, January 3 and 4, 2022 cash closes were subsequently retrieved in commit `cee01a1` and remain in Git history; raw option bundles remain unopened).
7. **Stage 5 Modeling Specification (21 October 2026):** Formalized the complete Stage 5 modeling specification in `stage5_modeling_specification.md` and updated `research_protocol.md`. Specified the 6-model comparison ladder ($B0$ unconditioned Gaussian, $B1$ volatility Student-$t$, $B2$ $Q$-only, $B3$ $X$-only, $B4$ combined non-regime baseline, $R1$ matched latent regime challenger), the causal HMM forward filtering recursion ($\pi_t \in \Delta^{K-1}$ with smoothed posteriors and Viterbi states strictly barred), training-only scaler fitting, expanding window 21-session monthly refits, paired Diebold-Mariano test with Newey-West HAC variance, stationary block bootstrap with automatic block length, secondary metrics with Benjamini-Hochberg FDR control, and explicit Gates B, C, D prerequisites. Crucially, the forecast information cutoff (16:00 vs. 16:15 ET lookahead risk) is explicitly treated as **unresolved**, and any operational use of option features in predictive models is **strictly gated** until quote timing is empirically verified in Gate B or a defensible cutoff is pre-specified. Furthermore, supervised training pairs are strictly restricted to origins $t \le \tau - 1$ where the next-day return label $r_{t+1}$ has already been observed, eliminating off-by-one future label leakage, while the HMM separately uses contemporaneous emissions through $\tau$. No models were fit, no walk-forward evaluations were executed, and raw 2022–2023 option bundles remained unopened.
8. **Stage 6 / Gate B Empirical Audit & Candidate Feature Datasets (21 October 2026, Revised):** Executed the authorized Gate B data audit across 2010-2021. Evaluated session continuity and arithmetic reconciliation against the authoritative 3,021-session exchange calendar (^GSPC benchmark): identified 2,994 observed option sessions, 30 missing sessions, and 3 market closure dates where OptionsDX propagated stale quotes (Hurricane Sandy Oct 29-30, 2012; President Bush funeral Dec 5, 2018), reconciling via $3021 - 30 + 3 = 2994$. While aggregate 12-year missingness is $0.993\% \le 1.0\%$, annual missingness exceeds 1.0% in 5 calendar years (2011 at 2.78%, 2014 at 1.19%, 2019 at 1.98%, 2020 at 1.19%, 2021 at 2.38%), meaning continuity is not a clean annual pass. Audited early strike breadth across 745 sessions in 2010-2012: standard monthly expiration cycles prevented 30-day bracketing on 76.4% of sessions in 2010 and 68.6% in 2011, while weekly option introduction in mid-2012 caused bracketing to jump to 95-100%. Derived and integrated exact day-count conversion from 13-week T-Bill discount yield (^IRX) to continuously compounded zero rate: $r_{\text{cont}} = -(365/91)\ln(1 - d(91/360))$. Causal carryforward on two bond market holiday closures (Columbus Day 2010 and Veterans Day 2016) was explicitly logged, eliminating silent imputation. Verified uniform '16:00' vendor readtime across all 12 vintages, but confirmed that vendor readtime alone does not prove synchronization with 16:00 ET cash closes. Generated candidate feature datasets in `output/stage6_features/`: Development (2010–2019, 2,516 sessions, 2,233 feature-complete rows [`valid_Q_all5 == True`, 88.75%], 283 incomplete [11.25%], yielding **2,232 usable supervised training pairs** $(Z_t, r_{t+1})$ after omitting terminal row 2019-12-31 whose target is nulled across the boundary, SHA-256: `138fa68af7f8f21da257f5d41332e583e73f32e358c6b2242a5d783dd5b2978e`) and Validation (2020–2021, 505 sessions, 496 feature-complete rows [98.22%], 9 incomplete [1.78%], yielding **495 usable validation scoring rows** $(Z_t, r_{t+1})$ after omitting terminal row 2021-12-31 whose target is nulled across the test boundary, SHA-256: `8bedc8b4e3ae3cf42a99c8ab8477950ab69244eb8e052c7afacef8ac9e7c19d7`). Crucially, downloading ^GSPC through January 2022 accessed both the 2022-01-03 close (4796.56) and 2022-01-04 close (4793.54) across the test boundary, compromising the test seal; these test closes and the derived 2021-12-31 validation return were committed in commit `cee01a1` and remain permanently recorded in Git repository history, although purged from the working tree cache. In response, boundary target returns on both 2019-12-31 (`UNOBSERVED_WITHOUT_VALIDATION_CLOSE`) and 2021-12-31 (`UNOBSERVED_WITHOUT_TEST_CLOSE`) were set strictly to NaN to guarantee partition purity. Gate B status is **Blocked / Qualified**: datasets are candidate outputs and not permanently frozen; operational model training remains gated pending formal resolution of the 16:00 vs. 16:15 ET cutoff and test boundary audit decisions. Complete details are documented in `gate_b_audit_report.md`.
**Higher-quality paid fallback:** Cboe DataShop's SPX EOD option products contain NBBO bid/ask and sizes, OHLC, volume, OI and optional calculated IV/Greeks, with historical coverage back to 2010 in its EOD product family. SPX-specific underlying bid/ask/calcs may require an additional Cboe Global Indices license. This is not a free route.

Any comparison with official Cboe volatility indices is a diagnostic, not a universal pass/fail correlation threshold. Match observation dates, close conventions, tenor, annualization, forward/dividend assumptions, and the exact moment definition first. For example, an ATM IV, VIX, and a model-free variance measure are related but are not identical quantities; likewise, a skew proxy need not equal the published SKEW index. Investigate material discrepancies rather than tuning cleaning choices to hit a preselected correlation.

### 5.2 Required fields

For each date and option contract: observation date/time, underlying/index level, expiry, strike, call/put flag, option price and ideally bid/ask or quote quality, volume, open interest, contract multiplier, settlement/European-style metadata, and a reliable risk-free rate or discount curve. Also obtain index closes and a trading calendar. Dividends/yield and forward level must be accounted for in option pricing/surface fitting.

### 5.3 Access routes

1. **OptionsDX SPX EOD (first candidate):** Select a free EOD year; download one normal and one stress date; check quote coverage, fields, timestamps, expiries/settlement roots, missing/crossed quotes and surface reconstruction. Confirm terms and that selected yearly EOD variants remain free.
2. **IIT Bombay LSEG Workspace / Capitaline:** Verify institutional licence allows research export/retention. Attempt a historical NIFTY or SPX option-chain export for a stress date and a normal date, including strikes/expiries and underlying levels. Record fields, coverage, gaps, export limits and restrictions.
3. **NSE public NIFTY reports:** Download a contract-wise report for a normal and stress date through the public CSV interface. Confirm practical range/export behavior. Use only OHLC-derived proxies unless bid/ask is obtained from another permitted source.
4. **NSE licensed historical data or Cboe DataShop:** If free sources fail validation, ask the institution about existing access before buying. Do not assume the course budget covers commercial data.
5. Do not substitute Yahoo-style single-contract history for a complete surface. Do not scrape in ways that violate exchange or vendor terms.

### 5.4 Hard gate criteria

Proceed with surface-based risk-neutral features only if the sample has enough dates and liquid strike/maturity coverage to fit a stable surface, includes synchronous index and contract metadata, and the use is permitted. Target a minimum of several years of daily observations and enough distinct stress/quiet periods for time-ordered evaluation; the exact count must be set after seeing actual coverage and missingness. If only a short sample or scattered chains are available, change the question to a feasibility/prototype study or stop rather than implying a robust regime test.

Deliverable at gate: a one-page source decision with a sample export, data dictionary, usable date range, missingness summary, licensing note, and go/no-go decision. No model implementation should precede this gate.

## 6. Data construction specification

### 6.1 Option chain cleaning

1. Normalize contract identifiers, expiry dates, strike units, call/put labels and multipliers; retain source fields unchanged alongside normalized fields.
2. Remove duplicate contracts and invalid prices; flag zero, crossed, stale, non-finite and implausible quotes. If bid/ask unavailable, treat closing-price quality as a documented limitation and use conservative liquidity thresholds based on volume/open interest and price sanity.
3. Use calls and puts where coverage permits. Restrict to a pre-defined maturity band (initially nearest monthly maturity with sufficient days to expiry, e.g. 20–60 calendar days) or interpolate to one fixed maturity. Exclude expiry-day contracts and very short maturities from the primary surface.
4. Estimate forward and discount inputs consistently. Check put-call parity only where quote quality and contract conventions make it meaningful.
5. Fit an arbitrage-aware smooth call-price or implied-volatility surface on each date and maturity (shape-preserving / constrained smoothing); do not take raw finite differences of noisy prices as if they were a valid density.
6. Extract a compact, fixed-dimensional feature vector: ATM IV, fixed-moneyness skew/smile slope or 25-delta risk reversal when reliably supported, curvature, term-structure slope, and (only when stable) risk-neutral variance/skew/tail summaries. Save diagnostics and surface-fit errors.
7. Standardize time to expiry, annualization, moneyness definition and units. Avoid option features whose support changes unpredictably across dates.

For the local OptionsDX schema specifically, strip whitespace from column names before parsing, reshape the paired call/put columns into one contract per row while retaining source columns, and do not treat `C_SIZE`/`P_SIZE` as open interest. The representative rows show sizes in a text form (for example, bid size x ask size); parse only if a defined use requires it. Volume is available, but open interest is not present in the sampled schema. Treat missing IV/Greeks as expected and calculate them from quote midpoints only after filtering. Preserve bid and ask separately and store a quote-rejection reason; a midpoint alone hides wide or unusable markets.

The 16:00 timestamp in the sampled rows is encouraging for close alignment, but it does not prove synchronization with the underlying close across all dates or product vintages. Fix a documented information cutoff and verify timestamps and exchange early-close days. Where a quote and underlying snapshot cannot be shown synchronous, either derive a forward from valid same-snapshot option quotes with a documented discount input or move the forecast origin to the next feasible time. Put-call parity is a consistency diagnostic, not a guarantee that an inferred forward repairs stale, crossed, or asynchronous quotes.

If constructing a risk-neutral density via the Breeden–Litzenberger relation, use an arbitrage-controlled call curve, correct discounting, a stated boundary/tail treatment, and checks for non-negative density and unit mass. If these checks fail, do not use that extracted density; retain robust surface summaries as inputs instead.

### 6.2 Historical inputs and target

- Compute index log returns from a verified total-return series if feasible; otherwise document that the price return excludes dividends. Apply corporate-action and holiday alignment consistently.
- Historical state (X_t): lagged returns (e.g. 1, 5, 20 sessions), trailing realized volatility/downside volatility, and a drawdown or trend summary. Limit feature count.
- Primary target: (r_{t+1}=\log(S_{t+1}/S_t)), observable after the next close. Align features to information available at close (t); if option data timestamp is not close-aligned, shift the forecast origin to the next feasible time.
- Secondary horizon only after primary succeeds: a fixed 5-session cumulative return. It overlaps if generated daily; use non-overlapping origins or purge/embargo and dependence-aware inference.

### 6.3 Dataset audit

Produce counts by date, contract, expiry, strike and moneyness; missingness heat maps; price/quote filters; liquidity distribution; surface fit and no-arbitrage diagnostics; underlying alignment; holiday/date checks; and final feature/label sample sizes. Preserve rejected observations and reason codes. Freeze the target and feature-generation version before evaluation.

## 7. Models and estimation

### 7.1 Model ladder and architecture specifications

All predictive models are structured in a strict hierarchy to isolate the incremental value of latent regimes:

- **B0 Historical unconditional:** Stationary expanding Gaussian density $\mathcal{N}(\mu_\tau, \sigma_\tau^2)$ estimated on historical returns through date $\tau$.
- **B1 Volatility baseline:** Location-scale Student-$t$ distribution with dispersion scaling strictly with trailing realized volatility: $\sigma_t = \alpha_0 + \alpha_1 \text{RV}_{20d,t}$, with $\alpha_0 > 0, \alpha_1 \ge 0, \nu > 2.1$.
- **B2 Q-only diagnostic:** Location-scale Student-$t$ model conditioned strictly on forward-looking option moments $Q_t \in \mathbb{R}^5$ ($\text{SVIX}_{30d}, \text{QSkew}_{30d}, \text{QKurt}_{30d}, \text{ATM\_IV}_{30d}, \text{TermSlope}_{60\_30}$).
- **B3 X-only diagnostic:** Location-scale Student-$t$ model conditioned strictly on historical state features $X_t \in \mathbb{R}^6$ ($r_{1d}, r_{5d}, \text{RV}_{5d}, \text{RV}_{20d}, \text{DSemi}_{20d}, \text{DD}_{20d}$).
- **B4 Combined non-regime (primary comparator):** Primary architecture is a parametric Student-$t$ location-scale regression conditioned on $[Q_t, X_t] \in \mathbb{R}^{11}$:
  $$\mu_t = \mathbf{w}_\mu^\top [Q_t, X_t] + b_\mu, \quad \sigma_t = \text{softplus}(\mathbf{w}_\sigma^\top [Q_t, X_t] + b_\sigma) + \sigma_{\min}, \quad \nu = \text{softplus}(w_\nu) + 2.1$$
  with $\sigma_{\min} = 10^{-4}$. Fallback is a compact 2-component Mixture Density Network (MDN) if multi-modality is established on validation data.
- **R1 Latent regime challenger (primary hypothesis test):** Matched architecture conditioned on $[Q_t, X_t, \pi_t] \in \mathbb{R}^{11+K}$, where $\pi_t \in \Delta^{K-1}$ is the forward-filtered latent regime probability vector. Shares identical functional form, activation functions, parameter constraints, optimizer, and $\ell_2$ regularization grid as $B4$.

### 7.2 Causal Hidden Markov Model (HMM) filtering

Fit a continuous Gaussian HMM with $K \in \{2, 3\}$ latent states on a low-dimensional bivariate emission vector $\mathbf{y}_t = [\widetilde{r}_t, \widetilde{\text{RV}}_{20d,t}]^\top$ (standardized return and 20-day realized volatility).
- **In-sample fitting:** Estimated strictly on expanding training windows via Baum-Welch EM.
- **Causal forward filtering:** At each forecast origin $t$, compute forward-filtered probabilities:
  $$\pi_{t,k} \equiv P(z_t = k \mid \mathbf{y}_1, \dots, \mathbf{y}_t) \propto p(\mathbf{y}_t \mid z_t = k) \sum_{j=1}^K A_{jk} \pi_{t-1,j}$$
- **Strict anti-leakage rule:** Smoothed probabilities $\gamma_{t,k} \equiv P(z_t = k \mid \mathbf{y}_1, \dots, \mathbf{y}_T)$ and full-sample Viterbi states are strictly prohibited.
- **$K$-selection:** Conducted on validation split (2020–2021). Requires state occupancy $\ge 5.0\%$ and dwell time $\ge 5$ sessions. Default to parsimonious $K=2$ unless $K=3$ improves validation NLL by $\ge 0.020$ nats.

### 7.3 Density validity and training constraints

All predictive densities must integrate to 1.0, remain finite and strictly positive at realized returns, and enforce parameter constraints ($\sigma_m > 10^{-4}$, $\nu_m \ge 2.1$). Use stable log-sum-exp implementations with numerical floors. All feature scalers and imputers are fit strictly on training data $s \le \tau$ and frozen out-of-sample.

Crucially, under user-authorized Proposal A, the operational target is $y_t \equiv \ln(S_{t+2}/S_{t+1})$. Supervised models $B0$–$B4$ and $R1$ at refit origin $\tau$ are trained strictly on observed complete-case pairs $\{(\mathbf{z}_t, y_t)\}_{t=1}^{\tau-2}$, because next-session return $y_{\tau-1} = \ln(S_{\tau+1}/S_\tau)$ has not closed at date $\tau$. The unsupervised HMM and feature scalers separately use contemporaneous information and emissions through date $\tau$.

## 8. Evaluation design (leakage-resistant)

1. Chronological order strictly preserved: Training (2010–2019, 10 years, ~71.4%), Validation (2020–2021, 2 years, ~14.3%), Held-Out Test (2022–2023, 2 years, ~14.3%, raw option bundles unopened; test cash close breach recorded in commit cee01a1).
2. The 2022–2023 raw option bundles remain unopened until all model choices, hyperparameters, and feature extraction algorithms are permanently frozen. (Note that January 3 and 4, 2022 cash closes were retrieved in commit `cee01a1` and remain in Git history; the test partition cannot be described as sealed or untouched). The known Jan 3-to-Jan 4 return is strictly excluded from any eventual test score.
3. Expanding-window walk-forward refit on a monthly cadence (every 21 active trading sessions). Supervised training strictly restricted to $t \le \tau - 2$ under Proposal A to prevent label leakage, while HMM emissions use $t \le \tau$.
4. Missing session handling: single-session option gap causally forward-filled ($Q_t \leftarrow Q_{t-1}$); multi-session gaps or missing cash closes omitted from evaluation with diagnostic codes logged.
5. The forecast information cutoff was resolved on 22 October 2026 via User-Authorized Project Decision adopting Proposal A ($y_t \equiv \ln(S_{t+2}/S_{t+1})$). Features at session $t$ close predict the physical return over session $t+1$ close to session $t+2$ close, cleanly eliminating the 16:00 vs. 16:15 option lookahead risk. The historical candidate target $r_{t+1} = \ln(S_{t+1}/S_t)$ is preserved in Stage 6 CSVs. Stage 7 operational datasets are generated separately.

### Forecast metrics and statistical inference

- **Primary metric:** Out-of-sample Negative Log-Likelihood (NLL) on held-out test data (raw option bundles unopened; cash close breach recorded in commit cee01a1): $\mathcal{L}(M) = -\frac{1}{N_{\text{test}}} \sum_{t=1}^{N_{\text{test}}} \ln \widehat{p}_{t+1}^{(M)}(r_{t+1})$.
- **Hypothesis test:** Paired Diebold-Mariano test on loss differential $d_t = \ln \widehat{p}_{t+1}^{(R1)}(r_{t+1}) - \ln \widehat{p}_{t+1}^{(B4)}(r_{t+1})$ with Newey-West (1987) HAC variance estimation and automatic bandwidth $L = \lfloor 4 (N_{\text{test}}/100)^{2/9} \rfloor$.
- **Stationary block bootstrap:** Politis & Romano (1994) bootstrap on $\{d_t\}$ with automatic block-length selection (Politis & White, 2004; Patton et al., 2009) and 2,000 replications to compute 95% confidence intervals.
- **Secondary diagnostics:** CRPS, PIT histograms, Kolmogorov-Smirnov and Berkowitz (2001) normality tests on $z_t = \Phi^{-1}(u_t)$, central interval coverage (50%, 80%, 95%), tail pinball loss ($\alpha \in \{0.01, 0.05, 0.10, 0.90, 0.95, 0.99\}$).
- **Multiple comparison control:** Benjamini-Hochberg (1995) FDR control at $q = 0.05$ across secondary metrics.
- **Significance threshold:** Statistical significance requires one-sided DM $p < 0.05$ and bootstrap CI excluding zero; practical significance requires $\bar{d} \ge 0.010$ nats/day (~2.5 nats/year).

### Portfolio translation (secondary only)

Long-only 1-asset volatility-targeting strategy (cash vs. index) with 15% annualized target, 5 bps transaction costs, and exposure bounded to $[0, 1]$. Strictly secondary and illustrative; cannot rescue a failed density hypothesis.

## 9. Falsification, ablations and robustness

Core tests, prioritized:

1. B4 versus R1 on identical dates, features, refit schedule and tuning budget.
2. Add current realized volatility/state to B4 before adding latent regime probabilities (tests the simpler explanation).
3. Remove option features; remove historical features; remove regime probabilities.
4. Replace filtered regime probabilities with a volatility threshold chosen on training data; shuffle regime probabilities within training/test blocks as a diagnostic, without using shuffled results to select a winning model.
5. Check (K=2) versus (K=3), regime occupancy and transition persistence on validation only.
6. Test alternative option feature groups and conservative liquidity filters.
7. Sensitivity to training window/refit cadence and a small change in forecast horizon, if time permits.
8. Report full sample and fixed high/low-volatility subsets, with thresholds determined from training data, not selected from test outcomes.

## 10. One-month work sequence and decision gates

| Phase / Week | Work Description | Deliverable / Gate Status |
|---|---|---|
| **Phase 1 (Week 1)** | Stage 1 Research Protocol, Stage 2 Feasibility Audit, Stage 3 Targeted Quality Check. | **Gate A: Qualified Pass.** 168 monthly SPX files inventoried; 2 pilot dates passed parsing, 16:00 timestamp, forward parity, and Martin SVIX integration. Early strike depth and full session continuity unverified. |
| **Phase 2 (Week 2)** | Stage 4 Feature Pipeline Specification & Pilot Algorithms, Stage 5 Modeling Specification. | **Stage 5 Complete.** Formally specified 6-model ladder, causal HMM forward filtering, tuning, inference, and stop/go criteria in `stage5_modeling_specification.md`. Models remain unfitted; raw 2022–2023 option bundles unopened at Phase 2 (subsequent Stage 6 cash close breach recorded in commit `cee01a1`). |
| **Stage 6 / Gate B Audit** | 2010-2021 calendar scan (0.993% missing sessions <= 1.0%), early strike coverage audited (2010-2012 monthly gap vs mid-2012 weekly transition), quote timing audited (uniform 16:00 vendor string, cash synchronization unproven), rate conversion derived, batch candidate feature extraction generated for 2010-2021 (not permanently frozen). | **Gate B: Calendar Audit & Feature Construction Gate (Qualified Pass under User-Authorized Decisions).** Candidate feature datasets produced; operational datasets constructed under user-authorized Proposal A timing ($y_t \equiv \ln(S_{t+2}/S_{t+1})$). Model training authorized under User Decisions UD-1 through UD-5. Test breach through cash close access recorded in commit cee01a1 (exclusion rule pre-registered); raw 2022-2023 option bundles remained unopened during Stage 6. |
| **Phase 3 (Week 3) / Stage 7** | Implement and fit models B0-B4 and challenger R1 on development split (2010-2019, $N=2,231$ pairs); execute expanding walk-forward validation (2020-2021, $N=494$ complete-case rows); test mid-2012 sensitivity benchmark ($N=1,844$). | **Gate C: Baseline & Density Stability Gate (QUALIFIED PASS / PASSED WITH VALIDATION CAVEATS).** Fully validated density stability: zero NaN/Inf, $\sigma_t > 10^{-4}, \nu \ge 5.01 \ge 2.1$, numerical integrals equal 1.0000 (error $<6 \times 10^{-6}$). Closed-form Student-$t$ CRPS verified against numerical quadrature. Per-refit HMM diagnostics verified (dwell $\ge 5$ sessions, occupancy $\ge 5\%$ at all 25 refits). Selected $K=2, \lambda=0.01$. Paired DM test on Validation: $\bar{d} = +0.0056$ nats ($p = 0.235$, bootstrap CI includes zero; not statistically significant). In mid-2012 sensitivity benchmark, $\bar{d}$ shifted to $-0.0052$ nats ($p = 0.707$, bootstrap CI includes zero). Documented validation caveats: prequential walk-forward incorporates matured labels, validation informed tuning, PIT KS tests reject uniformity at 5%, sensitivity reversal is inconclusive, and MDN check is exploratory. Raw 2022–2023 option bundles remained unopened during Stage 7; test cash close access retained in commit `cee01a1`. |
| **Phase 4 (Week 4) / Stage 8** | Execute Gate D final held-out test evaluation on 2022–2023 partition across 24 expanding walk-forward refit blocks with frozen Stage 7 configuration (Proposal A target $y_t \equiv \ln(S_{t+2}/S_{t+1})$, complete-case filtering, $K=2$, $\lambda=0.01$). Audit 24 monthly option bundles, forward-fill 5 isolated missing sessions, evaluate primary Jan 3-origin-score-excluded prequential trajectory, strictly isolated sensitivity, full compromised test set, and actual-quote scoring subset; execute paired DM tests and stationary block bootstrap. | **Gate D: Final Evaluation & Novelty Integrity Gate (COMPLETE / EVALUATION INCONCLUSIVE — NO STATISTICALLY SIGNIFICANT R1 ADVANTAGE).** Evaluated across 24 expanding walk-forward refit blocks on held-out 2022–2023 test partition ($N=500$ primary sessions). R1 vs B4 mean differential: $\bar{d} = +0.0054$ nats/session ($\text{DM} = 1.4521$, $p_{\text{one-sided}} = 0.0732$, $p_{\text{two-sided}} = 0.1465$, bootstrap 95% CI $[-0.001979, +0.013837]$ includes zero and extends above practical threshold $+0.010$). Strict isolation sensitivity ($N=500$, excluding Jan 3 from scoring and training): $\bar{d} = +0.0055$ nats/session ($\text{DM} = 1.5118$, $p_{\text{one-sided}} = 0.0653$, bootstrap 95% CI $[-0.002074, +0.013873]$ includes zero). Full test set ($N=501$, secondary): $\bar{d} = +0.0073$ ($p_{\text{two-sided}} = 0.0682$, CI includes zero). Actual-quote scoring subset ($N=495$): $\bar{d} = +0.0054$ ($p = 0.0751$, CI includes zero). All 5 isolated option gaps causally forward-filled; zero multi-session gaps. Raw 2022–2023 option bundles processed; 2024 cash closes truncated to 2024-01-03 to mature year-end labels; historical cash-close breach acknowledged. |
| **Final Days / Stage 9** | Prepare final research package: submission-ready research report, presentation slides, reproducibility guide, and complete documentation reconciliation. No retuning, refitting, or claims of statistical significance. | **Stage 9 Complete.** Final research package delivered: `final_research_report.md`, `final_presentation.md`, `reproducibility_guide.md`, and top-level `README.md`. Empirical conclusion: R1 gain over B4 is statistically inconclusive; baseline B4 preferred on parsimony. |

Parallel activities: data access request and literature search happen in week 1; implementation cannot assume either is resolved. Reserve final test dates before model iteration where possible.

## 11. Proposed repository layout and artifacts

```text
project/
  implementation.md
  README.md
  config/                 # frozen dates, horizons, thresholds, model settings
  data/                   # source data excluded from version control unless permitted
    raw/                   # immutable licensed/source files
    interim/               # normalized chains, aligned prices
    processed/             # features/labels and split IDs
  notebooks/              # exploration only; never the sole pipeline
  src/
    ingest/                # parsers and schema validation
    options/               # cleaning, forward/surface fit, Q summaries
    features/              # lagged X and targets
    models/                # baselines, HMM filter, density estimators
    evaluation/            # rolling splits, scoring, inference, plots
    portfolio/             # optional constrained cash/index simulation
  reports/                 # audit, results, final figures
  environment.yml or requirements.txt
```

Required outputs: source/data manifest; cleaning and coverage report; frozen configuration; date-level forecasts from each model; feature table with availability timestamps; filtered regime probabilities; model parameters/refit dates; density calibration plots; paired loss table with uncertainty; portfolio returns/cost/turnover only if run; final run instructions. Do not commit licensed market data or credentials.

## 12. Risks, mitigations and stop conditions

| Risk | Mitigation / decision |
|---|---|
| No permitted historical option-chain access | Stop before model work; test institutional access; pivot market/data only after confirming fields and rights. |
| EOD closing prices too noisy for a stable Q-density | Use surface summary features and quality screens; do not claim a recovered density; seek bid/ask or use an authorized vendor. |
| Too few observations/stress states | Reduce complexity; report pilot evidence and wide uncertainty; do not claim a regime improvement. |
| Regime component is just current volatility | Compare with matched volatility/state controls and observable threshold segmentation. |
| HMM unstable across refits | Report state instability; simplify to observed-state conditioning; revise research question. |
| (Q)-features do not help predict (P) | A valid negative result; investigate data quality/calibration, do not tune on final test. |
| Density estimator overfits | Use low-capacity Student-t/quantile baseline; regularize, validate chronologically and report calibration. |
| Portfolio optimizer magnifies noisy mean estimates | Keep allocation secondary, bounded, cost-aware and risk-budgeted; avoid unconstrained Markowitz. |
| Novelty is weaker than expected | Frame as replication/extension and transparent incremental test; avoid priority claims. |

Stop or re-scope at Gate A if lawful, usable chain data cannot be obtained. Stop the *regime claim* if state probabilities are unstable or do not add held-out density value. Neither null outcome means the implementation failed; it answers the question.

## 13. Expected project claim (conditional template)

The eventual conclusion should take this form, not be assumed in advance:

> Historical template: On [market/source/sample/horizon], adding filtered latent-state probabilities to [specified option and historical feature set] [did/did not] improve next-day physical-density forecasts over [specified non-regime baseline], measured by [pre-specified log score] on [held-out test dates], with [calibration and uncertainty results].
>
> **Final Realized Finding (Stage 8 / Gate D, 24 October 2026):** On the S&P 500 index using OptionsDX EOD chains (2010–2023), adding causally filtered latent-state probabilities ($\pi_t$) to option-implied and historical market features did **not** demonstrate a statistically significant out-of-sample physical density improvement over the primary non-regime baseline ($B4$) on the held-out 2022–2023 test partition ($\bar{d} = +0.0054$ nats/session, $p = 0.0732$ one-sided, $p = 0.1465$ two-sided; stationary block bootstrap 95% CI $[-0.00198, +0.01384]$ spans zero and extends beyond the $+0.010$ practical threshold). Under pre-registered decision rules, baseline $B4$ is favored on grounds of econometric parsimony. No portfolio or investment-performance claims are made.

The project does not establish that risk-neutral moments equal physical moments, that an HMM identifies economically unique regimes, or that backtest gains persist live.

## 14. Decisions to resolve at project kickoff

1. Which licensed data source can actually export a complete historical index option chain, and what are its reuse restrictions?
2. Choose India/NIFTY versus US index only after sample-export comparison.
3. Confirm daily close timestamps and whether quote-level bid/ask is included.
4. Freeze next-day close-to-close return as the primary horizon unless data timing requires an explicit shift.
5. Confirm course deadline, team size and available compute; shrink model capacity before expanding scope.
6. Decide whether portfolio translation is required by the course rubric; if required, use the cash/index experiment above.

## 15. Research references and data sources

### Papers supplied in this folder

1. DeMiguel, V., Plyakha, Y., Uppal, R., & Vilkov, G. *Improving Portfolio Selection Using Option-Implied Volatility and Skewness*. SSRN manuscript in `Papers/ssrn_id2085587_code417015.pdf`.
2. Bianchi, M. L., & Tassinari, G. L. *Forward-looking Portfolio Selection with Multivariate Non-Gaussian Models and the Esscher Transform*. arXiv:1805.05584, supplied as `Papers/1805.05584.pdf`.
3. Chernov, M., & Ghysels, E. (2000). *A Study Towards a Unified Approach to the Joint Estimation of Objective and Risk Neutral Measures for the Purpose of Options Valuation*. Journal of Financial Economics, 56, 407–458. Supplied as `Papers/main.pdf`.
4. Bali, T. G., Beckmeyer, H., Mörke, M., & Weigert, F. (2023). *Option Return Predictability with Machine Learning and Big Data*. Review of Financial Studies, 36(9), 3548–3602. Supplied as `Papers/hhad017.pdf`.
5. Ulrich, M., Walther, S., Rothfuss, J., & Ferreira, F. (2019). *Forward-looking P*. Supplied as `Papers/ssrn_id3437281_code3012080.pdf`.

### Data references checked for this plan (21 October 2026)

- NSE India, [Historical Reports](https://www.nseindia.com/static/resources/historical-reports-capital-market-daily-monthly-archives): lists public equity-derivatives contract-wise price/volume and daily/monthly F&O archives. The [contract-wise report interface](https://www.nseindia.com/report-detail/fo_eq_security) offers date-range filters and CSV download. NSE's [EOD report specification](https://archives.nseindia.com/content/press/EOD_CM_n_FAO.pdf) lists option OHLC, OI, traded quantity/contracts/trades, expiry and strike, but no bid/ask.
- OptionsDX, [SPX Option Chains](https://www.optionsdx.com/product/spx-option-chain/): advertises 2010–2023 monthly CSV bundles and end-of-day frequency; its [field definitions](https://www.optionsdx.com/option-chain-field-definitions/) list quote time, underlying, expiration, strike, bid/ask, IV and Greeks. The page shows $0–$50 variant pricing; verify selected year/frequency in the cart. Its [terms](https://www.optionsdx.com/terms/) state digital-content sales are final but do not provide a clear research redistribution grant; do not redistribute source files.
- Cboe DataShop, [Option EOD Summary](https://datashop.cboe.com/option-eod-summary): lists NBBO quote snapshots, OHLC, volume and OI with optional IV/Greeks. The [MDR Quotes & Trades product](https://datashop.cboe.com/mdr-quotes-trades-data) describes SPX history from January 1990. These are commercial products, not free public datasets.

- NSE India, [Paid End of Day / Historical Data](https://www.nseindia.com/static/market-data/eod-historical-data-subscription): describes EOD bhavcopy and historical order/trade data for F&O, delivery channels and contact for subscription. Confirm applicable current terms, fees and fields directly with NSE/institution before use.
- NSE India, [Derivatives reports](https://www.nseindia.com/all-reports-derivatives): lists current report families including F&O bhavcopy and UDiFF common bhavcopy; legacy bhavcopy format was discontinued from 8 July 2024, so parser design must use the correct format for each historical era.
- LSEG, [Workspace for Equities](https://www.lseg.com/en/data-analytics/products/workspace/equities): product page lists historical analysis tools including option/surface volatility functions, but does not establish IIT Bombay entitlement or historical contract-level export coverage. Verify locally.

