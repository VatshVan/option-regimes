

Saturday 7:38 PM
Yes. The constraint we had converged on was essentially:
~1 month total
The project must be research-oriented, not just an implementation/demo.
There needs to be a specific novelty claim—something that could plausibly become a paper contribution.
The baseline should be reproducible quickly (roughly 5–7 days).
Then the remaining time is spent attacking a specific limitation/failure boundary and implementing a genuinely new extension, analysis, or
theorem.
We were explicitly rejecting ideas that merely package known concepts into a new framework.
In particular, the earlier finite-sample EMM/scenario-reconstruction direction was rejected, and the Heston price-fit vs parameter-recovery
idea was also rejected because the relevant identifiability/conditioning literature was already substantial.
The direction you were favoring was closer to:
So yes, “finish an interesting financial project in one month” isn't sufficient. The one-month constraint has to be compatible with a paper-worthy
contribution.
For the next project selection, I would therefore apply a hard filter:
The important distinction is paper-worthy ≠ complicated. A one-month project can be publishable if the research question is sufficiently narrow and
the contribution is sharp—for example, discovering that a published numerical method fails under a particular regime, proving/characterizing the
failure mechanism, and implementing a modification that fixes it.
That is the standard I would use to judge the financial project options we're considering.
YOu know we were discussing about a Financial project to select, there was a debate going on to
complete it in one month, but the project has to implement somethng, new paper worhty right?
Worked for 7s
Take a recent, reproducible quantitative-finance paper/claim → reproduce its result → identify a precise weakness or unexplored boundary →
implement a targeted extension → demonstrate a measurable improvement or failure mode.
RequirementMust satisfy
Baseline reproducible≤ 5–7 days
Existing paper/baselineYes
Dataset/code availablePreferably yes
Novel contributionSpecific and defensible
ImplementationRequired
Quantitative evaluationRequired
Novel theorem/algorithm/empirical findingAt least one
Can produce meaningful result in ~3 weeks after baselineYes
“Just apply ML to finance dataset”Reject
“Combine existing methods” without new findingReject
Entirely theoretical framework requiring monthsReject
This is the course syllabus of that project:
## IE612
Introduction to Financial Engineering

Memory updated
Understood. I’ll use this IE612 syllabus as the scope/reference point for the project discussion.
Memory updated
I’ll treat the uploaded resume as the current reference for your technical background, especially when evaluating whether an IE612 project is feasible
within your existing skill set.
Your finance/quant background in particular includes alpha research, financial ML, portfolio optimization, derivatives pricing, Black–Scholes, risk-
neutral/martingale pricing, hedging, finite-difference methods, Vasicek interest-rate modeling, and options simulation.

I’ll also account for your broader ML, numerical methods, optimization, computational physics, and engineering/control background when
assessing project ideas.
Yes. Given the IE612 syllabus + your existing technical background + the one-month constraint + requirement for something genuinely
research/paper-worthy, I would not start by searching “financial project ideas.” That produces mostly portfolio/demo projects.
Instead, use a research-discovery stack: find recent papers → identify reproducible baselines → inspect limitations/open questions → test whether a
narrow extension can be implemented in ~1 month.
- Start with these research-paper sources
A. arXiv — Quantitative Finance
arXiv Quantitative Finance
This should be one of your primary sources. Look specifically at:
q-fin.PR — Pricing of Securities
q-fin.PM — Portfolio Management
q-fin.MF — Mathematical Finance
q-fin.ST — Statistical Finance
q-fin.TR — Trading and Market Microstructure
q-fin.RM — Risk Management
For your project, don't read papers indiscriminately. Search within these categories for terms such as:
There are already recent papers connecting several of these areas to ML/RL. For example, a 2024 paper studies RL for optimal stopping with
applications to American option pricing and portfolio choice.
Industrial Engineering and Operations Research  ●  6 credits  ●  Interdisciplinary
STEM Course.
The aim of this course is to cover some basic concepts of financial engineering: the issues that arise
in modeling, analysis and decision making involving financial instruments. Discrete time models
and computational tools will be the focus. Portfolio optimization: Markowitz model; Two and one
fund theorems; mutual funds. Capital Asset Pricing model; Security market line. Arbitrage; Hedging;
Pricing. Contingent claims; Forward and futures contracts. European and American options; Asian
and other path dependent options. One and multi-period binomial models; Finite state models.
Equivalent martingale measures; Completeness of markets; Fundamental asset pricing theorems;
Option pricing. Black-Scholes option pricing formula.
Just remember this things, I'll tell what to do
Now you know myself, what I know: This is me, more or less most things are included. So this is my
technical knowledge, remember that
bb3be664-5316-4806-82d6-7c0119d...bb3be664-5316-4806-82d6-7c0119d...bb3be664-5316-4806-82d6-7c0119d...
bb3be664-5316-4806-82d6-7c0119d...bb3be664-5316-4806-82d6-7c0119d...
Now time for project selection, I have to find resources to decide what project to build for that help
find me resources
option pricing, American options, implied volatility, hedging, binomial model, portfolio optimization, robust portfolio, transaction costs,
martingale, incomplete markets, regime switching, stochastic volatility, volatility forecasting, reinforcement learning.
arXiv
bb3be664-5316-4806-82d6-7c0119d8...
## PDF

B. SSRN — Financial Economics / Finance
SSRN Financial Economics Research Network
SSRN is particularly useful because finance research often appears there before journal publication.
Look for:
asset pricing
derivatives
portfolio management
financial econometrics
quantitative finance
market microstructure
For example, recent work has explored multivariate affine-GARCH models with heavy-tailed innovations for both portfolio optimization and option
valuation.
That kind of paper is useful to us not necessarily because we would reproduce it, but because its methodology can reveal smaller unresolved
subproblems.
## C. Google Scholar
## Google Scholar
This is probably the most important tool for determining whether an idea is actually novel.
Use searches like:
Then filter to 2021–2026.
For every promising paper, inspect:
## 1. References
- Cited by
- Related articles
- Future work
## 5. Limitations
The last two are particularly valuable for project selection.
- Use RePEc/IDEAS for finance literature
IDEAS/RePEc
This is particularly useful for economics/finance because you can search papers by subject and author and follow citation networks.
For example, there is already recent research on ML-based option pricing using Indian NIFTY 50 data, comparing models such as SGD, decision
trees, random forests, XGBoost and neural networks against Black-Scholes.
That immediately tells us something important:
We would need a much sharper research question.
## SSRN
"American option" "machine learning" pricing
"binomial tree" option pricing improvement
"robust portfolio optimization" transaction costs
"portfolio optimization" regime switching
"implied volatility" portfolio optimization
"option hedging" machine learning
"equivalent martingale measure" numerical
"market completeness" computational
IDEAS/RePEc
“Use ML to improve Black-Scholes pricing” is not, by itself, a novel project idea.
Plain text

- GitHub is extremely important for our one-month constraint
The objective isn't merely to find papers. We want:
because that can save ~1–2 weeks.
## Microsoft Qlib
Microsoft Qlib GitHub
Qlib provides an end-to-end quantitative research platform covering data, models, training and evaluation.
Its documentation is particularly useful for understanding what a modern quant research pipeline looks like.
However, I would not automatically choose a Qlib-based project. It can push us toward generic ML trading projects, which overlap heavily with
what you've already done.
## Quantopian Alphalens
Alphalens GitHub
Useful for factor/alpha research.
It provides:
returns analysis
information coefficient analysis
turnover analysis
grouped analysis
Again, because you already have substantial alpha research experience, I'd use this primarily as a research infrastructure/reference, rather than
make another generic alpha project.
## Zipline / Zipline Reloaded
Zipline GitHub
Useful for understanding rigorous backtesting infrastructure, including event-driven simulation, slippage, transaction costs and avoiding look-ahead
bias.
There is also:
## Zipline Reloaded
This is more useful than the original Zipline if we actually need a maintained implementation.
- Look for existing research implementations
There are some repositories that are useful specifically as baseline mines.
For example:
## Quant Option Research Platform
It contains implementations around:
Black-Scholes
## Greeks
implied volatility
## Monte Carlo
volatility modelling
backtesting
Paper + code + data + reproducible baseline
GitHub+1
GitHub
GitHub
GitHub+1

