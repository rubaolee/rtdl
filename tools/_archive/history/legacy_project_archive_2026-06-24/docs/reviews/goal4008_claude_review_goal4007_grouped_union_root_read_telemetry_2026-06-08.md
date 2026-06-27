# Goal4008 Claude Review: Goal4007 Grouped-Union Root-Read Telemetry

Date: 2026-06-08
Reviewer: Claude (external review, read-only)
Scope: `docs/reports/goal4007_grouped_union_root_read_telemetry_2026-06-08.md`,
`tests/goal4007_grouped_union_root_read_telemetry_test.py`,
`src/native/optix/rtdl_optix_core.cpp`, `src/rtdsl/optix_runtime.py`,
`scripts/goal3996_grouped_union_extended_telemetry_sweep_pod.py`,
pod artifacts in `docs/reports/goal4007_grouped_union_root_read_telemetry_pod/`.

## Verdict

`accept`

## Summary

Goal4007 adds two new device-side counters (`uint64[8]=root_find_invocations`,
`uint64[9]=root_find_parent_link_steps`) to the existing
`find_grouped_union_root_readonly` helper, exposes a 10-counter telemetry shape
as an explicit opt-in on top of the existing 4- and 8-counter contracts, and
ships pod evidence quantifying root-read cost on the accepted
`same_root_on_direct_off` route. I verified the native diff, the runtime
contract refactor, the pod sweep script change, and all three pod artifacts
against the report's claims. No defects found; no release-gate concerns raised
by this change.

## Findings

No correctness, claim-boundary, or evidentiary defects found. Detail by review
question below.

### Q1 — Diagnostic-only, no app-shaped ABI, no behavior-changing default

Confirmed. The native diff (`git show 94bf59a4` on
`src/native/optix/rtdl_optix_core.cpp`) adds exactly two
`grouped_union_telemetry_add` calls inside the existing
`find_grouped_union_root_readonly` device function — no new `__global__`
entry points, no new native symbol. The test's negative assertion
(`assertNotIn("rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_root_read", core)`)
holds against the current source. `grouped_union_telemetry_add` is bounds-checked
on `index < params.telemetry_count`, so callers passing 4- or 8-counter buffers
silently skip indices 8/9 — the new counters cannot corrupt or extend behavior
for callers that haven't opted in. The sweep script keeps
`--telemetry-counters` defaulting to 8 (`rtdl_optix_core.cpp` diff +
`goal3996_..._sweep_pod.py` diff both confirmed); Goal4007 passes `--telemetry-counters 10`
explicitly per the report's command shape. No default route, predicate, or
side-effect policy changed.

### Q2 — Old 4-/8-counter contracts preserved, 10 an explicit opt-in

Confirmed. The runtime diff replaces inline contract-string literals with a new
helper `_grouped_union_telemetry_contract(counter_count)` that returns:
- the original 4-field base string when `counter_count < 8`,
- the original 8-field extended string when `8 <= counter_count < 10`,
- the new 10-field string (appending `root_find_invocations` /
  `root_find_parent_link_steps`) when `counter_count >= 10`.

This is a faithful refactor — the pre-existing 4- and 8-counter strings are
reproduced verbatim inside the helper, not rewritten. `use_root_read_telemetry =
telemetry_buffer_length >= 10` gates `grouped_union_root_read_telemetry_enabled`
and bumps `telemetry_counter_count` to 10 only when the caller supplies a
buffer that large; smaller buffers fall through to the pre-existing 8/4/0
behavior unchanged. Both `PreparedOptixFixedRadiusCountThreshold3D` call sites
that build telemetry metadata were updated identically (verified via the diff
hunks touching lines ~6399 and ~6671).

### Q3 — Pod artifacts: source commit, ten-counter metadata, closed claim boundaries

