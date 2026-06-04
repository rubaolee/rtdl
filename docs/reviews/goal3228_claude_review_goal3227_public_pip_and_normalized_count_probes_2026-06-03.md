# Goal3228: Claude Review — Goal3227 Public PIP Count Probe and Normalized Goal3225 Rerun

**Date:** 2026-06-03
**Reviewer:** Claude (Sonnet 4.6) — independent review
**Scope:** Goal3227: bounded public RayJoin-style PIP count probe on `pip_county512`; boundary-normalized Goal3225 rerun on two public Brazil county/soil CDB slice overlay cases. Both probes rerun at commit `67dcad5b4beb5c0d462a13ab75bb681c4aaee611`.

## Verdict

**`accept`**

Goal3227 correctly reuses Goal2159 public CDB slice materialization, applies
the correct `positive_assignment_count` PIP contract, and produces 1430/1430
stable counts across five repeats on NVIDIA A40. The boundary normalization
correctly addresses the Goal3226 observation by adding
`true_zero_copy_claim_authorized: false` at the top and per-row levels in both
Goal3225 and Goal3227. Both probes now carry all six canonical claim-boundary
flags at the top and row levels, all `false`. Report, JSON artifact, stdout
file, and tests are internally consistent at the post-normalization commit
`67dcad5b`. No medium-severity issues are found.

Together, Goal3218 (LSI), Goal3225 (overlay active-count), and Goal3227 (PIP)
complete public count/parity coverage across all three current RayJoin
count-family workloads on public CDB slices.

This review does **not** authorize release, public speedup claims, broad
RT-core claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin
paper-reproduction claims.

---

## Findings by Severity

### Medium — No issues at this severity

No correctness bugs, ABI violations, claim-boundary overreach, contract
defects, or inconsistencies in artifact evidence were found at medium severity.

### Low — No blocking items

No low-severity items are identified.

### Informational — No action required for current scope

**I1: Per-measurement claim_boundary key set is inherited from the underlying
workload call and differs from the canonical six-key format at the top and row
levels**

Both Goal3225 and Goal3227 per-measurement `claim_boundary` blocks carry six
keys with different names:
```json
{
  "full_rayjoin_reproduction": false,
  "paper_scale_perf_claim_authorized": false,
  "requires_pod_for_optix_perf": false,
  "rtdl_beats_rayjoin_claim_authorized": false,
  "v2_0_release_authorized": false,
  "whole_app_speedup_claim_authorized": false
}
```
The top and row levels now use the canonical six-key format including
`true_zero_copy_claim_authorized`. All values at all levels remain `false`.
This inconsistency was noted as I1 in Goal3226 and is carried forward
unchanged; it is harmless, inherited from the workload call, and not a defect
at this scope. The artifact tests do not check the per-measurement blocks.

**I2: PIP count at 512-chain slice is 1430 — more discriminating than overlay
counts but still bounded**

The `pip_county512` case yields 1430 positive assignments, substantially more
discriminating than the overlay probe (1 and 9 active pairs). A broken or
trivially-zero PIP implementation would not produce 1430 consistently. The
count is bounded to 512 Brazil county chains and is not claimed to represent
full-dataset PIP behavior. This is correct and accurately described in the
report as a bounded probe. Future goals citing Goal3227 as PIP count evidence
on public data should acknowledge the slice boundary (0:512 county chains, 24 880
polygon segments).

---

## Review Question Answers

### Q1: Does Goal3227 correctly reuse public CDB slice materialization from Goal2159 rather than authored fixtures?

**Yes.**

The script imports five symbols directly from
`scripts.goal2159_rayjoin_public_cdb_runner`:
`CASES`, `DEFAULT_DATA_DIR`, `_materialize_slices`, `_maybe_download_samples`,
and `_resolve_dataset_template`. The `build_artifact` function calls all five
in the same sequence as the Goal2159 pattern: download check, slice
materialization, then template resolution per case.

The `pip_county512` case is a Goal2159 `CASES` entry, not an authored or
synthetic fixture. The JSON artifact confirms the resolved dataset path:
`/root/rtdl_goal3151/data/rayjoin/br_county_start0_count512.cdb` with 512
chains and 24 880 segments. The `dataset_note` field reads "External CDB
point-location case using probe points and polygons from one file," consistent
with Goal2159 public CDB provenance.