regime-aware ML
walk-forward testing
calibration
uncertainty analysis
This is exactly the sort of repository we can inspect to see:
Another useful example:
## Monte Carlo Option Pricing Lab
It already covers:
Monte Carlo pricing
variance reduction
American options
Longstaff-Schwartz
## Greeks
multi-asset derivatives
VaR
and explicitly includes validation against Black-Scholes and convergence tests.
That gives us a potential baseline, rather than something we would submit unchanged.
- Use current university research pages for project ideas
This is underrated.
University research/thesis pages frequently reveal problems researchers actually consider open enough to investigate.
For example, KIT currently lists research around:
where ML is used to forecast option returns and incorporate option-implied information into mean-variance portfolio construction.
That is much more useful for us than a random "50 finance project ideas" webpage.
Search university pages for:
- Use recent papers to identify the research frontier
A few examples show the kind of territory worth investigating.
American options + RL
A 2024 paper studies learning optimal stopping for diffusion processes and applies the method to American put pricing and portfolio choice.
Potential research direction:
GitHub
"What can already be implemented in a few days, and what research question remains beyond it?"
GitHub
Portfolio choice with option-implied information using machine learning
C-Financial Econ...
site:edu "financial engineering" "research project"
site:edu "option pricing" "machine learning" thesis
site:edu "portfolio optimization" "machine learning" thesis
site:edu "quantitative finance" "project"
site:edu "derivatives" "research project"
arXiv
Not "use RL for American options."
Plain text

## Instead:
That becomes an empirical research question.
Computational acceleration
A 2025 paper proposes RL to dynamically choose block-preconditioner sizes for iterative solvers appearing in portfolio optimization and option
pricing.
Interesting because it combines:
Financial engineering + numerical optimization + ML
which overlaps unusually well with your background.
Again, though, we would have to check whether there is a sufficiently narrow unexplored extension.
Stochastic volatility / portfolio / pricing
Recent research is combining heavy-tailed volatility models with portfolio optimization and option pricing.
Potentially interesting, but probably more mathematically demanding than what I'd initially target for a one-month project.
- A very useful source for identifying what actually matters in quantitative research
Campbell Harvey's Finance 656 materials
His current 2026 quantitative asset-management course covers topics including:
risk
systematic risk
strategy evaluation
rebalancing
risk targeting
drawdown control
crisis hedging
uncertainty
factors
distinguishing luck from skill
AI/ML in asset management
quantitative stock selection
His research page is also useful for following the literature:
## Campbell Harvey Research Papers
This is particularly useful for research methodology, not just project ideas.
- Don't ignore textbooks
For IE612 specifically, I would keep one strong reference open while exploring papers.
Hull — Options, Futures, and Other Derivatives
Useful for:
binomial trees
Black-Scholes
futures/forwards
Under what conditions does an RL optimal-stopping method outperform classical Longstaff-Schwartz/binomial approaches, and where does
it fail?
arXiv
## SSRN
## Duke People
## Duke People

## Greeks
hedging
American options
exotic options
Shreve — Stochastic Calculus for Finance
Useful when the project gets into:
martingales
risk-neutral measures
arbitrage
stochastic processes
option pricing
Glasserman — Monte Carlo Methods in Financial Engineering
Especially relevant if we go toward:
Monte Carlo pricing
variance reduction
## Greeks
rare events
computational acceleration
These shouldn't be our idea generators. They should be our theoretical verification layer.
- One resource I would particularly use for your project
Because you've already done substantial quant work, I would use WorldQuant's research material only as a secondary resource:
WorldQuant Learn2Quant
It covers alpha construction, diversification, risk management and advanced quantitative research techniques.
But I would deliberately avoid letting this turn the IE612 project into another alpha-generation/backtesting project. You already have much stronger
experience there, and it doesn't naturally exploit the full IE612 syllabus.
- The research-selection pipeline I'd use
Rather than searching randomly, I'd make a spreadsheet with these columns:
And I would not select the project until we have at least ~10–20 candidate papers.
Then eliminate anything where:
Reject immediately
It is simply an implementation of a textbook model.
"Compare XGBoost vs Random Forest vs neural network."
"Apply deep learning to option pricing."
"Use RL for portfolio optimization."
The novelty is merely combining two existing techniques.
It requires proprietary data.
WorldQuant
## 
PaperYearIE612 topicBaseline
available?
Code?Data?Main limitationPossible
extension
## Imp
Paper A2025American
options
## ✓✓✓XY
Paper B2024Portfolio✓✗✓XY
Paper C2026Hedging✓✓✗XY

The baseline itself takes >1 week.
The paper's claimed contribution is already extensively extended by later papers.
The only contribution would be testing it on Indian data.
It requires a mathematical derivation substantially beyond your available one-month time.
Keep for deeper investigation
A paper has a clear limitation.
There is an identifiable unexplored parameter/regime/boundary.
A theoretical result has an interesting empirical consequence we can test.
A numerical method has a known computational weakness.
A model makes an assumption that can be systematically relaxed.
A method works under one market condition but its failure boundary isn't characterized.
There is a reproducible baseline.
We can make the new experiment in 2–3 weeks.
The three research areas I'd investigate first for you
Given your background + IE612 + one month, I would search these three areas first:
- Derivative pricing / hedging + numerical methods
## Especially:
Binomial / Monte Carlo / finite difference / American options / Greeks / hedging
This lets you leverage your existing derivatives work while moving beyond the basic Black-Scholes implementation.
- Portfolio optimization under realistic constraints
Not another Markowitz implementation.
Instead investigate:
transaction costs, estimation error, regime shifts, distributional uncertainty, robust optimization, option-implied information, dynamic
rebalancing
This connects directly to IE612's portfolio material and your optimization/ML background.
- Market completeness / risk-neutral pricing / discrete-time models
This is less crowded with generic ML projects.
For example:
That type of question could potentially produce a much more financial-engineering-specific project than another ML prediction exercise.
One important point
I would not yet choose a project from these resources.
The next step should be a literature sweep, where we systematically collect perhaps 30–50 recent papers (roughly 2021–2026) across the IE612
topics, then classify each into:
already saturated / reproducible / promising gap / too difficult / too generic / potentially one-month feasible.
From that, we can narrow it to perhaps 5–8 serious project candidates, and only then investigate novelty deeply.
If you want, I can do that literature sweep next and build the candidate database rather than just giving you more generic resource links.
Can we computationally characterize how approximation/discretization/model misspecification affects the existence or stability of an equivalent
martingale measure?
I think this is a good project to work: Portfolio choice with option-implied information using
machine learning

