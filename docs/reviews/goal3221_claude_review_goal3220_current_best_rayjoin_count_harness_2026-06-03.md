# Goal3221: Claude Review — Goal3220 Current-Best RayJoin Count Harness

**Date:** 2026-06-03
**Reviewer:** Claude (Sonnet 4.6) — independent review
**Scope:** Goal3220: current-best internal Spatial RayJoin count/parity harness

## Verdict

**`accept-with-boundary`**

Goal3220 is correctly structured as an internal count/parity harness. It does not
rewrite or overload historical Goal2799. The route policy is sensible and
correctly implemented. The app-agnostic native boundary is preserved. All
prohibited claim-boundary flags are `False`. The pod evidence proves count/parity
correctness on the current fixture rows for all three workloads. Two low-severity
items are noted below.

This review does **not** authorize release, public speedup claims,
whole-app speedup claims, true zero-copy claims, `RTDL beats RayJoin` claims, or
RayJoin paper-reproduction claims.

---

## Findings by Severity

### Medium — No issues at this severity

No correctness bugs, claim-boundary violations, or ABI defects were found at
medium severity.

### Low — Items to address before stronger use

**L1: Hardware metadata reduced from the Goal3218 standard**

`_run_metadata()` (script lines 47–55) collects only `source_commit`,
`source_dirty`, and `gpu` (name + driver from `nvidia-smi --query-gpu`). It does
not collect `nvcc` version, CUDA toolkit version, or the OptiX library path —
information that Goal3218's `_hardware_metadata()` explicitly added to close
Goal3214 I2 and the Goal3217 future-work item on reproducibility.

For a harness focused on count/parity correctness rather than comparative timing,
the current metadata (`NVIDIA A40, 570.211.01`, commit
`06d86d597574550cde3f3775b3fc6c975e380606`) is minimally sufficient for internal
planning evidence. However, if any future goal cites this harness's timing numbers
for comparison, the reduced metadata would make the citation less reproducible than
Goal3218 evidence.

**What to fix:** For planning-level internal use, acceptable as-is. Before any
timing numbers from this harness are cited in an external comparison or a stronger
benchmark claim, expand `_run_metadata()` to match Goal3218's `_hardware_metadata`
pattern: add `nvcc --version` output, `nvidia-smi --query --display=COMPUTE`, and
the resolved `librtdl_optix.so` path.

**L2: `overlay_seed` expected count of 0 is a trivially weak parity test**

The artifact records `expected_count: 0` and `observed_count: 0` for
`overlay_seed` across all five repetitions. The CPU reference also returns
`pair_dependency_row_count: 0` for this fixture (county and soil subsets with no
overlapping polygon pairs). Any implementation that returns 0 unconditionally
would pass this parity check. The test does assert `matches_cpu_reference: true`,
but the fixture's ground-truth count of 0 means this assertion proves only
non-crash execution and consistent 0-returning behavior, not semantic correctness
of the overlay-seed route on a non-trivial fixture.

This is not a bug in Goal3220 — it records the fixture faithfully — but it is a
limitation of the parity evidence for the `overlay_seed` workload specifically.

**What to fix:** For the `overlay_seed` route to provide meaningful count/parity
evidence, a supplementary fixture with at least one confirmed overlay pair
dependency is needed. This can be deferred; it does not block the current
internal-evidence use of the harness. Document the limitation explicitly in the
report if this harness is cited in v2.8/v3.0 planning for the overlay-seed route.

### Informational — No action required for current scope

**I1: Pod was run with non-default warmup/repeat parameters**

The script's CLI defaults are `warmup=2, repeat=7`. The pod report and artifact
JSON record `warmup: 1, repeat: 5`. The artifact test
(`goal3220_spatial_rayjoin_current_best_count_harness_artifact_test.py`) does not
assert specific warmup/repeat values, so the test correctly validates the artifact
as produced. This is not an inconsistency — CLI defaults are advisory, not a pod
contract — but a reader comparing the harness defaults to the artifact would see a
discrepancy without an explanation in the report or the artifact. No action
required.

**I2: Fixture counts are very small (pip=6, lsi=1, overlay_seed=0)**