The workload guard `if case.workload != "pip": raise ValueError("goal3227 probe
supports only PIP cases")` ensures non-PIP cases cannot be silently mixed in.
The unit test `test_probe_reuses_public_cdb_runner_and_pip_case`
machine-checks all five import symbols and the guard phrase.

### Q2: Does it compare the correct PIP count contract: CPU `positive_assignment_count` versus prepared OptiX count?

**Yes.**

`_positive_assignment_count(summary)` (script lines 76–79) reads
`summary["positive_assignment_count"]` and raises `KeyError` if absent, making
the contract explicit and fail-closed.

The CPU reference is obtained via `rayjoin.run_rayjoin_workload("pip",
backend="cpu_python_reference", ...)` with `include_rows=False`. The prepared
OptiX route calls `run_rayjoin_prepared_optix_workload("pip",
result_mode="count", include_rows=False)`.

The JSON artifact confirms that each measurement's `summary` contains
`output_contract: "point_to_shape_positive_hit_count"` and
`positive_assignment_count: 1430`. The `row_count` extracted from each
prepared-count payload also equals 1430. The `counts_match` field is computed
as:
```python
bool(observed_counts) and all(count == expected_count for count in observed_counts)
```
This is an honest parity check. The row records `counts_match: true` and
`include_rows_measured: false`.

The unit test `test_probe_compares_positive_assignment_count_contract`
machine-checks `positive_assignment_count`, `expected_positive_assignment_count`,
`prepared_pip_count`, `include_rows_measured`, and
`run_rayjoin_prepared_optix_workload`.

### Q3: Does the PIP artifact provide meaningful bounded public evidence with stable 1430/1430 counts across five repeats?

**Yes.**

| Case | Expected positive assignments | Observed counts | Stable |
|------|--------------------------:|-----------------|--------|
| `pip_county512` | 1430 | [1430, 1430, 1430, 1430, 1430] | Yes |

1430 is a substantive non-trivial count on 512 Brazil county chains (24 880
polygon segments). A broken PIP implementation or a trivially-always-zero or
always-non-zero oracle would not reproduce this count deterministically.
The 5/5 stability confirms the prepared OptiX PIP count route is deterministic
on this input.

The warmup (sec=0.756065) is excluded from the five measured repeats
(sec range: 0.0667–0.0931). The median of the five repeats is
0.0749423447996378 s, verified by independent sort of the five values.

### Q4: Did the boundary normalization correctly address the Goal3226 observation by adding `true_zero_copy_claim_authorized: false` to Goal3225 and Goal3227?

**Yes.**

The Goal3226 review noted (Q7, item 5) that `true_zero_copy_claim_authorized`
was absent from Goal3225's claim boundary. The normalization at commit
`67dcad5b` adds this flag at the top and per-row levels in both probes.

Current state in both scripts, at `_run_case()` and `build_artifact()`:
```python
"claim_boundary": {
    "public_speedup_claim_authorized": False,
    "rt_core_speedup_claim_authorized": False,
    "true_zero_copy_claim_authorized": False,
    "rayjoin_paper_reproduction_claim_authorized": False,
    "rtdl_beats_rayjoin_claim_authorized": False,
    "release_authorized": False,
}
```
Both JSON artifacts confirm `"true_zero_copy_claim_authorized": false` at both
the top-level and per-row `claim_boundary` blocks. Both artifact tests
(`test_artifact_preserves_claim_boundaries`) now machine-check all six flags at
both the top-level and per-row levels.

### Q5: Do the reports, JSON artifacts, stdout files, and tests agree after the reruns at commit `67dcad5b4beb5c0d462a13ab75bb681c4aaee611`?

**Yes.**

**Goal3227 cross-artifact consistency:**

