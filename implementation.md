# Implementation Plan

## Regime-conditioned physical return density forecasts from option-implied information

**Document status:** Research and implementation specification; project not yet started; data-source and local-sample audit updated 21 October 2026  
**Course scope:** IE 612, one-month empirical project  
**Decision status:** Feasible as a focused single-index forecasting study if SPX EOD files from OptionsDX pass sample and licensing checks. Free NIFTY files appear available with contract-level EOD OHLC/OI/volume, but lack the bid/ask data preferred for risk-neutral surface construction. The broad multi-stock portfolio version is not implementation-ready.

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

- **H1 (primary):** The regime-augmented model has lower mean out-of-sample log loss than the strongest non-regime model on the untouched test period.
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

### 7.1 Baselines

- **B0 Historical unconditional:** training-window empirical return density or simple Gaussian with rolling mean/scale.
- **B1 Volatility baseline:** conditional location/scale model using trailing realized volatility (e.g. Student-t location-scale or quantile model).
- **B2 Q-only:** small distribution model using option features only.
- **B3 X-only:** same class using historical features only.
- **B4 Combined non-regime (primary comparator):** (Q_t+X_t) to a compact conditional density model. Start with a Student-t location/scale regression or quantile grid; use a small MDN only if its sample-size and numerical behavior are adequate.

Keep estimator family, capacity and hyperparameter budget comparable for B4 and regime model. The role of B1–B3 is diagnosis, not to dilute the main comparison.

### 7.2 Regime estimation and regime model

Fit a small Gaussian HMM (start (K=2), validate (K=2,3)) on a pre-declared, low-dimensional state such as standardized lagged return and realized volatility. Fit within each training window only. At each forecast origin use **filtered** probabilities (\pi_{t,k}=P(z_t=k\mid\mathcal F_t)), generated forward using information through (t). Never use smoothed probabilities or full-sample state labels in a backtest.

First regime challenger (**R1**): append filtered probabilities and perhaps one interaction block to the same B4 density estimator. This tests state information while limiting model count. Optional **R2**: mixture of regime-specific predictive densities weighted by filtered probabilities; implement only if R1 is stable and time permits. Compare against a control with current observable volatility/state features, plus a regime-probability ablation/shuffle. If regime definitions change materially across rolling fits or probabilities collapse to one state, report that and drop the regime claim.

### 7.3 Density validity

All predictive densities must integrate to one, remain finite and positive at realized values, and respect parameter constraints (positive scales, simplex mixture weights). Use stable log-sum-exp, clipping only with a stated numerical floor. For quantile models enforce monotonic quantiles and clearly identify their evaluation as quantile rather than full-density evidence.

## 8. Evaluation design (leakage-resistant)

1. Sort observations chronologically. Define an initial training segment, a validation segment for model and hyperparameter choice, and a final untouched test segment. Do not randomly split.
2. If data permit, reserve the latest contiguous 20% as a final test; set exact dates from actual coverage and report them. Within the earlier development data use expanding-window validation or rolling-origin folds.
3. Fit imputation, scaling, feature selection, surface-derived transformations, HMM, and predictive model using only data available by each refit date. Choose refit cadence in advance (monthly is a reasonable MVP).
4. Next-day target does not overlap. If extending to multi-day targets, purge/embargo overlaps; use block/HAC inference.
5. Keep the final test out of feature selection, regime-count selection, architecture choice, cost tuning and strategy design. Freeze a dated specification before the test is scored.

### Forecast metrics

- **Primary:** average negative log predictive density (log loss) of realized next-day returns; paired per-date loss difference, B4 minus R1.
- **Secondary:** CRPS (for densities with reliable numerical integration), PIT histogram and uniformity diagnostics, 50/80/95% interval coverage and width, quantile/pinball loss, tail-event Brier/log scores for fixed thresholds.
- Report calibration and sharpness together. Lower NLL alone can reward overconfident tails if density numerics or data alignment are faulty.
- Compare paired forecast losses with a Diebold–Mariano-style test with suitable variance estimation. Add a moving/block bootstrap confidence interval as a robustness summary. State that many close, dependent daily observations reduce effective sample size.
- Pre-specify a practically meaningful threshold as well as statistical evidence; do not hunt across metrics for a favorable result.

### Portfolio translation (secondary only)

With one index, use a transparent risk-budget allocation: allocate between cash and the index based on forecast mean and a fixed volatility/tail-risk budget, with bounds such as 0–100% exposure, predetermined turnover cap and rebalancing cadence. Compare cash, buy-and-hold index, fixed-volatility targeting, and the forecast-driven rule. Include a realistic transaction-cost assumption sourced or declared as a range, turnover, drawdown, realized volatility, Sharpe and certainty-equivalent return. Show gross and net results and sensitivity to costs. No leveraged short exposure in MVP. If forecasts do not provide stable expected return estimates, omit mean-seeking allocation and use forecast risk only; disclose the simplification.

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

| Week | Work | Deliverable / gate |
|---|---|---|
| 1 (days 1–5) | Confirm data permission and obtain representative chain exports; resolve market/universe/horizon; refresh targeted literature search; write frozen protocol and feature dictionary. | **Gate A:** documented adequate data, licence, historical span, fields, and viable option surface. If not met by day 5, pivot to feasible data or redefine scope before coding. |
| 2 (days 6–12) | Ingest/normalize; align index returns and options; cleaning and quality report; construct the first surface/features and diagnostics. | **Gate B:** enough clean dates and repeatable surface diagnostics. Freeze a dataset snapshot and code version. |
| 3 (days 13–19) | Implement B0–B4; time splits, validation and primary metrics; assess density validity and calibration. | **Gate C:** B4 yields stable, valid forecasts on chronological validation. If not, simplify to Student-t/quantile forecast. |
| 4 (days 20–26) | Fit filtered HMM and R1; run core ablations and paired comparisons; finalize test specification; score untouched test once. | **Gate D:** report regime result, including null/negative findings; no retroactive model selection on test. |
| Final days (27–30) | Optional simple portfolio translation; charts, method limitations, reproducibility and report/presentation. | Complete reproducible submission with data citations and clear feasibility/novelty limits. |

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

> On [market/source/sample/horizon], adding filtered latent-state probabilities to [specified option and historical feature set] [did/did not] improve next-day physical-density forecasts over [specified non-regime baseline], measured by [pre-specified log score] on [untouched dates], with [calibration and uncertainty results]. Portfolio implications are [secondary finding] under [cost and constraint assumptions].

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

