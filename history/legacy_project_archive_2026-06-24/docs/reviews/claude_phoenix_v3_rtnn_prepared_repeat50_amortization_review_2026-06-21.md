I'll read all the evidence and context files in parallel before rendering any judgment.
Now reading the context boundary files.
I've read all six primary and four context files. Here is my review.

---

# External Review: Phoenix V3 RTNN Prepared Repeat50 Amortization

**Candidate:** `rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02`
**Reviewer:** Claude Sonnet 4.6 (external, acting on 2026-06-21)
**Evidence read directly:** all six files listed in the call-for-review.

---

## 1. Verdict

**APPROVE\_WITH\_CONDITIONS**

The runner-wall speedup is real and material for the scoped prepared repeat50 contract, parity holds at the integer level, hardware is confirmed, and the amortization pattern matches prior approved M7 rows (AABB repeat50, grouped_sum repeat100). However, four conditions must be met before M7 promotion, all tied to wording precision and provenance disclosure — none of them require a rerun.

---

## 2. Critical Findings

### P0

**P0-A — Cold-plus-query (1.315x) is below the 2.0x material floor for single-use scenarios.**
Source: `summary.json:comparisons.rtdl_optix_over_cupy_grid_cold_plus_query_speedup = 1.3150`.
The runner-wall 3.761x is genuine only because 50 × (84ms − 11ms) = 3.65 s accumulates in the CuPy column across 50 repeated queries. One query cold-start yields 1.315x. Public wording must never present this row without the repeat50 amortization basis disclosed in the same sentence. Any wording that allows a reader to infer that RTDL OptiX is faster for single-shot RTNN is a P0 violation. The candidate documents themselves correctly flag this (`No one-shot or cold-start RTNN speedup claim; cold-plus-query is only 1.315x`) — the condition is to carry that language through to all public surfaces.

**P0-B — `exact: false` appears in the OptiX contract while `exact: true` appears in the CuPy contract.**
Source: `rtnn_full_batch_float32_optix.json:contract.exact = false`; `rtnn_full_batch_float32_cupy_grid.json:contract.exact = true`.
The actual parity is confirmed by integer-checksum match and sum_distance relative error 1.207e-10 (well within the 1e-4 tolerance). The precision difference is float32 OptiX versus float64 CuPy coordinate arithmetic. But a public row cannot present the comparison as same-precision unless this asymmetry is disclosed. The approved row must name "float32 OptiX ranked-summary vs float64-coordinate CuPy grid" as the contract pair; claiming "same-contract exactness" without the float32/float64 qualifier is a P0 wording violation.

---

### P1

**P1-A — No git provenance in the run environment.**
Source: `summary.json:environment.git_head = "fatal: not a git repository"`.
The source manifest (`source_manifest.sha256`) records four SHA256 hashes — runner scripts, `rtdl_optix_core.cpp`, and `librtdl_optix.so` — which are the only tie between the binary and the source tree. This is weaker than a committed git head. The condition is to cite the SHA256 manifest as the explicit provenance anchor in any public row record; "source verified by SHA256 manifest" must appear, not "source verified by git commit."

**P1-B — All three timing numbers must travel together in any public presentation.**
Source: `summary.json:comparisons` (hot 7.889x, cold+query 1.315x, runner-wall 3.761x).
Quoting 7.889x or 3.761x as headline figures without the 1.315x cold-plus-query figure in the same sentence is a P1 violation. The 7.889x hot-query number is the most impressive and the most likely to be excerpted; omitting context would mislead users into believing cold-start RTNN benefits exist at the same ratio.

**P1-C — CuPy grid baseline identity must be named explicitly.**
Source: `rtnn_full_batch_float32_cupy_grid.json:contract.uniform_grid_cuda_core = true, uses_rt_cores = false`.
This is a CUDA-core uniform-grid baseline, not Embree, not a CPU SIMD baseline, not the RTNN paper implementation. Public wording must name it as "CuPy uniform-grid CUDA-core" — not "nearest-neighbor baseline," "RTNN baseline," or anything that implies a general comparison to state-of-the-art NN implementations.

---

### P2

**P2-A — `execution_path_policy_version: null` in OptiX contract.**
Source: `rtnn_full_batch_float32_optix.json:contract.execution_path_policy_version = null`.
This is absent execution-path policy versioning. Not a blocker because the mode string (`ranked-summary-aggregate-prepared-query-batch-float32`) and batch_count (1) provide enough identification, but a future rerun should record the policy version.