| Field | Report | JSON | Stdout | Test |
|-------|--------|------|--------|------|
| Commit | `67dcad5b…` | `"67dcad5b4beb5c0d462a13ab75bb681c4aaee611"` | — | asserts `==` |
| GPU | `NVIDIA A40, 570.211.01` | `"NVIDIA A40, 570.211.01"` | — | asserts `==` |
| cuda_driver_query | present, CUDA 12.8 | NVSMI log, CUDA 12.8, driver 570.211.01 | — | asserts `"CUDA Version"` in |
| nvcc_version | present | V12.8.93, 2025-02-21 | — | asserts `"release 12.8"` in |
| rtdl_optix_library | `/root/rtdl_goal3151/build/librtdl_optix.so` | same | — | asserts `==` |
| Warmups | `1` | `1` | 1/1 warmup line | — |
| Repeats | `5` | `5` | 5/5 repeat lines | — |
| pip_county512 expected | 1430 | `1430` | rows=1430 × 5 | asserts `== 1430` |
| pip_county512 observed | [1430,…,1430] | `[1430,1430,1430,1430,1430]` | rows=1430 × 5 | asserts `== [1430,1430,1430,1430,1430]` |
| pip_county512 counts_match | — | `true` | — | asserts `assertTrue` |
| Median (s) | 0.0749423447996378 | `0.0749423447996378` | sec=0.074942 (repeat 5) | — |
| Status | `pass` | `"pass"` | — | asserts `== "pass"` |
| include_rows_measured | — | `false` | — | — |

Stdout repeat timing values match JSON measurement `total_seconds` values to
six decimal places (e.g., repeat 1: stdout=0.067785, JSON=0.06778521…). The
median is the third sorted value [0.06665, 0.06778, **0.07494**, 0.08271,
0.09308], confirmed as 0.0749423447996378.

**Goal3225 (rerun) cross-artifact consistency:**

| Field | county128_soil128 | county256_soil256 |
|-------|-------------------|-------------------|
| Commit | `67dcad5b…` | same |
| Expected active seeds | 1 | 9 |
| Observed | [1,1,1,1,1] | [9,9,9,9,9] |
| counts_match | true | true |
| Median (s) | 0.022725… | 0.062092… |

Median for county128: third sorted value [0.02247, 0.02255, **0.02272**, 0.02276,
0.02391] = 0.022725095972418785 ✓. Median for county256: third sorted value
[0.06058, 0.06118, **0.06209**, 0.07216, 0.08275] = 0.06209208257496357 ✓.
All stdout timing values match JSON measurement `total_seconds` fields to six
decimal places.

The Goal3225 artifact test now checks commit `67dcad5b4beb5c0d462a13ab75bb681c4aaee611`,
consistent with the rerun artifact.

### Q6: Are all claim boundaries preserved: no release, public speedup, broad RT-core, true zero-copy, `RTDL beats RayJoin`, or paper-reproduction authorization?

**Yes.**

Both Goal3225 and Goal3227 carry the six canonical flags at the top-level and
per-row `claim_boundary` blocks, all `false`:

```json
{
  "public_speedup_claim_authorized": false,
  "rt_core_speedup_claim_authorized": false,
  "true_zero_copy_claim_authorized": false,
  "rayjoin_paper_reproduction_claim_authorized": false,
  "rtdl_beats_rayjoin_claim_authorized": false,
  "release_authorized": false
}
```

Both artifact tests verify all six flags at both the top-level and per-row
levels. The per-measurement blocks inherited from the workload call carry a
different six-key set (see I1), but all values remain `false` at every level.

Both reports carry explicit boundary statements: "This report does not
authorize release, public speedup claims, broad RT-core claims, true zero-copy
claims, `RTDL beats RayJoin` claims, or RayJoin paper-reproduction claims."

No language in either script, report, or test implies or asserts any of the
prohibited claims.

### Q7: What remains before stronger RayJoin benchmark or paper-level claims?

The following open prerequisites carry forward from the Goal3218/3221/3223/3224/3225/3227
chain. Goal3227 closes the public-data PIP count gap; no other items are
closed here.

1. **Row PIP and overlay continuation.** Both Goal3225 and Goal3227 record
   `include_rows_measured: false`. Row materialization evidence for both the
   PIP and overlay routes on public data must be produced before any row-level
   claims. This is the nearest prerequisite for any claim beyond active-count
   or positive-assignment-count parity.

