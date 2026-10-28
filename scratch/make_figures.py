"""
make_figures.py
===============
Builds every figure (figures/*.png) and animation (figures/gifs/*.gif) for the README
from committed results only: no model is refitted and no data is downloaded.
Validation 2020-2021 and test 2022-2023 results are read from output/stage7_models_v2/
and output/stage8_test_v2/; Stage 7 / Gate D originals from output/stage7_models/ and
output/stage8_test/.

Style: black surface, validated dark categorical palette (fixed colour per model),
blue <-> red diverging map with a grey midpoint, single-hue blue sequential map.

Run from the repository root: python scratch/make_figures.py
"""
import json
import os
import sys
import warnings

sys.path.insert(0, ".")
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import animation, transforms
from matplotlib.colors import LinearSegmentedColormap
from scipy import stats

from src.models.evaluation_metrics import diebold_mariano_test, stationary_block_bootstrap
from src.models.recalibration import prequential_scale_recalibration

warnings.filterwarnings("ignore")
FIG, GIF = "figures", "figures/gifs"
V1, V2, T1, T2 = "output/stage7_models", "output/stage7_models_v2", "output/stage8_test", "output/stage8_test_v2"
DEV = "output/stage7_datasets/spx_stage7_operational_development_2010_2019.csv"
VAL = "output/stage7_datasets/spx_stage7_operational_validation_2020_2021.csv"

# ------------------------------------------------------------------ style
BG, INK, INK2, MUTED, GRID, AXIS = "#0b0b0b", "#f0efec", "#c3c2b7", "#898781", "#2c2c2a", "#383835"
COL = {"B4": "#3987e5", "GJR": "#d95926", "B3": "#199e70", "B2": "#c98500",
       "R1": "#d55181", "B1": "#008300", "B0": "#9085e9"}
LAB = {"B0": "B0 Gaussian", "B1": "B1 RV Student-t", "B2": "B2 option-implied (Q)", "B3": "B3 history (X)",
       "B4": "B4 Q + X", "R1": "R1 Q + X + HMM regime", "GJR": "GJR-GARCH-t"}
MODELS = ["B0", "B1", "B2", "B3", "B4", "R1", "GJR"]
DIV = LinearSegmentedColormap.from_list("div", ["#e66767", AXIS, "#3987e5"])  # negative red, positive blue
SEQ = LinearSegmentedColormap.from_list("seq", ["#0d366b", "#256abf", "#5598e7", "#9ec5f4", "#cde2fb"])
STRESS = ("2020-03-01", "2020-04-30")
plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG, "text.color": INK,
    "axes.labelcolor": INK2, "axes.edgecolor": AXIS, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "font.size": 10, "axes.titlesize": 12, "legend.frameon": False,
    "legend.labelcolor": INK2, "lines.linewidth": 1.6, "axes.axisbelow": True, "font.family": "DejaVu Sans",
})
COUNT = {"png": 0, "gif": 0}


def title(ax, head, sub=None):
    ax.set_title(head, loc="left", fontweight="bold", color=INK, pad=22 if sub else 8)
    if sub:
        ax.text(0, 1.02, sub, transform=ax.transAxes, color=MUTED, fontsize=9, va="bottom")


def suptitle(fig, head, sub=None):
    """Figure-level headline + subtitle, stacked with fixed point offsets; save() reserves the space."""
    fig.text(0.01, 0.995, head, ha="left", va="top", fontweight="bold", color=INK, fontsize=13)
    reserve = 26
    if sub:
        fig.text(0.01, 0.995, sub, ha="left", va="top", color=MUTED, fontsize=9.5,
                 transform=transforms.offset_copy(fig.transFigure, fig=fig, y=-21, units="points"))
        reserve = 44
    fig._reserve_top_pt = reserve