All three workloads operate on the `br_county_subset.cdb` (and
`br_soil_subset.cdb` for overlay_seed) fixture. The intersection counts are
fixture-minimal: 6, 1, 0. These are sufficient to prove count/parity on the
current fixture rows, consistent with the `tier_a_count_or_parity_only: true`
and `row_overlay_continuation_deferred_tier_b: true` boundary flags. They are not
sufficient for scale evidence, representative benchmarks, or any claim about
production workload performance.

**I3: Kernel patch stability remains open (inherited from Goal3214 I4)**

`ensure_segment_pair_left_id_count_device_columns_pipeline` builds the LSI count
kernel by string-patching the upstream intersection kernel source. This dependency
on a stable source string is unaddressed. `goal3210` provides detection; there is
no compile-time or test-time checksum guard. Acceptable maintenance risk at current
scope; remains a future hardening item.

**I4: All pre-stronger-claim gaps from Goal3219 Q6 remain open**

Goal3220 does not address any of the items identified in Goal3219's Q6 as
prerequisites for stronger benchmark claims:

- Full paper-scale dataset sizes (1.7M county / 690K soil segments).
- RayJoin-exported stream inputs for cross-system comparison (RTDL vs. RayJoin,
  not RTDL vs. RTDL).
- Broader GPU family evidence (all evidence remains on a single NVIDIA A40,
  Ampere, driver 570.211.01).
- LSI-only scope for the dense count route; PIP and overlay_seed still use the
  prepared-OptiX count route.

These are expected to remain open at Goal3220 scope and are carried forward.

---

## Review Question Answers

### Q1: Does Goal3220 correctly define a current-best internal Spatial RayJoin count/parity harness without rewriting or overloading historical Goal2799?

**Yes.**

The harness is self-contained in
`scripts/goal3220_spatial_rayjoin_current_best_count_harness.py` with its own
versioned identifier `"rtdl.goal3220.spatial_rayjoin_current_best_count_harness.v1"`.
There is no reference to Goal2799 in the script, report, or tests. The function
`run_goal3220_spatial_rayjoin_current_best_count_harness` is a new entry point
that records a new route-policy snapshot without modifying any prior harness.

### Q2: Does the route policy make sense — PIP uses the existing prepared OptiX count route, LSI uses the new fused dense left-id count route, and overlay-seed uses the existing prepared OptiX count route?

**Yes.**

`_run_best_count_route` (lines 86–98) implements the policy with a single
branch:

```python
if workload == "lsi":
    return rayjoin_app.run_rayjoin_prepared_optix_left_id_dense_count_workload(...)
return rayjoin_app.run_rayjoin_prepared_optix_workload(..., result_mode="count", ...)
```

The artifact confirms:
- `pip` → `"execution_route": "prepared_optix"`.
- `lsi` → `"execution_route": "prepared_optix_left_id_dense_count"`.
- `overlay_seed` → `"execution_route": "prepared_optix"`.

The top-level `"execution_route_policy": "lsi_dense_count_else_prepared_optix_count"`
is machine-checkable against the branch logic and verified by
`test_harness_routes_lsi_to_dense_count_and_keeps_other_routes`.

The LSI route (`run_rayjoin_prepared_optix_left_id_dense_count_workload`) was
established and reviewed through the Goal3210–3218 chain. Its selection here is
consistent with the findings of Goal3217 and Goal3219 that the fused dense count
is the current best route for the LSI workload.

### Q3: Does the harness preserve the app-agnostic native boundary, with RayJoin interpretation kept in Python and generic contracts passed to native OptiX?

**Yes.**

The harness script calls only `rayjoin_app.*` functions; it does not import any
native extension or C FFI symbol directly. The native boundary is inherited from
the underlying `rtdl_rayjoin_v2_spatial_join_app.py` and the native primitives,
which were reviewed and confirmed app-agnostic in Goals 3214, 3215, 3217, 3218,
and 3219.

The `GENERIC_PRIMITIVE_BY_WORKLOAD` dictionary (lines 22–26) uses correct
generic primitive names:
- `pip` → `"POINT_CLOSED_SHAPE_MEMBERSHIP_2D"`
- `lsi` → `"SEGMENT_PAIR_LEFT_ID_COUNT_DEVICE_COLUMNS_2D"`
- `overlay_seed` → `"SHAPE_PAIR_RELATION_FLAGS_2D"`

