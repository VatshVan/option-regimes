# Research Assessment: SPX Options Data Feasibility for IE 612

**Project Title:** Regime-Conditioned Mapping from Option-Implied Risk-Neutral Information to Physical Return Distributions  
**Course & Scope:** IE 612 (Introduction to Financial Engineering), 1-Month Empirical Research Project  
**Author:** Quantitative Research & Engineering Team  
**Date of Audit:** October 21, 2026  
**File Location:** `SPX_data_research.md`  

---

## 1. Executive Verdict & Feasibility Recommendation

### Overall Recommendation: **CONDITIONAL GO (Feasible with Methodological Scope Controls)**

Free, historical S&P 500 index options (SPX) data sourced from **OptionsDX** can support the primary research question formulated in [`implementation.md`](file:///C:/Users/Vatsh%20Van/Desktop/MECH_5-SEM/IE%20612/Project/implementation.md) and [`project_implementation_idea.md`](file:///C:/Users/Vatsh%20Van/Desktop/MECH_5-SEM/IE%20612/Project/project_implementation_idea.md):
$$\text{At date } t, \quad p(r_{t+1} \mid Q_t, X_t, \pi_t) \quad \text{versus} \quad p(r_{t+1} \mid Q_t, X_t)$$
where $Q_t$ denotes option-implied risk-neutral features, $X_t$ denotes observable historical market state variables, $\pi_t$ is a filtered latent regime probability from a Hidden Markov Model (HMM), and $r_{t+1} = \log(S_{t+1}/S_t)$ is the physical next-day close-to-close log return.

```
                    +------------------------------------+
                    |        SPX Option Chains           |
                    |     (OptionsDX EOD 2010-2020+)     |
                    +-----------------+------------------+
                                      |
                                      v
                    +------------------------------------+
                    |  Data Cleaning & Filtering Gate    |
                    |  - Remove non-positive bids (Bid>0)|
                    |  - Bid-ask spread relative filter  |
                    |  - Invert synthetic forward F_t    |
                    |  - Exclude DTE < 7 and DTE > 60    |
                    +-----------------+------------------+
                                      |
                         +------------+------------+
                         |                         |
                         v                         v
        +--------------------------------+  +--------------------------------+
        |   Feature Extraction Q_t       |  |  Validation Anchor (Free Cboe) |
        |   - Martin (2017) SVIX         |  |  - Cboe VIX History CSV        |
        |   - Bakshi et al. (2003) QSkew |  |  - Cboe SKEW History CSV       |
        |   - Term structure slope       |  |  Cross-check: Corr(SVIX,VIX)>0.98
        +----------------+---------------+  +--------------------------------+
                         |
                         v
        +--------------------------------+
        | Next-Day Density Forecast      |
        | p(r_{t+1} | Q_t, X_t, \pi_t)   |
        +--------------------------------+
```

### Key Findings & Justifications
1. **Critical Data Quality Advantage over NIFTY Bhavcopy `[Verified Fact]`:** Unlike free National Stock Exchange of India (NSE) historical reports—which only provide contract-level trade OHLC and trade volumes without bid/ask quotes—OptionsDX provides contract-level **Bid and Ask quotes** (`C_BID`, `C_ASK`, `P_BID`, `P_ASK`) alongside the underlying price (`UNDERLYING_LAST`). This makes quote-midpoint estimation, spread-based liquidity filtering, and arbitrage-aware implied volatility surface fitting technically possible.
2. **Free Historical Availability `[Verified Fact]`:** OptionsDX lists historical SPX full option chains from **2010 through 2023**. End-of-Day (EOD) frequency files for historical years (e.g., 2010–2020+) are available at **$0.00** at web checkout without requiring payment credentials, delivered directly via account download links.
3. **Primary Scope Limitation — Missing Open Interest `[Verified Fact]`:** OptionsDX CSV files **do not contain Open Interest (OI)**. Illiquidity filtering cannot rely on open interest thresholds and must instead enforce strict bid-ask spread constraints ($(Ask - Bid)/Mid \le \tau$), minimum trading volume, and non-zero bid filters.
4. **Settlement & Timestamp Discrepancy `[Verified Fact]`:** SPX options traditionally traded on Cboe until 16:15 Eastern Time (ET), whereas the cash S&P 500 index (`^GSPC`) stops calculating at 16:00 ET. In addition, standard monthly SPX options are AM-settled (settling against the Friday morning Special Opening Quotation, "SET"), whereas weekly/end-of-month options (SPXW) are PM-settled (settling against the 16:00 ET cash close). OptionsDX does not provide a separate contract root identifier (`SPX` vs `SPXW`). To prevent synthetic arbitrage, the project must extract the implied synthetic forward $F_{t,T}$ directly via put-call parity at each maturity rather than relying on the reported cash index close.
5. **Precalculated Greeks/IV Must Be Discarded `[Analytical Inference]`:** OptionsDX includes precalculated IV and Greeks, but the underlying pricing model, interest rate curve, and dividend assumptions are completely undocumented. For academic validity matching [Ulrich et al. (2019)](file:///C:/Users/Vatsh%20Van/Desktop/MECH_5-SEM/IE%20612/Project/Papers/ssrn_id3437281_code3012080.pdf) (*Forward-looking P*), the project must independently calculate mid-prices, estimate forward levels, and compute model-free moments (or SVI implied volatility).
6. **External Validation Anchor `[Verified Fact]`:** Cboe publishes official daily historical time series of the **VIX Index** (`VIX_History.csv`) and **SKEW Index** (`SKEW_History.csv`) for free on its CDN. These provide an external ground-truth validation anchor: model-free implied volatility and risk-neutral skewness extracted from OptionsDX must demonstrate near-perfect correlation ($\rho > 0.98$) with Cboe's official benchmarks.

---

## 2. Source Landscape & Comparison Matrix

The table below benchmarks all potential options data sources evaluated for this project:

| Feature / Criteria | OptionsDX SPX (Candidate) | Cboe DataShop Option EOD Summary | Cboe Official Daily Volatility CDN | DoltHub (`post-no-preference`) | WRDS / OptionMetrics (Institutional) | NSE Public Bhavcopy (NIFTY Baseline) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Data Provider** | OptionX / OptionsDX | Cboe Exchange Inc. | Cboe Global Indices | DoltHub Community | Wharton / OptionMetrics | National Stock Exchange of India |
| **Pricing / Cost** | **$0.00 (Free)** for EOD historical years; $25–$50 for intraday/recent | **Commercial Paid**; $145–$240+ /sym/yr. Academic min $500 | **$0.00 (Free)** public CDN download | **$0.00 (Free)** open-source SQL/git database | **Institutional Subscription** (Free if IITB subscribed) | **$0.00 (Free)** public web interface |
| **Coverage Period** | 2010 – 2023 (monthly archives) | 2010 – Present (custom range) | 1990 – Present (daily series) | ~2019 – Present | 1996 – Present (rolling updates) | Multi-year historical archives |
| **Quote Frequency** | End-of-Day (EOD), 30m, 15m, 5m, 1m | 15:45 ET snapshot & EOD snapshot | 1 daily close per index | End-of-Day | End-of-Day closing quotes | Daily closing report |
| **Bid & Ask Quotes** | **Yes** (`C_BID`, `C_ASK`, `P_BID`, `P_ASK`) | **Yes** (NBBO bid/ask at 15:45 and EOD) | **No** (Index level only) | **Yes** (Bid and Ask) | **Yes** (Best bid and best offer) | **No** (Only trade OHLC, no bid/ask) |
| **Underlying Price** | **Yes** (`UNDERLYING_LAST`) | **Yes** (Underlying Bid/Ask at 15:45 & EOD) | **No** (VIX/SKEW levels) | **Yes** | **Yes** | **Yes** (Underlying index close) |
| **Strike & Expiry** | **Yes** (Full chain) | **Yes** (Full chain) | **N/A** (Index-level aggregate) | **Yes** (Full chain) | **Yes** (Full chain) | **Yes** (Full chain) |
| **Volume & Open Interest**| Volume: **Yes**; Open Interest: **No** | Volume: **Yes**; Open Interest: **Yes** | **N/A** | Volume: **Yes**; Open Interest: **Yes** | Volume: **Yes**; Open Interest: **Yes** | Volume: **Yes**; Open Interest: **Yes** |
| **Greeks & IV** | **Yes** (Precalculated, opaque model) | Optional add-on ("Calcs") | **N/A** | **Yes** (Precalculated) | **Yes** (Standardized Cox-Rubinstein/BS) | **No** |
| **Contract Identifier**| Ambiguous (No root `SPX`/`SPXW`) | Explicit (`Root` field distinguishes SPX/SPXW) | **N/A** | Equity/ETF ticker symbol | Explicit Option Symbol / SecId | Explicit contract symbol |
| **Universe Scope** | SPX, SPY, VIX, QQQ, select equities | Full OPRA market (US listed options) | VIX, VIX3M, SKEW, VVIX | US Equities & ETFs (SPY, QQQ; **NO SPX**) | All US equities, ETFs, and indices | NIFTY 50, BANKNIFTY, Indian F&O |
| **Redistribution Terms**| Non-commercial personal study; **Redistribution prohibited** | Commercial license; redistribution strictly barred | Public index time series; citation permitted | Open database license | Academic research only; redistribution barred | Academic fair use; no commercial redistribution |
| **Suitability for Project**| **High (Primary Option Surface)** | **High (Cost-prohibitive unless funded)** | **Essential (Validation & Fallback Q)** | **Ineligible (Contains SPY, not SPX)** | **Gold Standard (If IITB has active WRDS)** | **Low (Lacks bid/ask; OHLC proxy only)** |

*Sources & Citations:*
- OptionsDX Product & Terms: [optionsdx.com/product/spx-option-chain/](https://www.optionsdx.com/product/spx-option-chain/) `[1]`; [optionsdx.com/terms/](https://www.optionsdx.com/terms/) `[2]`.
- Cboe DataShop Option EOD Summary: [datashop.cboe.com/option-eod-summary](https://datashop.cboe.com/option-eod-summary) `[3]`.
- Cboe Academic Discount Policy: [cboe.com/services/market-data-services/academic-pricing/](https://www.cboe.com/) `[4]`.
- Cboe Volatility Indices CDN: [cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv](https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv) `[5]`.
- DoltHub Options Database: [dolthub.com/repositories/post-no-preference/options](https://www.dolthub.com/repositories/post-no-preference/options) `[6]`.
- NSE Historical Reports: [nseindia.com/all-reports-derivatives](https://www.nseindia.com/all-reports-derivatives) `[7]`.

---

## 3. OptionsDX SPX Dataset: In-Depth Verification

### 3.1 Availability, Pricing, and Delivery Verification
- **Free vs. Paid Tiers `[Verified Fact]`:** OptionsDX markets SPX options data under a variable pricing structure ranging from **$0.00 to $50.00** ([optionsdx.com](https://www.optionsdx.com/product/spx-option-chain/)). 
  - **End-of-Day (EOD) frequency:** Configured at **$0.00** for individual historical years (specifically verified across 2010 through 2020/2021).
  - **Intraday intervals:** Frequencies such as 30-minute, 15-minute, 5-minute, and 1-minute intervals are premium tiers costing between $25.00 and $50.00 per year/dataset.
  - **Cart & Checkout Workflow:** Adding the $0.00 EOD SPX year products to the shopping cart allows checkout with standard name/email registration. **No credit card or billing details are required**.
  - **Delivery Mechanism:** For free $0.00 orders, download links are provisioned **immediately on the account order page**, bypassing the 24-hour Citrix ShareFile provisioning delay required for paid products ([optionsdx.com/terms/](https://www.optionsdx.com/terms/)).

### 3.2 Exact Field Schema & Completeness Audit
The standard schema for OptionsDX US options files is laid out horizontally in a **wide format**, pairing Call and Put quotes for identical strikes on each row ([optionsdx.com/option-chain-field-definitions/](https://www.optionsdx.com/option-chain-field-definitions/)). 

The complete 33-column schema is verified as follows:

| Column Header | Field Name / Meaning | Data Type / Example | Status in OptionsDX | Required by Project? |
| :--- | :--- | :--- | :--- | :--- |
| `QUOTE_UNIXTIME` | Quote timestamp (Unix epoch) | `1583508900` | **Present** | Optional |
| `QUOTE_READTIME` | Readable timestamp (`YYYY-MM-DD HH:MM`) | `2020-03-06 16:00` | **Present** | **Essential** (Alignment) |
| `QUOTE_DATE` | Quote date (`YYYY-MM-DD`) | `2020-03-06` | **Present** | **Essential** |
| `QUOTE_TIME_HOURS`| Quote time expressed in fractional hours | `16.00000` | **Present** | Informational |
| `UNDERLYING_LAST`| Reported closing price of underlying S&P 500 | `296.38` (or index level `3300.50`)| **Present** | **Essential** |
| `EXPIRE_DATE` | Expiration date (`YYYY-MM-DD`) | `2020-04-17` | **Present** | **Essential** |
| `EXPIRE_UNIX` | Expiration date (Unix epoch) | `1587153600` | **Present** | Informational |
| `DTE` | Days till Expiry (hours / 24, assumes 16:00 close)| `42.00` | **Present** | **Essential** (Maturity selection) |
| `C_DELTA` | Call Delta | `0.48512` | **Present** (Precalc) | Discard (Recalculate) |
| `C_GAMMA` | Call Gamma | `0.00215` | **Present** (Precalc) | Discard |
| `C_VEGA` | Call Vega | `0.35410` | **Present** (Precalc) | Discard |
| `C_THETA` | Call Theta | `-0.04120` | **Present** (Precalc) | Discard |
| `C_RHO` | Call Rho | `0.15230` | **Present** (Precalc) | Discard |
| `C_IV` | Call Implied Volatility | `0.22450` | **Present** (Precalc) | Discard (Model opaque) |
| `C_VOLUME` | Call trading volume for the session | `142` | **Present** | **Essential** (Liquidity check) |
| `C_LAST` | Call last traded price | `45.20` | **Present** | Secondary |
| `C_SIZE` | Bid/Ask lot size (e.g., `100 x 100`) | `150 x 200` | **Present** | Informational |
| `C_BID` | Call closing bid quote | `44.80` | **Present** | **Essential** (Midpoint calculation) |
| `C_ASK` | Call closing ask quote | `45.60` | **Present** | **Essential** (Midpoint calculation) |
| `STRIKE` | Option strike price ($K$) | `3300.00` | **Present** | **Essential** |
| `P_BID` | Put closing bid quote | `41.20` | **Present** | **Essential** (Midpoint calculation) |
| `P_ASK` | Put closing ask quote | `42.00` | **Present** | **Essential** (Midpoint calculation) |
| `P_SIZE` | Put bid/ask lot size | `100 x 100` | **Present** | Informational |
| `P_LAST` | Put last traded price | `41.50` | **Present** | Secondary |
| `P_DELTA` | Put Delta | `-0.51480` | **Present** (Precalc) | Discard |
| `P_GAMMA` | Put Gamma | `0.00215` | **Present** (Precalc) | Discard |
| `P_VEGA` | Put Vega | `0.35410` | **Present** (Precalc) | Discard |
| `P_THETA` | Put Theta | `-0.03980` | **Present** (Precalc) | Discard |
| `P_RHO` | Put Rho | `-0.14820` | **Present** (Precalc) | Discard |
| `P_IV` | Put Implied Volatility | `0.22810` | **Present** (Precalc) | Discard |
| `P_VOLUME` | Put trading volume for the session | `210` | **Present** | **Essential** (Liquidity check) |
| `STRIKE_DISTANCE`| Absolute distance $|K - S|$ | `0.50` | **Present** | Informational |
| `STRIKE_DISTANCE_PCT`| Percentage distance $(K - S) / S$ | `0.00015` | **Present** | Informational |
| **`OPEN_INTEREST`**| Contract open interest | *None* | **MISSING** | **Critical Gap** |
| **`ROOT` / `SYMBOL`**| Ticker root (`SPX` vs `SPXW`) | *None* | **MISSING** | **Critical Gap** |
| **`SETTLEMENT`** | Settlement style (AM opening vs PM close) | *None* | **MISSING** | **Critical Gap** |
| **`RATE` / `DIVIDEND`**| Risk-free rate / dividend yield used | *None* | **MISSING** | **Critical Gap** |

### 3.3 Critical Missing Fields Analysis
1. **Missing Open Interest (`C_OI`, `P_OI`):**
   - *Impact:* Traditional option filtering pipelines (e.g., [Bali et al., 2023](file:///C:/Users/Vatsh%20Van/Desktop/MECH_5-SEM/IE%20612/Project/Papers/hhad017.pdf)) discard quotes with zero or stale open interest ($OI < 100$). Because OptionsDX omits OI, illiquid strikes with zero trading interest might display artificial, stale dealer quotes.
   - *Remedy:* Substitute with strict bid-ask spread rules ($(Ask - Bid) / Mid \le 0.30$), require positive bids ($Bid > 0.05$), and check for non-zero trading volume where available.
2. **Missing Settlement Root (`SPX` vs `SPXW`):**
   - *Impact:* Cboe lists both standard monthly SPX options (which stop trading on Thursday afternoon and settle against the Friday morning settlement index `SET`) and weekly/EOM SPXW options (which trade until Friday 16:00 ET and settle against the 4:00 PM cash close). Both share identical expiration dates on the third Friday of each month. If merged without a root identifier, there may be two divergent option prices for the same strike and date.
   - *Remedy:* Group quotes strictly by `(QUOTE_DATE, EXPIRE_DATE, STRIKE)`. If duplicates exist, detect whether prices diverge; discard contracts expiring on the exact quote day ($DTE \le 1$) and focus on contracts with $20 \le DTE \le 50$.
3. **Missing Calibration Metadata:**
   - *Impact:* The interest rate $r$ and dividend yield $q$ used to calculate `C_IV` and `C_DELTA` are omitted.
   - *Remedy:* Discard precalculated Greeks and IV. Invert the implied forward $F_{t,T}$ and discount factor directly from at-the-money put-call parity ($C - P = (F - K)e^{-rT}$), using daily US Treasury yield curves from FRED for $r$.

### 3.4 Data Format & Ingestion Quirks
Empirical quantitative repositories parsing OptionsDX datasets (e.g., [`lambdaclass/options_portfolio_backtester`](https://github.com/lambdaclass/options_portfolio_backtester) and [`convert_optionsdx.py`](https://github.com/lambdaclass/options_portfolio_backtester/blob/main/scripts/convert_optionsdx.py)) document several known parsing artifacts `[Verified Fact]`:
- **Trailing Whitespace in Headers:** OptionsDX raw CSV headers frequently contain trailing whitespace or leading spaces (e.g., `'C_BID '`, `'STRIKE '`). Ingestion pipelines must immediately execute `df.columns = df.columns.str.strip()`.
- **Wide-to-Long Reshaping:** To calculate strike-level moments or calibrate volatility curves, wide rows must be split into call and put contract tables and stacked into standard tabular formats.
- **Monthly File Segmentation:** Data are downloaded as monthly CSV bundles (e.g., `spx_eod_202001.csv`, `spx_eod_202002.csv`), requiring concatenation and deduplication across boundary dates.

---

## 4. Data Provenance, Quality, and Structural Limitations

### 4.1 Provenance and Credibility
OptionsDX is a third-party commercial market-data aggregator operated by OptionX ([optionx.trade](https://optionx.trade/)). Unlike exchange-direct platforms (Cboe DataShop) or academic data repositories (WRDS OptionMetrics), OptionsDX does not publish an audited SSAE-16 SOC compliance report or detailed data-clearing pedigree. The company disclaims all liability, stating that datasets are provided on an *"as-is"* basis with a targeted error tolerance of $<1\%$ and completeness $>99\%$ ([optionsdx.com/terms/](https://www.optionsdx.com/terms/)). It is suitable for academic prototyping and coursework empirical testing, provided robust independent filtering and sanity benchmarks are applied.

### 4.2 Quote Timing & The 15-Minute Desynchronization Problem
A notorious issue in empirical finance literature involving SPX options ([Chernov & Ghysels, 2000](file:///C:/Users/Vatsh%20Van/Desktop/MECH_5-SEM/IE%20612/Project/Papers/main.pdf); [Ulrich et al., 2019](file:///C:/Users/Vatsh%20Van/Desktop/MECH_5-SEM/IE%20612/Project/Papers/ssrn_id3437281_code3012080.pdf)) is quote desynchronization `[Verified Fact]`:
- S&P 500 cash equity trading closes at **16:00:00 ET** (4:00 PM), at which point the official closing index value (`UNDERLYING_LAST` / `^GSPC`) freezes.
- S&P 500 index options on Cboe traditionally traded until **16:15:00 ET** (4:15 PM).
- If option quotes recorded at 16:15 ET are paired with the 16:00 ET underlying index close, any market-moving news occurring during that 15-minute window will produce severe artificial moneyness distortions and apparent put-call parity violations.
- **Methodological Fix:** Never feed `UNDERLYING_LAST` directly into moneyness or Black-Scholes formulas. Instead, determine the *implied forward price* $F_t$ using ATM call and put midpoints:
$$F_t = K^* + e^{r \tau} \big(C(K^*) - P(K^*)\big)$$
where $K^*$ is the strike where $|C - P|$ is minimized. This guarantees internal synchronization between option quotes and the underlying asset level.

### 4.3 Stale Quotes and Quality Anomalies
In budget EOD option datasets, dealer quotes in deep out-of-the-money (OTM) strikes often display quality defects `[Verified Fact]`:
1. **Zero Bids:** Deep OTM options frequently have $Bid = 0.00$ and nominal ask quotes ($Ask = 0.05$ or $0.10$). Midpoint calculation ($(0 + 0.10)/2 = 0.05$) creates severe upward volatility biases in the extreme tails. All quotes with $Bid \le 0$ must be pruned.
2. **Crossed Quotes:** Occasional data feed glitches produce $Bid > Ask$. These must be flagged and removed.
3. **Non-Convexity / Butterfly Arbitrage:** In raw data, noisy quotes can violate monotonicity ($\partial C / \partial K > 0$) or convexity ($\partial^2 C / \partial K^2 < 0$). These must be smoothed using an arbitrage-controlled surface model (e.g., SVI or constrained splines).

### 4.4 License & Terms of Academic Use
According to OptionsDX Terms and Conditions ([optionsdx.com/terms/](https://www.optionsdx.com/terms/)):
- **Permitted Use:** OptionsDX grants a non-exclusive, royalty-free license to access, store in cache, and utilize datasets for personal, educational, and non-commercial analysis. An academic course project for IE 612 is fully compliant.
- **Redistribution Bar:** Redistribution, public hosting, reselling, or bundling of raw CSV files in public repositories (e.g., a public GitHub repository) is **strictly prohibited**.
- **Project Compliance Rule:** The project repository must include `data/raw/` in `.gitignore`. The project deliverable should provide an automated download/ingest pipeline script that operates on locally placed user files, without storing proprietary raw CSVs in version control.

---

## 5. Methodological Suitability: Extracting Option-Implied Features & RND

### 5.1 Extraction of Model-Free Risk-Neutral Moments ($Q_t$)
The project specification ([`implementation.md`](file:///C:/Users/Vatsh%20Van/Desktop/MECH_5-SEM/IE%20612/Project/implementation.md)) mirrors [Ulrich et al. (2019)](file:///C:/Users/Vatsh%20Van/Desktop/MECH_5-SEM/IE%20612/Project/Papers/ssrn_id3437281_code3012080.pdf), requiring the extraction of compact forward-looking risk-neutral moments:
1. **Martin (2017) Simple Variance Swap Index ($\text{SVIX}^2$):**
   $$\text{SVIX}^2 = \frac{2 e^{r \tau}}{\tau} \left[ \int_0^F \frac{P(K)}{K^2} dK + \int_F^\infty \frac{C(K)}{K^2} dK \right]$$
   Martin (2017) proved that $\text{SVIX}^2$ constitutes a model-free lower bound on the expected equity risk premium ($E_t[R_{t+1}] - R_{f,t} \ge \text{SVIX}_t^2$).
2. **Bakshi, Kapadia, and Madan (2003) Risk-Neutral Skewness ($\text{QSkew}$) and Kurtosis ($\text{QKurt}$):**
   Calculated by integrating out-of-the-money calls and puts weighted by cubic ($K^{-3}$) and quartic ($K^{-4}$) payoff functions over a constant 30-day maturity horizon.
3. **Suitability Finding:** **OptionsDX SPX data is 100% SUITABLE for this calculation**. Because the integration uses out-of-the-money options across strikes, the existence of bid and ask quotes allows robust midpoint integration using the trapezoidal rule across liquid strikes.

### 5.2 Feasibility and Pitfalls of Breeden–Litzenberger Risk-Neutral Density (RND)
Under the Breeden and Litzenberger (1978) theorem, the risk-neutral probability density function $f_Q(S_T)$ is proportional to the second derivative of European call prices with respect to strike:
$$f_Q(K) = e^{r \tau} \left. \frac{\partial^2 C(K, \tau)}{\partial K^2} \right|_{K=S_T}$$
- **Critical Risk:** Taking raw second-order finite differences $\frac{C_{i+1} - 2C_i + C_{i-1}}{(\Delta K)^2}$ on discrete market quotes results in catastrophic numerical instability, exploding errors, and negative probabilities ($f_Q(K) < 0$).
- **Methodological Requirement:** If a full RND is extracted, an arbitrage-free parametric or semi-parametric model must be fitted first:
  - *Option A (Recommended for 1-Month Scope):* Fit a **Stochastic Volatility Inspired (SVI)** smile ([Gatheral & Jacquier, 2014](https://arxiv.org/abs/1204.0646)) to implied volatilities, which analytically guarantees absence of butterfly arbitrage.
  - *Option B (Simpler & More Robust):* **Do not extract the full continuous RND curve**. Instead, follow [Ulrich et al. (2019)](file:///C:/Users/Vatsh%20Van/Desktop/MECH_5-SEM/IE%20612/Project/Papers/ssrn_id3437281_code3012080.pdf) directly: extract summary moments ($\text{SVIX}^2$, $\text{QSkew}$, $\text{QKurt}$, ATM IV) and pass them as structured vector inputs $Q_t$ into the physical density model. This eliminates numerical differentiation errors.

### 5.3 Essential 10-Step Quality Control & Cleaning Checklist
To guarantee research-grade feature inputs, the following cleaning pipeline must be executed on OptionsDX data prior to model training:

```
+-----------------------------------------------------------------------------------+
|               10-Step OptionsDX SPX Cleaning & Quality Pipeline                   |
+-----------------------------------------------------------------------------------+
  [1] Header Normalization: Strip trailing whitespace; convert wide layout to long.
  [2] Maturity Window: Select contracts with 20 <= DTE <= 50 calendar days.
  [3] Non-Zero Bid Filter: Drop quotes where Bid <= 0.00.
  [4] Crossed Quotes Filter: Drop quotes where Bid >= Ask.
  [5] Maximum Relative Spread Filter: Drop contracts where (Ask - Bid) / Mid > 0.35.
  [6] Volume Filter: Discard contracts with zero trading volume if spread is wide.
  [7] Put-Call Parity Forward: Invert synthetic forward F_t and discount e^{-rT} at ATM.
  [8] OTM Selection: Retain OTM Puts (K < F_t) and OTM Calls (K >= F_t).
  [9] Monotonicity & No-Arbitrage: Verify dC/dK < 0, dP/dK > 0, and butterfly convexity.
 [10] Surface Spline / SVI: Fit smoothed smile; interpolate to constant 30-day maturity.
+-----------------------------------------------------------------------------------+
```

---

## 6. Authoritative Validation Benchmarks: Cboe DataShop vs. Free Cboe Indices

### 6.1 Cboe DataShop: Sample vs. Usable Coverage
- **Free Sample Offering `[Verified Fact]`:** Cboe DataShop ([datashop.cboe.com](https://datashop.cboe.com/option-eod-summary)) provides downloadable "Sample Files" on its product pages. These sample files contain only 1 single trading day or a few sample rows designed purely to inspect column headers and data delimiters. **They do not constitute usable historical coverage for empirical backtesting**.
- **Historical Subscription Costs `[Verified Fact]`:** Standard historical purchase of Cboe Option EOD Summary for a single ticker (SPX) across multi-year spans costs upwards of **$145 to $240+ per year**, running into thousands of dollars for full coverage. While Cboe offers a 50% discount for accredited academic institutions, it enforces a **$500.00 order minimum** ([cboe.com academic pricing](https://www.cboe.com/)). 
- **Verdict on Cboe DataShop:** Ineligible as a free data source. It serves only as a structural reference for schema design.

### 6.2 Official Cboe CDN Daily Volatility Indices as Validation Anchors
While Cboe charges for contract-level option chains, **Cboe publishes its calculated index-level volatility benchmarks for FREE** directly via its global CDN `[Verified Fact]`:
1. **Cboe VIX History:**  
   `https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv`  
   Contains daily Open, High, Low, and Close of the official 30-day model-free S&P 500 implied volatility index from 1990 to present.
2. **Cboe SKEW History:**  
   `https://cdn.cboe.com/api/global/us_indices/daily_prices/SKEW_History.csv`  
   Contains daily closing values of Cboe's S&P 500 tail-risk skewness index from 1990 to present. SKEW is calculated directly from SPX out-of-the-money options using the Bakshi, Kapadia, and Madan (2003) formula:
   $$\text{SKEW} = 100 - 10 \times S_Q$$
   where $S_Q$ is risk-neutral skewness.
3. **Validation Role in Project:**
   The research pipeline can use these official Cboe files as a **zero-cost validation anchor**:
   - Extract $\text{SVIX}_t$ and $\text{QSkew}_t$ from OptionsDX raw chains.
   - Compute the Pearson and Spearman rank correlation against official Cboe VIX and Cboe SKEW.
   - **Quality Gate Criterion:** If $\text{Corr}(\text{Model-Free IV}, \text{Cboe VIX}) < 0.98$ or $\text{Corr}(\text{Calculated Skew}, \text{Cboe SKEW}) < 0.90$, the cleaning or integration code has a bug and must not proceed to model estimation.

---

## 7. Exogenous Matching Data Infrastructure

To execute the physical return distribution forecasting model, matching daily series for returns, interest rates, dividends, and trading calendars are required:

### 7.1 S&P 500 Historical Returns
- **Target Variable:** Next trading day's close-to-close log return:
  $$r_{t+1} = \log\left(\frac{S_{t+1}}{S_t}\right)$$
- **Primary Source `[Verified Fact]`:** Yahoo Finance (`^GSPC` for price return, `^SP500TR` for total return) or the Federal Reserve Bank of St. Louis FRED API (`SP500`). Available programmatically via Python (`yfinance` or `pandas_datareader`) at zero cost.
- **Total Return vs. Price Return:** While index options are written on the price index (`^GSPC`), the investor's physical holding return is the total return (`^SP500TR`), which accounts for daily dividend reinvestment. Both can be downloaded freely; the project should use total return for physical portfolio evaluation and price return for option parity checks.

### 7.2 Risk-Free Rates & Discount Factors
- **Primary Source `[Verified Fact]`:** Federal Reserve Bank of St. Louis (FRED) Daily Constant Maturity Treasury (CMT) rates:
  - `DGS1MO`: 1-Month Treasury Constant Maturity Rate ([fred.stlouisfed.org/series/DGS1MO](https://fred.stlouisfed.org/series/DGS1MO))
  - `DGS3MO`: 3-Month Treasury Constant Maturity Rate ([fred.stlouisfed.org/series/DGS3MO](https://fred.stlouisfed.org/series/DGS3MO))
  - `DTB3`: 3-Month Treasury Bill Secondary Market Rate
  - `SOFR`: Secured Overnight Financing Rate (for recent post-2018 years)
- **Application:** Linearly interpolate the rate to match the option contract's exact Days to Expiry ($\tau = \text{DTE}/365$).

### 7.3 Dividend Yield & Forward Estimation
- **Option Parity Implied Yield:** For liquid European index options, the continuous dividend yield $q$ is best estimated directly from ATM put-call parity at each maturity:
  $$q = r - \frac{1}{\tau} \log\left(\frac{F_{t,\tau}}{S_t}\right)$$
- **Macro Benchmark:** Trailing 12-month S&P 500 dividend yield published freely in Robert Shiller’s online dataset (Yale University: [econ.yale.edu/~shiller/data.htm](http://www.econ.yale.edu/~shiller/data.htm)).

### 7.4 Trading Calendar & Holiday Alignment
- **Implementation `[Verified Fact]`:** Python package `pandas_market_calendars` provides full historical calendars for Cboe and NYSE (`mcal.get_calendar('CBOE_Index_Options')` and `mcal.get_calendar('NYSE')`).
- **Critical Edge Cases:** Accounts for scheduled exchange holidays, early closes (13:00 ET on day after Thanksgiving / Christmas Eve), and unscheduled emergency closures (e.g., Hurricane Sandy on October 29–30, 2012; National Day of Mourning for President George H.W. Bush on December 5, 2018).

---

## 8. IE 612 Project Feasibility & Scope Alignment

### 8.1 Direct Comparison Against `implementation.md` Requirements

| Requirement from `implementation.md` | Status with OptionsDX SPX | Assessment & Action Required |
| :--- | :--- | :--- |
| **Single Underlying Index** | **Fully Met** | SPX options represent the deepest, most liquid derivatives market globally. |
| **Daily EOD Observations** | **Fully Met** | Daily EOD chains available for multiple years (2010–2020+). |
| **Bid/Ask Quotes for Spread Screening** | **Fully Met** | `C_BID`, `C_ASK`, `P_BID`, `P_ASK` are available; midpoints easily computed. |
| **Next-Day Close-to-Close Target ($r_{t+1}$)** | **Fully Met** | Clean alignment with Yahoo/FRED daily $S_{t+1}/S_t$. |
| **Risk-Neutral Summaries ($Q_t$)** | **Fully Met** | Option chains support Bakshi et al. (2003) / Martin (2017) moments. |
| **Observable State Features ($X_t$)** | **Fully Met** | Lagged returns, realized volatility, and drawdown computed from daily SPX. |
| **Filtered HMM Latent Regime ($\pi_t$)** | **Fully Met** | Gaussian HMM ($K=2$ or $3$) fit strictly on in-sample rolling windows. |
| **Evaluation via Log Predictive Density** | **Fully Met** | Next-day non-overlapping returns evaluated via out-of-sample log-loss and PIT. |
| **1-Month Time Budget Scope** | **Feasible** | Narrowing to compact $Q_t$ moments avoids time-consuming 2D surface PDEs. |

### 8.2 Necessary Scope & Methodological Adjustments
To ensure project completion within the 1-month timeline without compromising mathematical rigor, the following scope constraints are established:
1. **Scope Adjustment 1 — Avoid Full RND Inversion via Numerical Splines:** Extracting a continuous risk-neutral probability density function via Breeden-Litzenberger requires complex non-parametric shape-preserving splines to prevent negative probabilities. **Adjustment:** Follow [Ulrich et al. (2019)](file:///C:/Users/Vatsh%20Van/Desktop/MECH_5-SEM/IE%20612/Project/Papers/ssrn_id3437281_code3012080.pdf) and [DeMiguel et al. (2013)](file:///C:/Users/Vatsh%20Van/Desktop/MECH_5-SEM/IE%20612/Project/Papers/ssrn_id2085587_code417015.pdf): use numerical quadrature to compute the 4 discrete summary moments ($\text{SVIX}^2$, $\text{QSkew}$, $\text{QKurt}$, ATM IV) and pass them as vector inputs $Q_t$.
2. **Scope Adjustment 2 — Substitute Volume/Spread Filtering for Missing Open Interest:** Because OptionsDX lacks open interest, liquidity filtering must strictly enforce:
   $$\text{Filter: } \quad C\_BID > 0.05, \quad \frac{C\_ASK - C\_BID}{(C\_BID + C\_ASK)/2} \le 0.35, \quad 20 \le DTE \le 50$$
3. **Scope Adjustment 3 — Retain Constant 30-Day Interpolation:** Linear interpolation across the two nearest maturities flanking 30 days (e.g., 25 DTE and 35 DTE) will standardize $Q_t$ moments, eliminating artificial maturity-decay variance.
4. **Scope Adjustment 4 — Keep Portfolio Evaluation Strictly Illustrative (Secondary):** In accordance with Section 8 of `implementation.md`, avoid multi-asset Markowitz optimizations. Restrict portfolio translation to an illustrative 1-asset volatility-targeting index/cash rule with fixed transaction costs (5 bps).

### 8.3 Multi-Tiered Fallback Plan

If OptionsDX data encounter unexpected license hurdles, missing file dates, or persistent corruption during Gate A ingestion, the project should immediately pivot to one of three pre-planned fallback routes:

```
[Primary Candidate: OptionsDX SPX Chains (2010-2020)]
                      |
           (If Gate A fails)
                      v
+-----------------------------------------------------------------------------------+
| Fallback Tier 1: Published Cboe Volatility Indices (VIX, SKEW, VIX3M, VVIX)      |
| - Description: Use official daily Cboe closing indices directly as Q_t features.  |
| - Feasibility: 100% free, zero cleaning risk, perfectly synchronized to close.    |
| - Impact on Question: Completely preserves the core research question:           |
|   p(r_{t+1} | Q_t, X_t, \pi_t) vs p(r_{t+1} | Q_t, X_t).                          |
+-----------------------------------------------------------------------------------+
                      |
        (If custom surface is strictly required)
                      v
+-----------------------------------------------------------------------------------+
| Fallback Tier 2: DoltHub Open-Source SPY Options Database                         |
| - Description: Clone `post-no-preference/options` containing daily SPY chains.     |
| - Feasibility: 100% free, includes Bid/Ask and Open Interest, SQL accessible.     |
| - Limitation: SPY is an American ETF option; requires dividend tree or Bjerksund. |
+-----------------------------------------------------------------------------------+
                      |
        (If exchange-certified data is mandatory)
                      v
+-----------------------------------------------------------------------------------+
| Fallback Tier 3: Institutional WRDS / OptionMetrics IvyDB US via IIT Bombay       |
| - Description: Check institutional library access for OptionMetrics S&P 500 table.|
| - Feasibility: Gold standard in literature (Bali et al., 2023; DeMiguel et al.).   |
| - Limitation: Subject to institutional workstation access and export quotas.      |
+-----------------------------------------------------------------------------------+
```

---

## 9. Research-Ready Implementation Checklist (Gate A Verification Protocol)

Before initiating model code in Week 2, the following Gate A checklist must be completed and signed off:

- [ ] **Sample File Acquisition:** Download 1 representative calendar year (e.g., 2019 or 2020) of EOD SPX option chains from OptionsDX at $0.00.
- [ ] **Schema & Header Verification:** Run `df.columns = df.columns.str.strip()` and verify presence of all 33 columns.
- [ ] **Calendar Continuity Check:** Match `QUOTE_DATE` against `mcal.get_calendar('CBOE_Index_Options')` for the selected year. Ensure missing dates do not exceed 1% of total trading sessions.
- [ ] **Strike Grid & Expiry Inspection:** Verify that each trading date contains at least 30 liquid strike quotes spanning moneyness $0.85 \le K/S \le 1.15$ in the 20–50 DTE bucket.
- [ ] **Put-Call Parity Synchrony Test:** Invert implied forward $F_t$ at ATM strike; compare $|F_t - S_t|$ against theoretical cost-of-carry bounds ($S_t e^{(r-q)\tau}$).
- [ ] **Model-Free IV Benchmark Test:** Compute 30-day Martin SVIX on 10 random dates; verify that calculated values fall within $\pm 1.0$ vol point of official Cboe VIX on those same dates.
- [ ] **License & Version Control Compliance:** Ensure raw CSV files are placed in `data/raw/` and explicitly ignored by `.gitignore`.

---

## 10. References & Primary Source Documentation

### Core Literature Pack (Supplied in Workspace)
1. **DeMiguel, V., Plyakha, Y., Uppal, R., & Vilkov, G.** (2013). *Improving Portfolio Selection Using Option-Implied Volatility and Skewness*. SSRN Electronic Journal. [`Papers/ssrn_id2085587_code417015.pdf`](file:///C:/Users/Vatsh%20Van/Desktop/MECH_5-SEM/IE%20612/Project/Papers/ssrn_id2085587_code417015.pdf).
2. **Bianchi, M. L., & Tassinari, G. L.** (2018). *Forward-Looking Portfolio Selection with Multivariate Non-Gaussian Models and the Esscher Transform*. arXiv:1805.05584. [`Papers/1805.05584.pdf`](file:///C:/Users/Vatsh%20Van/Desktop/MECH_5-SEM/IE%20612/Project/Papers/1805.05584.pdf).
3. **Chernov, M., & Ghysels, E.** (2000). *A Study Towards a Unified Approach to the Joint Estimation of Objective and Risk Neutral Measures for the Purpose of Options Valuation*. Journal of Financial Economics, 56(3), 407–458. [`Papers/main.pdf`](file:///C:/Users/Vatsh%20Van/Desktop/MECH_5-SEM/IE%20612/Project/Papers/main.pdf).
4. **Bali, T. G., Beckmeyer, H., Mörke, M., & Weigert, F.** (2023). *Option Return Predictability with Machine Learning and Big Data*. The Review of Financial Studies, 36(9), 3548–3602. [`Papers/hhad017.pdf`](file:///C:/Users/Vatsh%20Van/Desktop/MECH_5-SEM/IE%20612/Project/Papers/hhad017.pdf).
5. **Ulrich, M., Walther, S., Rothfuss, J., & Ferreira, F.** (2019). *Forward-looking P*. SSRN Electronic Journal. [`Papers/ssrn_id3437281_code3012080.pdf`](file:///C:/Users/Vatsh%20Van/Desktop/MECH_5-SEM/IE%20612/Project/Papers/ssrn_id3437281_code3012080.pdf).

### Foundational Theoretical & Methodological Papers
6. **Bakshi, G., Kapadia, N., & Madan, D.** (2003). *Stock Return Characteristics, Skewness Laws, and the Differential Pricing of Individual Equity, Index, and Option Prices*. The Review of Financial Studies, 16(1), 101–143.
7. **Breeden, D. T., & Litzenberger, R. H.** (1978). *Prices of State-Contingent Claims Implicit in Option Prices*. The Journal of Business, 51(4), 621–651.
8. **Martin, I.** (2017). *What is the Expected Return on the Market?* The Quarterly Journal of Economics, 132(1), 367–433.
9. **Gatheral, J., & Jacquier, A.** (2014). *Arbitrage-free SVI volatility surfaces*. Quantitative Finance, 14(1), 59–71. [arXiv:1204.0646](https://arxiv.org/abs/1204.0646).

### Primary Data Source URLs & Documentation
10. **OptionsDX SPX Product Page:** [https://www.optionsdx.com/product/spx-option-chain/](https://www.optionsdx.com/product/spx-option-chain/)
11. **OptionsDX Data Field Definitions:** [https://www.optionsdx.com/option-chain-field-definitions/](https://www.optionsdx.com/option-chain-field-definitions/)
12. **OptionsDX Terms & Privacy:** [https://www.optionsdx.com/terms/](https://www.optionsdx.com/terms/)
13. **Cboe DataShop Option EOD Summary Specification:** [https://datashop.cboe.com/option-eod-summary](https://datashop.cboe.com/option-eod-summary)
14. **Cboe Official VIX Historical Data CDN:** [https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv](https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv)
15. **Cboe Official SKEW Historical Data CDN:** [https://cdn.cboe.com/api/global/us_indices/daily_prices/SKEW_History.csv](https://cdn.cboe.com/api/global/us_indices/daily_prices/SKEW_History.csv)
16. **Federal Reserve Bank of St. Louis (FRED) Interest Rates:** [https://fred.stlouisfed.org/series/DGS3MO](https://fred.stlouisfed.org/series/DGS3MO)
17. **DoltHub US Options Database:** [https://www.dolthub.com/repositories/post-no-preference/options](https://www.dolthub.com/repositories/post-no-preference/options)
18. **LambdaClass OptionsDX Converter Script:** [https://github.com/lambdaclass/options_portfolio_backtester/blob/main/scripts/convert_optionsdx.py](https://github.com/lambdaclass/options_portfolio_backtester/blob/main/scripts/convert_optionsdx.py)