def save(fig, name):
    reserve = getattr(fig, "_reserve_top_pt", None)
    if reserve is not None:
        fig.tight_layout(rect=(0, 0, 1, 1 - reserve / (fig.get_figheight() * 72)))
    fig.savefig(f"{FIG}/{name}.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    COUNT["png"] += 1
    print("  saved", name)


def shade_stress(ax):
    ax.axvspan(pd.Timestamp(STRESS[0]), pd.Timestamp(STRESS[1]), color=INK, alpha=0.06, lw=0)


# ------------------------------------------------------------------ data
def load():
    dev, val = pd.read_csv(DEV), pd.read_csv(VAL)
    df_all = pd.concat([dev, val], ignore_index=True)
    pos = {d: i for i, d in enumerate(df_all["date"].values)}

    def with_gjr(frame, gjr):
        assert list(frame["date"]) == list(gjr["date"])
        for f in ["mu", "sigma", "nu", "log_p"]:
            frame[f"GJR_{f}"] = gjr[f"GJR_{f}"].values
        frame["date"] = pd.to_datetime(frame["date"])
        return frame

    vclip = with_gjr(pd.read_csv(f"{V2}/step6_predictions_a_clip.csv"), pd.read_csv(f"{V2}/benchmark_gjr_predictions_validation.csv"))
    vraw = with_gjr(pd.read_csv(f"{V2}/validation_predictions_primary_v2.csv"), pd.read_csv(f"{V2}/benchmark_gjr_predictions_validation.csv"))
    tclip = with_gjr(pd.read_csv(f"{T2}/test_predictions_clipped.csv"), pd.read_csv(f"{T2}/benchmark_gjr_predictions_test.csv"))
    traw = with_gjr(pd.read_csv(f"{T2}/test_predictions_unclipped.csv"), pd.read_csv(f"{T2}/benchmark_gjr_predictions_test.csv"))

    v_idx = np.array([pos[d.strftime("%Y-%m-%d")] for d in vclip["date"]])
    v_tau = {b["block"]: b["refit_origin_tau"] for b in json.load(open(f"{V2}/refit_diagnostics_primary_v2.json"))["blocks"]}
    test_start = len(df_all)
    t_idx = test_start + np.arange(len(tclip))
    assert np.array_equal((t_idx - test_start) // 21, tclip["block"].values)
    t_tau = {b: test_start - 1 + 21 * b for b in np.unique(tclip["block"])}
    return dict(dev=dev, val=val, df_all=df_all, vclip=vclip, vraw=vraw, tclip=tclip, traw=traw,
                v_idx=v_idx, v_tau=v_tau, t_idx=t_idx, t_tau=t_tau,
                stage7=pd.read_csv(f"{V1}/validation_predictions_primary.csv"),
                gated=pd.read_csv(f"{T1}/test_predictions.csv"))


def recal_frame(frame, idx, taus):
    out = {}
    for m in MODELS:
        nu = None if m == "B0" else frame[f"{m}_nu"].values
        r = prequential_scale_recalibration(frame["target_y"].values, frame[f"{m}_mu"].values,
                                            frame[f"{m}_sigma"].values, nu, idx, frame["block"].values, taus)
        out[m] = {"log_p": r["log_p"], "c": r["per_block"]}
    return out


def pit(frame, m):
    y, mu, s = frame["target_y"].values, frame[f"{m}_mu"].values, frame[f"{m}_sigma"].values
    if m == "B0":
        return stats.norm.cdf(y, mu, s)
    return stats.t.cdf(y, df=frame[f"{m}_nu"].values, loc=mu, scale=s)


def interval(frame, m, cov):
    a = (1 - cov) / 2
    mu, s = frame[f"{m}_mu"].values, frame[f"{m}_sigma"].values
    if m == "B0":
        return stats.norm.ppf(a, mu, s), stats.norm.ppf(1 - a, mu, s)
    nu = frame[f"{m}_nu"].values
    return stats.t.ppf(a, nu, mu, s), stats.t.ppf(1 - a, nu, mu, s)


def pdf(m, row, x):
    mu, s = row[f"{m}_mu"], row[f"{m}_sigma"]
    if m == "B0":
        return stats.norm.pdf(x, mu, s)
    return stats.t.pdf(x, row[f"{m}_nu"], mu, s)


CMP = [("Q1: B4 vs B3", "B4", "B3"), ("Q2a: B2 vs B1", "B2", "B1"), ("Q3: B3 vs B1", "B3", "B1"),
       ("R1 vs B4", "R1", "B4"), ("B4 vs GJR", "B4", "GJR"), ("B2 vs GJR", "B2", "GJR")]


def summ(d, with_draws=False):
    out = {"mean": float(np.mean(d)), **{f"p{L}": diebold_mariano_test(d, max_lag=L)["p_value_one_sided"] for L in (5, 10, 21)}}
    b = stationary_block_bootstrap(d, n_boot=2000, expected_block_len=5, seed=42, return_draws=with_draws)
    out.update(lo=b["ci_95_lower"], hi=b["ci_95_upper"])
    if with_draws:
        out["draws"] = b["draws"]
    return out


# ================================================================== A. data
def fig_data(D):
    dev, val = D["dev"], D["val"]
    d_all = D["df_all"].copy()
    d_all["date"] = pd.to_datetime(d_all["date"])
    g = D["gated"].copy()
    g["date"] = pd.to_datetime(g["date"])

    # 01 price with partitions
    fig, ax = plt.subplots(figsize=(11, 4.6))
    ax.plot(d_all["date"], d_all["S_t"], color=INK, lw=1.2)
    ax.plot(g["date"], g["S_t"], color=INK, lw=1.2)
    ax.set_yscale("log")
    for (a, b, lab) in [("2010-01-01", "2019-12-31", "Development\n2010-2019"), ("2020-01-01", "2021-12-31", "Validation\n2020-21"),
                        ("2022-01-01", "2023-12-31", "Test\n2022-23")]:
        ax.axvspan(pd.Timestamp(a), pd.Timestamp(b), color={"D": "#256abf", "V": "#c98500", "T": "#d95926"}[lab[0]], alpha=0.12, lw=0)
        top = lab.startswith("D")  # the price is low in 2010-2019 and high afterwards
        ax.text(pd.Timestamp(a) + pd.Timedelta(days=30), 0.95 if top else 0.04, lab, color=INK2, fontsize=9,
                va="top" if top else "bottom", transform=ax.get_xaxis_transform())
    ax.set_ylabel("S&P 500 close (log scale)")
    title(ax, "Thirteen years of S&P 500 closes, split into develop / validate / test",
          "3,522 sessions; models refit every 21 sessions on an expanding window; 2022-2023 scored only under committed protocols")
    save(fig, "01_spx_price_partitions")

    # 02 returns
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(d_all["date"], 100 * d_all["r_1d"], color="#5598e7", lw=0.6)
    shade_stress(ax)
    ax.axvline(pd.Timestamp("2020-01-01"), color=MUTED, lw=0.8, ls="--")
    ax.set_ylabel("daily log return (%)")
    title(ax, "Volatility clusters: calm years punctuated by 2011, 2015-16, 2018 and the 2020 crash",
          "r_t = ln(S_t / S_t-1), 2010-2021; shaded band = March-April 2020 stress window used in robustness checks")
    save(fig, "02_daily_returns")

    # 03 distribution
    y = dev["target_y_next2"].dropna().values
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    ax.hist(100 * y, bins=120, density=True, color="#256abf", alpha=0.8, edgecolor=BG, lw=0.4)
    x = np.linspace(-8, 6, 600)
    mu, sd = np.mean(100 * y), np.std(100 * y)
    nu_, loc_, sc_ = stats.t.fit(100 * y)
    ax.plot(x, stats.norm.pdf(x, mu, sd), color=COL["B0"], label=f"Normal fit")
    ax.plot(x, stats.t.pdf(x, nu_, loc_, sc_), color=COL["GJR"], label=f"Student-t fit (nu = {nu_:.1f})")
    ax.set_yscale("log")
    ax.set_ylim(1e-4, 1.5)
    ax.set_xlabel("next-period log return y_t (%)")
    ax.set_ylabel("density (log scale)")
    ax.legend(loc="upper left")
    title(ax, "Returns have fat tails: a Student-t fits, a Gaussian badly misses the crashes",
          f"Target y_t = ln(S_t+2 / S_t+1), development 2010-2019 (n = {len(y)}); kurtosis {stats.kurtosis(y):.1f}")
    save(fig, "03_return_distribution")

    # 04 QQ
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.4))
    z = np.sort((y - y.mean()) / y.std())
    qn = stats.norm.ppf((np.arange(1, len(z) + 1) - 0.5) / len(z))
    tq = stats.t.ppf((np.arange(1, len(z) + 1) - 0.5) / len(z), nu_) * np.sqrt((nu_ - 2) / nu_)
    for ax, q, nm, c in [(axes[0], qn, "Normal", COL["B0"]), (axes[1], tq, f"Student-t (nu={nu_:.1f})", COL["GJR"])]:
        ax.scatter(q, z, s=8, color=c, alpha=0.7, lw=0)
        lim = [min(q.min(), z.min()), max(q.max(), z.max())]
        ax.plot(lim, lim, color=MUTED, lw=1, ls="--")
        ax.set_xlabel(f"{nm} quantiles")
        ax.set_ylabel("standardised return quantiles")
        title(ax, f"QQ vs {nm}")
    suptitle(fig, "The left tail is far heavier than Gaussian; a Student-t is close",
             "Standardised y_t, development 2010-2019")
    save(fig, "04_qq_plots")

    # 05/06 features
    for name, cols, head in [("05_option_features", ["SVIX_30d", "QSkew_30d", "QKurt_30d", "ATM_IV_30d", "TermSlope_60_30"],
                              "Option-implied (Q) features: implied volatility spikes lead, skew stays negative"),
                             ("06_history_features", ["r_1d", "r_5d", "rv_5d", "rv_20d", "dsemi_20d", "dd_20d"],
                              "Historical-state (X) features: realised risk reacts after the fact")]:
        fig, axes = plt.subplots(len(cols), 1, figsize=(11, 1.55 * len(cols)), sharex=True)
        for ax, c in zip(axes, cols):
            ax.plot(d_all["date"], d_all[c], color="#5598e7" if name.startswith("05") else "#199e70", lw=0.7)
            ax.set_ylabel(c, rotation=0, ha="right", va="center", fontsize=9)
            shade_stress(ax)
        suptitle(fig, head, "Daily values 2010-2021 from the committed Stage 7 datasets (30-day constant maturity for Q)")
        fig.tight_layout(rect=(0, 0, 1, 0.94))
        save(fig, name)

    # 07 correlation
    cols = ["SVIX_30d", "QSkew_30d", "QKurt_30d", "ATM_IV_30d", "TermSlope_60_30", "r_1d", "r_5d", "rv_5d", "rv_20d", "dsemi_20d", "dd_20d"]
    C = d_all[cols].corr().values
    fig, ax = plt.subplots(figsize=(8, 6.8))
    im = ax.imshow(C, cmap=DIV, vmin=-1, vmax=1)
    ax.set_xticks(range(len(cols)), cols, rotation=60, ha="right", fontsize=8.5)
    ax.set_yticks(range(len(cols)), cols, fontsize=8.5)
    ax.grid(False)
    for i in range(len(cols)):
        for j in range(len(cols)):
            ax.text(j, i, f"{C[i, j]:.2f}", ha="center", va="center", fontsize=6.5, color=INK if abs(C[i, j]) > 0.4 else INK2)
    cb = fig.colorbar(im, ax=ax, fraction=0.046)
    cb.outline.set_edgecolor(AXIS)
    title(ax, "Features are highly collinear: SVIX vs ATM IV 0.99, skew vs kurtosis -0.97",
          "Pearson correlation, 2010-2021; collinearity drives the sigma extrapolation fixed by clipping")
    save(fig, "07_feature_correlation")

    # 08 implied vs realised
    fig, ax = plt.subplots(figsize=(8, 5.4))
    yr = pd.to_datetime(d_all["date"]).dt.year
    sc = ax.scatter(d_all["rv_20d"], d_all["SVIX_30d"], c=yr, cmap=SEQ, s=7, lw=0)
    lim = [0, max(d_all["rv_20d"].max(), d_all["SVIX_30d"].max())]
    ax.plot(lim, lim, color=MUTED, ls="--", lw=1)
    ax.text(lim[1] * 0.62, lim[1] * 0.55, "implied = realised", color=MUTED, fontsize=8.5, rotation=33)
    cb = fig.colorbar(sc, ax=ax)
    cb.set_label("year", color=INK2)
    cb.outline.set_edgecolor(AXIS)
    ax.set_xlabel("realised volatility, 20-day (annualised)")
    ax.set_ylabel("SVIX, 30-day (annualised)")
    title(ax, "Implied volatility usually sits above realised: the variance risk premium",
          "Most days lie above the diagonal; in crashes realised volatility overshoots")
    save(fig, "08_implied_vs_realised")


