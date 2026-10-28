# Appendix A: Experiment inventory, provenance and contradictions catalogue

This appendix supports `docs/complete_research_report.md`. Commit hashes are those on branch `fix/optimizer-calibration` at the time of writing; the revision commits were rewritten once to remove attribution trailers, and the hashes below are the current ones. Dates come from the commit metadata. Where the order of events cannot be established from metadata, this is stated.

## A.1 Chronological inventory

| # | Date | Commit(s) | Experiment | Partition | Pre-specified? | Artifacts | Key numbers | Main limitation |
|---|---|---|---|---|---|---|---|---|
| 1 | 2026-10-21 | `2bdd9c9`, `9120fe0` | Research protocol (H1: R1 vs B4) and Stage 5 specification (+0.010-nat practical threshold) | none | the design itself | `docs/research_protocol.md`, `docs/stage5_modeling_specification.md` | none | later edited after Gate D (`6b2e3a4`, `7f06ab7`) |
| 2 | 2026-10-21 | `cee01a1` | Stage 6 feature construction 2010–2021; Gate B audit | dev + val | yes, with user decisions UD-1 to UD-5 | `output/stage6_features/*`, `output/stage6_audit/*` | 2,232 dev pairs (legacy target) | exposed the 2022-01-03/04 ^GSPC closes; ^IRX downloaded to 2022-01-05; silent r = 0.015 fallback |
| 3 | 2026-10-22 | `395bb35` | Stage 7 Proposal A datasets; λ × K grid; primary validation; MDN check; mid-2012 sensitivity (Gate C) | val | tuning pre-specified | `output/stage7_datasets/*`, `output/stage7_models/*` | λ = 0.01, K = 2; R1 − B4 +0.0056 (p 0.235); MDN −0.027 NLL | unconverged fits; B0 PIT bug |
| 4 | 2026-10-24 | `66924f3` | Stage 7 verification (analytic CRPS, per-refit HMM diagnostics); declared frozen | val | n/a | as above | n/a | n/a |
| 5 | 2026-10-24 | `67a9642` | **Gate D** test: N = 500 primary, strict isolation, N = 501, N = 495 | test | **pre-registered, scored once** | `output/stage8_test/*` | R1 − B4 +0.005417, p 0.0732, CI [−0.00198, +0.01384] | test period partially exposed beforehand |
| 6 | 2026-10-24 | `6b2e3a4`, `7f06ab7` | Stage 9 package (final report, slides, reproducibility guide) | none | n/a | `docs/final_*`, `docs/reproducibility_guide.md` | n/a | protocol edited after results |
| 7 | 2026-10-28 | `029c16d` | Step 1: fit reports, no behaviour change | val | audit | `scratch/check_step1_fit_diagnostics.py` | original predictions reproduced to 3.6e-15; 100/100 B2–R1 fits hit `max_iter` | n/a |
| 8 | 2026-10-28 | `779ee45` | Step 2: unit tests (known bugs recorded as strict xfails) | dev | audit | `tests/` | nesting violated (B4 −3.4730 vs B2 −3.4849) | n/a |
| 9 | 2026-10-28 | `ed68c4c` | Step 3: converged float64 fits; reference-optimizer acceptance | dev + 6 val refits | audit with stated acceptance criteria | `output/stage7_models_v2/step3_convergence_check.json` | gap ≤ 8.1e-14; random starts agree to 4.6e-13 | n/a |
| 10 | 2026-10-28 | `b5b2ed6` | Step 4: B1 convergence, B0 PIT per-row, true-LL HMM monitor | val | audit | `step4_hmm_b1_b0_check.json` | B1 ν 3.77–3.99; B0 KS p 0.0017; HMM \|ΔA\| ≤ 1.1e-5 | HMM ρ not re-estimated; single start |
| 11 | 2026-10-28 | `727539e` | Step 5: converged validation run and λ grid | val | λ rule from Stage 7 | `paired_comparisons_v2.json` etc. | λ = 1e-4; Q1 +0.054 (p 0.004); R1 − B4 −0.008 | σ blow-up in March 2020 |
| 12 | 2026-10-28 | `e8294fc` → `50672f7` | Step 6: clipping control; π₁-only | val | **rule committed first** | `step6_*` | max σ ≤ 0.063; clipping adopted; Q1 +0.033 (p 0.020) | n/a |
| 13 | 2026-10-28 | `1380231` → `377e7e4` → `43e5f31` | Step 7: prequential recalibration; shuffled-π and RV-median ablations | val | **specification committed first** | `step7_width_controlled.json` | recalibrated Q1 +0.016 (p 0.095); ablations null | recalibration is period-dependent |
| 14 | 2026-10-28 | `77d51fd` → `069272a` → `851d3a2` | Step 8: post-hoc test re-score (clipped / strict / unclipped; N = 500/501/495) | test | **protocol committed first**; Q1 decision rule | `output/stage8_test_v2/test_rescore_v2.json` | Q1 +0.0121, p 0.052 (not rejected) | post-hoc; Q1 chosen after Gate D |
| 15 | 2026-10-28 | `25bdec6` | Literature review | none | n/a | `docs/literature/` | n/a | limited search |
| 16 | 2026-10-28 | `27cda26` → `0917f32` | GJR-GARCH-t benchmark on validation | val | **specification committed first** | `benchmark_gjr_validation.json` | B4 − GJR +0.0445 (p 0.010) | n/a |
| 17 | 2026-10-28 | `e6ff614` → `ee9977d` → `a40bb28` → `b990f7f` | GJR-GARCH-t on test | test | **addendum committed first** | `benchmark_gjr_test.json` | B4 − GJR −0.0038 (p 0.645) | post-hoc |
| 18 | 2026-10-28 | `5520a26`, `5a68e44`, `2f10266`, `4f92e33` | Documentation move, figures, README | none | n/a | `figures/`, `README.md` | n/a | README §9 test PIT row and figures 31–32 use N = 501 |
| 19 | 2026-10-28 | (this report) | Appendix B statistics and Appendix C conditioning | all | new read-only analysis | `docs/report_appendices/*` | B4 θ-Hessian condition 1.68e8 | n/a |

