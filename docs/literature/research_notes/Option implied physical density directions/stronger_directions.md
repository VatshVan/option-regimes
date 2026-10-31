# Which option-implied modelling directions give the strongest evidence for better S&P 500 physical density and risk forecasts

Scope note: about 15 searches and fetches. Most findings come from abstracts, repository records and bibliographic pages, not full texts, so effect sizes are given only where an abstract states them. Citations not confirmed by search are flagged.

## (a) Full risk-neutral density plus a measure change (pricing kernel / tilting) used as the physical density

### Takeaway
This is the most direct published test of "option-implied physical density". The main S&P 500 evidence (Lancaster group) says risk-transformed RNDs beat historical/ARCH densities at 2- and 4-week horizons but lose at the 1-day horizon, where historical densities win and mixtures do best. At a 1-day horizon this direction is unlikely to give a big standalone gain. It is promising when the horizon matches the option maturity and when the RND is combined with a historical density.

### Cited Findings
- Liu, Shackleton, Taylor & Xu (2007), *Journal of Banking & Finance* 31(5), 1501-1520: two parametric risk transformations turn RNDs (generalized beta and lognormal-mixture families) into real-world densities. Each is estimated by maximising the likelihood of observed index levels. They are compared with historical densities, and a combination of parametric real-world and historical densities gives the preferred predictive densities — [IDEAS/RePEc](https://ideas.repec.org/a/eee/jbfina/v31y2007i5p1501-1520.html); [Lancaster eprint](https://eprints.lancs.ac.uk/id/eprint/44582/)
- Shackleton, Taylor & Yu (2010), *Journal of Banking & Finance* 34(11), 2678-2693, S&P 500, 1991-2004: RNDs come from SV diffusion / jump-diffusion fits to options, then three transformations to real-world densities, compared with ARCH densities using daily and 5-minute returns. Ranked by out-of-sample likelihood, risk-transformed RNDs are best at the 2- and 4-week horizons, historical forecasts are better at 1 day, and mixtures of real-world and historical densities have higher likelihood than either component at short horizons — [Lancaster eprint](https://eprints.lancs.ac.uk/id/eprint/45542); [EconPapers](https://econpapers.repec.org/RePEc:eee:jbfina:v:34:y:2010:i:11:p:2678-2693)
- Beare & Dossani (2018), *Quantitative Finance* 18(4), 623-635 (journal and pages inferred from the RePEc handle in the search result, abstract not opened): they transform a historical baseline density forecast so that its ratio to the option RND (the pricing kernel) is monotone. This gives only a modest improvement in density-forecast calibration — [IDEAS/RePEc](https://ideas.repec.org/a/taf/quantf/v18y2018i4p623-635.html)
- Background: empirical S&P 500 pricing kernels are often U-shaped / locally increasing (the "pricing kernel puzzle"). Dalderop & Linton (2024 working paper, Cambridge) propose a local inverse-density-weighting kernel estimator and attribute the U-shape to heterogeneous beliefs about conditional volatility — [Cambridge Janeway WP](https://www.janeway.econ.cam.ac.uk/working-paper-pdfs/jiwp2405.pdf)
- Chang, Choi, Kim & Park (2025, SSRN 5632350, "Market Returns Dormant in Option Panels"): functional predictive regression on the whole S&P 500 option panel / risk-neutral density using functional principal components. Out-of-sample R² above 4% for *monthly* returns, as reported in a search snippet (the SSRN page returned 403, so this is not verified from the abstract) — [SSRN](https://papers.ssrn.com/abstract=5632350)
- Christoffersen, Jacobs & Chang (2013), "Forecasting with Option-Implied Information", *Handbook of Economic Forecasting* Vol. 2, ch. 10, pp. 581-656: survey of forecasting with implied volatility, skewness, kurtosis and densities, and of adjusting for risk premia to remove biases in forecasting regressions — [EconPapers](https://econpapers.repec.org/RePEc:eee:ecofch:2-581); [CREATES WP](https://repec.econ.au.dk/repec/creates/rp/11/rp11_46.pdf)

### Inferences
- The project's 1-day result (a small gain, mostly through scale) matches Shackleton-Taylor-Yu: at 1 day, recent realized variation dominates. A measure-change density is likely to help mainly at 5-21 day horizons. At 1 day, the most defensible design is a log-score-weighted mixture or pool of a tilted RND and the historical Student-t.
- An exponential-tilting / power-kernel transform with one or two parameters, estimated walk-forward by maximum likelihood, is cheap and close to Liu et al. (2007). The main pitfall is that a 30-day RND has to be rescaled to a 1-day density, which needs a term-structure or variance-scaling assumption. That step brings back the scale problem the project already has.
- Pitfalls: RND tails depend on extrapolation beyond quoted strikes, the pricing kernel is non-monotone, and a constant-parameter kernel cannot track a time-varying risk premium.

### Gaps
- No study was found that evaluates tilted RNDs at a 1-day horizon with log score *and* a scale-recalibrated historical benchmark.
- Effect sizes in nats from Shackleton-Taylor-Yu (2010) were not retrieved, since the full text was not opened.

## (b) Tail risk: VaR / ES with implied volatility, skew and tail measures

### Takeaway
The evidence is mixed but structured. Implied volatility gains *more* explanatory power deeper in the left tail when it is combined with time-series quantile models (Jeon & Taylor 2013). Used alone and without adjustment, IV-based VaR loses to GJR-GARCH because of the variance risk premium (Bams et al. 2017). Tail-specific option measures (Andersen-Fusari-Todorov) carry information that volatility does not span. Evaluating with joint VaR-ES scoring (Fissler-Ziegel / Patton-Ziegel-Chen) is the right tool, and the tails are where a combination model is most likely to show a gain that recalibrating scale does not remove.

### Cited Findings
- Jeon & Taylor (2013), *Journal of Forecasting* 32(1), 62-74, S&P 500 daily: add an implied-volatility-based quantile predictor as an extra regressor in CAViaR. Implied volatility has more explanatory power as the focus moves further into the left tail. The combined methods are comparable or superior to standard CAViaR and to IV-only quantiles — [Strathprints](https://strathprints.strath.ac.uk/39598/); [EconPapers](https://econpapers.repec.org/RePEc:wly:jforec:v:32:y:2013:i:1:p:62-74)
- Bams, Blanchard & Lehnert (2017), *International Journal of Forecasting* 33(4), 848-863, S&P 500 / DJIA / Nasdaq-100, about 20+ years of daily data: IV-based VaR cannot beat, and tends to be beaten by, GJR-GARCH VaR (LR tests, dynamic quantile test, loss function). They blame the non-linear, regime-changing volatility risk premium. VRP corrections reduce bias but do not overturn the result. They stress that volatility forecasting and quantile forecasting are different objectives — [IDEAS/RePEc](https://ideas.repec.org/a/eee/intfor/v33y2017i4p848-863.html); [OU research portal](https://research.ou.nl/en/publications/volatility-measures-and-value-at-risk/)
- Slim, Dahmene & Boughrara (2020), *Quarterly Review of Economics and Finance* 76, 22-37: in developed markets, adding the relative variance risk premium to GARCH "greatly enhances" one-day-ahead VaR for long positions. In emerging markets, standard GARCH is best. Results hold in distressed periods and for alternative VRP measures — [IDEAS/RePEc](https://ideas.repec.org/a/eee/quaeco/v76y2020icp22-37.html)
- Nossman & Vilhelmsson, *Journal of Risk* (year not confirmed), S&P 500 1990-2010: a nonparametric VIX-based forward-looking VaR compares favourably with GARCH-type models, with roughly 40% higher (MCR, metric not defined in the snippet) before the financial crisis — [Risk.net](https://www.risk.net/journal-risk/2340057/nonparametric-forward-looking-value-risk)
- Andersen, Fusari & Todorov (2015), "The Risk Premia Embedded in Index Options", *JFE* 117(3), 558-584: the left tail of the S&P 500 risk-neutral distribution has a separate tail factor that volatility does not span. It helps predict future equity and variance risk premia — [EconPapers](https://econpapers.repec.org/RePEc:eee:jfinec:v:117:y:2015:i:3:p:558-584)
- Patton, Ziegel & Chen (2019), *Journal of Econometrics* 211(2), 388-413: dynamic semiparametric joint VaR-ES models based on the Fissler-Ziegel joint elicitability result. On four international equity indices they beat GARCH and rolling-window forecasts — [EconPapers](https://econpapers.repec.org/RePEc:eee:econom:v:211:y:2019:i:2:p:388-413); [arXiv 1707.05108](https://arxiv.org/abs/1707.05108v1)

### Inferences
- "Is the advantage larger in the tails?" Jeon & Taylor's left-tail result says yes, *conditionally* on combining with historical information. Bams et al. say no for IV used alone. The project's Student-t with constant nu cannot express a tail-specific gain. A quantile / joint VaR-ES regression (for example a Patton-Ziegel-Chen style model with VIX, BKM skewness or a left-tail measure as covariates), evaluated by the FZ0 loss, is a direct and cheap test.
- Mechanism: options price crash risk that has not yet shown up in realized returns. That information is about the shape of the left tail, not about the centre.
- Pitfall: at 1% / 2.5% levels a 2-year validation window (about 500 days) has only about 5-12 exceedances, so the tests will have low power. A longer sample is needed.

### Gaps
- Giot (2005), Chong, Kim & Lee and Barone-Adesi et al. were not verified in this search budget. The Bollerslev-Todorov tail index papers and Andersen-Fusari-Todorov "left tail variation" (JFE 2020) were also not verified separately.
- No out-of-sample S&P 500 study scoring ES from option-implied measures with FZ loss was found.

## (c) Horizon matching and short-dated options (weeklies, 0DTE, VIX1D)

### Takeaway
There is strong, consistent evidence that option information matters more when the option maturity matches the forecast horizon. 30-day options lose to historical models at 1 day (Shackleton-Taylor-Yu 2010), while 1-day implied volatility (VIX1D) gives competitive or better 1-day volatility forecasts once the risk premium is adjusted for. Of all the options here, using matched-maturity information is probably the single highest-value change for a 1-day density model.

### Cited Findings
- Shackleton, Taylor & Yu (2010): option-based densities win at 2 and 4 weeks, historical densities win at 1 day (S&P 500, 1991-2004) — [Lancaster eprint](https://eprints.lancs.ac.uk/id/eprint/45542)
- Albers (2025), "A New Star Is Born: Does the VIX1D Render Common Volatility Forecasting Models for the U.S. Equity Market Obsolete?", *Journal of Futures Markets* 45(11), 2092-2108: VIX1D overestimates S&P 500 volatility, but a simple VRP adjustment gives 1-day forecasts more precise than HAR and HAR-VIX1D while needing less historical data — [IDEAS/RePEc](https://ideas.repec.org/a/wly/jfutmk/v45y2025i11p2092-2108.html); [TU Dresden](https://fis.tu-dresden.de/portal/en/publications/a-new-star-is-born-does-the-vix1d-render-common-volatility-forecasting-models-for-the-us-equity-market-obsolete(cdf81654-bf7d-41b6-a165-af0168c8b016).html)
- Another study (Otago archive, details only in a search snippet) reports that VIX1D in HAR-RV clearly improves on VIX for one-day-ahead forecasts, and that its predictive power decays faster than VIX's. A separate paper suggests 0DTE-implied 1-day IV may be better for VaR — [Otago archive](https://ourarchive.otago.ac.nz/esploro/outputs/journalArticle/VIX-term-structure-and-future-realized/9926827081601891) (snippet-level, not verified)
- Andersen, Fusari & Todorov (2017), "Short-Term Market Risks Implied by Weekly Options", *Journal of Finance* 72(3), 1335-1386: weekly S&P 500 options are mostly insensitive to shifts in the investment opportunity set. They reveal variation in negative jump tail risk that volatility does not span, and identify periods of tail concern that volatility does not signal — [EconPapers NBER WP](https://econpapers.repec.org/RePEc:nbr:nberwo:21491); [Kellogg](https://www.kellogg.northwestern.edu/academics-research/research/detail/2017/short-term-market-risks-implied-by-weekly-options/)
- Busch, Christensen & Nielsen (2011), *Journal of Econometrics* 160(1), 48-57: implied volatility contains incremental information about future volatility beyond past continuous and jump components (HAR / VecHAR). It is unbiased in FX and stock markets, and the jump component is partly predictable from options — [EconPapers](https://econpapers.repec.org/RePEc:eee:econom:v:160:y:2011:i:1:p:48-57)
- Bollerslev, Tauchen & Zhou (2009): VRP return predictability is strongest at the *quarterly* horizon — [SSRN](https://papers.ssrn.com/abstract=948309)

### Inferences
- Two cheap tests follow. (1) Rerun the existing pipeline at 5-day and 21-day horizons with non-overlapping or HAC-adjusted scoring, where theory and evidence say the 30-day features should matter more. (2) For 1 day, add the shortest available maturity, using VIX9D (from 2011) or VIX1D (from 2023, so a short sample). VIX1D's short history is a constraint for a 2020-2021 validation window.
- Pitfalls: overlapping multi-day targets inflate the effective significance unless the tests are adjusted. 0DTE IV has strong intraday and day-of-week patterns and event spikes, for example around FOMC and CPI.

### Gaps
- Bandi, Fusari & Renò 0DTE papers were not verified. No 1-day *density* (log-score) study using weekly or 0DTE RNDs was found.

## (d) Skewed / time-varying-tail distributions driven by option-implied skew and kurtosis

### Takeaway
Risk-neutral skewness does carry information about future physical skewness and volatility (Le et al. 2023), but risk-neutral skewness is systematically more negative than physical skewness, and at a 1-day horizon skewness has a small effect on the log score. Expect modest gains. They may be larger in the tails, and only if the skewness risk premium is modelled, for example with a free intercept and slope.

### Cited Findings
- Le et al. (2023), *Journal of Futures Markets* (UEA eprint): option-implied skewness estimators that account for the skewness risk premium are generally more informative about future skewness than realized-skewness or GARCH-type conditional-skewness models built on past returns only (including GJR-GARCH with time-varying shape) — [UEA eprint](https://ueaeprints.uea.ac.uk/91269/7/Le_etal_2023_JFuturesMarkets.pdf)
- Neuberger (2012), "Realized Skewness", *RFS* 25(11), 3423-3455: index-return skewness *increases* with horizon up to one year and is economically large. This implies 1-day skewness is small relative to monthly skewness — [EconPapers](https://econpapers.repec.org/RePEc:oup:rfinst:v:25:y:2012:i:11:p:3423-3455)
- Risk-neutral skewness is more negative than physical skewness at short and medium maturities, i.e. there is a skewness risk premium — [Unimore WP](https://iris.unimo.it/retrieve/e31e124d-7ab7-987f-e053-3705fe0a095a/0132.pdf)
- A CRRA representative-investor transformation explains the S&P 500 variance risk premium but cannot match variance and skewness premia at the same time — [OptionMetrics-hosted paper](https://optionmetrics.com/?p=1011)

### Inferences
- Implementation: a Hansen (1994) skew-t or Jones-Faddy / Johnson SU with the skewness parameter linear in BKM skewness, and nu linear in BKM kurtosis or a left-tail measure. Score it with log score *and* a tail-weighted CRPS or FZ loss. Neuberger's horizon result suggests the gain will be larger at 5-21 days than at 1 day.
- Pitfall: BKM higher moments are noisy and depend on strike-range truncation. Using them in shape parameters can overfit, so regularisation or shrinkage toward a constant shape is advisable.

### Gaps
- Conrad-Dittmar-Ghysels (2013, JF), Chang-Christoffersen-Jacobs (2013, JFE), Hansen (1994), Creal-Koopman-Lucas (2013) and Harvey (2013) were not separately verified in this budget, though they are well-known references. No study was found of a GAS / skew-t model with option-implied skew as a driver for SPX daily density forecasts.

## (e) Variance risk premium as a predictor of physical scale and returns

### Takeaway
The VRP is well established as a predictor of *returns* at monthly to quarterly horizons (BTZ 2009; Bekaert-Hoerova 2014). Much of that predictability comes from jump tail risk premia (Bollerslev-Todorov-Xu 2015). For *scale*, the key point is that the implied variance minus the VRP gives the conditional physical variance. Explicitly modelling or removing the VRP is what makes IV useful for VaR, and for 1-day VIX1D forecasts. The project's finding that the gain disappears after scale recalibration is consistent with the option features mostly acting as a biased scale proxy.

### Cited Findings
- Bollerslev, Tauchen & Zhou (2009), *RFS* 22(11), 4463-4492: model-free implied minus realized variance explains a nontrivial share of post-1990 aggregate return variation. Predictability is strongest at the quarterly horizon and beats P/E, the default spread and cay — [SSRN](https://papers.ssrn.com/abstract=948309)
- Bekaert & Hoerova (2014), *Journal of Econometrics* 183(2), 181-192: they split VIX² into conditional variance and the variance premium. The premium predicts stock returns, while conditional variance predicts economic activity and financial instability — [NBER WP 18995](https://www.nber.org/papers/w18995); [ECB WP 1675](https://ideas.repec.org/p/ecb/ecbwps/20141675.html)
- Bollerslev, Todorov & Xu (2015), *JFE* 118(1), 113-134 (not RFS): much of the VRP's return predictability can be attributed to time variation in tail shape and to compensation for jump tail risk — [EconPapers](https://econpapers.repec.org/RePEc:eee:jfinec:v:118:y:2015:i:1:p:113-134); [CREATES WP 2014-49](https://repec.econ.au.dk/repec/creates/rp/14/rp14_49.pdf)
- Adding a VRP adjustment fixes VIX1D's upward bias and makes it beat HAR (Albers 2025), and VRP in GARCH improves developed-market VaR (Slim et al. 2020) — [IDEAS](https://ideas.repec.org/a/wly/jfutmk/v45y2025i11p2092-2108.html); [IDEAS](https://ideas.repec.org/a/eee/quaeco/v76y2020icp22-37.html)

### Inferences
- For daily density forecasting, use the VRP mainly to *de-bias the scale* (for example SVIX² minus a HAR forecast of RV as a regressor in log-scale) rather than to predict mu. Daily return predictability from the VRP is economically tiny relative to daily noise.
- Pitfall: the VRP is estimated using a realized-variance forecast. If that forecast is built from the same historical features, the VRP regressor overlaps heavily with them.

### Gaps
- No study was found that reports daily *log-score* gains from VRP-adjusted densities for the S&P 500.

## (f) Distributional / quantile ML with option features

### Takeaway
There is little direct evidence for SPX daily return densities. The ML literature with option data mostly forecasts the implied-volatility surface (Fed 2026) or monthly returns from option panels, or uses firm-level quantile neural networks. With about 5,000 daily observations and a low signal-to-noise ratio, flexible learners are unlikely to beat a well-specified parametric or quantile-regression model robustly. Conformal methods are useful for guaranteeing calibration, not for finding signal.

### Cited Findings
- Kim & Oh (2026), Federal Reserve FEDS 2026-049, "Capturing Heterogeneity: Machine Learning Approaches to Implied Volatility Forecasting": boosted trees on the S&P 500 option surface give the lowest out-of-sample errors at all horizons. The target is IV, not returns — [Federal Reserve](https://www.federalreserve.gov/econres/feds/capturing-heterogeneity-machine-learning-approaches-to-implied-volatility-forecasting.htm)
- Quantile neural networks for stock return distributions (arXiv 2408.07497) beat parametric and ML benchmarks out of sample for *next-month, firm-level* returns in US and international markets — [arXiv](https://arxiv.org/html/2408.07497v2)
- Chang, Choi, Kim & Park (2025) use functional PCA of the full option panel and report monthly OOS R² above 4% (snippet-level) — [SSRN](https://papers.ssrn.com/abstract=5632350)
- Bleher, Dimpfl & Koch (2023): quantile autoregression density forecasts applied to option pricing — [RiuNet record](https://riunet.upv.es/entities/publication/af9cde7e-9f18-41bf-9d3e-659cbadb7a05/full)
- Bőők, Imbet, Reinke & Sala (2022 WP): option-implied quantile- and expectile-based moments from weekly S&P 500 options predict the equity premium and higher moments in and out of sample, beating return-based equivalents (peer-review status not verified) — [Informa / QuantMinds PDF](https://assets.informa.com/connectls/GLOBAL%20FINANCE/2022/Risk%20and%20QuantMinds/Paper.pdf)

### Inferences
- A linear quantile regression across many quantile levels with option features is the lowest-risk "distributional" extension, and it overlaps with (b). Tree or neural learners are better framed as a robustness check than as the headline.

### Gaps
- No published SPX daily study using QRF, DRF, NGBoost or MDNs with option-implied features was found.

## (g) Panel extension across indices, ETFs and stocks

### Takeaway
No direct evidence was retrieved for pooled density-forecast panels. The adjacent evidence suggests option-implied VaR gains hold in developed markets but not in emerging markets (Slim et al. 2020). Andersen-Fusari-Todorov's work on international option markets suggests tail-factor pricing is shared across major indices (not verified here). A panel's main value would be statistical power: more independent tail events, which is the binding constraint in (b).

### Cited Findings
- VRP-augmented GARCH improves developed-market 1-day VaR but not emerging-market VaR — [IDEAS/RePEc](https://ideas.repec.org/a/eee/quaeco/v76y2020icp22-37.html)
- Patton-Ziegel-Chen evaluate their ES/VaR models on four international equity indices — [EconPapers](https://econpapers.repec.org/RePEc:eee:econom:v:211:y:2019:i:2:p:388-413)

### Inferences
- Index panels (SPX, NDX, RUT, Euro Stoxx 50, Nikkei, DAX) have highly correlated tail events, so the effective gain in sample size is smaller than the count of series suggests. Individual stocks add idiosyncratic jumps (for example earnings) where options do have known predictive content, but that changes the research question.

### Gaps
- Andersen-Fusari-Todorov international tail-risk paper (JBES, around 2020) was not verified. No pooled density-forecast panel study with option features was found.

## Overall ranking: which direction is most likely to give large, robust out-of-sample gains, and why

### Takeaway
In order, most likely first: (c) horizon matching, (b) tail and quantile evaluation, then (a) the tilted-RND mixture. Each of these is most promising when the option information is combined with historical information rather than replacing it. (e) is best used to de-bias scale, not as a separate headline. (d) is likely modest at 1 day. (f) and (g) are low-yield given the data and the absence of evidence. The economic mechanism is that options price forward-looking crash and jump risk plus a time-varying risk premium. The crash-risk information is concentrated in the left tail and in horizons near the option maturity, while 1-day central-density forecasts are dominated by recent realized variance.

### Cited Findings
- Option densities win at 2-4 weeks and lose at 1 day, and mixtures win at short horizons — [Lancaster eprint](https://eprints.lancs.ac.uk/id/eprint/45542)
- IV gains explanatory power further into the left tail when combined with CAViaR — [Strathprints](https://strathprints.strath.ac.uk/39598/)
- IV alone, with the VRP left in, loses for VaR — [IDEAS/RePEc](https://ideas.repec.org/a/eee/intfor/v33y2017i4p848-863.html)
- Matched-maturity VIX1D with a VRP adjustment beats HAR at 1 day — [IDEAS/RePEc](https://ideas.repec.org/a/wly/jfutmk/v45y2025i11p2092-2108.html)
- Tail factors from weekly and monthly options are not spanned by volatility — [EconPapers](https://econpapers.repec.org/RePEc:nbr:nberwo:21491); [EconPapers](https://econpapers.repec.org/RePEc:eee:jfinec:v:117:y:2015:i:3:p:558-584)

### Inferences
- Concrete design for the project: (1) multi-horizon (1, 5, 21-day) Student-t or skew-t with the same feature sets, using HAC Diebold-Mariano tests on log score. (2) Joint VaR-ES regressions at 1%, 2.5% and 5% with FZ0 loss, comparing historical-only against historical plus option features (SVIX, a left-tail measure, BKM skewness). (3) A tilted-RND / historical linear pool with walk-forward weights. Use the longest available option sample (from 1996 with OptionMetrics) so the tail tests have enough exceedances.
- The fact that the gain vanishes after scale recalibration is itself in line with the literature: at 1 day, 30-day option features act mostly as a biased scale signal. The evidence suggests incremental information should be looked for in tail shape and at matched horizons.

### Gaps
- Several requested references were not verified within the search budget: Giot (2005), Chong, Kim & Lee, Barone-Adesi et al., Andersen-Fusari-Todorov (2020) left-tail variation, Bollerslev-Todorov tail index, Bandi-Fusari-Renò 0DTE, Conrad-Dittmar-Ghysels (2013), Chang-Christoffersen-Jacobs (2013), Kourtis-Markellos-Symeonidis (2016), Fissler-Ziegel (2016) and the GAS papers. They should be checked before citing.