# ================================================================== B. optimizer
def fig_optimizer(D):
    s3 = json.load(open(f"{V2}/step3_convergence_check.json"))["cases"]
    val_cases = [c for c in s3 if c["case"].startswith("val")]
    # Stage 7 torch gaps from the optimizer audit (penalised objective vs float64 optimum)
    old = {"B2": [.0077, .0180, .0242, .0187, .0149, .0141], "B3": [.0005, .0014, .0011, .0007, .0007, .0007],
           "B4": [.0245, .0400, .0427, .0374, .0325, .0300], "R1": [.0200, .0193, .0189, .0168, .0147, .0134]}
    fig, axes = plt.subplots(1, 4, figsize=(13, 4), sharey=True)
    for ax, m in zip(axes, ["B2", "B3", "B4", "R1"]):
        new = [max(abs(c["models"][m]["gap_to_reference"]), 1e-16) for c in val_cases]
        x = np.arange(len(new))
        ax.bar(x - 0.2, old[m], 0.38, color=MUTED, label="Stage 7 (float32, 60 iters)")
        ax.bar(x + 0.2, new, 0.38, color=COL[m], label="converged (this work)")
        ax.set_yscale("log")
        ax.set_xticks(x, [c["refit_date"][:7] for c in val_cases], rotation=50, fontsize=8)
        title(ax, LAB[m])
    axes[0].set_ylabel("penalised NLL gap to optimum (log)")
    axes[0].legend(loc="center left", fontsize=8)
    suptitle(fig, "Root cause 1 fixed: optimisation error fell from ~1e-2 to ~1e-13 nats",
             "Gap of each fit's objective to an independent SciPy float64 optimum, six representative validation refits")
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    save(fig, "09_convergence_gap")

    # 10 nu stuck
    s7, v = D["stage7"], D["vclip"]
    fig, ax = plt.subplots(figsize=(11, 4))
    dt = pd.to_datetime(s7["date"])
    for m, ls in [("B4", "-"), ("B1", "-")]:
        ax.plot(dt, s7[f"{m}_nu"], color=MUTED, ls="--", lw=1.2)
        ax.plot(v["date"], v[f"{m}_nu"], color=COL[m], lw=1.8, label=f"{LAB[m]} converged")
    ax.plot([], [], color=MUTED, ls="--", label="Stage 7 (both stuck at the 5.0 start)")
    ax.set_ylabel("degrees of freedom nu")
    ax.legend(loc="center right")
    title(ax, "Tail thickness was never estimated: nu sat at its starting value 5.0",
          "Fitted Student-t degrees of freedom by scoring day, validation 2020-2021")
    save(fig, "10_nu_stuck_vs_converged")

    # 11 iterations / 12 Hessian
    blocks = json.load(open(f"{V2}/refit_diagnostics_primary_v2.json"))["blocks"]
    dates = [b["refit_date"][:7] for b in blocks]
    fig, ax = plt.subplots(figsize=(11, 4.2))
    for m in ["B1", "B2", "B3", "B4", "R1"]:
        ax.plot(range(len(blocks)), [b["fit_reports"][m]["n_iter"] for b in blocks], color=COL[m], marker="o", ms=4, label=LAB[m])
    ax.axhline(60, color=MUTED, ls="--", lw=1)
    ax.text(0, 61.5, "Stage 7 hard cap: every B2-R1 fit stopped here", color=MUTED, fontsize=8.5)
    ax.set_xticks(range(len(blocks))[::2], dates[::2], rotation=45, fontsize=8)
    ax.set_ylabel("L-BFGS iterations to converge")
    ax.legend(ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.22), fontsize=8.5)
    title(ax, "Converged fits need 22-90 iterations; the old cap of 60 cut them short",
          "Each fit stops at max|grad| <= 1e-8 with a positive-definite Hessian (L-BFGS + Newton polish)")
    save(fig, "11_iterations_per_refit")

    fig, ax = plt.subplots(figsize=(11, 4.2))
    for m in ["B1", "B2", "B3", "B4", "R1"]:
        ax.plot(range(len(blocks)), [b["fit_reports"][m]["hessian_min_eig"] for b in blocks], color=COL[m], marker="o", ms=4, label=LAB[m])
    ax.set_yscale("log")
    ax.set_xticks(range(len(blocks))[::2], dates[::2], rotation=45, fontsize=8)
    ax.set_ylabel("smallest Hessian eigenvalue (log)")
    ax.legend(ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.22), fontsize=8.5)
    ax.annotate("R1: pi_0 + pi_1 = 1 duplicates the intercept,\nso one direction is identified only by the ridge",
                xy=(12, blocks[12]["fit_reports"]["R1"]["hessian_min_eig"]), xytext=(14, 1e-6), color=INK2, fontsize=8.5,
                arrowprops=dict(arrowstyle="->", color=MUTED))
    title(ax, "Every optimum is a strict minimum, but R1 is nearly singular",
          "Minimum eigenvalue of the exact Hessian at each converged fit (lambda = 1e-4), validation refits")
    save(fig, "12_hessian_min_eigenvalue")

    # 13 nesting
    devc = s3[0]["models"]
    old_pen = {"B2": -3.48487, "B3": -3.48112, "B4": -3.47301, "R1": -3.4783}  # Step 1 fit reports, dev in-sample
    fig, ax = plt.subplots(figsize=(8.5, 4.3))
    ms_ = ["B3", "B2", "B4", "R1"]
    for i, m in enumerate(ms_):
        ax.plot([old_pen[m], devc[m]["penalized_loss"]], [i, i], color=AXIS, lw=2)
        ax.scatter(old_pen[m], i, color=MUTED, s=60, zorder=3)
        ax.scatter(devc[m]["penalized_loss"], i, color=COL[m], s=80, zorder=3)
    ax.scatter([], [], color=MUTED, label="Stage 7 fit")
    ax.scatter([], [], color=INK2, label="converged fit")
    ax.set_yticks(range(len(ms_)), [LAB[m] for m in ms_])
    ax.set_xlabel("penalised training objective (lower is better)")
    ax.legend(loc="lower right")
    ax.invert_xaxis()
    title(ax, "Root cause 2 fixed: nested models are ordered again (B4 beats its parts)",
          "Development in-sample objective; old B4 was worse than B2, a model it contains")
    save(fig, "13_nesting_restored")

    # 14 lambda grid
    grid = json.load(open(f"{V2}/lambda_grid_K2_v2.json"))
    lams = [g["lambda"] for g in grid["grid"]]
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    for m in ["B1", "B2", "B3", "B4", "R1"]:
        ax.plot(lams, [-g[f"{m}_nll"] for g in grid["grid"]], color=COL[m], marker="o", ms=6, label=LAB[m])
    ax.set_xscale("log")
    ax.set_xlabel("ridge penalty lambda")
    ax.set_ylabel("validation mean log score (higher is better)")
    ax.legend(fontsize=8.5)
    ax.axvline(grid["selected_lambda"], color=MUTED, ls="--", lw=1)
    ax.text(grid["selected_lambda"] * 1.1, ax.get_ylim()[0] + 0.005, "selected (argmax B4)", color=MUTED, fontsize=8.5)
    title(ax, "With converged fits the lightest penalty wins; Stage 7 had picked 1e-2",
          "Lambda grid, K = 2, unclipped validation walk-forward; B0 (-2.12) off scale")
    save(fig, "14_lambda_grid")