## A.2 Provenance matrix

| Generation | Authoritative data | Authoritative narrative | Superseded or caveated statements |
|---|---|---|---|
| O-VAL | `output/stage7_models/*` | `docs/gate_c_model_validation_report.md` | B0 PIT p (0.044 should be 0.0017); σ range; B0 mean scale; unbacked in-sample DM 1.9165; ν "stability" (stuck at its initial value) |
| O-TEST | `output/stage8_test/*` | `docs/gate_d_final_test_report.md`, `docs/final_research_report.md`, `docs/final_presentation.md` | B0 PIT p (0.321 should be 0.3905) |
| Revision audit | `output/stage7_models_v2/step3_*`, `step4_*`; Appendix C | `docs/complete_research_report.md` §14 | pre-fix gaps in figure 09 come from external audit notes |
| R-VALU / R-VAL | `output/stage7_models_v2/*` | this report; `README.md` | n/a |
| R-TEST | `output/stage8_test_v2/*` | this report; `README.md` | README §9 test PIT row and figures 31–32 use N = 501 (the primary sample is 500) |

## A.3 Contradictions catalogue

### Original documents vs code and artifacts
1. **Scaler window.** Gate C §2 UD-2 (L76) and §4 (L145), the Stage 5 specification (L42, L240), `implementation.md` (L186, L188) and the original `walk_forward_pipeline.py` docstring (L13, now corrected) all say $t\le\tau$. The code at `66924f3` uses $t\le\tau-2$. `research_protocol.md` L359 and L364 agree with the code.
2. **DTE window.** 20–50 in `SPX_data_research.md` (L219, L307), `data_feasibility_audit.md` (L138) and Gate B (L80–81); 15–90 in the code (`pipeline.py` L114, `batch_feature_pipeline.py` L161, `extract_stage8_test_features.py` L184). Gate B's 30-day bracketing failure rates were computed on the narrower window.
3. **Spread threshold.** 0.30 (`SPX_data_research.md` L148) vs 0.35 elsewhere and in the code.
4. **Forward-fill.** The protocol (L370–374), `implementation.md` (L195) and Stage 5 OD-4 ("reduces validation missingness … to 0.00%") vs the code, which applies the rule to test only; validation keeps 9 missing dates.
5. **Rate substitution.** Original metadata and Gate B (L180) say "zero silent constant substitution"; the original batch script at `cee01a1` (L39, L132) used r = 0.015 silently. `scratch/correct_feature_datasets.py` patched the committed CSVs, but the 2016-11-11 QKurt_30d and ATM_IV_60d were not recomputed, and the three replacement values are hard-coded without generating code.
6. **Exposure disclosure.** The ^GSPC Jan-2022 exposure is disclosed; the ^IRX download to 2022-01-05 (`cee01a1` L66) is not.
7. **Missing-date count.** Gate B §6.1 cites "missing vendor dates (30 days)" for the development data; 30 is the 2010–2021 total, and 21 fall in development.
8. **Half-day timestamp evidence.** Gate B L110 cites 2020-11-27 and 2020-12-24, both of which are missing sessions.
9. **ATM strike.** The documents say "the strike closest to F"; the code uses the parity strike $\arg\min|C-P|$.
10. **Feature labels.** `dsemi_20d` is a semi-volatility (square root taken), not a semivariance. `dd_20d` is the current drawdown, not the maximum drawdown.
11. **BKM description.** `SPX_data_research.md` L200 (K⁻³, K⁻⁴ weights) does not match the implemented weights (log-moneyness polynomials over K²).
12. **Generator of the committed CSVs.** The committed development/validation CSVs came from the `cee01a1` batch script plus the correction script (they contain `status_X`), not from the current batch script.
13. **HMM diagnostics.** The protocol (L513) states dwell ≥ 17.6 and occupancy ≥ 19.8%; the artifacts show minima of 40.96 and 26.4% (validation), 31.98 and 21.9% (mid-2012) and 45.19 and 29.3% (test).
14. **Unbacked Gate C numbers.** Not stored in any artifact: the in-sample DM 1.9165 (p 0.0277), the CRPS audit errors, the σ range [0.0039, 0.6767] (artifact range 0.0023–1.7264) and the B0 mean scale 0.010000 (artifact 0.010622; Gate D 0.010186 vs artifact 0.011023).
15. **Mid-2012 pair count.** 1,845 (Gate B L18, L296, L331) vs 1,844 (Gate B L363, Gate C, artifacts).
16. **Reproducibility guide.** Pinball levels "(10th, 50th, 90th)" vs the stored 0.01–0.99 levels with no 50th; "integrals = 1.0000" vs the stored 0.99999434.
17. **Gate C environment.** "Python 3.12, PyTorch 2.14.1, SciPy 1.14.1" is unverifiable: there is no lock file and the bytecode is cpython-313.