Yes, the core direction is strong, but I would change one important part of the proposed architecture.
The project should not be framed as:
That has a theoretical problem: no-arbitrage/risk-neutral pricing does not by itself give the physical expected stock return. Option prices primarily
identify information under the risk-neutral measure . To turn that into an investment expectation under the physical measure , you need an
additional model for the risk premium / stochastic discount factor / pricing kernel.
That distinction can actually become the interesting research contribution.
What the literature says
The basic idea is already established.
A 2020/2021 paper explicitly studies optimal portfolio allocation using option-implied information, constructing state variables for the risk premium
and market price of risk, and using implied risk-neutral densities.
Earlier work has also used option-implied distributions for portfolio choice, including martingale-based approaches. Aït-Sahalia and Brandt, for
example, use option-implied state prices in a portfolio/consumption problem.
And there is already evidence that option-implied variables can predict future equity returns and realized variance. One study finds predictive
information in the correlation and variance risk premia and evaluates the economic value for portfolio timing.
Even more directly, the exact project title you found is a current KIT research topic: the proposed project uses ML such as LASSO to forecast option
returns and then uses option-implied information for mean-variance portfolio selection.
So the idea is definitely legitimate—but we cannot claim novelty merely from combining option information + ML + portfolio optimization.
I would modify your idea into this
Proposed architecture
## ↓
- Extract option-implied information
From the cross-section of calls/puts:
extract:
implied volatility
volatility skew
term structure
risk-neutral moments
risk-neutral density
variance risk premium
skewness risk premium
possibly higher moments
## ↓
- Model the latent market state
Here your Markov model becomes useful.
For example:
We can incorporate Matringale and Makrov models + ML algos to predict option pricing and use
that to get ane xepcted stock price under no-arbitrage and use that in protfolio construction
ML predicts option prices → use no-arbitrage → obtain expected stock price → Markowitz portfolio.
## QP
## Wiley Online Lib...+1
## National Bureau...
## Taylor & Francis ...
C-Financial Econ...
## Options Market
## C(K,T),P(K,T)
## Z ∈
t
{Low Vol,Normal,High Vol}

with
using an HMM / Markov regime-switching model.
The state can depend on:
historical returns
realized volatility
option-implied volatility
skew
risk-neutral moments
macro variables
This gives:
rather than simply predicting returns with an ML black box.
- ML predicts the physical distribution
This is where I think your idea can become substantially more interesting.
Instead of:
we attempt:
or at least:
The input contains option-implied information, not just historical stock returns.
For example:
and ML predicts:
- The critical theoretical bridge:
This is where martingale theory becomes genuinely relevant.
Under the risk-neutral measure:
but the investor cares about:
Those aren't automatically equal.
## Conceptually:
The difference contains information about risk premia.
## P(Z =
t+1
j∣Z =
t
i)=P
ij
## P(Z ∣I )
t+1t
## ML→E[S ]
t+1
## ML:I

## →
t
P-distribution of R
t+1

## ,

## ,

## ,
μ^
t+1
σ^
t+1
## 2
## Skew
## ^
t+1
## Kurtosis
## ^
t+1
## X

## =
t
## [IV

,Skew

,TermStructure

## ,VRP

## ,RRP

## ,R

## ,RV

,Macro

## ]
tttttttt
## =μ^
t+1
f (X )
θt
## Q→P
## E
## =
t
## Q
## [
## B
t+1
## S
t+1
## ]
## B
t
## S
t
## E

## [
## R

## ]
t
## P
t+1
Q-distribution=P-distribution

One possible framework is a stochastic discount factor:
and
for excess returns.
This gives us a principled way of asking:
That's considerably more interesting than "ML predicts options."
- Then portfolio construction
Once we have:
and
we solve something like:
subject to:
and potentially:
plus:
turnover constraints
transaction costs
position limits
volatility target
Then compare:
## Baseline 1
## Historical Markowitz
## Baseline 2
Option-implied portfolio
## Baseline 3
ML using historical information
Proposed model
## M

## =
t+1

dP
dQ
## E
## [
## M R
## ]=
t
## P
t+1t+1
## 0
Can ML learn the transformation from option-implied risk-neutral information into economically useful physical-measure forecasts while
respecting no-arbitrage restrictions?
μ^
t+1
## Σ
## ^
t+1

w

## −
w
max
## ⊤
μ^

ww
## 2
λ
## ⊤
## Σ
## ^

w

## =
i
## ∑
i
## 1
w≥
i
## 0
(μ ,Σ )
historicalhistorical
(μ ,Σ )
## OIOI
(μ ,Σ )
## MLML
Option information+Markov state+ML+no-arbitrage constraints

Where I think the real research question should be
Rather than claiming:
I'd formulate the research question approximately as:
And then an even more interesting sub-question:
That gives us an actual experimental hypothesis.
And your IE612 syllabus fits this unusually well
So the project can remain inside IE612, while using your ML/quant background to go beyond the basic syllabus.
But there is a major novelty problem we need to solve
There is already substantial literature on:
option-implied information → portfolio allocation
option-implied variables → return prediction
option-implied volatility/skewness → portfolio selection
risk-adjusted option-implied distributions → portfolio choice
ML → option-implied information extraction
ML/high-dimensional methods → cross-sectional stock-return prediction from option characteristics; a 2025 Management Science paper
explicitly studies this.
"We build an ML portfolio using options."
Can option-implied risk-neutral information, combined with regime-dependent machine learning estimates of the physical return
distribution, improve out-of-sample portfolio allocation relative to historical and purely option-implied approaches?
Does explicitly modelling the -to- transformation through regime-dependent risk premia provide incremental portfolio value over
directly predicting returns from option characteristics?
## QP
IE612 conceptProject component
MarkowitzPortfolio optimization
CAPMExpected return / risk premium baseline
ArbitrageNo-arbitrage constraints
HedgingOptional extension / validation
Contingent claimsOptions
European optionsOption data
American optionsPotential extension
Binomial modelsRisk-neutral distribution baseline
Finite-state modelsMarkov regime model
Equivalent martingale measures-measure framework
CompletenessLimitations of recovering distributions
Fundamental asset-pricing theoremNo-arbitrage foundation
Black-ScholesBenchmark implied-volatility extraction
## Q
## Wiley Online Lib...
## Taylor & Francis ...
## Cambridge Univ...
PubsOnLine
## Taylor & Francis ...
## Google Sites

And the KIT project itself proposes LASSO + option returns + portfolio selection.
Therefore, we should not yet commit to the exact architecture you proposed.
Instead, I think the next research task should be:
Literature-gap investigation
Take these four components separately:
and search 2020–2026 literature specifically for papers combining each pair/triple.
The goal is to find a hole such as:
If that gap survives a proper literature search, then we have a potentially very good one-month IE612 project.
And importantly, we can make the first version much smaller: S&P 500 constituents / liquid options → option-implied moments → regime model
→ constrained ML  forecast → Markowitz → strict walk-forward evaluation. That is computationally realistic for your existing skill set.
Yes. Given what you already know, I would not give you introductory finance papers or highly mathematical stochastic-calculus papers. You need a
sequence where each paper teaches one component of the eventual project.
I would read these 4 papers in this order:
- DeMiguel et al. (2013) — start here
“Improving Portfolio Selection Using Option-Implied Volatility and Skewness”
Journal of Financial and Quantitative Analysis
Paper / SSRN full text
This is the best starting point for your project.
The paper asks almost exactly the first-level question we care about:
They examine option-implied:
volatility
correlation
risk premium
skewness
and incorporate this information into expected-return/portfolio estimation. They evaluate out-of-sample volatility, Sharpe ratio and turnover.
What you should learn from it:
C-Financial Econ...
Option-implied information
Q→P transformation
Markov/regime switching
ML portfolio optimization
option-implied → portfolio: already done
option-implied → ML prediction: already done
Markov → option pricing: already done
ML → portfolio: heavily done
option-implied + regime-dependent  transformation + portfolio construction: potentially less exploredQ→P
## Q→P
Good, we will go in these direction, your role is to just find 3-4 resrearch papers through which I
can understand how to start the proejct, see use research papes levels I can understand, you know
me
Can option-implied information improve mean-variance portfolio selection?
## Cambridge Univ...+1