# ================================================================== C. forecasts
def fig_forecasts(D):
    v, vr, t = D["vclip"], D["vraw"], D["tclip"]

    # 15 sigma blow-up
    m1 = (v["date"] >= "2020-01-15") & (v["date"] <= "2020-06-30")
    fig, ax = plt.subplots(figsize=(11, 4.6))
    ax.scatter(v["date"][m1], np.abs(v["target_y"][m1]), color=INK2, s=10, label="|realised y|", zorder=3)
    ax.plot(vr["date"][m1], vr["B3_sigma"][m1], color=COL["B3"], ls=":", lw=1.8, label="B3 unclipped")
    ax.plot(vr["date"][m1], vr["B4_sigma"][m1], color=COL["B4"], ls=":", lw=1.8, label="B4 unclipped")
    ax.plot(v["date"][m1], v["B4_sigma"][m1], color=COL["B4"], lw=2, label="B4 clipped (adopted)")
    ax.plot(v["date"][m1], v["GJR_sigma"][m1], color=COL["GJR"], lw=1.6, label="GJR-GARCH-t")
    ax.set_yscale("log")
    ax.set_ylabel("predicted daily scale sigma (log)")
    ax.legend(ncol=3, fontsize=8.5, loc="upper left")
    shade_stress(ax)
    title(ax, "Root cause 3 fixed: unclipped features pushed daily sigma to 70-180%",
          "Linear-in-features scale extrapolates when inputs reach 10-16 robust z; clipping to training quantiles caps it near 5%")
    save(fig, "15_sigma_blowup_march_2020")

    for name, fr, head, sub in [
        ("16_sigma_paths_validation", v, "Option models track the crash; trailing RV reacts late",
         "Predicted daily scale, validation 2020-2021, clipped configuration; dots = |realised y|"),
        ("17_sigma_paths_test", t, "In 2022-2023 the option models and GARCH agree closely",
         "Predicted daily scale, test 2022-2023 (post-hoc), clipped configuration; dots = |realised y|")]:
        fig, ax = plt.subplots(figsize=(11, 4.4))
        ax.scatter(fr["date"], np.abs(fr["target_y"]), color=AXIS, s=6, zorder=1)
        for m in ["B1", "B3", "B2", "B4", "GJR"]:
            ax.plot(fr["date"], fr[f"{m}_sigma"], color=COL[m], lw=1.3, label=LAB[m], zorder=2)
        ax.set_yscale("log")
        ax.set_ylabel("predicted daily sigma (log)")
        ax.legend(ncol=5, fontsize=8.3, loc="upper center", bbox_to_anchor=(0.5, -0.1))
        title(ax, head, sub)
        save(fig, name)

    for name, fr, head, sub in [
        ("18_fan_chart_validation", v, "B4 predictive intervals widen with the 2020 crash and narrow afterwards",
         "50 / 80 / 95% central intervals of B4 (clipped), validation; dots = realised y, red = outside 95%"),
        ("19_fan_chart_test", t, "In 2022-2023 B4's intervals run slightly narrow: the 50% band covers 44%",
         "50 / 80 / 95% central intervals of B4 (clipped), test 2022-2023 (post-hoc)")]:
        fig, ax = plt.subplots(figsize=(11, 4.4))
        for cov, a in [(0.95, 0.18), (0.80, 0.28), (0.50, 0.45)]:
            lo, hi = interval(fr, "B4", cov)
            ax.fill_between(fr["date"], lo, hi, color=COL["B4"], alpha=a, lw=0, label=f"{int(cov * 100)}%")
        lo95, hi95 = interval(fr, "B4", 0.95)
        out = (fr["target_y"] < lo95) | (fr["target_y"] > hi95)
        ax.scatter(fr["date"][~out], fr["target_y"][~out], color=INK2, s=5, zorder=3)
        ax.scatter(fr["date"][out], fr["target_y"][out], color="#e66767", s=12, zorder=4, label=f"outside 95% ({out.mean():.1%})")
        ax.set_ylabel("y_t (log return)")
        ax.legend(ncol=4, fontsize=8.5, loc="lower left")
        title(ax, head, sub)
        save(fig, name)

    # 20 HMM regimes
    fig, axes = plt.subplots(2, 1, figsize=(11, 5), sharex=True, gridspec_kw=dict(height_ratios=[1, 1.3]))
    axes[0].fill_between(vr["date"], 0, vr["pi_state_1"], color=COL["R1"], alpha=0.7, lw=0, step="mid")
    axes[0].set_ylabel("P(high-vol state)")
    axes[0].set_ylim(0, 1.05)
    axes[1].plot(vr["date"], vr["target_y"], color="#5598e7", lw=0.8)
    axes[1].set_ylabel("y_t")
    suptitle(fig, "The HMM finds the high-volatility state, but options already price it",
             "Filtered (causal) probability of the high-volatility state, validation 2020-2021; R1 adds it to B4 and gains nothing")
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    save(fig, "20_hmm_regime_probability")