None encode RayJoin semantics. The `native_engine_boundary` field in every artifact
row states: "The native engine sees generic prepared point/shape, segment-pair,
segment-pair left-id count, or shape-pair contracts; RayJoin workload
interpretation stays in Python." The test
`test_harness_preserves_claim_boundaries_and_generic_language` verifies
`"RayJoin workload"` and `"interpretation stays in Python"` appear in the script.

### Q4: Does the pod evidence prove only count/parity correctness on the current fixture rows, and avoid overclaiming row overlay continuation, release readiness, public speedup, true zero-copy, or RayJoin paper reproduction?

**Yes, with the qualification in L2 for the overlay_seed workload.**

The artifact `claim_boundary` block:

```json
{
  "canonical_harness_candidate": true,
  "tier_a_count_or_parity_only": true,
  "row_overlay_continuation_deferred_tier_b": true,
  "public_speedup_claim_authorized": false,
  "whole_app_speedup_claim_authorized": false,
  "true_zero_copy_claim_authorized": false,
  "paper_reproduction_claim_authorized": false,
  "rtdl_beats_rayjoin_claim_authorized": false,
  "native_engine_customization": false
}
```

All prohibited claims are `False`. The `tier_a_count_or_parity_only: true` and
`row_overlay_continuation_deferred_tier_b: true` flags correctly describe the
harness scope. `include_rows: false` is set at both the row and top level,
confirmed in the artifact.

The parity check is sound for pip (6 vs. 6, five stable repetitions) and lsi (1
vs. 1, five stable repetitions). As noted in L2, the overlay_seed check
(0 vs. 0) is nominally correct but trivially weak.

The report boundary section correctly states: "This harness does not authorize
release, public speedup claims, whole-app speedup claims, true zero-copy claims,
`RTDL beats RayJoin` claims, or RayJoin paper-reproduction claims."

### Q5: Are the hardware metadata, commit provenance, test assertions, and claim-boundary flags sufficient for internal v2.8/v3.0 planning evidence?

**Minimally yes, with the hardware metadata note in L1.**

- **Commit provenance:** `source_commit: "06d86d597574550cde3f3775b3fc6c975e380606"` is
  machine-pinned and matches the report. `source_dirty: ["?? data/"]` confirms no
  modified tracked sources at run time.
- **GPU:** `"NVIDIA A40, 570.211.01"` is sufficient to identify the execution
  environment for internal planning. CUDA toolkit and OptiX SDK version are absent
  (see L1).
- **Test assertions:** `goal3220_spatial_rayjoin_current_best_count_harness_artifact_test.py`
  verifies goal, status, harness_version, source_commit, gpu, execution_route_policy,
  row_count, per-row execution_route and generic_primitive, per-row match and pass
  status, and all six prohibited claim boundary flags. This is comprehensive for
  artifact-level evidence.
- **Claim boundary flags:** All nine flags are present and machine-checkable.

The evidence is sufficient for v2.8/v3.0 internal planning use subject to the
caveat that timing numbers from this harness should not be cited externally without
expanding the hardware metadata to Goal3218 standard (L1).

### Q6: What remains before this harness can support stronger RayJoin benchmark claims or paper-level comparison?

The following prerequisites apply before any stronger claim can be authorized,
drawn from the Goal3214 / Goal3219 chains and the Goal3220 evidence:

1. **overlay_seed non-trivial fixture (L2):** Add a fixture with at least one
   confirmed overlay pair dependency so the overlay_seed parity test has
   discriminating power.

2. **Expanded hardware metadata (L1):** Add nvcc version, CUDA toolkit version,
   and OptiX library path to `_run_metadata()` to match Goal3218 standard before
   citing any timing numbers externally.

3. **Full paper-scale dataset evidence:** The current fixture produces
   pip=6, lsi=1, overlay_seed=0. Paper-level comparison requires the full Brazil
   county (≈1.7M segments) and soil (≈690K segments) datasets at ICS-2024 scale.