**P2-B — CuPy grid is not the strongest available GPU CUDA baseline (e.g., cuML, FAISS).**
Source: baseline choice documented in `summary.json:checks.cupy_grid_reference_route_present = true`.
The comparison is honest for what it is, but a cautious reader may ask why CuPy's uniform grid was chosen over optimized libraries. No action required before M7 — this is a known limitation of the row scope — but the public wording must not imply generality to other GPU NN baselines.

---

## 3. Required Changes Before M7

1. **Repeat50 scope disclosure in every public sentence.** Any sentence quoting a speedup number must include the phrase "across 50 prepared repeated queries on the same search structure" or equivalent. The row ID itself encodes repeat50, which is good; the prose must match.

2. **Three-number presentation rule.** Public wording must present hot-query (7.889x), cold-plus-query (1.315x), and runner-wall (3.761x) together, in that order, with no selective use of any one figure alone.

3. **float32/float64 disclosure.** Public row wording must state "RTDL OptiX (float32 internal precision) versus CuPy uniform-grid CUDA-core (float64 coordinates)" and note that parity is confirmed at sum_distance relative error 1.207e-10.

4. **Provenance citation.** The M7 row record must cite: "source provenance verified by `source_manifest.sha256`; no git head available from the run environment."

5. **Baseline name.** CuPy uniform-grid CUDA-core must be named as the reference, not abbreviated to "CuPy" without the "grid" qualifier, and never called "the RTNN baseline" or "nearest-neighbor baseline."

No rerun is required.

---

## 4. Allowed Public Wording (if conditions met)

The following is an example of compliant wording; variations must preserve every bracketed scope qualifier:

> On a single NVIDIA RTX 4000 Ada Generation GPU, RTDL OptiX ranked-summary (float32, CUBIN cache) achieves **7.889x hot-query speedup**, **3.761x full-session speedup**, and **1.315x cold-plus-prepare speedup** over a CuPy uniform-grid CUDA-core reference, at 1,048,576 points (k=50, radius=0.02), across 50 prepared repeated queries on the same search structure. Source provenance: `source_manifest.sha256`. This is a scoped prepared repeated-session amortization result only; it is not a one-shot, cold-start, paper-equivalent, or general nearest-neighbor speedup claim.

The row may be listed in M7 row records as:

> `rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02` — **ranked_summary / rtnn** — M7-qualified row-scoped, prepared repeat50 amortization only, RTX 4000 Ada, float32 OptiX vs float64 CuPy grid, not V3 release authorization.

---

## 5. Forbidden Wording

The following must remain explicitly blocked regardless of M7 promotion:

- "RTNN is solved" / "RTNN acceleration is achieved" / "V3 solves nearest-neighbor search."
- "RTDL beats RTNN" or any comparison to the RTNN paper implementation.
- Any V3-over-V2 inference drawn from this row.
- Using the 7.889x hot-query figure alone without the 1.315x cold figure in the same presentation.
- Using 3.761x as a single-query or cold-start speedup — it is a 50-query session figure only.
- "Beats nearest-neighbor methods" or any generalization beyond the specific CuPy uniform-grid CUDA-core baseline.
- Claims valid for other hardware, scales (other than 1,048,576 points), k values, radii, or precision modes.
- "Release authorized," "V3 ready," or any inference that this row implies release authorization.
- Any wording that omits the repeat50 session scope from the speedup description.
- Using runner-wall 3.761x as a headline figure without disclosing it is an amortized 50-query result.

---

## 6. Final Recommendation

**Promote the exact row `rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02` to M7 status under the ranked_summary capability, subject to the four wording/provenance conditions above.**

Rationale: The evidence is structurally sound. The repeat50 amortization pattern is the same contract type used by two already-approved AABB rows and the grouped_sum row. The 3.761x runner-wall speedup is arithmetically well-explained by the 7.889x hot-query advantage compounding over 50 iterations; it is not inflated. Integer-level parity is confirmed. Hardware is confirmed on the correct RTX Ada pod. The candidate packet correctly keeps all release flags false and explicitly names the one-shot boundary.

The four conditions (scope disclosure, three-number presentation, float32/float64 naming, provenance citation) are all editorial requirements on public wording — no rerun is needed. If those conditions are met in the M7 row record before publication, this row is approvable.