Confirmed for all three artifacts (`clustered3d_65536.json`, `road3d_65536.json`,
`ngsim_dense_65536.json`):
- `source_commit: "94bf59a421314d371e9c82746f4d0558d29a2f30"` — full hash of
  the cited commit `94bf59a4` (`git log` confirms this is "Goal4007 add grouped
  union root-read telemetry").
- `status: "pass"`, `telemetry_counter_capacity: 10`.
- `claim_boundary.performance_claim_authorized: false`,
  `claim_boundary.release_authorized: false`.
- The `same_root_on_direct_off` variant's `last_metadata` carries
  `grouped_union_telemetry_counter_count: 10`,
  `grouped_union_root_read_telemetry_enabled: true`, and a
  `grouped_union_telemetry_contract` string containing
  `root_find_invocations` / `root_find_parent_link_steps`, matching the test's
  assertions and the runtime's new contract string exactly.
- `telemetry[8] > 0` and `telemetry[9] >= telemetry[8] - point_count` hold in
  all three artifacts (e.g., clustered3d: 548,003,862 vs. 708,889,367 −
  point_count well within bound).

### Q4 — Report interpretation supported by the evidence

Confirmed — I recomputed the derived columns directly from `last_telemetry`:

| Profile | Candidates | Root calls | Root calls/candidate | Steps/root call |
| --- | ---: | ---: | ---: | ---: |
| `clustered3d` | 273,911,978 | 548,003,862 | 2.0007 → 2.001 | 1.2936 → 1.294 |
| `road3d` | 85,627,372 | 171,688,664 | 2.0049 → 2.005 | 1.7759 → 1.776 |
| `ngsim_dense` | 12,299,418 | 24,764,290 | 2.0136 → 2.013 | 1.3416 → 1.342 |

All match the report table to the displayed precision, as do the median elapsed
times, candidate/culled/reported counts, and radii (`0.055` / `0.030` / `0.012`).
The "≈ two readonly root finds per candidate" and "parent-link walks are
nontrivial (road3d 1.776 steps/root call)" claims are directly supported by
this data — not exaggerated. The chain of reasoning to Goal4002 (direct side
effect rejected) and Goal4004 (microcell rejected) is consistent with those
goals' own commits ("Goal4002 reject grouped union direct side effect default",
"Goal4004 reject microcell route as grouped union baseline"), and the summary
of the Goal4005 `partition_convergence_hybrid` candidate's four requirements
maps cleanly onto the actual `candidate_requirements` list in
`docs/reports/goal4005_partition_convergence_candidate_front_door_contract_2026-06-08.md`
(items 1–3 are verbatim renames of `device_resident_partition_aabb_and_count_columns`,
`safe_full_partition_pair_summary_without_pair_materialization`, and
`ambiguous_boundary_pair_rt_traversal`; item 4 is a fair compression of
`deterministic_component_root_policy` + `explicit_convergence_and_staleness_counters`).

### Q5 — Overclaims, stale release wording, hidden dispatch/partner claims

None found. The report's "Claim Boundary" section explicitly disclaims a v2.x
release claim, DBSCAN-native ABI claim, paper speedup claim, broad RT-core
speedup claim, and any default switch away from `grouped_stream` — and these
disclaimers are corroborated by the artifacts'
`performance_claim_authorized: false` / `release_authorized: false` flags and
by the per-sample metadata carrying `true_zero_copy_authorized: false`,
`paper_speedup_claim_authorized: false`, and `v2_0_release_authorized: false`
(spot-checked in `clustered3d_65536.json` lines 51–68; same fields recur
identically across all sampled variants). No hidden-dispatch or partner-facing
language appears anywhere in the report or test.

## Test Coverage

`tests/goal4007_grouped_union_root_read_telemetry_test.py` directly checks the
native counter additions, the negative-ABI assertion, the runtime's
diagnostic-only ten-counter contract strings and claim flags, the sweep
script's unchanged default and new opt-in flag, and per-artifact metadata/
telemetry invariants (`telemetry[8] > 0`,
`telemetry[9] >= telemetry[8] - point_count`). The assertions line up with what
I independently verified in the source and artifacts; I did not re-execute the
suite (would require pod/GPU access and out-of-scope command approval for this
read-only review), but every string and structural assertion in the test
matches what is present in the current tree.