This gives you the base architecture of our project.
It is also at a level you should be able to follow without learning a huge amount of new mathematics.
- Bianchi & Tassinari (2018) — learn the Q → P bridge
“Forward-looking portfolio selection with multivariate non-Gaussian models and the Esscher transform”
arXiv paper
This one is much closer to the part you specifically want to add.
The authors construct a portfolio framework using option-implied information, while modelling non-Gaussian return distributions. Crucially, they
connect the historical/physical measure  and risk-neutral measure  using the Esscher transform.
The basic idea is:
and
with a transformation connecting them.
They then use the resulting distributional information for portfolio selection.
This is the paper I want you to pay particular attention to, because it prevents us from making the mistake we discussed earlier:
You need some mechanism to bridge  and .
For you, this paper is probably the conceptual bridge between IE612's equivalent martingale measures and the portfolio/ML project.
- Chernov & Ghysels (2000) — understand how option data informs  and
“A Study Towards a Unified Approach to the Joint Estimation of Objective and Risk Neutral Measures for the Purpose of Options Valuation”
Journal of Financial Economics paper
Don't try to reproduce the mathematics.
Read it for the conceptual architecture.
The paper explicitly tries to bridge:
and
using both the underlying asset and option information. They demonstrate the approach using Heston's model and S&P 500 data.
This gives you the theoretical background for the question:
Option prices
## ↓
Option-implied quantities
## ↓
Expected return / risk estimates
## ↓
Mean-variance portfolio
## ↓
Out-of-sample evaluation
## PQ
arXiv
P⟶return dynamics
Q⟶option prices

risk-neutral expected price=physical expected price
## QP
## PQ
physical/objective measure P
risk-neutral measure Q
ScienceDirect+1
Plain text

That is a very important question for our project.
- Gu et al. (2023) — then bring in ML
“Option Return Predictability with Machine Learning and Big Data”
Review of Financial Studies
Oxford Academic paper
This is where your existing ML/quant knowledge becomes directly relevant.
The paper uses 12+ million observations from 1996–2020 and investigates nonlinear ML relationships between option/stock characteristics and
future option returns. It finds that nonlinear ML models provide substantial out-of-sample predictive information, with option characteristics being
particularly important predictors.
You don't need to learn ML from this paper—you already know that part.
Instead, study:
What are their input features?
What exactly is the prediction target?
How do they construct the training/test split?
How do they avoid look-ahead bias?
What constitutes an economically meaningful prediction?
How do they convert predictions into portfolio positions?
How do they evaluate out-of-sample performance?
Those are the research-design lessons we need.
So these four papers form a progression
I would visualize your eventual project as:
What exactly are we learning from the options market that isn't already contained in historical stock returns?
OUP Academic
## 
## 
## IE612 THEORY
## │
## ┌──────────────┴──────────────┐
## │                             │
## Risk-neutral Q                 Physical P
## │                             │
│                     Historical returns
## │                             │
## └───────────┬─────────────────┘
## │
Q → P bridge
(Esscher / SDF /
regime-dependent
transformation)
## │
## ▼
Option-implied features
## │
## ▼
ML prediction
## │
## ▼
Expected return / distribution
## │
## ▼
Markowitz / portfolio
## │
## ▼
Walk-forward testing
Plain text

And each paper teaches one block:
One newer paper is worth keeping in reserve
There is a 2026 paper called “Forward-looking physical tail risk: a deep learning approach” that is extremely close to the direction we're discussing. It
explicitly tries to extract physical-measure information from risk-neutral information using deep learning, using S&P 500 option data.
I would not start with this one.
It is closer to the research frontier and could be very useful later for identifying what has already been done. In particular, its existence means we
have to be careful about claiming that simply doing
is novel.
Your reading order
Read only the abstracts/introduction/conclusion first:
DeMiguel → Bianchi → Chernov/Ghysels → Gu et al.
Then, on the second pass, read the methodology sections of DeMiguel and Bianchi carefully.
After that, we can take these four papers and construct a “what already exists → what each paper leaves open → what our one-month
contribution could actually be” map. That is the point at which I would start designing the actual project rather than adding more components
blindly.
Today 1:22 AM
PaperWhat you learn
DeMiguel et al. 2013Option information → portfolio optimization
Bianchi & Tassinari 2018 ↔  transformation → portfolio choice
Chernov & Ghysels 2000Why/how physical and risk-neutral measures are jointly connected
Gu et al. 2023ML + option information + rigorous out-of-sample prediction
## PQ
## Taylor & Francis ...+1
## Q→ML→P
From any one of this, would I be able to get the options data for US or Indian Market?
## Databases / Standard Databases
ABI/Inform Database
American Ceramic Society-Phase Equilibria Diagrams (10 Users) (Registration required)
Bloomberg (Terminal available at Central Library, Circulation Area)
## Bloomsbury Visual Arts Hub
## Crisil Research
Capitaline AWS Database (To use this facility please register using IITB email id)
CMIE Database
Dataful (Click on “Sign In” and then click on “Sign Up with IP”)
## EMIS
EPWRF India Time Series
## Euromonitor Passport
## Grove Music Library
HS Talks Business and Management Collection
## Indian Boards Database
ICSD : Inorganic Crystal Structure Database
IndiaStat (Click IP Login)
## Inspec Database
## Journal Citation Report

Yes. For this specific project, your IIT Bombay database access is potentially very useful. In fact, I would **prefer institutional Bloomberg/LSEG data
over trying to build the entire project from Yahoo Finance
LSEG Workspace (Previously known as Refinitiv : For Login contact Journals Section)
MathSciNet
Naxos Music Library (Contact: Journal Section)
ProQuest
Qualtrics (For Login contact Journals Section)
## Reaxys Database
SciFinder Scholar
Scite (Smart Citation)
## SCOPUS
## Statista
The Cambridge Structural Database (CSD) (For Activation key contact Journal Section)
The Ken (For Registration)
The Ken (For Login)
Tracxn Database (User Guide)
VCCEdge Database (Contact: Journal Section)
## Venture Intelligence Database
Web of Science
YNOS Venture Engine
## Standard Databases
ASTM Digital Library With Standards
IEC Standards
## Indian Standards
ISO Standard (Custom Collection)
These and also any open source like yahoo and all for this particular project?
From any one of this, would I be able to get the options data for US or Indian Market?
## Databases / Standard Databases
ABI/Inform Database
## Bloomsbury Visual Arts Hub
## Crisil Research
Capitaline AWS Database (To use this facility please register using IITB email id)
CMIE Database
Dataful (Click on “Sign In” and then click on “Sign Up with IP”)
## EMIS
EPWRF India Time Series
## Euromonitor Passport
## Grove Music Library
HS Talks Business and Management Collection
## Indian Boards Database
ICSD : Inorganic Crystal Structure Database
IndiaStat (Click IP Login)
## Inspec Database
## Journal Citation Report
LSEG Workspace (Previously known as Refinitiv : For Login contact Journals Section)
MathSciNet
ProQuest
## Reaxys Database
SciFinder Scholar
Scite (Smart Citation)
## SCOPUS
## Statista
The Ken (For Registration)