**Release authorization remains false. Broad V3-over-V2, whole-RTNN, one-shot RTNN, and paper-equivalent wording remain forbidden. This review does not close any release blocker listed in `v3_release_authorization_blockers_2026-06-20.md`.**
I've read all six primary and four context files. Here is my review.

---

# External Review: Phoenix V3 RTNN Prepared Repeat50 Amortization

**Candidate:** `rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02`
**Reviewer:** Claude Sonnet 4.6 (external, acting on 2026-06-21)
**Evidence read directly:** all six files listed in the call-for-review.

---

## 1. Verdict

**APPROVE\_WITH\_CONDITIONS**

The runner-wall speedup is real and material for the scoped prepared repeat50 contract, parity holds at the integer level, hardware is confirmed, and the amortization pattern matches prior approved M7 rows (AABB repeat50, grouped_sum repeat100). However, four conditions must be met before M7 promotion, all tied to wording precision and provenance disclosure — none of them require a rerun.

---

## 2. Critical Findings

### P0

**P0-A — Cold-plus-query (1.315x) is below the 2.0x material floor for single-use scenarios.**
Source: `summary.json:comparisons.rtdl_optix_over_cupy_grid_cold_plus_query_speedup = 1.3150`.
The runner-wall 3.761x is genuine only because 50 × (84ms − 11ms) = 3.65 s accumulates in the CuPy column across 50 repeated queries. One query cold-start yields 1.315x. Public wording must never present this row without the repeat50 amortization basis disclosed in the same sentence. Any wording that allows a reader to infer that RTDL OptiX is faster for single-shot RTNN is a P0 violation. The candidate documents themselves correctly flag this (`No one-shot or cold-start RTNN speedup claim; cold-plus-query is only 1.315x`) — the condition is to carry that language through to all public surfaces.

**P0-B — `exact: false` appears in the OptiX contract while `exact: true` appears in the CuPy contract.**
Source: `rtnn_full_batch_float32_optix.json:contract.exact = false`; `rtnn_full_batch_float32_cupy_grid.json:contract.exact = true`.
The actual parity is confirmed by integer-checksum match and sum_distance relative error 1.207e-10 (well within the 1e-4 tolerance). The precision difference is float32 OptiX versus float64 CuPy coordinate arithmetic. But a public row cannot present the comparison as same-precision unless this asymmetry is disclosed. The approved row must name "float32 OptiX ranked-summary vs float64-coordinate CuPy grid" as the contract pair; claiming "same-contract exactness" without the float32/float64 qualifier is a P0 wording violation.

---

### P1

**P1-A — No git provenance in the run environment.**
Source: `summary.json:environment.git_head = "fatal: not a git repository"`.
The source manifest (`source_manifest.sha256`) records four SHA256 hashes — runner scripts, `rtdl_optix_core.cpp`, and `librtdl_optix.so` — which are the only tie between the binary and the source tree. This is weaker than a committed git head. The condition is to cite the SHA256 manifest as the explicit provenance anchor in any public row record; "source verified by SHA256 manifest" must appear, not "source verified by git commit."

**P1-B — All three timing numbers must travel together in any public presentation.**
Source: `summary.json:comparisons` (hot 7.889x, cold+query 1.315x, runner-wall 3.761x).
Quoting 7.889x or 3.761x as headline figures without the 1.315x cold-plus-query figure in the same sentence is a P1 violation. The 7.889x hot-query number is the most impressive and the most likely to be excerpted; omitting context would mislead users into believing cold-start RTNN benefits exist at the same ratio.

**P1-C — CuPy grid baseline identity must be named explicitly.**
Source: `rtnn_full_batch_float32_cupy_grid.json:contract.uniform_grid_cuda_core = true, uses_rt_cores = false`.
This is a CUDA-core uniform-grid baseline, not Embree, not a CPU SIMD baseline, not the RTNN paper implementation. Public wording must name it as "CuPy uniform-grid CUDA-core" — not "nearest-neighbor baseline," "RTNN baseline," or anything that implies a general comparison to state-of-the-art NN implementations.

---

### P2

**P2-A — `execution_path_policy_version: null` in OptiX contract.**
Source: `rtnn_full_batch_float32_optix.json:contract.execution_path_policy_version = null`.
This is absent execution-path policy versioning. Not a blocker because the mode string (`ranked-summary-aggregate-prepared-query-batch-float32`) and batch_count (1) provide enough identification, but a future rerun should record the policy version.

