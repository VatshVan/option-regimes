# Benchmarks and Forecast-Evaluation Methods Referees Expect for Daily S&P 500 Density / Risk Forecasts

Source-quality note: items marked **[verified]** had their bibliographic details (authors, year, venue, volume/pages) confirmed this session from a publisher, RePEc/EconPapers, journal-society, or library record. Items marked **[KB]** are standard references whose details come from the researcher's background knowledge. Their DOI links are given but were **not** fetched this session, so a report writer should check them before quoting volume/page numbers. No empirical magnitudes are reported unless a source stated them.

---

## 1. Benchmark models: which ones are hardest to beat for one-day SPX density/VaR, what option-implied variables add, and what works with daily closes only

### Takeaway
The minimum benchmark set a referee will expect is (a) GARCH(1,1) and an asymmetric GARCH (GJR or EGARCH) with Student-t or skew-t innovations, (b) filtered historical simulation (FHS), and (c) a GARCH-X/GJR-X that adds lagged VIX. All of these need only daily closes plus the daily VIX close. For equity indices, the leverage effect matters: plain GARCH(1,1) is clearly beaten by asymmetric models on equity data. Realized-measure models (HAR-RV, Realized GARCH, HEAVY) are the strongest variance benchmarks, but they need intraday data. Older S&P 100 studies (Blair-Poon-Taylor 2001) found that VIX carries most of the forecast-relevant information, even compared with 5-minute returns.