Yes. I checked the databases you listed specifically against the data requirements of our proposed project.
The important distinction is that we don't merely need "stock prices." We need an option panel over time:
ideally including expired contracts, because otherwise we cannot do a proper historical walk-forward study.
Short answer
The two sources I would investigate first at IIT Bombay are LSEG and Bloomberg.
- LSEG Workspace — probably your best option
This is the most interesting one on your list.
LSEG explicitly provides exchange-traded options data, including:
US options
international options
option reference data
historical contracts
pricing
implied volatility
The Ken (For Login)
Tracxn Database (User Guide)
## Venture Intelligence Database
Web of Science
YNOS Venture Engine
## Standard Databases
ASTM Digital Library With Standards
IEC Standards
## Indian Standards
ISO Standard (Custom Collection)
These and also any open source like yahoo and all for this particular project?
(t,S ,K,T,C/P,P ,Volume,OI,IV,...)
tt
SourceUS optionsIndian optionsHistorical optionsUseful for our
project?
LSEG WorkspaceYesYes, depending on subscribed
exchange package
Yes, potentially extensive⭐⭐⭐⭐⭐
Bloomberg TerminalYesYesYes, depending on terminal/data
entitlement
## ⭐⭐⭐⭐⭐
NSENoYesYes⭐⭐⭐⭐
CapitalineNoSome derivatives/market dataNeed to verify exact options history⭐⭐⭐
CMIE ProwessNoUnderlying equities, fundamentalsYes⭐⭐
DatafulPrimarily India
datasets
Possibly derivatives-related datasetsDepends on dataset⭐⭐
Yahoo FinanceCurrent option chainsLimited/poor for Indian optionsNot sufficient for historical option
panel
## ⭐
Other open-source
sources
SometimesSometimesUsually fragmented⭐–⭐⭐

## Greeks
volatility surfaces
LSEG says its derivatives coverage spans 100+ exchanges, and its options reference data includes both active and expired options. Its stated history
includes selected contracts from 2000 and higher-quality options histories from 2018 depending on the product.
More importantly, LSEG explicitly lists OPRA US options market data among its derivatives datasets.
So conceptually:
could give us:
and potentially Indian exchange derivatives as well.
## BUT
This is the critical caveat:
I cannot conclude from IITB's library listing alone that your particular IITB LSEG Workspace subscription includes historical US/Indian options
pricing.
IITB has access to LSEG Workspace, but the exact data entitlements are subscription-dependent.
So this is the first thing I would check with the library/data desk.
Ask them specifically:
That wording matters.
- Bloomberg Terminal — also potentially excellent
You have:
That is potentially very useful.
Bloomberg provides options information through the terminal, including option chains and derivatives analytics.
For our project, however, don't just ask:
Obviously it can.
## Ask:
## LSEG+1
## LSEG
## LSEG
## US:
## S&P 500
## SPY
individual equities
options
strikes
expiries
prices
volume
## OI
## IV
## Greeks
## ...
"Does IIT Bombay's LSEG Workspace subscription include historical exchange-traded equity/index options data for US markets (OPRA/US
options) and NSE India? In particular, can we download historical option contract-level data containing trade date, expiration, strike, call/put,
price, volume and open interest?"
Bloomberg — Terminal available at Central Library, Circulation Area
"Can Bloomberg show options?"
Plain text

Because our project requires historical reconstruction, not simply looking at today's chain.
## US
Bloomberg should be particularly attractive for:
because the US options market is enormously deep.
## India
## Potentially:
but again, verify the exact historical entitlement.
- NSE itself — surprisingly useful for India
If we decide to do the project on India, NSE is actually a very interesting source.
The NSE option chain exposes:
strike
call/put
## LTP
bid
ask
volume
open interest
implied volatility
for equity derivatives.
NSE also provides historical contract-wise price-volume data with fields including:
date
expiry
open/high/low/close
## LTP
settlement price
number of contracts
turnover
open interest
change in OI
underlying value.
And NSE explicitly provides historical F&O data through its paid historical-data service, including F&O order/trade data.
So there is a possible India pipeline:
However, there is a problem.
The freely accessible NSE historical contract interface currently restricts the selectable time period to 90 days.
So for a multi-year academic dataset, we'd need either:
- IITB's licensed data source, or
- NSE's paid historical dataset, or
- another provider.
Can I download historical option-chain/contract-level data for expired US equity/index options and/or NSE options, including strike,
expiration, call/put, price, volume and open interest?
S&P500/SPY/individual US stocks
NIFTY, BANKNIFTY, NSE stocks
NSE India+1
NSE India
NSE India

## →
NSE optionsIV / risk-neutral distribution→ML→portfolio
NSE India

Also, NSE's website explicitly places restrictions on copying/aggregating data from the site, so I would not build a research pipeline by scraping the
live option-chain webpage.
## 4. Capitaline
Capitaline is definitely useful for the Indian side of the project, but I wouldn't rely on it yet for options.
Capitaline says its database includes market data on Indian securities, derivatives and commodities.
However, what I can verify publicly is much stronger for:
company fundamentals
equity prices
financial statements
ratios
corporate data
than for the full historical option-contract panel we need.
## So:
but:
until we inspect your IITB subscription/interface.
- CMIE Prowess — useful, but NOT for options
CMIE Prowess is primarily an Indian company database.
It has:
financial statements
quarterly data
daily share prices
corporate actions
total returns
company characteristics
and long historical coverage.
So it could supply:
but I would not expect it to supply the option chain required by our project.
It could nevertheless become useful later for additional ML features.
- Yahoo Finance — don't use it as the main options source
This is where I'd be particularly careful.
Yahoo is fine for:
and basic current option-chain information.
But our project requires something much more demanding:
NSE India
## Capitaline
Capitaline→ Excellent supplementary Indian equity/fundamental data
## Capitaline⇒

confirmed historical options dataset
## CMIE+1
Indian stock fundamentals+historical stock returns
## S
t

across many historical dates.
Yahoo Finance is not a sufficiently reliable institutional historical options database for this project.
So I would use Yahoo for:
quick prototyping
underlying prices
sanity checks
but not as the research dataset.
- There is an even more important issue: US vs India
For this project, I would actually lean toward US data if LSEG/Bloomberg gives us proper historical access.
## Why?
Because our proposed model needs a reasonably rich cross-section:
The US options market gives us an enormous cross-section.
That makes it much easier to estimate:
and features such as:
For example:
alone can give us a huge amount of information.
And then we could construct a portfolio of, say:
liquid US equities depending on data availability.
- The dataset we actually need
Before selecting US vs India, I would define the minimum dataset.
## Underlying
For each stock:
## Option
For each contract:
## {
## C
## ,
## P
## }

t,K,Tt,K,T
t=1
## T
stock×date×strike×maturity
Risk-neutral density
IV,skew,term structure,VRP,risk neutral moments.
SPY options
## 100−500
date
close
adjusted close
returns
volume
Plain text
Plain text

## Ideally:
although we can calculate these ourselves.
## Additional
## Then:
is enough to start building the research pipeline.
- One particularly important thing for our project
We don't actually need option prices predicted by ML as the first step.
I'd revise our project architecture slightly.
We can extract the risk-neutral distribution from observed option prices:
using something like the Breeden-Litzenberger relationship:
## Then:
giving:
Then the interesting problem becomes:
using:
Markov/regime model
date
underlying
option_type
strike
expiration
bid
ask
mid
last
volume
open_interest
implied_volatility
delta
gamma
vega
theta
risk_free_rate
dividend_yield
market_return
Options panel+Underlying panel+Risk-free rates
C(K,T)→q (S )
tT
q(K)∝
## ∂K
## 2
## ∂C(K,T)
## 2
q (S )→
tT
risk-neutral moments
## E
## [
## S
## ],
## V
a
r
## (
## S
## ),
## Sk
e
w
## (
## S
## ),...
## Q
## T
## Q
## T
## Q
## T
Q-information→P-forecast
Plain text
Plain text