**P2-B — CuPy grid is not the strongest available GPU CUDA baseline (e.g., cuML, FAISS).**
Source: baseline choice documented in `summary.json:checks.cupy_grid_reference_route_present = true`.
The comparison is honest for what it is, but a cautious reader may ask why CuPy's uniform grid was chosen over optimized libraries. No action required before M7 — this is a known limitation of the row scope — but the public wording must not imply generality to other GPU NN baselines.

---

## 3. Required Changes Before M7

1. **Repeat50 scope disclosure in every public sentence.** Any sentence quoting a speedup number must include the phrase "across 50 prepared repeated queries on the same search structure" or equivalent. The row ID itself encodes repeat50, which is good; the prose must match.

2. **Three-number presentation rule.** Public wording must present hot-query (7.889x), cold-plus-query (1.315x), and runner-wall (3.761x) together, in that order, with no selective use of any one figure alone.

3. **float32/float64 disclosure.** Public row wording must state "RTDL OptiX (float32 internal precision) versus CuPy uniform-grid CUDA-core (float64 coordinates)" and note that parity is confirmed at sum_distance relative error 1.207e-10.

4. **Provenance citation.** The M7 row record must cite: "source provenance verified by `source_manifest.sha256`; no git head available from the run environment."

5. **Baseline name.** CuPy uniform-grid CUDA-core must be named as the reference, not abbreviated to "CuPy" without the "grid" qualifier, and never called "the RTNN baseline" or "nearest-neighbor baseline."

No rerun is required.

---

## 4. Allowed Public Wording (if conditions met)

The following is an example of compliant wording; variations must preserve every bracketed scope qualifier:

> On a single NVIDIA RTX 4000 Ada Generation GPU, RTDL OptiX ranked-summary (float32, CUBIN cache) achieves **7.889x hot-query speedup**, **3.761x full-session speedup**, and **1.315x cold-plus-prepare speedup** over a CuPy uniform-grid CUDA-core reference, at 1,048,576 points (k=50, radius=0.02), across 50 prepared repeated queries on the same search structure. Source provenance: `source_manifest.sha256`. This is a scoped prepared repeated-session amortization result only; it is not a one-shot, cold-start, paper-equivalent, or general nearest-neighbor speedup claim.

The row may be listed in M7 row records as:

> `rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02` — **ranked_summary / rtnn** — M7-qualified row-scoped, prepared repeat50 amortization only, RTX 4000 Ada, float32 OptiX vs float64 CuPy grid, not V3 release authorization.

---

## 5. Forbidden Wording

The following must remain explicitly blocked regardless of M7 promotion:

- "RTNN is solved" / "RTNN acceleration is achieved" / "V3 solves nearest-neighbor search."
- "RTDL beats RTNN" or any comparison to the RTNN paper implementation.
- Any V3-over-V2 inference drawn from this row.
- Using the 7.889x hot-query figure alone without the 1.315x cold figure in the same presentation.
- Using 3.761x as a single-query or cold-start speedup — it is a 50-query session figure only.
- "Beats nearest-neighbor methods" or any generalization beyond the specific CuPy uniform-grid CUDA-core baseline.
- Claims valid for other hardware, scales (other than 1,048,576 points), k values, radii, or precision modes.
- "Release authorized," "V3 ready," or any inference that this row implies release authorization.
- Any wording that omits the repeat50 session scope from the speedup description.
- Using runner-wall 3.761x as a headline figure without disclosing it is an amortized 50-query result.

---

## 6. Final Recommendation

**Promote the exact row `rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02` to M7 status under the ranked_summary capability, subject to the four wording/provenance conditions above.**

Rationale: The evidence is structurally sound. The repeat50 amortization pattern is the same contract type used by two already-approved AABB rows and the grouped_sum row. The 3.761x runner-wall speedup is arithmetically well-explained by the 7.889x hot-query advantage compounding over 50 iterations; it is not inflated. Integer-level parity is confirmed. Hardware is confirmed on the correct RTX Ada pod. The candidate packet correctly keeps all release flags false and explicitly names the one-shot boundary.

The four conditions (scope disclosure, three-number presentation, float32/float64 naming, provenance citation) are all editorial requirements on public wording — no rerun is needed. If those conditions are met in the M7 row record before publication, this row is approvable.

**Release authorization remains false. Broad V3-over-V2, whole-RTNN, one-shot RTNN, and paper-equivalent wording remain forbidden. This review does not close any release blocker listed in `v3_release_authorization_blockers_2026-06-20.md`.**
