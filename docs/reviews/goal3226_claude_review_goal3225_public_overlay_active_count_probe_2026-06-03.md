# Goal3226: Claude Review — Goal3225 Public Overlay Active-Count Probe

**Date:** 2026-06-03
**Reviewer:** Claude (Sonnet 4.6) — independent review
**Scope:** Goal3225: bounded public RayJoin-style overlay active-count probe on Brazil county/soil CDB slices

## Verdict

**`accept`**

Goal3225 correctly extends the overlay active-count evidence from the
authored fixture level (Goal3223's 64-seed tiled fixture) to two bounded
public CDB slice cases. The public CDB slice machinery is correctly reused
from Goal2159. The count contract is correct: CPU `active_seed_count` is
compared against prepared OptiX `overlay_active_pair_dependency_count`, which
is the same contract correction established in Goal3223. Both public overlay
cases produce nonzero counts (1/1 and 9/9) that are stable across five
repetitions. Hardware metadata meets the Goal3218 standard. Report, JSON,
stdout, and tests are self-consistent. All prohibited claim-boundary flags
remain `false` at the artifact, row, and per-measurement levels.

No medium-severity issues are found. Two informational observations are noted
below.

This review does **not** authorize release, public speedup claims,
broad RT-core claims, true zero-copy claims, `RTDL beats RayJoin` claims, or
RayJoin paper-reproduction claims.

---

## Findings by Severity

### Medium — No issues at this severity

No correctness bugs, ABI violations, claim-boundary overreach, contract
defects, or inconsistencies in artifact evidence were found at medium severity.

### Low — No blocking items

No low-severity items are identified.

### Informational — No action required for current scope

**I1: Per-measurement claim_boundary uses a different key set than per-row and
top-level**

The per-measurement `claim_boundary` block within each entry of
`prepared_overlay_active_count` uses six keys with distinct names
(`full_rayjoin_reproduction`, `paper_scale_perf_claim_authorized`,
`requires_pod_for_optix_perf`, `rtdl_beats_rayjoin_claim_authorized`,
`v2_0_release_authorized`, `whole_app_speedup_claim_authorized`), while the
per-row and top-level `claim_boundary` blocks use the five canonical keys
(`public_speedup_claim_authorized`, `rt_core_speedup_claim_authorized`,
`rayjoin_paper_reproduction_claim_authorized`,
`rtdl_beats_rayjoin_claim_authorized`, `release_authorized`). All flags at
all levels are `false`. The artifact test checks the per-row and top-level
blocks but not the per-measurement block. The inconsistency in key names is
harmless at this scope — the per-measurement block is inherited from the
underlying workload call and not the canonical boundary format — but a reader
comparing blocks will see different keys. No action required.

**I2: Active pair counts on public slices remain small (1 and 9)**

The two public cases produce 1 active pair at the 128-chain slice and 9 active
pairs at the 256-chain slice. These counts are strictly nonzero, which closes
the public-data analog of Goal3221 L2 (the zero-count trivial parity
problem). They are, however, sparse relative to the full Brazil dataset.
Count correctness on 1 and 9 active pairs does not characterize dense overlay
behavior on realistic intersection densities. This is expected and correctly
described in the report as a bounded probe; it is not a defect in Goal3225's
scope. The informational context is: if future goals cite Goal3225 as evidence
of overlay count correctness on public data, the sparsity of these counts
should be acknowledged.

---

## Review Question Answers

### Q1: Does Goal3225 correctly reuse public CDB slice materialization from Goal2159 rather than authored fixtures?

**Yes.**

The script imports `CASES`, `DEFAULT_DATA_DIR`, `_materialize_slices`,
`_maybe_download_samples`, and `_resolve_dataset_template` directly from
`scripts.goal2159_rayjoin_public_cdb_runner`. The `build_artifact` function
calls `_maybe_download_samples`, `_materialize_slices`, and
`_resolve_dataset_template` in sequence, precisely following the Goal2159
public CDB pattern.

The selected cases (`overlay_county128_soil128`, `overlay_county256_soil256`)
are CASES entries defined in Goal2159, not authored or synthetic fixtures. The
JSON artifact confirms the actual resolved CDB paths:
- `br_county_start0_count128.cdb` + `br_soil_start0_count128.cdb`
- `br_county_start0_count256.cdb` + `br_soil_start0_count256.cdb`

The `dataset_note` field in each artifact row reads "External CDB overlay
pair-dependency case using left/right polygon chains," consistent with Goal2159
public CDB provenance.

The `build_artifact` guard (`if case.workload != "overlay_seed": raise
ValueError`) ensures that non-overlay cases cannot be silently mixed in. The
test `test_probe_reuses_public_cdb_runner_and_overlay_cases` machine-checks all
five import symbols and the guard phrase.

### Q2: Does it compare the correct overlay count contract: CPU `active_seed_count` versus prepared OptiX `overlay_active_pair_dependency_count`?

**Yes.**

`_active_seed_count(summary)` (script line 79–82) reads
`summary["active_seed_count"]` and raises `KeyError` if the field is absent,
making the contract explicit and fail-closed. This is the same count field
that Goal3223 corrected from the prior `pair_dependency_row_count` comparison
(Goal3221 L2).

`_run_prepared_count` calls `run_rayjoin_prepared_optix_workload` with
`result_mode="count"` and `include_rows=False`. The JSON artifact confirms that
each measurement's `summary.output_contract` field is
`"overlay_active_pair_dependency_count"` — the prepared OptiX route's declared
contract. The two contracts match semantically.

The `counts_match` field in each row is computed as:
```python
bool(observed_counts) and all(count == expected_active_count for count in observed_counts)
```
This is an honest parity check, not a proximity comparison. Both rows record
`counts_match: true`. The test `test_probe_compares_active_seed_count_contract`
machine-checks all five relevant terms.

### Q3: Are the two public overlay cases meaningful but bounded, and are their counts interpreted honestly as active-count parity rather than full row overlay continuation?

**Yes.**

| Case | Expected active seeds | Observed counts | Stable |
|------|---------------------:|-----------------|--------|
| `overlay_county128_soil128` | 1 | [1, 1, 1, 1, 1] | Yes |
| `overlay_county256_soil256` | 9 | [9, 9, 9, 9, 9] | Yes |

Both counts are nonzero and discriminating (an always-zero or always-wrong
implementation would fail). The 5/5 stability across repeats confirms that
the count route is deterministic on these inputs.

The report's interpretation section precisely separates the two count concepts:
the CPU reference computes the full overlay dependency summary and exposes
`active_seed_count`; the prepared OptiX route returns
`overlay_active_pair_dependency_count`. Neither the script nor the report
implies that row overlay continuation is exercised. `include_rows_measured:
false` is recorded in the measurements block.

The report boundary is explicit: "It does not claim full row overlay
continuation, paper-scale reproduction, or external RayJoin performance
parity." The row overlay continuation path is correctly deferred as Tier B.

### Q4: Is the hardware metadata sufficient for internal reproducibility?

**Yes.**

The JSON artifact `hardware` block contains:
- `nvidia_smi`: `"NVIDIA A40, 570.211.01"` — GPU identity and driver ✓
- `cuda_driver_query`: Full NVSMI log confirming Driver Version 570.211.01
  and CUDA Version 12.8 ✓
- `nvcc_version`: Full nvcc output, CUDA 12.8 V12.8.93, built 2025-02-21 ✓
- `rtdl_optix_library`: `/root/rtdl_goal3151/build/librtdl_optix.so` ✓

This matches the Goal3218 `_hardware_metadata` standard that was closed as L1
in Goal3221 and verified again in Goal3224. The commit
`021ee498711eb5ad8b21231872930b35461ed4a6` corresponds to the "Goal3225 add
public RayJoin overlay count probe" commit, confirming the pod ran from the
correct source state.

The `_hardware_metadata` function in Goal3225 follows the same dual-path
pattern (system path with `/usr/bin/` and `/usr/local/cuda/bin/` fallbacks)
established in Goal3223, ensuring the function is portable without being
fragile.

### Q5: Do the report, JSON artifact, stdout, and tests agree?

**Yes.**

Cross-check of all four artifacts:

| Field | Report | JSON | Stdout | Test |
|-------|--------|------|--------|------|
| county128 expected | 1 | `expected_active_seed_count: 1` | `rows=1` × 5 | asserts `== 1` |
| county128 observed | [1,1,1,1,1] | `observed_counts: [1,1,1,1,1]` | rows=1 × 5 | asserts `== [1,1,1,1,1]` |
| county128 median (s) | 0.023577 | `0.023576615378260612` | — | — |
| county256 expected | 9 | `expected_active_seed_count: 9` | `rows=9` × 5 | asserts `== 9` |
| county256 observed | [9,9,9,9,9] | `observed_counts: [9,9,9,9,9]` | rows=9 × 5 | asserts `== [9,9,9,9,9]` |
| county256 median (s) | 0.06121 | `0.061211783438920975` | — | — |
| status | pass | `"pass"` | — | asserts `== "pass"` |
| GPU | NVIDIA A40, 570.211.01 | same | — | asserts `==` |
| commit | 021ee498… | `"021ee498711eb5ad8b21231872930b35461ed4a6"` | — | asserts `==` |

The county256 median is verified: the five repeat values sorted are
[0.0605, 0.0606, 0.0612, 0.0709, 0.0781]; the third (median) is
0.0612, consistent with the JSON field value.

The stdout file ends with `[goal3225] wrote …json` and records 5/5 repeats for
each case. The artifact test's `test_report_and_stdout_are_consistent` checks
six report phrases and the stdout terminal lines.

### Q6: Are all claim boundaries preserved: no release, public speedup, broad RT-core, true zero-copy, `RTDL beats RayJoin`, or paper-reproduction authorization?

**Yes.**

At the top-level artifact:
```json
{
  "public_speedup_claim_authorized": false,
  "rt_core_speedup_claim_authorized": false,
  "rayjoin_paper_reproduction_claim_authorized": false,
  "rtdl_beats_rayjoin_claim_authorized": false,
  "release_authorized": false
}
```

All five flags are verified by `test_artifact_preserves_claim_boundaries`
at both the top level and per-row level. The per-measurement blocks carry
six additional flags (see I1), all `false`.

The report boundary section states: "This report does not authorize release,
public speedup claims, broad RT-core claims, true zero-copy claims, `RTDL
beats RayJoin` claims, or RayJoin paper-reproduction claims." The row overlay
continuation path is explicitly deferred. There is no language in the report,
script, or tests that asserts or implies any of the prohibited claims.

### Q7: What remains before stronger RayJoin overlay benchmark or paper-level claims?

The following prerequisites carry forward from the Goal3221/3224 chain. Goal3225
closes the public-data active-count gap specifically; all other items remain open.

1. **Row overlay continuation (Tier B).** `include_rows_measured: false` is
   explicit in all measurements. Row materialization evidence for the overlay
   route on public data must be produced before Tier B claims. This is the
   nearest prerequisite for any overlay-level claim beyond active-count parity.

2. **Full paper-scale dataset evidence.** Goal3225 uses slices of 128 and 256
   chains. The full Brazil county dataset has approximately 1.7M segments; soil
   approximately 690K. Paper-level comparison requires the full ICS-2024 scale
   inputs with the complete overlay result, not a bounded active-count probe.

3. **Cross-system comparison methodology.** Goal3225 compares RTDL's prepared
   OptiX overlay count against RTDL's own CPU reference. An `RTDL beats
   RayJoin` claim requires the same inputs as RayJoin would use, run under a
   properly scoped benchmark protocol on the same hardware, against RayJoin's
   own query execution as the baseline.

4. **Broader GPU family evidence.** All evidence in this chain (Goal3218,
   3220, 3223, 3225) is from a single NVIDIA A40 (Ampere, driver 570.211.01,
   CUDA 12.8). Architecture-specific RT-core claims require evidence from
   additional GPU families.

5. **True zero-copy claim.** `true_zero_copy_claim_authorized` does not appear
   in Goal3225's claim boundary (the flag is not included), but this claim
   remains unestablished in the chain. It is correctly absent from Goal3225's
   scope.

6. **Overlay active-count density.** The two probe cases yield 1 and 9 active
   pairs. Count correctness at this sparsity level is a necessary condition for
   the overlay route, but is not sufficient to characterize the dense overlay
   behavior expected on full-scale inputs.

---

## Prior Review Chain Closure Verification

| Item | Origin | Status in Goal3225 |
|------|--------|--------------------|
| L1: Hardware metadata regression | Goal3221 | Closed by Goal3223; Goal3225 adopts the same pattern correctly. |
| L2: Trivially weak overlay parity (zero count) | Goal3221 | Closed at fixture level by Goal3223 (64-seed authored); Goal3225 closes at public-data level (1 and 9). |
| L2: Incorrect count contract (pair_dependency_row_count) | Goal3221 | Closed by Goal3223; Goal3225 uses correct `active_seed_count` from the start. |
| I1: Non-default warmup/repeat | Goal3221 | Not applicable — Goal3225 defaults are `warmup=1, repeat=5` and the artifact records exactly those values. No discrepancy. |
| I2: LSI fixture scale | Goal3224 | Out of scope for Goal3225 (overlay_seed cases only). |
| Public-data gap for overlay route | Goal3224 Q7 | **Closed by Goal3225.** Active-count parity on two public CDB slice cases. |
| Row overlay continuation | Multiple | Open; explicitly deferred Tier B. |
| Paper-scale dataset | Multiple | Open; carries forward. |
| Cross-system comparison | Multiple | Open; carries forward. |
| Broader GPU family | Multiple | Open; carries forward. |

---

## Artifact Consistency Check

| Field | Report | JSON | Consistent |
|-------|--------|------|------------|
| Goal | Goal3225 | `3225` | Yes |
| Schema | — | `"rtdl.goal3225.rayjoin_public_overlay_active_count_probe.v1"` | Yes |
| Commit | `021ee498…` | `"021ee498711eb5ad8b21231872930b35461ed4a6"` | Yes |
| GPU | `NVIDIA A40, 570.211.01` | `"NVIDIA A40, 570.211.01"` | Yes |
| cuda_driver_query | present | Full NVSMI log, CUDA 12.8 | Yes |
| nvcc_version | present | V12.8.93, 2025-02-21 | Yes |
| rtdl_optix_library | present | `/root/rtdl_goal3151/build/librtdl_optix.so` | Yes |
| Warmups | `1` | `1` | Yes |
| Repeats | `5` | `5` | Yes |
| county128 expected | 1 | `1` | Yes |
| county128 observed | [1,1,1,1,1] | `[1,1,1,1,1]` | Yes |
| county128 counts_match | — | `true` | Yes |
| county256 expected | 9 | `9` | Yes |
| county256 observed | [9,9,9,9,9] | `[9,9,9,9,9]` | Yes |
| county256 counts_match | — | `true` | Yes |
| Status | `pass` | `"pass"` | Yes |
| include_rows_measured | — | `false` (both cases) | Yes |
| All claim boundary flags | false | false (all levels) | Yes |

---

## Summary

Goal3225 is a well-scoped and correctly implemented public-data active-count
probe. It reuses Goal2159's public CDB slice machinery without deviation,
applies the correct `active_seed_count` contract established in Goal3223, and
produces nonzero count parity on two Brazil county/soil CDB slice cases using
the prepared OptiX overlay route. The hardware metadata meets the Goal3218
reproducibility standard. Report, JSON, stdout, and tests are self-consistent.
All prohibited claim-boundary flags remain `false` at every level.

Two informational observations are noted: a minor key-name inconsistency in
per-measurement claim boundary blocks (I1, harmless), and the small magnitude
of public overlay active counts (I2, expected given bounded slice sizes).
Neither requires action at this scope.

Goal3225 closes the public-data gap in the overlay active-count evidence chain.
It is correctly positioned as internal planning evidence for active-count parity
only. The row overlay continuation path, paper-scale dataset evidence,
cross-system comparison methodology, and broader GPU family evidence all remain
open prerequisites for any stronger overlay benchmark or paper-level claim.

**This review does not authorize release, public speedup claims, broad RT-core
claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin
paper-reproduction claims.**
