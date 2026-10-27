# Frontier of option-implied information for physical index return densities (2019-2026), and open gaps

Scope note: about 20 search and fetch calls. Several journal pages (ScienceDirect, Wiley) returned 403, so for those papers only the abstract or search-snippet level is verified. Items marked [training knowledge, not re-verified] come from prior knowledge and were not confirmed in this session. Treat them as leads, not citations.

## Q1. Recent papers forecasting the physical return DENSITY or quantiles of SPX/indices from option information (including ML)

### Takeaway
The recent frontier (2020-2026) mostly estimates the **pricing kernel / conditional physical distribution jointly with option prices**, evaluated on economic properties or option-pricing fit. Separately, there is **ML on option data for the cross-section** (stock or option returns, mean prediction). I found no 2019-2026 paper that forecasts the one-day-ahead SPX physical density from option features with out-of-sample log scores and DM tests, ML or otherwise. The closest density-forecast-comparison work on SPX with options predates 2019.

### Cited Findings
**Pricing kernel / conditional distribution estimation (closest economic frontier)**
- Schreindorfer & Sichert, "Conditional risk and the pricing kernel", *Journal of Financial Economics* vol. 171 (2025), DOI 10.1016/j.jfineco.2025.104106. Proposes a way to estimate the pricing kernel and conditional return distributions jointly from option prices. Finds that market losses hurt investors more in low-volatility periods, that leading macro-finance models fail to match conditional return distributions or the kernel, and that a one-SD rise in volatility raises expected returns by about 3.8 pp per year. Replication code is on Mendeley. — [IDEAS](https://ideas.repec.org/a/eee/jfinec/v171y2025ics0304405x2500114x.html); [SSE summary](https://www.hhs.se/en/houseoffinance/research/featured-topics/2025/study-finds-investors-feel-losses-more-in-calm-markets-challenges-core-models); [replication code](https://data.mendeley.com/datasets/34n3j4vhkf/2). (Verified at abstract/summary level. The full text was blocked, so whether they report out-of-sample log scores is NOT verified.)
- Schreindorfer, "Volatility and the Pricing Kernel" (AFA program paper). Estimates the kernel by maximum likelihood, with a parametric physical density and the kernel backed out from the density ratio. — [AFA](https://afajof.org/management/viewp.php?n=24612) (search-snippet level only).
- Sichert, "The Pricing Kernel is U-shaped" (AEA 2019 preliminary program). — [AEA](https://www.aeaweb.org/conference/2019/preliminary/paper/4idzhSbN) (title/author verified only).
- Heston, Jacobs & Kim, "The Pricing Kernel in Options", FEDS 2023-053 (April 2023; presented at AFA 2023 and SoFiE 2022). Extends Rubinstein-Brennan kernels to dynamic path- and volatility-dependent kernels. Because of low statistical power, kernels with different economic properties can produce similar overall option fit. Imposing monotonicity and path-independence gives reasonable equity and variance risk premiums. — [FEDS PDF](https://www.federalreserve.gov/econres/feds/files/2023053pap.pdf) (abstract read directly).
- Kim, "Characterizing the Conditional Pricing Kernel: A New Approach", FEDS 2026-059. Estimates a conditional pricing kernel with conditioning variables. **The VIX and the term spread are the most informative variables.** In bad times the equity premium is fully attributable to left-tail compensation. The evaluation is **out-of-sample option pricing**, not a physical density score. Data are OptionMetrics. — [FEDS PDF](https://www.federalreserve.gov/econres/feds/files/2026059pap.pdf) (abstract read directly).
- "Estimating a conditional density ratio model for asset returns and option demand", *Journal of Econometrics* (2026, PII S0304407626000126). A local density-ratio estimator that is competitive with correctly specified parametric MLE in simulations. — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0304407626000126) (403 on fetch; authors and details NOT verified, snippet only).
- Chabi-Yo & Loudis, "The conditional expected market return", *JFE* 137(3), 2020, pp. 752-786. Bounds on the conditional expected excess market return from risk-neutral volatility, skewness and kurtosis, computable in real time, with no distributional assumptions; average expected excess return about 5.2%. — [EconPapers](https://econpapers.repec.org/RePEc:eee:jfinec:v:137:y:2020:i:3:p:752-786). A follow-up by the same pair in *Management Science* 70(10), 2024 decomposes conditional risk premia — [IDEAS](https://ideas.repec.org/a/inm/ormnsc/v70y2024i10p6804-6834.html) (title not fetched).

**ML with option data (cross-section, means; not index densities)**
- Kelly, Kuznetsov, Malamud & Xu, "Deep Learning from Implied Volatility Surfaces", SFI Research Paper 23-60 (Aug 2023). Applies image-recognition ML to IV surfaces to predict the **cross-section of stock returns**. The signal is largely uncorrelated with existing option characteristics and gives significant alpha. — [SSRN](https://papers.ssrn.com/abstract=4531181); [SFI](https://www.sfi.ch/en/publications/n-23-60-deep-learning-from-implied-volatility-surfaces). Final published version not verified, and SSRN shows revision dates into 2026.
- Bali, Beckmeyer, Moerke (Mörke) & Weigert, "Option Return Predictability with Machine Learning and Big Data", *RFS* 36(9), 2023, pp. 3548-3602, DOI 10.1093/rfs/hhad017. About 12M delta-hedged equity option returns from 1996-2020, 265 characteristics, GBRT/RF/NN. Nonlinear models give profitable long-short strategies after costs. — [Münster CRIS](https://cris-portal.uni-muenster.de/portal/en/publication/98329575); [EconPapers](https://econpapers.repec.org/RePEc:oup:rfinst:v:36:y:2023:i:9:p:3548-3602.) (EconPapers adds a spurious fifth author; four authors is correct per other sources).

**Distributional ML for returns (no option inputs)**
- arXiv 2408.07497, "Forecasting stock return distributions around the globe with quantile neural networks" (two-stage quantile NN plus splines, individual stocks; the v1 title is "Predicting the distributions of stock returns around the globe in the era of big data and learning"). — [arXiv](https://arxiv.org/pdf/2408.07497)
- Fred Liu, "Stock Distribution and Risk Premia Predictability with Quantile Machine Learning" (SSRN 4491887): non-crossing multi-quantile network on firm and macro characteristics. — [SSRN](https://ssrn.com/abstract=4491887)
- MDPI 2025, "Deep Quantile Forecasting ... Multi-Horizon Value-at-Risk": QR, LightGBM, MLP/LSTM/TCN/TiDE/TFT on S&P 500 with realized-volatility inputs only. — [MDPI](https://www.mdpi.com/2227-7072/14/8/218)
- "Neural Lévy SDE for State-Dependent Risk and Density Forecasting" (arXiv 2509.01041). S&P 500 density forecasting with a 2020-2024 test window. It includes a risk-neutralization construction but reportedly does not calibrate to options. — [Pith review](https://pith.science/paper/2509.01041) (third-party summary only; not verified).

**Older SPX density comparisons using options (the direct ancestors of this project)**
- "A multi-horizon comparison of density forecasts for the S&P 500 using index returns and option prices", *Journal of Banking & Finance* (2010). Weighted combinations of historical and option densities beat either alone at **one-day and one-week** horizons. — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0378426610001834). Authors not visible on the page; believed to be Shackleton, Taylor & Yu [training knowledge, not re-verified].
- arXiv 1801.08007, "A comprehensive comparison of risk-neutral and historical ..." S&P 500 1991-2004: RNDs need transformation, VG has the best out-of-sample likelihood, GJR-FHS is the most consistent, and lognormal, Heston and Breeden-Litzenberger densities are biased. — [arXiv](https://arxiv.org/pdf/1801.08007)
- Liu, Shackleton, Taylor & Xu-style closed-form RN-to-real-world transformations (*JBF* 2007). — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0378426607000258) (authors from training knowledge).

**Related recalibration result**
- Goyle & Revtsov, "When Does Option-Implied Variance Add to Physical Forecasts? Evidence from S&P 500 Leveraged ETF Drag" (SSRN 7325618). The raw option signal loses skill at 66 days, Mincer-Zarnowitz calibration restores it, the calibrated forecast does not clearly beat HAR, and results differ across losses (gain under MSE/MAE, not QLIKE). — [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7325618) (snippet-level only). This is very relevant to the project's Step 7 recalibration, because it is the same "the option signal works mainly via calibrated scale" story, for variance rather than density.

### Inferences
- The kernel literature (Schreindorfer-Sichert 2025, Kim 2026, Heston-Jacobs-Kim 2023) is the true frontier for "options to physical distribution". It is judged on economics or option fit, and on monthly-ish horizons, not on daily physical density scoring.
- The ML-with-options literature is cross-sectional and mean-focused. The ML density literature does not use options. **The intersection (option features, then a learned conditional index density, scored by log score) appears unoccupied**, but this is an absence-of-evidence claim from a limited search.

### Gaps
- Could not read the full text of Schreindorfer & Sichert (2025) to check whether they report out-of-sample likelihood of returns; this is the single most important paper to check before claiming novelty for Gap B below.
- I did not search for Martin (2017, QJE "What is the expected return on the market?") or Martin & Wagner (2019, JF) [training knowledge]. Both are about expected returns (location), not densities.
- I did not verify any "physical density from option prices with machine learning" title. No such paper surfaced.

## Q2. Whole IV surface or full RND as input to a learned conditional physical density; ML-estimated pricing-kernel tilt

### Takeaway
I found no paper using the whole surface or RND as input to a learned conditional physical density scored out of sample. The kernel-tilt-by-MLE idea is classic: it uses a parametric physical density, or a kernel fitted to realized returns, with Schreindorfer as a recent example. Neural parameterisations of the tilt fitted by MLE on realized index returns did not surface.

### Cited Findings
- Neural work on option densities targets the **risk-neutral** side only. Examples are Risk-Neutral Generative Networks (arXiv 2405.17770), "Shallow Representation of Option Implied Information" (Lin, arXiv 2603.17151, Mar 2026: no-arbitrage neural RND/IV representation, synthetic experiments only, no physical returns), and Gated NNs for option pricing (arXiv 1609.07472). — [2405.17770](https://pith.science/paper/2405.17770); [2603.17151](https://arxiv.org/abs/2603.17151); [1609.07472](https://arxiv.org/pdf/1609.07472)
- "Risk-Neutral Market Simulation" (arXiv 2202.13996) goes the other way. It trains a neural spline flow toward the RND using physical samples, minimising KL. — [arXiv](https://arxiv.org/pdf/2202.13996)
- Kelly et al. (2023) use whole IV surfaces as images, but for cross-sectional stock mean returns. — [SSRN](https://papers.ssrn.com/abstract=4531181)
- Kim (2026) conditions the kernel on VIX and term spread. This is the closest conditional tilt, but it is evaluated by option pricing. — [FEDS](https://www.federalreserve.gov/econres/feds/files/2026059pap.pdf)
- Beta/kernel calibration of RNDs into real-world densities, ranked by out-of-sample log likelihood, exists for older SPX samples and, recently, for crude-oil ETF options. The crude-oil evidence comes via a LinkedIn summary, so it is weak. — [ScienceDirect 2007](https://www.sciencedirect.com/science/article/abs/pii/S0378426607000258); [ResearchGate calibration function](https://www.researchgate.net/publication/316550510_Estimation_of_option-implied_risk-neutral_into_real-world_density_by_using_calibration_function)

### Inferences
- A **low-dimensional, state-dependent exponential/polynomial tilt of the 30-day (or short-dated) RND, estimated by MLE on realised daily returns and scored against the project's Student-t baseline**, sits between the classic static calibration papers and the 2025-26 conditional-kernel papers, and has not obviously been done at the daily horizon.

### Gaps
- No direct search hit on "exponential tilting" plus "log score" plus SPX, 2019-2026. Absence is suggestive but not conclusive.

## Q3. Scale vs shape vs location decomposition; implied vol vs implied skew/kurtosis; tails vs centre

### Takeaway
I found no paper that explicitly decomposes the density-forecast gain from option information into scale, shape and location components. I also found none that localises the gain within the distribution using tail-weighted scoring rules. This looks like the cleanest open gap, and it extends the project's existing finding directly.

### Cited Findings
- Bakshi, Kapadia & Madan (2003, RFS): skewness is first-order relative to kurtosis for option prices. — [PDF](https://people.umass.edu/nkapadia/docs/Bakshi_Kapadia_Madan_2003_RFS.pdf)
- The old SPX comparison found GJR-FHS "most consistent across the density range" while VG had the best likelihood. That is an implicit hint that where in the density a model wins differs from the aggregate score. — [arXiv 1801.08007](https://arxiv.org/pdf/1801.08007)
- The search for tail-vs-centre scoring of option-informed density forecasts returned nothing relevant. — (search noted in session; no source)

### Inferences
- The tools exist for this decomposition: threshold- or quantile-weighted CRPS (Gneiting & Ranjan 2011, JBES) and censored/conditional likelihood scores (Diks, Panchenko & van Dijk 2011, J. Econometrics) [training knowledge, not re-verified]. Applying them to nested Student-t specifications is a straightforward, novel diagnostic. The nested specifications are: scale from options, then plus df/skew from options, then plus mean from options.

### Gaps
- Not verified: whether Schreindorfer-Sichert or Chabi-Yo-Loudis papers contain such a decomposition implicitly.

## Q4. Regime-switching / Markov models with option-implied information

### Takeaway
The evidence is old and mixed. Markov-switching models improve density forecasts when they use realized variance, and Markov-switching EGARCH volatility carries information similar to the VIX. Regime information is therefore plausibly subsumed by option-implied scale, which is consistent with the project's null HMM result.

### Cited Findings
- Liu & Maheu: a Markov-switching model with realized variance improves equity return density forecasts. — [MPRA 71120](https://mpra.ub.uni-muenchen.de/71120/)
- MIT thesis: Markov-switching EGARCH volatility forecasts carry similar information to the VIX. — [DSpace@MIT](https://dspace.mit.edu/handle/1721.1/153697)
- Haidinger & Warnung: a two-state hidden Markov model with GH returns, calibrated partly to VDAX, on DAX 2005-2009. — [arXiv 1212.4126](https://arxiv.org/pdf/1212.4126)
- Regime-switching SV estimated from returns and IV, checked against implied skew and kurtosis (JBES 2013). — [IDEAS](https://ideas.repec.org:443/a/taf/jnlbes/v31y2013i1p107-121.html)
- Kim (2026) finds strong state dependence of the kernel conditioned on VIX. That suggests the "regime" lives in option-implied state variables rather than in latent return-based states. — [FEDS](https://www.federalreserve.gov/econres/feds/files/2026059pap.pdf)

### Inferences
- The null HMM result should be framed as an encompassing result ("regime probabilities are spanned by option-implied scale"), not as a failure. A formal encompassing or forecast-combination test would make it a contribution, though a modest one.

### Gaps
- No 2019-2026 paper found that formally tests HMM regime probabilities against option-implied features in daily density forecasting.

## Q5. Very short-dated SPX options (weekly, 0DTE, VIX1D) for one-day-ahead forecasting; availability in OptionsDX 2010-2023

### Takeaway
VIX1D research (2024-2025) shows that 1-day implied volatility, after a risk-premium adjustment, beats HAR models for 1-day volatility. It is evaluated on volatility or VaR, not full densities, and it covers only the short post-2023 VIX1D history. The project's own data audit shows that OptionsDX contains weekly expiries from mid-2012 and DTE = 0 contracts. A synthetic 1-day implied variance or density can therefore be built for about 2012-2023, though SPX and SPXW are not distinguished.

### Cited Findings
- Albers, "A New Star Is Born: Does the VIX1D Render Common Volatility Forecasting Models for the US Equity Market Obsolete?", *Journal of Futures Markets* (2025), DOI 10.1002/fut.70023. VIX1D overestimates volatility, but once adjusted for the risk premium it beats HAR and HAR-VIX1D at 1 day. — [Wiley](https://onlinelibrary.wiley.com/doi/full/10.1002/fut.70023)
- "Forecasting the worst: is implied volatility forward-looking enough?" (Springer, *Journal of Asset Management*-type venue, s41261-025-00306-w): using VIX1D as 1-day volatility in VaR reduces loss magnitude on violations. — [Springer](https://link.springer.com/article/10.1057/s41261-025-00306-w) (journal name not confirmed)
- VIX1D has an overnight bias (*Finance Research Letters*, 2024). — [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S1544612324002162)
- 0DTE SPXW payoff distributions working paper (Vilkov): there is a positive 0DTE variance risk premium of modest economic magnitude. — [GitHub](https://github.com/vilkovgr/0dte-strategies/blob/main/docs/paper/paper-annotated.md)
- Andersen, Fusari & Todorov, "Short-Term Market Risks Implied by Weekly Options", *JF* 72(3), 2017, pp. 1335-1386. Negative jump tail risk varies separately from volatility and predicts returns. — [IDEAS](https://ideas.repec.org/a/bla/jfinan/v72y2017i3p1335-1386.html)
- Bollerslev, Todorov & Xu-type left-tail measures from short-dated deep OTM puts. — [Kellogg PDF](https://www.kellogg.northwestern.edu/faculty/todorov/htm/papers/tvt_pred.pdf)
- **Project-local evidence on OptionsDX:**
  - `data_feasibility_audit.md` records that weekly options appear in the data around June/July 2012, when 30-day bracketing jumps to 95-100%, against 76.4% bracketing failure in 2010.
  - The same audit records that DTE = 0 expiry-day contracts are present, and that the later expansion of listings includes Monday/Wednesday and Tuesday/Thursday expiries.
  - `SPX_data_research.md` notes there is no `SPX`/`SPXW` root field and that AM and PM settlement are mixed, so the forward must come from put-call parity per expiry.
  - Files: D:/IE612_Project/.claude/worktrees/fix-optimizer-calibration/data_feasibility_audit.md (lines 50, 137-138, 363-364); D:/IE612_Project/.claude/worktrees/fix-optimizer-calibration/SPX_data_research.md (lines 55, 141).
- Cboe added Tuesday/Thursday SPXW expirations in 2022, making daily expiries available. — [Cboe](https://www.cboe.com/insights/posts/how-to-make-the-most-of-added-spxw-options-expirations/)

### Inferences
- From mid-2012 onward, an implied variance from options with roughly 1-7 DTE can be built. Before May 2022 there were gaps of several days between expiries on non-Monday/Wednesday/Friday days, and some days have no expiry within a week before about 2016 [training knowledge on the listing timeline; check against the data]. A "1-day SVIX / short-dated BKM moments" feature evaluated on full density log scores 2012-2021 appears new, because the VIX1D papers use only the official index (2023+) and volatility or VaR losses.
- Note: the audit's "weeklies introduced mid-2012" describes what the data shows. Cboe SPXW weeklies existed earlier, in 2005 and expanded in 2010-2011 [training knowledge]. OptionsDX coverage of early weeklies may be incomplete.

### Gaps
- Could not confirm from OptionsDX's own site whether SPXW rows are fully included before 2012. The project audit is the best evidence available.

## Q6. Concrete open gaps (4-6) with closest papers, feasibility and risk

All gains found on 2022-2023 are contaminated because that test data has already been looked at. Every direction below must be pre-registered and confirmed on **fresh 2024-2025 (or later) data**, or its 2022-23 results labelled exploratory.

### Takeaway
The most defensible gaps are A and C. Gap A is a scale/shape/location plus tail-localisation decomposition of the option gain. Gap C is a short-dated (weekly/0DTE-based) 1-day implied feature scored on full densities. Both are cheap, extend the existing pipeline, and have no direct competitor in the searched literature. Gap B, an MLE-estimated conditional RND tilt, is novel at the daily horizon but must be checked against Schreindorfer-Sichert (2025) full text.

### Cited Findings (basis for each gap)
- **Gap A: Where does the option gain live?** Nested Student-t models: scale-only from options; plus df/shape; plus location. Evaluate by log score plus threshold/quantile-weighted CRPS and censored likelihood on left tail, centre and right tail, with DM tests per region. The same split separates ATM IV and term slope from BKM skew and kurtosis.
  - Open because none of the closest papers do this decomposition for daily density forecasts. Kernel papers focus on economics ([Schreindorfer-Sichert 2025](https://ideas.repec.org/a/eee/jfinec/v171y2025ics0304405x2500114x.html); [Kim 2026](https://www.federalreserve.gov/econres/feds/files/2026059pap.pdf)). The old density comparisons report aggregate likelihood only ([arXiv 1801.08007](https://arxiv.org/pdf/1801.08007)). Goyle-Revtsov show loss-dependence for variance forecasts ([SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7325618)), which motivates region-dependent evaluation.
  - Feasibility: very high, since this is existing features and models plus new scoring functions.
  - Main risk: the gain is about 0.03 nats/day and splitting by region cuts DM power. The answer may simply be "it is all scale", but stated rigorously that is still a finding.
- **Gap B: Conditional exponential tilt of the RND, fitted by MLE on realised 1-day returns.** Take the 30-day (or shortest available) RND from the chain, rescale to the 1-day horizon, and tilt by exp(θ(state)·x) with θ depending on SVIX and term slope. Compare log score against the Student-t regression.
  - Closest papers: [Schreindorfer-Sichert 2025](https://ideas.repec.org/a/eee/jfinec/v171y2025ics0304405x2500114x.html) (joint kernel and conditional distribution), [Kim 2026](https://www.federalreserve.gov/econres/feds/files/2026059pap.pdf) (VIX-conditioned kernel, option-pricing evaluation), [Heston-Jacobs-Kim 2023](https://www.federalreserve.gov/econres/feds/files/2023053pap.pdf) (kernels hard to distinguish on option fit, which motivates evaluating them on physical returns instead), and the static calibration literature ([JBF 2007](https://www.sciencedirect.com/science/article/abs/pii/S0378426607000258)).
  - Feasibility: moderate. It needs RND extraction (the BKM integration is already in place) and a horizon map from 30 days to 1 day, which is the hard and arbitrary part.
  - Main risk: horizon mismatch dominates, and Schreindorfer-Sichert may already report out-of-sample likelihood. Check their full text first.
- **Gap C: Short-dated implied 1-day features (synthetic "VIX1D" / 1-7 DTE SVIX and BKM moments, 2012-2023) in density forecasts.**
  - Closest papers: [Albers 2025 JFM](https://onlinelibrary.wiley.com/doi/full/10.1002/fut.70023) (official VIX1D, volatility loss), ["Forecasting the worst"](https://link.springer.com/article/10.1057/s41261-025-00306-w) (VaR), [Andersen-Fusari-Todorov 2017](https://ideas.repec.org/a/bla/jfinan/v72y2017i3p1335-1386.html) (weekly options, tail risk, return prediction, not density scoring).
  - Feasibility: the data contain weeklies from mid-2012 and DTE = 0 contracts (project audit).
  - Main risks: SPX and SPXW cannot be distinguished, AM and PM settlement are mixed, overnight and weekend effects ([overnight bias](https://www.sciencedirect.com/science/article/pii/S1544612324002162)), and wide spreads at very short DTE. The sample shrinks to 2012+.
- **Gap D: Whole-surface input to distributional regression.** Use a small set of functional-PCA factors of the (moneyness × maturity) IV surface as inputs to the Student-t location, scale and df, with heavy regularisation, against the 4-feature baseline.
  - Closest papers: [Kelly et al. 2023](https://papers.ssrn.com/abstract=4531181) (surfaces, cross-sectional means) and [Bali et al. 2023](https://econpapers.repec.org/RePEc:oup:rfinst:v:36:y:2023:i:9:p:3548-3602.) (option ML, option returns). Neither does index densities or scoring rules.
  - Feasibility: good, since the data have per-strike IV.
  - Main risk: about 3,000 daily observations means overfitting. Gain beyond scale is likely tiny, consistent with the project's finding. Neural or MDN variants are not advisable at this sample size.
- **Gap E (smaller): Formal encompassing test of regime models by option-implied state.** Test whether HMM regime probabilities add anything once option-implied scale is included, using forecast combination or encompassing on log scores.
  - Context: [Liu & Maheu](https://mpra.ub.uni-muenchen.de/71120/) (MS plus RV helps), [MIT thesis](https://dspace.mit.edu/handle/1721.1/153697) (MS-EGARCH is about as informative as VIX), [Kim 2026](https://www.federalreserve.gov/econres/feds/files/2026059pap.pdf) (state lives in VIX).
  - Feasibility: trivial, since the components already exist.
  - Main risk: low novelty, because it repackages the existing null result.

### Inferences
- Recommended priority: A (cheap, interpretable, directly extends the "mainly through scale" finding), then C (most novel data angle, with microstructure risk), then B (most ambitious; check the competitor first). Treat D and E as robustness or appendix items.
- Every gap needs confirmation on 2024+ data. A and E could be re-run on 2022-23 only as exploratory analysis.

### Gaps
- Novelty claims rest on a limited search of about 20 queries. Before writing, the student should check SSRN and Google Scholar for "density forecast" plus "option-implied" plus "log score" in 2021-2026. They should also check the full texts of Schreindorfer-Sichert (2025) and the J. Econometrics 2026 density-ratio paper.
- Not verified: OptionsDX availability and pricing for 2024-2025 SPX data, which would be needed for fresh confirmation.