## ML
risk-premium model
and then portfolio construction.
That is much more defensible than simply training an ML model to predict option prices.
What I would do at IITB
First priority — LSEG
Go to the LSEG Workspace terminal and determine whether you can access:
## US:
## SPX
## SPY
individual US equity options
historical expired contracts
## India:
## NIFTY
## BANKNIFTY
NSE equity options
historical expired contracts
Second priority — Bloomberg
Check the same thing.
Third — NSE
Determine what historical F&O data IITB can legally obtain/download.
## Fourth — Yahoo/open-source
Use only for prototyping and cross-checking.
My current ranking for our project
If the data is available through IITB:
And I would prefer US options over Indian options initially, unless IITB's Indian options history is substantially easier to obtain.
The next thing I would do is not start coding yet. First, we should determine exactly what LSEG Workspace and Bloomberg at IIT Bombay can
export. Once we know that, we can choose US vs India based on the actual available historical option panel rather than guessing.
LSEG≈Bloomberg>NSE>Capitaline/CMIE>Yahoo
Bruh forget bloomberg this is the updated list:
From any one of this, would I be able to get the options data for US or Indian Market?
## Databases / Standard Databases
ABI/Inform Database
## Bloomsbury Visual Arts Hub
## Crisil Research
Capitaline AWS Database (To use this facility please register using IITB email id)
CMIE Database
Dataful (Click on “Sign In” and then click on “Sign Up with IP”)
## EMIS
EPWRF India Time Series
## Euromonitor Passport
## Grove Music Library

Yes — with the updated list, the answer is much clearer. I checked the relevant providers rather than assuming that every finance database has
options.
Bottom line
For our project, among the databases you listed:
 Most promising
##  Open-source
HS Talks Business and Management Collection
## Indian Boards Database
ICSD : Inorganic Crystal Structure Database
IndiaStat (Click IP Login)
## Inspec Database
## Journal Citation Report
MathSciNet
ProQuest
## Reaxys Database
SciFinder Scholar
Scite (Smart Citation)
## SCOPUS
## Statista
The Ken (For Registration)
The Ken (For Login)
Tracxn Database (User Guide)
## Venture Intelligence Database
Web of Science
YNOS Venture Engine
## Standard Databases
ASTM Digital Library With Standards
IEC Standards
## Indian Standards
ISO Standard (Custom Collection)
These and also any open source like yahoo and all for this particular project?
DatabaseUS optionsIndian optionsHistorical contract-level options?Verdict
LSEG WorkspaceYESPotentially YESYESBest option if IITB subscription includes
it
CapitalineNoSome derivatives dataPossibly, but not confirmed for full
option panel
Useful backup for India
DatafulUnclearPossiblyDataset-dependentInvestigate
CMIE/ProwessNoNo options—Useful for stock/fundamental data only
EPWRFNoPrimarily macro/financial time seriesNot suitable for option chainNot our options source
CRISIL ResearchNoMostly Indian
market/fundamental/credit research
Not a suitable options panel sourceNot primary
Everything elseNoNo—Not relevant
SourceOptionsHistorical optionsUse
Yahoo FinanceUSVery limited for our purposePrototype/sanity check

- LSEG is the one I would investigate first
Your list has:
This is by far the strongest candidate.
LSEG's own documentation confirms that it has global exchange-traded options data, including historical options. Their options reference dataset
covers 100+ regulated exchanges across 35 countries, with more than 120 million expired options where exchange coverage is available.
For the US specifically, LSEG provides OPRA data, which consolidates data from 17 US options exchanges and covers US equity, index and ETF
options. It includes:
last-sale data
quotes
## NBBO
contract specifications
expiration/series information
historical observations
analytics/Greeks where available
That is almost exactly the type of data our project needs.
## So:
The important question is whether IIT Bombay's particular LSEG subscription gives you access to the relevant historical dataset.
Don't assume that because IITB has "LSEG Workspace" listed, every LSEG dataset is automatically included.
- What about Indian options through LSEG?
This is also plausible.
LSEG says its derivatives coverage spans global regulated exchanges across Asia-Pacific as well as North America.
But again, we need to distinguish:
from
The second one needs to be verified.
For our project, I'd specifically ask the IITB library:
If yes, India becomes very viable.
SourceOptionsHistorical optionsUse
NSEIndianSome historical F&O dataPotentially useful
Stooq / Alpha Vantage etc.Generally not suitableNoDon't depend on them
GitHub datasetsSometimesDataset-dependentUseful if properly documented
LSEG Workspace (Previously Refinitiv)
## LSEG
## LSEG
US options→LSEG: YES
## LSEG
LSEG as a company has Indian options data
IITB's LSEG subscription gives students access to the historical Indian options data.
Does our LSEG Workspace subscription provide historical NSE equity/index options data at the contract level, including trade date, strike,
expiry, call/put, price, volume and open interest?

- Capitaline is interesting for Indian options
I initially wouldn't have put much weight on Capitaline, but after checking its current product information, there is evidence that it covers
derivatives.
Capitaline explicitly says its market-data coverage includes securities, derivatives, and commodities traded on Indian stock markets.
More specifically, its TradeCues product has a:
section with open-interest and price analysis.
So I would classify Capitaline as:
but not yet
The publicly available documentation doesn't establish that you can export a panel like:
for thousands of historical contracts.
That is what we need to verify inside the IITB Capitaline account.
- CMIE/Prowess: useful, but not for options
CMIE Prowess is actually very useful for the portfolio side.
It provides Indian:
stock prices
corporate actions
daily total returns
financial statements
company fundamentals
and has time-series data going back to 1990.
So we could potentially have:
but I would not use CMIE as our options source.
It can complement an options dataset.
For example:
could be useful.
## Capitaline+1
"Scans on Derivatives Data"
TradeCues
Indian derivatives: YES

full historical option-chain research dataset: confirmed
date
underlying
strike
expiry
## CE/PE
bid
ask
close
volume
## OI
## IV
## Prowessdx
CMIE→Indian stocks + fundamentals
NSE/LSEG options+CMIE fundamentals
Plain text

## 5. Yahoo Finance
Yahoo is useful, but not for the dataset we ultimately want.
Yahoo does provide option chains for US securities, and there are open-source libraries/APIs that expose:
expiration dates
strikes
calls
puts
For example, the open-source Yahoo API implementations demonstrate retrieving option expiration dates and option contracts.
But there's a major issue:
We need historical option chains.
Suppose our training observation is:
We need to know:
Yahoo's ordinary historical-price infrastructure isn't designed to provide that complete historical option surface. Yahoo's own documentation is
primarily about historical price/dividend/split data and notes that downloadable historical data availability varies by instrument.
## So:
But it is perfectly fine for building the first prototype.
- NSE is probably our strongest free/official Indian fallback
If we decide:
then NSE's own derivatives data becomes important.
We can potentially obtain historical contract-level F&O data containing things like:
The difficulty is how much historical data we can access conveniently and under what licensing/subscription arrangement.
For a one-month academic project, I'd strongly prefer a clean institutional download over building a scraper.
- What we actually need for the proposed research
This is the important part.
For the project:
we don't need every possible option.
Our minimum viable dataset is something like:
Option data
GitHub
t=2021-06-01
What did the entire option surface look like on 2021-06-01?
## Yahoo Help
Yahoo=our final research dataset

## India
expiry,K,option type,price,volume,OI
Option-implied information →  →  transformation → ML/regime model → portfolioQP
(t,S,K,T,Call/Put,P,V,OI)

where:
= observation date
= underlying price
= strike
= expiry
= option price
= volume
= open interest
Then we can calculate:
ourselves.
And from the cross-section:
we can estimate the risk-neutral distribution.
## Potentially:
and extract:
etc.
Then our ML/regime model attempts:
That's the interesting part.
- Therefore, I'd rank your available options like this
If we want US
- LSEG Workspace
This is the one to investigate at IITB.
## 2. Yahoo
Only for prototyping, not final historical research.
- Other open-source datasets
Potentially useful if we find a clean historical dataset, but I wouldn't design the project around one before verifying it.
If we want India
- LSEG Workspace
t
## S
## K
## T
## P
## V
## OI
## IV
## C(K,T)
q(S )∝
## T