# ================================================================== D. scores & tests
def fig_tests(D, R):
    v, t = D["vclip"], D["tclip"]
    tp = t[t["date"] != "2022-01-03"].reset_index(drop=True)
    rv, rt = R["val"], R["test"]

    # 21 log score vs GJR, by setting
    settings = [("validation raw", {m: v[f"{m}_log_p"].values for m in MODELS}),
                ("validation recalibrated", {m: rv[m]["log_p"] for m in MODELS}),
                ("test raw", {m: tp[f"{m}_log_p"].values for m in MODELS}),
                ("test recalibrated", {m: rt[m]["log_p"] for m in MODELS})]
    ms_ = ["B1", "B2", "B3", "B4", "R1"]
    fig, axes = plt.subplots(1, 4, figsize=(14, 4.4), sharey=True)
    for ax, (nm, lp) in zip(axes, settings):
        vals = [np.mean(lp[m] - lp["GJR"]) for m in ms_]
        ax.bar(range(len(ms_)), vals, color=[COL[m] for m in ms_], width=0.7)
        ax.axhline(0, color=COL["GJR"], lw=1.2)
        ax.set_xticks(range(len(ms_)), ms_)
        for i, val in enumerate(vals):
            ax.text(i, val + (0.002 if val >= 0 else -0.002), f"{val:+.3f}", ha="center", va="bottom" if val >= 0 else "top", fontsize=8, color=INK2)
        title(ax, nm)
    axes[0].set_ylabel("mean log score minus GJR-GARCH (nats/day)")
    suptitle(fig, "Option models beat GARCH on validation and tie it on test; history alone does not",
             "Bars above the orange line beat GJR-GARCH-t. Clipped configuration; test N = 500 (2022-01-03 excluded); B0 off scale")
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    save(fig, "21_log_score_vs_gjr")

    # 22-24 cumulative differentials
    both = pd.concat([v.assign(period="val"), t.assign(period="test")], ignore_index=True)
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.2))
    for ax, fr, nm in [(axes[0], v, "validation 2020-2021"), (axes[1], tp, "test 2022-2023")]:
        d = fr["B4_log_p"] - fr["B3_log_p"]
        ax.plot(fr["date"], d.cumsum(), color=COL["B4"], lw=2)
        ax.axhline(0, color=MUTED, lw=0.8)
        ax.set_ylabel("cumulative log-score gain (nats)")
        title(ax, nm, f"mean {d.mean():+.4f}/day")
    suptitle(fig, "Q1: adding option features to history gains steadily, more strongly in 2020",
             "Cumulative sum of log p(B4) - log p(B3); rising = option information helps")
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    save(fig, "22_cumulative_q1")

    for name, pairs, head, sub in [
        ("23_cumulative_vs_gjr", [("B4", "GJR"), ("B2", "GJR"), ("B3", "GJR")],
         "Against GARCH: a lead built in 2020-2021 is not extended in 2022-2023",
         "Cumulative log p(model) - log p(GJR-GARCH-t), validation then test (shaded, post-hoc); clipped configuration"),
        ("24_cumulative_r1", [("R1", "B4")],
         "The regime model's increment is noise: it drifts down, then up in 2022",
         "Cumulative log p(R1) - log p(B4), validation then test (shaded)")]:
        fig, ax = plt.subplots(figsize=(11, 4.3))
        for a, b in pairs:
            d = both[f"{a}_log_p"] - both[f"{b}_log_p"]
            ax.plot(both["date"], d.cumsum(), color=COL[a], lw=2, label=f"{a} - {b}")
            ax.text(both["date"].iloc[-1], d.cumsum().iloc[-1], f"  {a}", color=COL[a], va="center", fontsize=9)
        ax.axvspan(pd.Timestamp("2022-01-01"), both["date"].iloc[-1], color=INK, alpha=0.05, lw=0)
        ax.axhline(0, color=MUTED, lw=0.8)
        ax.set_ylabel("cumulative log-score difference (nats)")
        ax.legend(loc="upper left")
        title(ax, head, sub)
        save(fig, name)

    # 25/26 block heatmaps
    for name, fr, head in [("25_block_heatmap_validation", v, "Validation: block-by-block differences are noisy around their means"),
                           ("26_block_heatmap_test", tp, "Test: block results are mixed for every comparison")]:
        mat = np.array([[np.mean((g[f"{a}_log_p"] - g[f"{b}_log_p"]).values) for _, g in fr.groupby("block")] for _, a, b in CMP])
        lim = np.nanpercentile(np.abs(mat), 95)
        fig, ax = plt.subplots(figsize=(12, 3.8))
        im = ax.imshow(mat, cmap=DIV, vmin=-lim, vmax=lim, aspect="auto")
        ax.set_yticks(range(len(CMP)), [c[0] for c in CMP])
        starts = fr.groupby("block")["date"].min().dt.strftime("%Y-%m").values
        ax.set_xticks(range(len(starts))[::2], starts[::2], rotation=45, fontsize=8)
        ax.grid(False)
        cb = fig.colorbar(im, ax=ax, fraction=0.03)
        cb.set_label("mean d per block (nats)", color=INK2)
        cb.outline.set_edgecolor(AXIS)
        title(ax, head, "Mean log-score difference per 21-session block; blue favours the first model, red the second")
        save(fig, name)

    # 27 forest
    res = {}
    for nm, a, b in CMP + [("Q2b: B2 vs B0", "B2", "B0")]:
        res[nm] = {
            "val raw": summ(v[f"{a}_log_p"].values - v[f"{b}_log_p"].values),
            "val recal": summ(rv[a]["log_p"] - rv[b]["log_p"]),
            "test raw": summ(tp[f"{a}_log_p"].values - tp[f"{b}_log_p"].values),
            "test recal": summ(rt[a]["log_p"] - rt[b]["log_p"]),
        }
    R["summ"] = res
    styles = {"val raw": (INK, "o", True), "val recal": (INK, "o", False), "test raw": ("#e66767", "s", True), "test recal": ("#e66767", "s", False)}
    fig, ax = plt.subplots(figsize=(10, 6))
    names = [c[0] for c in CMP]
    for i, nm in enumerate(names):
        for k, (key, (c, mk, filled)) in enumerate(styles.items()):
            yv = i + (k - 1.5) * 0.17
            s = res[nm][key]
            ax.plot([s["lo"], s["hi"]], [yv, yv], color=c, lw=1.4, alpha=0.8)
            ax.scatter(s["mean"], yv, color=c if filled else BG, edgecolor=c, marker=mk, s=45, zorder=3, lw=1.5)
    for key, (c, mk, filled) in styles.items():
        ax.scatter([], [], color=c if filled else BG, edgecolor=c, marker=mk, label=key)
    ax.axvline(0, color=MUTED, lw=1)
    ax.set_yticks(range(len(names)), names)
    ax.invert_yaxis()
    ax.set_xlabel("mean log-score difference d (nats/day) with 95% stationary-bootstrap CI")
    ax.legend(loc="lower right", fontsize=8.5)
    title(ax, "Every comparison, both periods, with and without recalibration",
          "Right of zero favours the first model. Circles = validation 2020-21, squares = test 2022-23 (post-hoc); hollow = recalibrated")
    save(fig, "27_forest_all_comparisons")

    # 28 DM p-values across lags
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6), sharey=True)
    for ax, key in [(axes[0], "val raw"), (axes[1], "test raw")]:
        for i, nm in enumerate(names):
            ps = [res[nm][key][f"p{L}"] for L in (5, 10, 21)]
            ax.plot(ps, [i] * 3, color=AXIS, lw=2)
            for p, mk in zip(ps, ["o", "s", "D"]):
                ax.scatter(p, i, color=COL[CMP[i][1]], marker=mk, s=45, zorder=3)
        ax.axvline(0.05, color="#e66767", ls="--", lw=1)
        ax.set_xscale("log")
        ax.set_xlim(1e-4, 1.2)
        ax.set_yticks(range(len(names)), names)
        ax.invert_yaxis()
        ax.set_xlabel("one-sided DM p-value (log)")
        title(ax, "validation" if key.startswith("val") else "test (post-hoc)")
    for mk, L in zip(["o", "s", "D"], (5, 10, 21)):
        axes[1].scatter([], [], color=INK2, marker=mk, label=f"HAC {L} lags")
    axes[1].legend(loc="lower right", fontsize=8.5)
    suptitle(fig, "Significance is robust to the HAC lag choice; the test period is weaker",
             "Diebold-Mariano p-values for 'first model better' at 5 / 10 / 21 Newey-West lags; dashed = 5%")
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    save(fig, "28_dm_pvalues_by_lag")

    # 29 bootstrap distributions
    fig, axes = plt.subplots(2, 2, figsize=(12, 6.4))
    for row, (nm, a, b) in enumerate([CMP[0], CMP[4]]):
        for col, (fr, lab) in enumerate([(v, "validation"), (tp, "test")]):
            ax = axes[row, col]
            s = summ(fr[f"{a}_log_p"].values - fr[f"{b}_log_p"].values, with_draws=True)
            ax.hist(s["draws"], bins=60, color=COL[a], alpha=0.85, edgecolor=BG, lw=0.3)
            for x_ in (s["lo"], s["hi"]):
                ax.axvline(x_, color=INK2, ls="--", lw=1)
            ax.axvline(0, color="#e66767", lw=1.4)
            title(ax, f"{nm}, {lab}", f"mean {s['mean']:+.4f}; 95% CI [{s['lo']:+.4f}, {s['hi']:+.4f}]")
    suptitle(fig, "Bootstrap: the validation gains exclude zero, the test gains do not",
             "2,000 stationary-block bootstrap means (mean block 5); dashed = 95% interval, red = zero")
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    save(fig, "29_bootstrap_distributions")