2. **Full paper-scale dataset evidence.** Goal3227 uses 512 county chains
   (24 880 segments). The full Brazil county dataset has approximately 1.7M
   segments. Paper-level comparison requires full ICS-2024 scale inputs with
   complete results, not bounded slice probes.

3. **Cross-system comparison methodology.** Both probes compare RTDL's
   prepared OptiX output against RTDL's own CPU reference. An `RTDL beats
   RayJoin` claim requires the same inputs as RayJoin would use, run under a
   properly scoped benchmark protocol on the same hardware, against RayJoin's
   own query execution as the baseline.

4. **Broader GPU family evidence.** All count-chain evidence (Goal3218, 3220,
   3223, 3225, 3227) is from a single NVIDIA A40 (Ampere, driver 570.211.01,
   CUDA 12.8). Architecture-specific RT-core claims require evidence from
   additional GPU families.

5. **True zero-copy claim.** `true_zero_copy_claim_authorized: false` is now
   explicitly recorded in both probes. The underlying true-zero-copy
   implementation evidence chain remains separate and has not been advanced by
   Goal3225 or Goal3227.

6. **Overlay active-count density.** Goal3225 public cases yield 1 and 9
   active pairs on 128- and 256-chain slices. These counts are necessary but
   not sufficient to characterize dense overlay behavior at realistic
   intersection densities. Carries forward as in Goal3226 review.

---

## Boundary Normalization Verification

| Probe | Flag | Script | JSON top-level | JSON per-row | Test |
|-------|------|--------|---------------|--------------|------|
| Goal3225 | `true_zero_copy_claim_authorized` | `False` ✓ | `false` ✓ | `false` ✓ (both rows) | checked ✓ |
| Goal3227 | `true_zero_copy_claim_authorized` | `False` ✓ | `false` ✓ | `false` ✓ | checked ✓ |
| Goal3225 | all other 5 canonical flags | `False` ✓ | `false` ✓ | `false` ✓ | checked ✓ |
| Goal3227 | all other 5 canonical flags | `False` ✓ | `false` ✓ | `false` ✓ | checked ✓ |

The Goal3226 observation is fully addressed. Both scripts, both JSON artifacts,
and both artifact tests are consistent with the normalization at commit
`67dcad5b`.

---

## Prior Review Chain Closure Verification

| Item | Origin | Status after Goal3227 + normalized Goal3225 |
|------|--------|----------------------------------------------|
| L1: Hardware metadata regression | Goal3221 | Closed by Goal3223; Goal3225 and Goal3227 adopt same pattern. ✓ |
| L2: Trivially weak overlay parity (zero count) | Goal3221 | Closed at fixture level (Goal3223); closed at public-data level (Goal3225: counts 1 and 9). ✓ |
| L2: Incorrect count contract (pair_dependency_row_count) | Goal3221 | Closed by Goal3223; Goal3225 uses `active_seed_count` correctly. ✓ |
| Public-data gap for overlay route | Goal3224 Q7 | Closed by Goal3225. ✓ |
| Public-data gap for PIP route | Goal3226 Q7 | **Closed by Goal3227.** ✓ |
| `true_zero_copy_claim_authorized` absent from claim boundary | Goal3226 Q7 I (noted) | **Closed by normalization at `67dcad5b`.** ✓ |
| Per-measurement claim_boundary key inconsistency (I1) | Goal3226 I1 | Carried forward; harmless; no action required. |
| Row PIP continuation | Multiple | Open; `include_rows_measured: false`. |
| Row overlay continuation | Multiple | Open; explicitly deferred Tier B. |
| Paper-scale dataset | Multiple | Open; carries forward. |
| Cross-system comparison | Multiple | Open; carries forward. |
| Broader GPU family | Multiple | Open; carries forward. |
| True zero-copy implementation claim | Multiple | Open; flag now explicitly `false` in both probes. |
| Overlay active-count density | Goal3226 I2 | Carried forward; expected given bounded slice sizes. |

---

## Artifact Consistency Summary

### Goal3227

| Field | Report | JSON | Stdout | Test | Consistent |
|-------|--------|------|--------|------|------------|
| Goal | Goal3227 | `3227` | — | — | Yes |
| Schema | — | `"rtdl.goal3227.rayjoin_public_pip_count_probe.v1"` | — | checked | Yes |
| Commit | `67dcad5b…` | `"67dcad5b4beb5c0d462a13ab75bb681c4aaee611"` | — | asserts `==` | Yes |
| GPU | NVIDIA A40, 570.211.01 | same | — | asserts `==` | Yes |
| CUDA driver | present | CUDA 12.8, driver 570.211.01 | — | asserts substring | Yes |
| nvcc | present | V12.8.93, 2025-02-21 | — | asserts substring | Yes |
| OptiX library | `/root/…/librtdl_optix.so` | same | — | asserts `==` | Yes |
| Warmups | `1` | `1` | 1 warmup line | — | Yes |
| Repeats | `5` | `5` | 5 repeat lines | — | Yes |
| pip_county512 expected | 1430 | `1430` | rows=1430 × 5 | asserts `== 1430` | Yes |
| pip_county512 observed | [1430×5] | `[1430,1430,1430,1430,1430]` | rows=1430 × 5 | asserts `==` | Yes |
| counts_match | — | `true` | — | asserts `assertTrue` | Yes |
| Median (s) | 0.0749423… | `0.0749423447996378` | sec=0.074942 (repeat 5) | — | Yes |
| Status | `pass` | `"pass"` | — | asserts `== "pass"` | Yes |
| include_rows_measured | — | `false` | — | — | Yes |
| All 6 claim boundary flags | false | false at top and row | — | all checked | Yes |

### Goal3225 (normalized rerun)

| Field | Report | JSON | Stdout | Test | Consistent |
|-------|--------|------|--------|------|------------|
| Goal | Goal3225 | `3225` | — | — | Yes |
| Schema | — | `"rtdl.goal3225.rayjoin_public_overlay_active_count_probe.v1"` | — | checked | Yes |
| Commit | `67dcad5b…` | `"67dcad5b4beb5c0d462a13ab75bb681c4aaee611"` | — | asserts `==` | Yes |
| GPU | NVIDIA A40, 570.211.01 | same | — | asserts `==` | Yes |
| county128 expected | 1 | `1` | rows=1 × 5 | asserts `== 1` | Yes |
| county128 observed | [1×5] | `[1,1,1,1,1]` | rows=1 × 5 | asserts `==` | Yes |
| county128 median (s) | 0.022725… | `0.022725095972418785` | sec=0.022725 (repeat 2) | — | Yes |
| county256 expected | 9 | `9` | rows=9 × 5 | asserts `== 9` | Yes |
| county256 observed | [9×5] | `[9,9,9,9,9]` | rows=9 × 5 | asserts `==` | Yes |
| county256 median (s) | 0.06209… | `0.06209208257496357` | sec=0.062092 (repeat 5) | — | Yes |
| Status | `pass` | `"pass"` | — | asserts `== "pass"` | Yes |
| All 6 claim boundary flags | false | false at top and row | — | all checked | Yes |

---

## Summary

Goal3227 is a well-scoped and correctly implemented public-data PIP count
probe. It reuses Goal2159's public CDB slice machinery without deviation,
applies the correct `positive_assignment_count` PIP contract, and produces
stable 1430/1430 counts across five repeats on NVIDIA A40. Hardware metadata
meets the Goal3218 reproducibility standard. Report, JSON, stdout, and tests
are internally consistent.

The boundary normalization at commit `67dcad5b` correctly addresses the
Goal3226 observation by adding `true_zero_copy_claim_authorized: false` at the
top and per-row levels in both Goal3225 and Goal3227. Both scripts, both JSON
artifacts, and both artifact tests now carry all six canonical claim-boundary
flags uniformly at `false`. The per-measurement block key-name inconsistency
(I1, inherited from the workload call) is carried forward unchanged and remains
harmless.

Together with Goal3218 (LSI) and Goal3225 (overlay active-count), Goal3227
completes public count/parity coverage for all three current RayJoin
count-family workloads on bounded public CDB slices. The row-continuation
paths, paper-scale dataset evidence, cross-system comparison methodology,
broader GPU family evidence, and true zero-copy implementation claim all remain
open prerequisites for any stronger RayJoin benchmark or paper-level claim.

**This review does not authorize release, public speedup claims, broad RT-core
claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin
paper-reproduction claims.**