## ∂K
## 2
## ∂C(K,T)
## 2
## E
## [
## S
## ]
## Q
## T
## V
a
r
## [
## S
## ]
## Q
## T
## Sk
e
w
## [
## S
## ]
## Q
## T

Q-information→P-distribution
## ⭐⭐⭐⭐⭐
## ⭐⭐
## ⭐

if IITB's subscription includes NSE historical options.
## 2. Capitaline
Definitely has Indian derivatives coverage, but we need to verify the granularity and historical export.
## 3. NSE
Potentially excellent official source, subject to historical-data accessibility/licensing.
## 4. CMIE
For underlying stocks/fundamentals, not options.
One thing I would do before choosing US vs India
Don't choose the market yet.
Go into LSEG Workspace at IITB and Capitaline AWS and see whether you can actually retrieve an historical option contract.
For example, try to answer:
and:
If either works, we have our dataset.
If you want, I can next give you a very specific checklist of exactly what fields/data frequency/history we need to verify in LSEG, Capitaline and
NSE, so you can spend 10–15 minutes checking IITB access and come back with the result.
Good. Now we should stop adding papers for the moment and use those four to reconstruct the research landscape.
The next step I suggest is that you tell me, in your own words, what you understood from each paper—even if it is rough.
For each of the four, give me just:
- What problem does the paper solve?
- What is their methodology?
- What data do they use?
- What is their main result?
- What did you find confusing / unclear?
You don't need to write a polished summary. Even something like:
is enough.
Then I can do something much more useful than another literature search:
We'll construct this map
## ⭐⭐⭐⭐⭐
## ⭐⭐⭐
## Capitaline+1
## ⭐⭐⭐⭐
## ⭐⭐
## Prowessdx
Can I obtain all NIFTY options on 15 January 2024, including strike, expiry, CE/PE, price, volume and OI?
Can I obtain all SPY/SPX options on 15 January 2024, with the same fields?
I read the abstract, intro, and conclusion of all the 4 papers
Paper 1: They take option IV and skewness → estimate something → put it into Markowitz. I'm not fully clear how they get expected returns.

## →
Paper 1what it establishes

## →
Paper 2what it adds

## Then:
That last transition is the important one. We should not assume that adding Markov + ML + martingale automatically makes the project novel. We
need to identify exactly what those four papers leave open and then formulate a contribution that can actually be completed in one month.

## →
Paper 3Q vs P / martingale framework

## →
Paper 4where ML enters

## →
Existing literature
## →
what is already done
## →
what is missingour project
- DeMiguel‡
The paper tried to examine whether one can use option-implied information to improve the
selection of mean-variance portfolios with a large number of stocks
Use of option implied volatilities and correlations to improve out of-sample performance of
mean-variance portfolios invested in only risky stocks. Next,  examine the use of risk-premium
corrected option-implied correlations to improve the performance of minimum-variance
portfolios. Finally, to improve the out-of-sample performance of mean-variance portfolios they
consider the use of option-implied volatility, risk premium for stochastic volatility, and option-
implied skewness.
S&P 500 stocks and options data and also the derived options data like IV and other stuffs
They found option-implied volatilities can lead to a significant improvement in portfolio
volatility. However, option-implied correlations are less useful in reducing portfolio volatility
and also, forming portfolios using expected returns that exploit information in option-implied
model-free skewness and implied volatility achieve a higher Sharpe ratio than portfolios that
ignore option-implied information; even after adjusting for transaction costs. They also
conclude that prices of stock options contain information that can be useful for improving the
out-of-sample performance of portfolios.
I didn’t understand the idea behind, how did they model the system exactly in detail to include
all these options features in deciding the optimal portfolio weights and also how did they
conclude the IV surface is very helpful, what metrics did they use to deduce that part.
## 2. Bianchia
They suggest a portfolio selection framework based on option implied information and
multivariate non-Gaussian models.
They considered two models, which are a multivariate extension of the normal tempered stable
(NTS) model and the generalized hyperbolic (GH) model and the connection between the
historical measure P and the risk-neutral measure Q is given by the Esscher transform.
They didn’t mention any particular data, as this one’s the theoretical implementation of the two
models idea they have proposed.
First, they proposed a multivariate option pricing framework based on heavy tails, negative
skewness and asymmetric dependence. Second, they conduct a large scale empirical study
based on a joint calibration-estimation of the univariate option surfaces and of the time series
of log-returns has been proposed. Third, show how to use the proposed framework to evaluate
portfolio risk measures. Finally, the multivariate non-Gaussian models proposed in this work
together with the double calibration approach can be used to explore the interdependencies in
financial markets, not only for solving portfolio allocation problems, but also as a statistical tool
for financial stability purposes.
I didn’t understand how they quantified the two models i.e., NTS and GH. And how did they
incorporate it into option pricing.
## 3. Chernov
The paper addresses the challenge of jointly estimating objective (historical) and risk-neutral
probability measures to accurately price equity options while reconciling time-series dynamics
with cross-sectional option prices.
They propose a unified estimation framework using a Efficient Method of Moments (EMM)
approach combined with stochastic volatility and jump-diffusion models to simultaneously fit
underlying asset returns and option prices.

Your understanding is broadly correct. More importantly, your four summaries reveal that the papers are not four independent ideas—they form a
fairly coherent chain:
But there are some important gaps in your current understanding. Before deciding our contribution, I would resolve those gaps.
- DeMiguel — this should become our portfolio baseline
Your interpretation is correct.
The important thing you missed is how option information enters the portfolio problem.
They aren't simply saying:
Instead, think of the pipeline as:
The fundamental portfolio problem remains something like
The research question is:
That's why their evaluation is ultimately based on out-of-sample portfolio performance, not simply whether the IV surface "looks informative."
The relevant metrics are things such as:
realized portfolio volatility
Sharpe ratio
portfolio returns
turnover
transaction costs
Daily S&P 500 index returns along with S&P 500 index call option prices across various
maturities and strike prices.
Incorporating both stochastic volatility and price jumps is essential for joint consistency
between objective time-series return models and risk-neutral option pricing models,
significantly reducing option pricing errors.
The precise parameterization of the risk premium specifications linking the physical and risk-
neutral measures and the empirical identification of volatility jump sizes were somewhat
complex and hard to follow.
## 4. Bali
The paper addresses the challenge of predicting individual equity option returns in a high-
dimensional setup, where traditional linear models struggle due to complex nonlinearities and
interaction effects among numerous predictive features.
They implement machine learning methods (such as neural networks and tree-based models)
combining options-specific characteristics, underlying stock signals, and macroeconomic
variables to forecast out-of-sample option returns and construct long-short portfolios.
Large-scale US equity options dataset (OptionMetrics) alongside underlying stock
characteristics (CRSP/COMPUSTAT) and macroeconomic indicators.
Machine learning models significantly outperform traditional benchmark linear models in
predicting option returns out-of-sample, generating economically and statistically significant
Sharpe ratios even after accounting for transaction costs and market friction.
It was not entirely clear which specific categories of features (e.g., options-level vs. stock-level
characteristics) contributed most to the predictive performance during market stress periods
versus normal market conditions.
Option surface→Q-distribution→P-distribution→forecast→portfolio
"IV is high → increase/decrease the stock weight."
Option prices→option-implied quantities→estimates of moments→
## (

## ,)→
μ^Σ
## ^
## Markowitz→w
## ∗
w
μ−
w
max
## ⊤
w
## Σ
w
## 2
λ
## ⊤
Can option information produce better estimates of  and/or  than conventional historical estimates?μΣ