# ================================================================== E. calibration
def fig_calibration(D):
    v, t = D["vclip"], D["tclip"]
    for name, fr, head in [("30_pit_validation", v, "PIT, validation 2020-21: only the option models pass a KS uniformity test"),
                           ("31_pit_test", t, "PIT, test 2022-23: the option models are now too narrow; GARCH and B1 pass")]:
        fig, axes = plt.subplots(2, 4, figsize=(13, 5.6), sharey=True)
        n, bins = len(fr), 10
        band = stats.binom.ppf([0.025, 0.975], n, 1 / bins) / (n / bins)
        for ax, m in zip(axes.flat, MODELS):
            u = pit(fr, m)
            ax.hist(u, bins=bins, range=(0, 1), density=True, color=COL[m], edgecolor=BG, lw=1)
            ax.axhspan(band[0], band[1], color=INK, alpha=0.08, lw=0)
            ax.axhline(1, color=MUTED, lw=1)
            ks = stats.kstest(u, "uniform").pvalue
            title(ax, LAB[m], f"KS p = {ks:.3f}")
            ax.set_ylim(0, 2.4)
        axes.flat[-1].axis("off")
        axes.flat[-1].text(0, 0.5, "Flat = calibrated.\nGrey band = 95% range\nfor a uniform histogram.\nU-shape = too narrow;\nhump = too wide.",
                           color=INK2, fontsize=10, va="center")
        suptitle(fig, head, "Probability integral transform of realised y under each predictive density (10 bins)")
        fig.tight_layout(rect=(0, 0, 1, 0.9))
        save(fig, name)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True)
    for ax, fr, nm in [(axes[0], v, "validation"), (axes[1], t, "test (post-hoc)")]:
        for k, m in enumerate(MODELS):
            emp = []
            for cov in (0.5, 0.8, 0.95):
                lo, hi = interval(fr, m, cov)
                emp.append(np.mean((fr["target_y"] >= lo) & (fr["target_y"] <= hi)))
            ax.plot(np.array([0.5, 0.8, 0.95]) + (k - 3) * 0.006, emp, color=COL[m], marker="o", ms=6, lw=1, label=LAB[m])
        ax.plot([0.45, 1], [0.45, 1], color=MUTED, ls="--", lw=1)
        ax.set_xlabel("nominal central-interval coverage")
        title(ax, nm)
    axes[0].set_ylabel("empirical coverage")
    axes[1].legend(fontsize=8, loc="lower right")
    suptitle(fig, "Coverage is close to nominal in 2020-21 but mostly too narrow in 2022-23",
             "50 / 80 / 95% central intervals; points below the diagonal = intervals too narrow")
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    save(fig, "32_interval_coverage")


# ================================================================== F. controls, recalibration, ablations
def fig_controls(D, R):
    s6 = json.load(open(f"{V2}/step6_sigma_controls.json"))["results"]
    ms_ = ["B2", "B3", "B4", "R1"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4))
    base = [s6["baseline"]["max_sigma_mar_apr_2020"][m] for m in ms_]
    clip = [s6["a_clip"]["criterion1_max_sigma_mar_apr_2020"][m] for m in ms_]
    x = np.arange(len(ms_))
    axes[0].bar(x - 0.2, base, 0.38, color=MUTED, label="before (Step 5)")
    axes[0].bar(x + 0.2, clip, 0.38, color=[COL[m] for m in ms_], label="clipped (adopted)")
    axes[0].axhline(0.10, color="#e66767", ls="--", lw=1)
    axes[0].text(-0.4, 0.115, "pre-declared limit 0.10", color="#e66767", fontsize=8.5)
    axes[0].set_yscale("log")
    axes[0].set_xticks(x, ms_)
    axes[0].set_ylabel("max predicted daily sigma, Mar-Apr 2020 (log)")
    axes[0].legend(fontsize=8.5)
    title(axes[0], "Criterion 1: plausible scale")
    ch = [-s6["a_clip"]["criterion2"][m]["nll_change"] for m in ["B2", "B3", "B4"]]
    axes[1].bar(range(3), ch, color=[COL[m] for m in ["B2", "B3", "B4"]], width=0.6)
    axes[1].axhline(-0.005, color="#e66767", ls="--", lw=1)
    axes[1].text(-0.4, -0.009, "harm limit -0.005", color="#e66767", fontsize=8.5)
    axes[1].set_xticks(range(3), ["B2", "B3", "B4"])
    axes[1].set_ylabel("change in validation log score (nats/day)")
    title(axes[1], "Criterion 2: no material harm")
    suptitle(fig, "The pre-declared clipping control passed both criteria and was adopted",
             "Step 6 rule committed before running; clipping also improved every model's log score")
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    save(fig, "33_step6_clipping_control")

    # 34 recalibration factors
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.4), sharey=True)
    for ax, key, nm in [(axes[0], "val", "validation"), (axes[1], "test", "test (post-hoc)")]:
        for m in ["B0", "B1", "B3", "B4", "GJR"]:
            pb = R[key][m]["c"]
            ks = sorted(pb)
            ax.step(ks, [pb[k]["c"] for k in ks], where="post", color=COL[m], lw=1.8, label=LAB[m])
        ax.axhline(1, color=MUTED, lw=0.8)
        ax.set_xlabel("refit block")
        title(ax, nm)
    axes[0].set_ylabel("prequential scale factor c_b")
    axes[1].legend(fontsize=8.5, ncol=2)
    suptitle(fig, "After the 2020 shock every model is judged too narrow (c > 1); B0 and B1 most of all",
             "c_b fitted on matured past scored rows only (s <= tau_b - 2); c > 1 means the model was too narrow")
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    save(fig, "34_recalibration_factors")

    # 35 ablations
    s7 = json.load(open(f"{V2}/step7_width_controlled.json"))["results"]["clipped"]
    ms_ = ["B4", "R1", "R1_shuffled_pi", "R1_rv_median"]
    labs = ["B4 (no regime)", "R1 (HMM filter)", "R1 shuffled pi", "R1 RV-median threshold"]
    cols = [COL["B4"], COL["R1"], "#e87ba4", "#a03b63"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.3), sharey=True)
    for ax, key, nm in [(axes[0], "nll_raw", "raw"), (axes[1], "nll_recalibrated", "recalibrated")]:
        vals = [-(s7[key][m] - s7[key]["B4"]) for m in ms_]
        ax.bar(range(4), vals, color=cols, width=0.6)
        ax.axhline(0, color=MUTED, lw=1)
        ax.set_xticks(range(4), labs, rotation=15, fontsize=8.5)
        for i, val in enumerate(vals):
            ax.text(i, val, f"{val:+.4f}", ha="center", va="bottom" if val >= 0 else "top", color=INK2, fontsize=8.5)
        title(ax, nm)
    axes[0].set_ylabel("log score minus B4 (nats/day)")
    suptitle(fig, "Ablations: scrambling or replacing the regime signal changes nothing",
             "Research-protocol ablations 2 and 3, validation, clipped. If HMM timing mattered, shuffling would hurt")
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    save(fig, "35_regime_ablations")

    # 36 Gate D / Stage 7 vs this work
    s7v, gd = D["stage7"], D["gated"]
    gd = gd[gd["date"] != "2022-01-03"]
    v, t = D["vclip"], D["tclip"]
    t = t[t["date"] != "2022-01-03"]
    cm = CMP[:4]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4), sharey=True)
    for ax, old, new, nm in [(axes[0], s7v, v, "validation"), (axes[1], gd, t, "test (N = 500)")]:
        o = [np.mean(old[f"{a}_log_p"] - old[f"{b}_log_p"]) for _, a, b in cm]
        n_ = [np.mean(new[f"{a}_log_p"].values - new[f"{b}_log_p"].values) for _, a, b in cm]
        x = np.arange(len(cm))
        ax.bar(x - 0.2, o, 0.38, color=MUTED, label="original (unconverged)")
        ax.bar(x + 0.2, n_, 0.38, color=[COL[a] for _, a, _ in cm], label="this work (converged, clipped)")
        ax.axhline(0, color=MUTED, lw=0.8)
        ax.set_xticks(x, [c[0] for c in cm], rotation=12, fontsize=8.5)
        title(ax, nm)
    axes[0].set_ylabel("mean d (nats/day)")
    axes[0].legend(fontsize=8.5)
    suptitle(fig, "Fixing the fits changed the validation conclusions: Q1 grew and R1's edge vanished",
             "Original Stage 7 / Gate D predictions vs the converged, clipped re-runs")
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    save(fig, "36_original_vs_this_work")

    # 37 GJR parameters
    fits = json.load(open(f"{V2}/benchmark_gjr_validation.json"))["fits"] + json.load(open(f"{T2}/benchmark_gjr_test.json"))["fits"]
    dts = pd.to_datetime([f["refit_date"] for f in fits])
    P = pd.DataFrame([f["params"] for f in fits])
    P["persistence"] = P["alpha[1]"] + 0.5 * P["gamma[1]"] + P["beta[1]"]
    fig, axes = plt.subplots(1, 4, figsize=(14, 3.6))
    for ax, c, lab in zip(axes, ["gamma[1]", "beta[1]", "persistence", "nu"],
                          ["leverage gamma", "GARCH beta", "persistence", "t degrees of freedom"]):
        ax.plot(dts, P[c], color=COL["GJR"], marker="o", ms=3.5)
        ax.axvline(pd.Timestamp("2022-01-01"), color=MUTED, ls="--", lw=0.8)
        ax.tick_params(axis="x", rotation=45, labelsize=8)
        title(ax, lab)
    suptitle(fig, "The GARCH benchmark is all asymmetry: alpha ~ 0, gamma ~ 0.33, persistence ~ 0.97",
             "GJR-GARCH(1,1)-t parameters at each 21-session refit, 2020-2023 (dashed = start of test)")
    fig.tight_layout(rect=(0, 0, 1, 0.85))
    save(fig, "37_gjr_parameters")

    # 38 rolling log score vs GJR
    both = pd.concat([D["vclip"], D["tclip"]], ignore_index=True)
    fig, ax = plt.subplots(figsize=(11, 4.4))
    for m in ["B1", "B2", "B3", "B4", "R1"]:
        r = (both[f"{m}_log_p"] - both["GJR_log_p"]).rolling(63, min_periods=40).mean()
        ax.plot(both["date"], r, color=COL[m], lw=1.5, label=LAB[m])
    ax.axhline(0, color=COL["GJR"], lw=1.2)
    ax.axvspan(pd.Timestamp("2022-01-01"), both["date"].iloc[-1], color=INK, alpha=0.05, lw=0)
    ax.set_ylabel("63-day mean log score minus GJR")
    ax.legend(ncol=5, fontsize=8.3, loc="upper center", bbox_to_anchor=(0.5, -0.1))
    title(ax, "Who beats GARCH changes over time; B4 and B2 lead most of 2020-2021",
          "Rolling quarter (63 sessions) of log p(model) - log p(GJR); test period shaded (post-hoc)")
    save(fig, "38_rolling_log_score_vs_gjr")