4. **Row overlay continuation (tier B):** `row_overlay_continuation_deferred_tier_b:
   true` is explicit. Tier B cannot be claimed until row materialization evidence
   is produced.

5. **Cross-system comparison methodology:** An RTDL-vs-RayJoin claim requires the
   same prepared-right and query-left inputs as RayJoin would use, run under a
   properly scoped benchmark protocol on the same hardware. The current harness
   compares OptiX routes only within RTDL.

6. **Broader GPU family evidence:** All evidence remains on a single NVIDIA A40
   (Ampere, driver 570.211.01). Architecture-specific or RT-core claims require
   evidence from additional GPU families.

7. **Kernel patch stability (Goal3214 I4):** The string-patch approach for the
   LSI count kernel has no compile-time guard; only detection via `goal3210` source
   assertion. This is an acceptable risk at current scope but must be hardened
   before stable public API promotion.

---

## Artifact Consistency Check

| Field | Report | JSON | Consistent |
|---|---|---|---|
| Goal | Goal3220 | `"Goal3220"` | Yes |
| Commit | `06d86d59...` | `"06d86d597574550cde3f3775b3fc6c975e380606"` | Yes |
| GPU | `NVIDIA A40, 570.211.01` | `"NVIDIA A40, 570.211.01"` | Yes |
| Status | `pass` | `"pass"` | Yes |
| Warmup | `1` | `1` | Yes |
| Repeat | `5` | `5` | Yes |
| pip route | `prepared_optix` | `"prepared_optix"` | Yes |
| lsi route | `prepared_optix_left_id_dense_count` | `"prepared_optix_left_id_dense_count"` | Yes |
| overlay_seed route | `prepared_optix` | `"prepared_optix"` | Yes |
| pip count | 6 | 6 | Yes |
| lsi count | 1 | 1 | Yes |
| overlay_seed count | 0 | 0 | Yes |
| All `matches_cpu_reference` | true | true (all three rows) | Yes |

The `.stdout` artifact is byte-for-byte identical to the `.json` artifact (both
1,167 lines, same content). This is consistent with the `main()` function printing
and writing the same `json.dumps(payload)` output.

---

## Prior Review Chain Carry-Forward

| Item | Origin | Status in Goal3220 |
|---|---|---|
| L1: Non-atomic overflow write | Goal3214 | Closed by Goal3215; not re-opened. |
| L2: ABI release pairing | Goal3214 | Closed by Goal3215; not re-opened. |
| L3: include_rows methodology | Goal3214 | Closed by Goal3215; Goal3220 uses `include_rows=False` throughout. |
| I1: Synthetic-only evidence | Goal3214 | Partially closed by Goal3218 (CDB slices); Goal3220 uses the same br_county_subset fixture — no regression. |
| I2: Hardware metadata | Goal3214 | Closed by Goal3218; Goal3220 regresses (new L1 above). |
| I4: Kernel patch stability | Goal3214 | Open; acceptable maintenance risk. |
| Real-world data (future work) | Goal3217 | Open; Goal3220 does not extend beyond the existing subset fixture. |
| Paper-scale, cross-system comparison | Goal3219 Q6 | Open; not addressed in Goal3220 (expected). |

---

## Summary

Goal3220 is a well-scoped internal harness that correctly records the current best
route policy for the three Spatial RayJoin workloads (pip, lsi, overlay_seed) in
a single versioned artifact. It does not disturb Goal2799. The route policy
(LSI → dense count, PIP and overlay_seed → prepared OptiX count) is correctly
implemented and machine-verified. The app-agnostic native boundary is preserved.
Count/parity correctness is established for all three workloads on the current
fixture rows. All prohibited claim-boundary flags are `False`.

Two low-severity items are noted: a regression in hardware metadata detail relative
to Goal3218 (L1), and a trivially weak parity test for the overlay_seed workload
whose fixture count is 0 (L2). Neither blocks the current internal planning use of
the harness. L2 is the more substantive gap if overlay_seed route correctness is
to be evidenced at the same tier as pip and lsi.

**This review does not authorize release, public speedup claims, whole-app speedup
claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin
paper-reproduction claims.**