statistical significance of performance differences
So when you later read the methodology, don't think:
## Think:
That is the key.
- Bianchi — your biggest conceptual gap
Your question:
is exactly the right question.
But don't start by trying to understand all the mathematics of NTS/GH.
At the conceptual level, they are doing:
and
Then they impose a particular relationship:
through the Esscher transform.
The NTS/GH models give them a flexible distribution that can represent:
fat tails
skewness
dependence between assets
rather than assuming simple Gaussian returns.
So their contribution is basically:
You don't need to reproduce NTS/GH yet.
For our project, the lesson is:
There is a measure transformation/model connecting  to .
That's going to be extremely important if we pursue your idea.
- Chernov — this explains why the Bianchi idea is necessary
Your summary is accurate.
Chernov is effectively asking:
"How did they use IV as a trading signal?"
"Which component of the Markowitz inputs did they replace/improve using option information?"
"How did they quantify NTS and GH and incorporate it into option pricing?"
historical returns→estimate distribution under P
option prices→information about distribution under Q
## P⟷Q
"Let's build a sufficiently flexible multivariate distribution, make it consistent with option prices under , connect it to historical returns under ,
and then use the resulting distribution for portfolio risk/selection."
## QP
Option prices do not directly give us the investor’s expected return.
## QP
Can we construct a model that is simultaneously consistent with historical returns and observed option prices?

Their architecture is approximately:
while simultaneously:
and the model must connect the two.
The important takeaway for us is not EMM itself.
It is:
and conversely:
Chernov's joint estimation attempts to prevent those two worlds from becoming disconnected.
This is directly relevant to our project.
- Bali — this tells us how we can use ML
You understood this one well.
The important thing to extract is the research methodology:
then:
and evaluate strictly out-of-sample.
This is where your existing ML experience becomes useful.
You don't need Bali to teach you Random Forest/XGBoost/NN.
The useful part is:
Now look at what happens when we put the papers together
This is where I think the project becomes interesting.
## Existing Paper 1
DeMiguel
## Existing Paper 2
## Bianchi
## Existing Paper 3
Historical S&P returns→P-dynamics
S&P option prices→Q-pricing
A model can fit historical returns beautifully but price options badly.
A model can fit option prices beautifully but describe physical returns poorly.
## X =
t
[option characteristics,stock characteristics,macro variables]
## =y^
t+1
f(X )
t
How do we turn a huge option dataset into economically meaningful predictive features and then evaluate whether those predictions
actually improve a portfolio?
Option information→portfolio
P↔Q→portfolio risk

## Chernov
## Existing Paper 4
## Bali
And here's the interesting gap
The papers give us four pieces:
but they don't simply combine them into the exact architecture we're considering.
Our potential research question could therefore become:
And we can introduce your Markov/regime-switching component:
such that:
rather than assuming one stationary relationship between option-implied -information and future -returns.
That gives:
But I would make one correction to our earlier idea
You originally said:
I would not do that.
It creates an unnecessary intermediate problem:
Why predict option prices if we already have observed option prices?
## Instead:
and then:
return dynamics+option prices→joint P/Q model
high-dimensional option/stock/macro features→ML→future option returns
## Q
## P
## Q↔P
## ML
Can machine learning exploit option-implied risk-neutral information to estimate economically useful physical-measure return distributions,
and does incorporating these forecasts into portfolio optimization improve out-of-sample performance?
## Z

## =
t
latent market regime
## P(R ∣
t+1
## X ,Z )
tt
## QP
Options→Q-features→Regime→ML→P-forecast→Portfolio
"use ML algos to predict option pricing and use that to get an expected stock price under no-arbitrage"
## ML→
## →
Option PriceQ→P

Observed option prices→Q-information
Q-information→ML/regimemodel→P

The ML problem should be the Q-to-P/investment-information problem, not merely option-price prediction.
That is also much more aligned with your four papers.
The project now has three distinct layers
Layer 1 — Financial engineering
From option prices:
derive:
This is the IE612 component.
Layer 2 — Statistical/ML
Use those variables to estimate:
and potentially:
conditioned on regime:
This is your ML component.
## Layer 3 — Portfolio
## Use:
in:
and compare against:
historical Markowitz
option-implied baseline
ML without options
proposed option + regime + ML model
This is the economic validation.
One thing I would NOT add yet
Don't add all of these simultaneously:
## HMM
Markov chain
## NTS
## GH
## Esscher
stochastic volatility
jumps
## C(K,T),P(K,T)
IV,skew,term structure,Q-moments,...
μ^
t+1

## ,
σ^
t+1
skew
## ^
t+1
## Z .
t
## (

## ,)
μ^Σ
## ^
w=
## ∗
arg w − ww
w
max[
## ⊤
μ^
## 2
λ
## ⊤
## Σ
## ^
## ]

Black-Scholes
XGBoost
## Random Forest
neural network
## LSTM
## RL
That would turn into a kitchen-sink project and become impossible to explain.
Instead, we need to determine:
My current candidate is:
But we haven't established that this is actually novel yet.
That's the next research task I would do.
We should now go one level deeper into the methodology of these four papers, specifically extracting:
- What exactly goes in
- What exactly comes out
- Mathematical transformation
- Data required
- Portfolio construction
- Evaluation metrics
- What each paper does NOT do
Once we have that table, we can identify the missing cell(s). That missing cell is where our one-month project should live.
Yes. We can freeze the literature set at 5 papers for the initial project-design phase.
One correction in terminology: the extra paper, Ulrich, Walther, Rothfuss & Ferreira, “Forward-looking P” (2019), is not itself the gap. It is important
because it closes a major part of the apparent gap: it already uses option-implied risk-neutral information with a neural network to estimate the
physical return distribution.
So the final reading set is:
What is the minimum new mechanism that produces a defensible contribution?
Regime-conditioned ML estimation of the physical return distribution using option-implied risk-neutral information, followed by portfolio
optimization.
I think this is good to go, We should keep it final and the extra recommended paper which is a gap
here has to be added
Pasted text
#PaperRole in our project
1DeMiguel et al. (2013), Improving Portfolio Selection Using Option-Implied
Volatility and Skewness
Option information → portfolio optimization
2Bianchi & Tassinari (2020), Forward-looking Portfolio Selection with
Multivariate Non-Gaussian Models
– connection + portfolio risk
3Chernov & Ghysels (2000), A Study Towards a Unified Approach to the Joint
Estimation of Objective and Risk Neutral Measures
Joint  modelling
4Bali et al. (2023), Option Return Predictability with Machine Learning and Big
## Data
ML + option information + rigorous OOS prediction
5Ulrich et al. (2019), Forward-looking PCritical prior art for option-implied -information →
physical -density using neural networks
## PQ
## P/Q
## Q
## P
Pasted text(20261006-205209).txt
## Document

The fifth paper is particularly important because its architecture is already close to:
using a mixture-density network.
That changes how we should formulate our eventual contribution. We cannot claim novelty for merely:
Likewise, adding an HMM by itself is insufficient, because option-implied skewness regimes combined with portfolio optimization have already been
studied.
The potentially defensible direction is narrower:
in the relationship
and testing whether that persistence gives incremental value over a sufficiently flexible non-regime model and ordinary time-varying calibration. The
audit explicitly identifies this as the candidate extension, while stressing that its novelty is still provisional.
So I would now consider these 5 papers our core literature pack. We don't need another batch of papers yet. The next step is to extract the actual
mathematical/model architecture from these five and turn it into a concrete one-month implementation with a clearly defined baseline, proposed
model, and novelty test.
Options→Q-moments→neural density model→  (r)p
t
Pasted text
“Use ML to transform option-implied information into physical expected returns.”
Pasted text
persistent latent regime dependence
Q-information→P-density
Pasted text