def fig_scorecard(R):
    s = R["summ"]
    rows = [("Q1: B4 vs B3", "Do option features add to history?"), ("Q2a: B2 vs B1", "Options alone vs trailing RV"),
            ("Q3: B3 vs B1", "History features vs trailing RV"), ("R1 vs B4", "Does an HMM regime add value?"),
            ("B4 vs GJR", "Q + X vs GARCH benchmark"), ("B2 vs GJR", "Options alone vs GARCH")]
    fig, ax = plt.subplots(figsize=(13, 4.6))
    ax.axis("off")
    hdr = ["comparison", "question", "validation d (p)", "val. recal. d (p)", "test d (p)", "test recal. d (p)"]
    xs = [0.0, 0.16, 0.45, 0.59, 0.73, 0.87]
    for x_, h in zip(xs, hdr):
        ax.text(x_, 0.95, h, color=MUTED, fontsize=9.5, fontweight="bold", transform=ax.transAxes)
    for i, (nm, q) in enumerate(rows):
        yv = 0.82 - i * 0.135
        ax.text(xs[0], yv, nm, color=INK, fontsize=10, transform=ax.transAxes, fontweight="bold")
        ax.text(xs[1], yv, q, color=INK2, fontsize=9.5, transform=ax.transAxes)
        for x_, key in zip(xs[2:], ["val raw", "val recal", "test raw", "test recal"]):
            e = s[nm][key]
            sig = e["p5"] < 0.05 and e["lo"] > 0
            col = "#5598e7" if sig else (INK2 if e["mean"] >= 0 else "#e66767")
            ax.text(x_, yv, f"{e['mean']:+.4f} ({e['p5']:.3f})", color=col, fontsize=10, transform=ax.transAxes,
                    fontweight="bold" if sig else "normal")
    ax.text(0, -0.05, "d = mean log-score difference (nats/day), one-sided HAC-5 DM p in brackets. Blue bold = p < 0.05 and "
            "bootstrap CI above zero; red = first model worse. Clipped configuration; test N = 500, post-hoc.",
            color=MUTED, fontsize=8.5, transform=ax.transAxes)
    title(ax, "Results scorecard")
    save(fig, "39_results_scorecard")


# ================================================================== GIFs
def save_gif(anim, name, fps):
    anim.save(f"{GIF}/{name}.gif", writer=animation.PillowWriter(fps=fps), dpi=80, savefig_kwargs={"facecolor": BG})
    plt.close("all")
    COUNT["gif"] += 1
    print("  saved gif", name)


def gif_density(D):
    v = D["vclip"]
    w = v[(v["date"] >= "2020-02-14") & (v["date"] <= "2020-04-30")].reset_index(drop=True)
    x = np.linspace(-0.14, 0.14, 500)
    fig, axes = plt.subplots(2, 1, figsize=(9, 6.2), gridspec_kw=dict(height_ratios=[2.2, 1]))
    cum = np.cumsum(w["B4_log_p"] - w["GJR_log_p"])

    def frame(i):
        for ax in axes:
            ax.cla()
        r = w.iloc[i]
        for m in ["B3", "GJR", "B4"]:
            axes[0].plot(x * 100, pdf(m, r, x) / 100, color=COL[m], lw=2, label=f"{LAB[m]}  log p = {r[f'{m}_log_p']:.2f}")
        axes[0].axvline(r["target_y"] * 100, color=INK, lw=1.5, ls="--")
        axes[0].text(r["target_y"] * 100, axes[0].get_ylim()[1] * 0.9, " realised", color=INK, fontsize=9)
        axes[0].set_xlim(-14, 14)
        axes[0].set_xlabel("next-period return (%)")
        axes[0].set_ylabel("predictive density")
        axes[0].legend(loc="upper left", fontsize=8.5)
        title(axes[0], f"Predictive densities through the COVID crash - {r['date']:%d %b %Y}")
        axes[1].plot(w["date"][: i + 1], cum[: i + 1], color=COL["B4"], lw=2)
        axes[1].axhline(0, color=MUTED, lw=0.8)
        axes[1].set_xlim(w["date"].iloc[0], w["date"].iloc[-1])
        axes[1].set_ylim(min(cum.min(), 0) - 0.3, max(cum.max(), 0) + 0.3)
        axes[1].set_ylabel("cum. B4 - GJR")
        axes[1].tick_params(axis="x", labelsize=8)
        fig.tight_layout()

    save_gif(animation.FuncAnimation(fig, frame, frames=len(w), interval=200), "g1_densities_covid_crash", fps=4)