### Cited Findings
- **Hansen & Lunde (2005), "A forecast comparison of volatility models: does anything beat a GARCH(1,1)?", J. Applied Econometrics 20(7):873-889 [verified].** The study compares 330 ARCH-type models out-of-sample using the SPA test and White's reality check. For DM-$ exchange rates, nothing beats GARCH(1,1). For IBM equity returns, GARCH(1,1) is "clearly inferior to models that can accommodate a leverage effect". The reality check had too little power to separate good from bad models. Replication data are on the ZBW journal data archive. — [EconPapers](https://econpapers.repec.org/RePEc:jae:japmet:v:20:y:2005:i:7:p:873-889); [PDF copy](https://www.bauer.uh.edu/rsusmel/phd/HansenLunde_Garch.pdf); [R replication vignette (forecastdom)](https://archive.linux.duke.edu/cran/web/packages/forecastdom/vignettes/hl2005-spa-garch.html)
- **GJR-GARCH: Glosten, Jagannathan & Runkle (1993), J. Finance 48(5):1779-1801 [KB]** — [DOI](https://doi.org/10.1111/j.1540-6261.1993.tb05128.x)
- **EGARCH: Nelson (1991), Econometrica 59(2):347-370 [KB]** — [DOI](https://doi.org/10.2307/2938260)
- **Kuester, Mittnik & Paolella (2006), "Value-at-Risk Prediction: A Comparison of Alternative Strategies", J. Financial Econometrics 4(1):53-89 [verified].** The data are more than 30 years of daily NASDAQ Composite returns. "Most approaches perform inadequately." The best overall method is a heavy-tailed GARCH filter combined with EVT, "closely followed by a variant on a filtered historical simulation" and a heteroskedastic mixture model. CAViaR models performed poorly overall, though one extension beat the other CAViaR variants. — [EconPapers](https://econpapers.repec.org/RePEc:oup:jfinec:v:4:y:2006:i:1:p:53-89); [IDEAS](https://ideas.repec.org/a/oup/jfinec/v4y2006i1p53-89.html)
- **HAR-RV: Corsi (2009), "A Simple Approximate Long-Memory Model of Realized Volatility", J. Financial Econometrics 7(2):174-196, DOI 10.1093/jjfinec/nbp001 [verified].** The model is an additive cascade of daily, weekly and monthly RV components, which gives an AR-type model. It reproduces long memory, fat tails and self-similarity, and it reports good forecasting performance. — [EconPapers](https://econpapers.repec.org/RePEc:oup:jfinec:v:7:y:2009:i:2:p:174-196); [SSRN](https://papers.ssrn.com/abstract=1365738); [PDF copy](https://statmath.wu.ac.at/~hauser/LVs/FinEtricsQF/References/Corsi2009JFinEtrics_LMmodelRealizedVola.pdf)
- **Realized GARCH: Hansen, Huang & Shek (2012), J. Applied Econometrics 27(6):877-906, DOI 10.1002/jae.1234 [verified].** It was first online in March 2011, so some indexes list it as 2011. It adds a measurement equation linking the realized measure to the conditional variance. — [CREATES working paper](https://repec.econ.au.dk/repec/creates/rp/10/rp10_13.pdf); [record](https://zendy.io/title/10.1002/jae.1234)
- **HEAVY: Shephard & Sheppard (2010), "Realising the future: forecasting with high-frequency-based volatility (HEAVY) models", J. Applied Econometrics 25(2):197-231, DOI 10.1002/jae.1158 [verified].** — [EconPapers](https://econpapers.repec.org/RePEc:jae:japmet:v:25:y:2010:i:2:p:197-231)
- **Koopman, Jungbacker & Hol (2005), "Forecasting daily variability of the S&P 100 stock index using historical, realised and implied volatility measurements", J. Empirical Finance 12(3):445-475 [verified].** The sample is S&P 100, January 1997 to November 2003 (1,725 trading days). The study compares GARCH, SV, and RV models, and GARCH/SV extended with RV and implied-volatility regressors, using SPA tests with a stationary bootstrap. The headline finding is that RV models give "considerably more accurate" forecasts than daily-return models. I could not confirm the implied-volatility-specific results from the abstract. — [Tinbergen WP PDF](https://papers.tinbergen.nl/04016.pdf); [EconBiz](https://www.econbiz.de/Record/forecasting-daily-variability-of-the-s-p-100-stock-index-using-historical-realised-and-implied-volatility-measurements/10005537649)
- **Martens, van Dijk & de Pooter (2009), "Forecasting S&P 500 volatility: Long memory, level shifts, leverage effects, day-of-the-week seasonality, and macroeconomic announcements", Int. J. Forecasting 25(2):282-303 [verified].** The data are daily RV of S&P 500 futures. Modelling long memory, level shifts, leverage, day-of-week effects and announcements improves out-of-sample accuracy up to 20 days ahead. A high-order AR approximation beats ARFIMA, especially at long horizons. Note: the abstract does **not** frame this as a VIX/implied-vol paper. If the project cites it as "HAR-X with VIX", check the full text first. — [EconPapers](https://econpapers.repec.org/RePEc:eee:intfor:v:25:y:2009:i:2:p:282-303); [EUR repository](https://repub.eur.nl/pub/18152)
- **Blair, Poon & Taylor (2001), "Forecasting S&P 100 volatility: the incremental information content of implied volatilities and high-frequency index returns", J. Econometrics 105(1):5-26 [verified].** The study uses ARCH models with daily returns, daily VIX and 5-minute squared returns. In-sample, VIX carries almost all relevant information. Out-of-sample, VIX gave the most accurate forecasts at 1-20 day horizons, and intraday returns added nothing statistically significant. — [EconPapers](https://econpapers.repec.org/RePEc:eee:econom:v:105:y:2001:i:1:p:5-26); [Lancaster eprints](https://eprints.lancs.ac.uk/id/eprint/43424)
- **Patton, Ziegel & Chen (2019), "Dynamic semiparametric models for expected shortfall (and Value-at-Risk)", J. Econometrics 211(2):388-413 [verified].** The ES-VaR models built on Fissler-Ziegel joint elicitability outperform GARCH and rolling-window forecasts on four international equity indices. These GAS-type models are a newer, credible benchmark for VaR/ES. — [EconPapers](https://econpapers.repec.org/RePEc:eee:econom:v:211:y:2019:i:2:p:388-413); [arXiv 1707.05108](https://arxiv.org/abs/1707.05108v1)

### Inferences
- **Implementable with daily closes only:** GARCH(1,1), GJR, EGARCH (Normal, Student-t, Hansen skew-t), FHS (GARCH filter plus bootstrap of standardized residuals), GARCH-X/GJR-X with lagged log VIX or VIX^2/252 as a variance regressor, EWMA/RiskMetrics, historical simulation, and Patton-Ziegel-Chen GAS ES-VaR models. HAR-RV, Realized GARCH and HEAVY need a realized measure. A daily-data substitute is a range-based estimator (Parkinson / Garman-Klass) from daily OHLC, or a "HAR on squared returns / VIX^2" variant. These are proxies, and a referee will know they are noisier than 5-minute RV.
- **Hardest to beat for a 1-day SPX density** (synthesising the sources above): an asymmetric GARCH (GJR/EGARCH) with fat-tailed or skewed innovations, and FHS on the same filter. If option data are used, a GJR-X with VIX is the natural "fair" benchmark. Blair-Poon-Taylor suggests VIX alone is already very informative, so a new option-implied method must beat GARCH-X-VIX, not just plain GARCH.
- **How much option-implied variables add on top of these:** the sources found here give direction but no consensus magnitude for 1-day density scores. For variance forecasts, VIX adds a lot over daily-return GARCH (BPT 2001). Its added value over RV models is mixed in the literature, and the KJH 2005 abstract favours RV models.
- **Python:** `arch` (`arch_model(..., vol='GARCH', p=1, o=1, q=1, dist='skewt')` gives GJR; `vol='EGARCH'`; an exogenous regressor in the variance equation is not natively supported in all versions, so GARCH-X may need a custom `minimize` likelihood). `arch` forecast with `method='bootstrap'` gives an FHS-style simulation. For HAR, use `statsmodels` OLS with HAC standard errors.

### Gaps
- No source found that gives a quantitative consensus (for example, the percent log-score gain) for adding VIX to GJR-t for 1-day SPX densities. Do not quote a number.
- The Oxford-Man Realized Library was the usual free source of SPX 5-minute RV. To the researcher's knowledge it stopped updating in 2022, but this was **not verified** this session. Check before planning HAR/Realized-GARCH benchmarks.
- I did not verify that the `arch` package version in use supports exogenous variance regressors.

---

## 2. Scoring rules for density and tail/quantile forecasts

### Takeaway
Report the log score and CRPS as headline proper scores. Add tail-focused proper scores (censored likelihood from Diks-Panchenko-van Dijk, threshold-weighted CRPS from Gneiting-Ranjan) and the quantile (pinball) loss and Fissler-Ziegel joint VaR-ES loss at the 1% and 5% levels. Do not use the unweighted "weighted likelihood" score of Amisano-Giacomini for tail comparisons, because DPvD and Gneiting-Ranjan show it can be hedged or biased toward forecasts with more mass in the region.

### Cited Findings
- **Gneiting & Raftery (2007), "Strictly proper scoring rules, prediction, and estimation", JASA 102(477):359-378 [KB].** The canonical reference for propriety, log score and CRPS. — [DOI](https://doi.org/10.1198/016214506000001437)
- **Gneiting & Ranjan (2011), "Comparing density forecasts using threshold- and quantile-weighted scoring rules", JBES 29(3):411-422 [verified].** Proposes weighted CRPS (threshold- or quantile-weighted) to focus on tails or the centre. Unlike the weighted likelihood-ratio test, which can be hedged, it stays proper. — [EconPapers](https://econpapers.repec.org/RePEc:taf:jnlbes:v:29:y:2011:i:3:p:411-422)
- **Diks, Panchenko & van Dijk (2011), "Likelihood-based scoring rules for comparing density forecasts in tails", J. Econometrics 163(2):215-230 [verified].** Existing weighted-likelihood scores favour forecasts with more mass in the region of interest. The paper proposes proper conditional-likelihood and censored-likelihood scores. The working paper illustrates them on **daily S&P 500 returns**, and censored likelihood performed better in all cases considered. — [EconPapers](https://econpapers.repec.org/RePEc:eee:econom:v:163:y:2011:i:2:p:215-230); [WP PDF](https://repub.eur.nl/pub/13975/2008-0504.pdf)
- **Fissler & Ziegel (2016), "Higher order elicitability and Osband's principle", Annals of Statistics 44(4):1680-1707 [KB].** (VaR, ES) is jointly elicitable. — [DOI](https://doi.org/10.1214/16-AOS1439); see also [Fissler, Ziegel & Gneiting, "Expected Shortfall is jointly elicitable with VaR - implications for backtesting" (arXiv 1507.00244)](https://ar5iv.arxiv.org/html/1507.00244)
- **Patton, Ziegel & Chen (2019)** use the "FZ0" member of the Fissler-Ziegel family as their loss for ES-VaR forecasting [verified as published, see Section 1; the FZ0 naming is KB]. — [arXiv](https://arxiv.org/abs/1707.05108v1)
- **Python `scoringrules`:** a port of the R `scoringRules` package. It has closed-form CRPS and log score for many parametric families, plus threshold-weighted CRPS (`twcrps_ensemble`, using a chaining function for weighting such as [t, inf)). I did not find a weighted log score or censored-likelihood score in the Python API. The R package does have weighted log-score versions. — [scoringrules docs](https://scoringrules.readthedocs.io/en/latest/); [API reference](https://scoringrules.readthedocs.io/en/latest/reference.html); [twcrps_ensemble](https://scoringrules.readthedocs.io/en/latest/generated/scoringrules.twcrps_ensemble.html); [Allen et al. arXiv 2305.07312](https://arxiv.org/pdf/2305.07312v1)

### Inferences
- The censored-likelihood score for a left-tail region A = {y < r} is easy to code by hand. Score log f(y) if y is in A, and log(1 - F(r)) otherwise. Choose r from a fixed in-sample quantile, such as the in-sample 5% or 10% return quantile, **declared in advance**.
- `properscoring` (older package) also offers `crps_gaussian` and `crps_ensemble` [KB, not verified this session]. Prefer `scoringrules`.
- Pinball loss and FZ0 loss take a few lines of NumPy each.

### Gaps
- I did not verify a Python implementation of the censored-likelihood score. Assume it must be hand-coded.

---

## 3. Inference: pairwise and multiple-model tests, nesting, and data snooping

### Takeaway
For pairwise score differences, use Diebold-Mariano with HAC errors, interpreted under Giacomini-White (2006). With a **rolling** (fixed-length) estimation window, GW's conditional and unconditional tests are valid even for nested models, because they test the forecasting *method* including estimation error. With expanding windows and nested models, DM/GW asymptotics can fail, and for MSE comparisons Clark-West is the usual fix. For many models or variants, report Hansen's SPA and the Model Confidence Set, and use Romano-Wolf StepM where several "improvements" are tested at once. All three are in `arch.bootstrap`.

### Cited Findings
- **Diebold & Mariano (1995), "Comparing predictive accuracy", JBES 13(3):253-263 [KB].** — [DOI](https://doi.org/10.1080/07350015.1995.10524599)
- **Giacomini & White (2006), "Tests of Conditional Predictive Ability", Econometrica 74(6):1545-1578 [verified].** An out-of-sample framework valid under misspecification. It accounts for estimation uncertainty, handles nested and non-nested models, and allows conditioning on current information (conditional predictive ability). — [Econometric Society](https://econometricsociety.org/publications/econometrica/2006/11/01/tests-conditional-predictive-ability); [EconPapers](https://econpapers.repec.org/RePEc:ecm:emetrp:v:74:y:2006:i:6:p:1545-1578)
- **Amisano & Giacomini (2007), "Comparing density forecasts via weighted likelihood ratio tests", JBES 25(2):177-190 [KB for details].** A Bank of Canada summary describes it as a likelihood-ratio test on log predictive scores that uses GW asymptotics. — [Bank of Canada slides](https://www.bankofcanada.ca/wp-content/uploads/2010/09/clark.pdf); [DOI](https://doi.org/10.1198/073500106000000332)
- **Clark & West (2007), "Approximately normal tests for equal predictive accuracy in nested models", J. Econometrics 138(1):291-311 [verified].** The adjusted MSE difference corrects for estimation noise in the larger model under the null, and N(0,1) critical values approximate the true ones reasonably well. It has become the norm for nested out-of-sample comparisons. Note: it is designed for MSE/point forecasts, not log scores. — [EconPapers](https://econpapers.repec.org/RePEc:eee:econom:v:138:y:2007:i:1:p:291-311); [NBER WP](https://www.nber.org/papers/t0326); [Bank of Canada slides](https://www.bankofcanada.ca/wp-content/uploads/2010/09/clark.pdf)
- **White (2000), "A reality check for data snooping", Econometrica 68(5):1097-1126 [KB for pages; reference listed in arch docs]**; **Hansen (2005), "A test for superior predictive ability", JBES 23(4) [verified via arch docs]**; **Romano & Wolf (2005), "Stepwise multiple testing as formalized data snooping", Econometrica 73(4):1237-1282 [verified via arch docs]**; **Hansen, Lunde & Nason (2011), "The model confidence set", Econometrica 79(2):453-497 [verified via arch docs].** `arch` implements SPA, StepM and MCS as bootstrap multiple-comparison procedures controlling the family-wise error rate. — [arch docs: background & references](https://arch.readthedocs.io/en/latest/multiple-comparison/background.html); [arch multiple comparisons](https://arch.readthedocs.io/en/latest/multiple-comparison/multiple-comparisons.html)
- Hansen & Lunde (2005) found that White's reality check lacks power relative to SPA in their volatility application. — [EconPapers](https://econpapers.repec.org/RePEc:jae:japmet:v:20:y:2005:i:7:p:873-889)

### Inferences
- For a project with one proposed model and several ablations or variants, the cleanest design is: (i) pairwise DM/GW on log score, CRPS, censored-likelihood and FZ0 loss against the strongest benchmark, with Newey-West HAC errors; (ii) MCS at 75% or 90% over all models, per loss; (iii) if many variants of "our method" were tried, a StepM or SPA test with the best benchmark as the reference, which addresses data snooping.
- Use a **rolling** estimation window if you want GW validity for nested comparisons, such as GJR-t vs GJR-t + VIX. Otherwise state the expanding-window caveat.
- Small samples: with about 250-1,000 out-of-sample days, tail-score differences (1% VaR has about 2.5-10 hits) will have low power. Report this honestly rather than over-interpreting point estimates. Small-sample corrections such as Harvey-Leybourne-Newbold (1997) for DM [KB] are cheap to add.
- Class names in `arch.bootstrap` (KB, check in the installed version): `SPA`, `StepM`, `MCS`.

### Gaps
- I did not fetch Python implementations of the GW conditional test or Clark-West. Both are short regressions in `statsmodels`, with an HAC t-test or Wald test.

---

## 4. Calibration diagnostics: PIT tests and VaR/ES backtests

### Takeaway
Report a PIT histogram plus formal tests. Berkowitz (2001) is the likelihood-ratio test on inverse-normal PITs, covering both uniformity and independence. Knüppel (2015) gives raw-moment tests robust to serial dependence. Rossi-Sekhposyan (2019) gives KS/CvM-type tests that account for parameter estimation. For VaR at 1% and 5%, report Kupiec unconditional coverage, Christoffersen independence and conditional coverage, and the Engle-Manganelli dynamic quantile test. For ES, use an Acerbi-Szekely test or a test based on the FZ loss.

### Cited Findings
- **Diebold, Gunther & Tay (1998), "Evaluating density forecasts with applications to financial risk management", Int. Economic Review 39(4):863-883 [KB].** — [DOI](https://doi.org/10.2307/2527342)
- **Berkowitz (2001), "Testing density forecasts, with applications to risk management", JBES 19(4):465-474 [KB].** — [DOI](https://doi.org/10.1198/07350010152596718)
- **Knüppel (2015), "Evaluating the calibration of multi-step-ahead density forecasts using raw moments", JBES 33(2):270-281, DOI 10.1080/07350015.2014.948175 [verified].** This handles serial correlation in PITs, for example from multi-step forecasts. The test uses standard critical values, includes the chosen moments, and has correct asymptotic size. It has good finite-sample size and power when based on standardized PITs. — [EconPapers](https://econpapers.repec.org/RePEc:taf:jnlbes:v:33:y:2015:i:2:p:270-281); [Bundesbank WP](https://bundesbank.de/resource/blob/703634/766e285ef812d86d49c02dd8033d7333/472B63F073F071307366337C94F8C870/2011-12-30-dkp-32-data.pdf)
- **Rossi & Sekhposyan (2019), "Alternative tests for correct specification of conditional predictive densities", J. Econometrics, DOI 10.1016/j.jeconom.2018.07.008 [verified; volume/issue not confirmed].** These are KS and CvM tests on PITs that evaluate the model and estimation technique jointly, at actual parameter estimates rather than pseudo-true values. They do not need dynamic correct specification. Monte Carlo shows good size and power. — [UPF WP](https://econ-papers.upf.edu/en/onepaper.php?id=1416); [GWU WP PDF](https://www2.gwu.edu/~forcpgm/RossiSekhposyan2014.pdf)
- **Kupiec (1995), J. Derivatives 3(2):73-84 [KB]** — [DOI](https://doi.org/10.3905/jod.1995.407942); **Christoffersen (1998), "Evaluating interval forecasts", Int. Economic Review 39(4):841-862 [KB]** — [DOI](https://doi.org/10.2307/2527341); **Engle & Manganelli (2004), "CAViaR", JBES 22(4):367-381 [KB]**, which introduces the dynamic quantile (DQ) test — [DOI](https://doi.org/10.1198/073500104000000370)
- **Acerbi & Szekely (2014), "Backtesting expected shortfall", Risk (December) [KB; not verified].** Secondary literature (Fissler-Ziegel-Gneiting) places it in the debate over whether and how ES can be backtested. — [arXiv 1507.00244](https://ar5iv.arxiv.org/html/1507.00244)

### Inferences
- With 1-day horizons, PIT serial dependence comes mainly from misspecification, not from overlapping horizons. Still, testing the independence of PIT, PIT^2 and |PIT-0.5| (Ljung-Box) is cheap and expected.
- Everything here is a few lines in NumPy/SciPy/`statsmodels` (DQ = OLS of hit sequence on its lags and the VaR forecast, chi-square Wald test).

### Gaps
- I found no maintained Python package bundling Kupiec, Christoffersen, DQ and Acerbi-Szekely that I could verify this session. Plan to hand-code them.

---

## 5. Economic-value evaluation

### Takeaway
The standard economic-value test is the Fleming-Kirby-Ostdiek (2001) volatility-timing framework. It compares a mean-variance (or volatility-target) investor's realized utility under each model's variance forecast and reports the fee (basis points per year) the investor would pay to switch models, along with certainty-equivalent returns.

### Cited Findings
- **Fleming, Kirby & Ostdiek (2001), "The Economic Value of Volatility Timing", J. Finance 56(1):329-352 [verified].** Uses conditional mean-variance analysis for short-horizon investors. Volatility-timing strategies outperform unconditionally efficient static portfolios with the same target return and volatility, and the result is robust to estimation risk and transaction costs. Their 2003 J. Financial Economics follow-up uses realized volatility. — [EconPapers](https://econpapers.repec.org/RePEc:bla:jfinan:v:56:y:2001:i:1:p:329-352); [Fleming CV](https://business.rice.edu/sites/default/files/uploads/cv/Fleming_CV-2_2.pdf)

### Inferences
- For a single-index SPX project: build a volatility-target portfolio (SPX vs. T-bill) with weight w_t = target_vol / sigma_hat_t, capped. Report realized Sharpe ratio, the volatility of realized portfolio volatility, and FKO's performance fee under quadratic utility at relative risk aversion of 1 and 10. A VaR-based capital-charge comparison is a second option.

### Gaps
- No source fetched on certainty-equivalent formulas beyond FKO. These are standard but were not verified this session.

---

## 6. Out-of-sample design, pre-registration, and an already-observed test set

### Takeaway
Referees expect a fixed, pre-declared split (estimation, validation or tuning, test), rolling or expanding refits stated in advance, all model choices frozen before the test period is scored, and multiple-comparison corrections (SPA, StepM, MCS) for anything searched over. If the test set has already been looked at, it should be labelled honestly as pseudo-out-of-sample, and the strongest remedy is a fresh hold-out, such as data after the last observed date accumulated over the project.

### Cited Findings
- Hansen & Lunde (2005) and Koopman, Jungbacker & Hol (2005) both use bootstrap SPA tests for many-model comparisons, which is the field's de facto data-snooping control. — [HL 2005](https://econpapers.repec.org/RePEc:jae:japmet:v:20:y:2005:i:7:p:873-889); [KJH WP](https://papers.tinbergen.nl/04016.pdf)
- White (2000) and Romano & Wolf (2005) formalise data snooping. Both are implemented, or listed as references, in `arch.bootstrap`. — [arch docs](https://arch.readthedocs.io/en/latest/multiple-comparison/background.html)
- Review articles a referee may expect cited: **Gneiting & Katzfuss (2014), "Probabilistic forecasting", Annual Review of Statistics and Its Application 1:125-151 [KB]** — [DOI](https://doi.org/10.1146/annurev-statistics-062713-085831); **Corradi & Swanson (2006), "Predictive density evaluation", Handbook of Economic Forecasting Vol. 1, ch. 5 (Elsevier) [KB]** — [DOI](https://doi.org/10.1016/S1574-0706(05)01005-0)

### Inferences
- Practical protocol (fits the repository's existing "pre-declare then run" commit pattern): (1) commit the specification, loss list, thresholds, benchmark set and test list before scoring; (2) score the test set once; (3) present any post-hoc re-scoring as exploratory and label it clearly; (4) extend the sample with data released after the original test end date and report it as a genuine hold-out, even if it is short; (5) report every variant tried, not only the winner, and run StepM, SPA or MCS over them.
- With only a few weeks, prioritise: GJR-skew-t, GJR-t-X(VIX), FHS, and the proposed model. Score with log score, CRPS, censored-likelihood at the 5% left tail, and FZ0 at 2.5%/5%. Run DM/GW against the best benchmark, MCS, Berkowitz/Knüppel PIT tests, Kupiec, Christoffersen and DQ tests, and the FKO fee.

### Gaps
- I found no econometrics-specific source in this session that formally prescribes pre-registration for forecasting studies. The advice above is synthesis, not a cited standard.
- Patton (2011, J. Econometrics, "Volatility forecast comparison using imperfect volatility proxies") [KB, not verified] is relevant when variance forecasts are scored against squared daily returns: only some loss functions (MSE, QLIKE) stay robust to proxy noise. Check before citing.