### Within the original documents
18. Target notation $r_{t+1}$ left in the Stage 5 specification after Proposal A.
19. Hypothesis labels: H3 and H4 swapped between `project_implementation_idea.md` and the protocol.
20. Model-ladder labels differ between `project_implementation_idea.md` and the final ladder; the "strong nonlinear baseline" was never built.
21. Label cutoff $\tau-1$ (`implementation.md` L107; Stage 5 Gate C box L346) vs $\tau-2$ elsewhere.
22. Forecast block indexing: $\tau+1\ldots\tau+21$ (protocol L367) vs $\tau\ldots\tau+20$ (Stage 5 L243). The code uses $\tau+1\ldots\tau+21$.
23. Gap rule ">2 days" (protocol L180) vs ">1 day" (protocol L373, Stage 5 L49).
24. HAC rationale: "non-overlapping, negligible autocorrelation" (protocol L401) vs "MA(1)" (Stage 5 L34). The latter is incorrect.
25. Bootstrap: Politis–White automatic block length and studentized intervals were pre-registered; a fixed length of 5 and percentile intervals were used.
26. Benjamini–Hochberg FDR was pre-registered and never applied.
27. Ablations were decision criteria (protocol §1.4) but were not run in the original pipeline.
28. MDN: "dropped due to loss instability" (protocol L512) vs "exploratory" (`implementation.md` L231).
29. The UD-4 pre-registered exclusion targeted the Jan 3→Jan 4 return (a nulled validation label under Proposal A); what was actually excluded was origin 2022-01-03, whose target uses the exposed Jan 4 close as its base. The N = 501 note calls that target "uncompromised", while the CSV `breach_note` says it used the accessed close.
30. The "frozen" protocol carries post-Gate-D edits and results.

### Original vs revised
31. Primary question: H1 (R1 vs B4) vs Q1 (B4 vs B3). Q1 was designated after Gate D.
32. λ: 0.01 vs 1e-4. Under converged fits λ = 0.01 is the worst value.
33. R1 − B4 on validation: +0.0056 vs −0.0040 (clipped) or −0.0081 (unclipped).
34. Validation calibration of B4 and R1: original "reject"; revised "pass".
35. Test R1 − B4: original +0.0054 (p 0.073) vs revised +0.0076 (p 0.025). The revised value is more favourable to R1 at the nominal level but still fails the pre-registered CI and threshold criteria.
36. README §13 calls the original outputs "unchanged". True as files, but re-running the original scripts on this branch would overwrite them with different numbers.

### Within the revision
37. README §9 test PIT row and figures 31–32 use N = 501; the primary sample is N = 500.
38. The pre-fix values in figure 09 come from uncommitted audit notes.
39. `scratch/check_step1_fit_diagnostics.py` reproduces the original predictions only at commit `029c16d`; on the current branch it reports differences by design.