def gif_race(D):
    both = pd.concat([D["vclip"], D["tclip"]], ignore_index=True)
    ms_ = ["B1", "B2", "B3", "B4", "R1"]
    cum = {m: np.cumsum(both[f"{m}_log_p"] - both["GJR_log_p"]).values for m in ms_}
    idxs = list(range(9, len(both), 10)) + [len(both) - 1]
    lo = min(min(c.min() for c in cum.values()), 0) - 1
    hi = max(max(c.max() for c in cum.values()), 0) + 1
    fig, ax = plt.subplots(figsize=(9, 4.6))

    def frame(k):
        ax.cla()
        i = idxs[k]
        vals = [cum[m][i] for m in ms_]
        ax.barh(range(len(ms_)), vals, color=[COL[m] for m in ms_], height=0.6)
        ax.axvline(0, color=COL["GJR"], lw=1.5)
        ax.set_yticks(range(len(ms_)), [LAB[m] for m in ms_])
        ax.set_xlim(lo, hi)
        for j, val in enumerate(vals):
            ax.text(val + (0.3 if val >= 0 else -0.3), j, f"{val:+.1f}", va="center", ha="left" if val >= 0 else "right", color=INK2, fontsize=9)
        d = both["date"].iloc[i]
        period = "validation" if d < pd.Timestamp("2022-01-01") else "test (post-hoc)"
        title(ax, f"Cumulative log score vs GJR-GARCH - {d:%b %Y} ({period})",
              "Right of the orange line = ahead of GARCH (total nats)")
        ax.set_xlabel("cumulative log-score difference vs GJR (nats)")

    save_gif(animation.FuncAnimation(fig, frame, frames=len(idxs), interval=120), "g2_log_score_race_vs_gjr", fps=8)


def gif_fan(D):
    t = D["tclip"]
    win, step = 80, 5
    starts = list(range(0, len(t) - win, step))
    lo95, hi95 = interval(t, "B4", 0.95)
    lo50, hi50 = interval(t, "B4", 0.50)
    glo, ghi = interval(t, "GJR", 0.95)
    fig, ax = plt.subplots(figsize=(9.5, 4.4))

    def frame(k):
        ax.cla()
        s = slice(starts[k], starts[k] + win)
        d = t["date"].iloc[s]
        ax.fill_between(d, lo95[s], hi95[s], color=COL["B4"], alpha=0.22, lw=0, label="B4 95%")
        ax.fill_between(d, lo50[s], hi50[s], color=COL["B4"], alpha=0.5, lw=0, label="B4 50%")
        ax.plot(d, glo[s], color=COL["GJR"], lw=1.2, ls="--", label="GJR 95%")
        ax.plot(d, ghi[s], color=COL["GJR"], lw=1.2, ls="--")
        yv = t["target_y"].iloc[s]
        out = (yv < lo95[s]) | (yv > hi95[s])
        ax.scatter(d[~out], yv[~out], color=INK2, s=10, zorder=3)
        ax.scatter(d[out], yv[out], color="#e66767", s=22, zorder=4)
        ax.set_ylim(-0.065, 0.065)
        ax.set_ylabel("y_t")
        ax.legend(loc="lower left", fontsize=8, ncol=3)
        title(ax, f"Test-period forecast intervals, {d.iloc[0]:%b %Y} - {d.iloc[-1]:%b %Y}",
              "B4 50/95% bands vs GJR-GARCH 95% (dashed); red = outside B4 95%")

    save_gif(animation.FuncAnimation(fig, frame, frames=len(starts), interval=150), "g3_test_fan_chart_scroll", fps=7)


def gif_pit(D):
    t = D["tclip"]
    u = {m: pit(t, m) for m in ["B4", "GJR", "B1"]}
    ns = list(range(30, len(t) + 1, 10))
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.8), sharey=True)

    def frame(k):
        n = ns[k]
        for ax, m in zip(axes, u):
            ax.cla()
            ax.hist(u[m][:n], bins=10, range=(0, 1), density=True, color=COL[m], edgecolor=BG, lw=1)
            ax.axhline(1, color=MUTED, lw=1)
            ax.set_ylim(0, 2.5)
            title(ax, LAB[m], f"n = {n}, KS p = {stats.kstest(u[m][:n], 'uniform').pvalue:.2f}")
        fig.suptitle(f"PIT histograms filling in over the test period - through {t['date'].iloc[n - 1]:%b %Y}",
                     x=0.01, ha="left", color=INK, fontweight="bold")
        fig.tight_layout(rect=(0, 0, 1, 0.9))

    save_gif(animation.FuncAnimation(fig, frame, frames=len(ns), interval=150), "g4_pit_buildup_test", fps=6)


def gif_walkforward(D):
    both = pd.concat([D["vclip"].assign(p="v"), D["tclip"].assign(p="t")], ignore_index=True)
    blocks = both.groupby(["p", "block"], sort=False)["date"].agg(["min", "max"]).reset_index()
    fig, axes = plt.subplots(2, 1, figsize=(10, 5.6), gridspec_kw=dict(height_ratios=[1, 2.4]))
    t0 = pd.Timestamp("2010-01-04")

    def frame(k):
        for ax in axes:
            ax.cla()
        b = blocks.iloc[k]
        axes[0].barh(0, (b["min"] - t0).days, left=t0, color="#256abf", height=0.5, label="training window (expanding)")
        axes[0].barh(0, max((b["max"] - b["min"]).days, 20), left=b["min"], color=COL["GJR"], height=0.5, label="21-session scoring block")
        axes[0].set_xlim(t0, pd.Timestamp("2024-01-31"))
        axes[0].set_yticks([])
        axes[0].legend(loc="upper left", fontsize=8, ncol=2)
        axes[0].grid(False)
        title(axes[0], f"Walk-forward refit {k + 1} of {len(blocks)}: refit at {b['min']:%d %b %Y}")
        upto = both["date"] <= b["max"]
        axes[1].scatter(both["date"][upto], np.abs(both["target_y"][upto]), color=AXIS, s=5)
        axes[1].plot(both["date"][upto], both["B4_sigma"][upto], color=COL["B4"], lw=1.4, label=LAB["B4"])
        axes[1].plot(both["date"][upto], both["GJR_sigma"][upto], color=COL["GJR"], lw=1.2, label=LAB["GJR"])
        axes[1].set_xlim(both["date"].iloc[0], both["date"].iloc[-1])
        axes[1].set_ylim(1e-4, 0.15)
        axes[1].set_yscale("log")
        axes[1].axvline(pd.Timestamp("2022-01-01"), color=MUTED, ls="--", lw=0.8)
        axes[1].set_ylabel("predicted sigma vs |y|")
        axes[1].legend(loc="upper right", fontsize=8)
        fig.tight_layout()

    save_gif(animation.FuncAnimation(fig, frame, frames=len(blocks), interval=300), "g5_walk_forward_refits", fps=3)


def main():
    os.makedirs(GIF, exist_ok=True)
    D = load()
    print("recalibration ...")
    prim = (D["tclip"]["date"] != "2022-01-03").values  # protocol: recalibrate on the primary N = 500 sample
    R = {"val": recal_frame(D["vclip"], D["v_idx"], D["v_tau"]),
         "test": recal_frame(D["tclip"][prim].reset_index(drop=True), D["t_idx"][prim], D["t_tau"])}
    print("A. data");
    fig_data(D)
    print("B. optimizer");
    fig_optimizer(D)
    print("C. forecasts");
    fig_forecasts(D)
    print("D. tests");
    fig_tests(D, R)
    print("E. calibration");
    fig_calibration(D)
    print("F. controls");
    fig_controls(D, R)
    fig_scorecard(R)
    if "--png-only" in sys.argv:
        print(f"done: {COUNT['png']} figures (GIFs skipped)")
        return
    print("GIFs");
    gif_density(D)
    gif_race(D)
    gif_fan(D)
    gif_pit(D)
    gif_walkforward(D)
    print(f"done: {COUNT['png']} figures, {COUNT['gif']} gifs")


if __name__ == "__main__":
    main()
