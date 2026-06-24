# Goal2320 Claude Final v2.0 Release Cleanup Review

Reviewer: Claude (claude-sonnet-4-6)
Date: 2026-05-18
Scope: Goal2319 final cleanup packet, current-head `main` at `fc6b0e36`

## Verdict

`accept-with-boundary`

---

## Artifacts Reviewed

- `docs/reports/goal2319_v2_0_final_cleanup_release_candidate_2026-05-18.md`
- `docs/reports/goal2068_final_v2_0_release_matrix.json`
- `docs/reports/goal2069_v2_0_pre_release_gate.json`
- `docs/reports/goal2072_v2_0_final_readiness_aggregator.json`
- `docs/reports/goal2085_v2_perf_table_after_streaming_witness_update_2026-05-15.json`
- `docs/reports/goal2088_v2_0_release_prep_after_streaming_witness_2026-05-15.md`
- `docs/reports/goal2315_rayjoin_v2_0_bounded_closure_2026-05-17.md`
- `docs/reports/goal2318_rayjoin_v2_0_closure_and_release_prep_2ai_consensus_2026-05-17.md`
- `src/native/optix/rtdl_optix_workloads.cpp` (diagnostic/profile string verification)
- `src/native/hiprt/rtdl_hiprt_prelude.h` (RTDL_DB_* constant verification)
- `tests/goal1680_current_native_app_leakage_gap_test.py` (scan logic verification)
- `tests/goal2319_v2_0_final_cleanup_release_candidate_test.py` (cleanup assertions)

---

## Verification Checklist

### 1. Native Strict Scan Position

**Pass.** Direct inspection of `src/native/hiprt/rtdl_hiprt_prelude.h` confirms exactly 9 uppercase `RTDL_DB_*` constants:
`RTDL_DB_KIND_INT64`, `RTDL_DB_KIND_FLOAT64`, `RTDL_DB_KIND_BOOL`,
`RTDL_DB_OP_EQ`, `RTDL_DB_OP_LT`, `RTDL_DB_OP_LE`, `RTDL_DB_OP_GT`,
`RTDL_DB_OP_GE`, `RTDL_DB_OP_BETWEEN`.

These are numeric type/operator constants, not app-shaped symbols. The test
`goal1680_current_native_app_leakage_gap_test` encodes `assertEqual(9,
len(strict_symbols))`, `assertEqual(0, len(real_symbols))`, confirming the
false-positive set exactly covers the strict-match set. No real app-shaped
`rtdl_...` symbols are present. The previously-banned symbols (e.g.,
`rtdl_optix_run_pip`, `rtdl_embree_run_bfs_expand`, and 16 others) remain
absent.

### 2. OptiX Diagnostic/Profile Environment String Rename

**Pass.** Grep across `src/native/optix/` finds zero occurrences of
`RTDL_OPTIX_PIP_*` or `rtdl_optix_pip_profile`. The three live environment
strings are now:
- `RTDL_OPTIX_POINT_PRIMITIVE_ANYHIT_PROFILE`
- `RTDL_OPTIX_POINT_PRIMITIVE_ANYHIT_DISABLE_DEVICE_PREFILTER`
- `RTDL_OPTIX_POINT_PRIMITIVE_ANYHIT_DISABLE_ONE_PASS_COMPACT`

These names are app-agnostic. The `goal2319` test suite asserts both the new
names are present and the old PIP names are absent.

### 3. Goal2068 Post-Streaming Evidence State

**Pass.** The `goal2068_final_v2_0_release_matrix.json` reflects the
Goal2085 streaming witness update:

- `mixed_apps: []` — no mixed rows remain.
- `post_goal2085_streaming_evidence: true`
- `all_current_optix_rt_ratios_below_1: true`
- 16 of 16 OptiX/RT rows with measured v2/v1.8 ratio below 1.0.
- `source: "docs/reports/goal2085_v2_perf_table_after_streaming_witness_update_2026-05-15.json"` confirms the table is drawn from the post-streaming evidence, not the pre-streaming packet.
- Slowest current row: `robot_collision_screening` at ratio `0.367` — still well below 1.0.

The 4 bounded rows (`database_analytics`, `graph_analytics`,
`polygon_pair_overlap_area_rows`, `polygon_set_jaccard`) are correctly
classified `pod-evidence-collected-bounded` with documented comparison caveats.
The non-bounded 12 rows are `pod-evidence-collected`.

### 4. Goal2069 Gate Status

**Pass.** `goal2069_v2_0_pre_release_gate.json` records:
- `status: "pass"`
- `gate_tests.summary: "40 tests, 1 skipped"`, `returncode: 0`
- `v2_0_release_authorized: false`
- `whole_app_speedup_claim_authorized: false`

Goal2069 is correctly scoped as an engineering pre-release gate. It confirms
the implementation and evidence are coherent; it does not constitute release
authorization.

### 5. Goal2072 Aggregator Blocked State

**Pass.** `goal2072_v2_0_final_readiness_aggregator.json` records:
- `status: "blocked"`
- `external_reviews.claude.present: false`
- `external_reviews.gemini.present: false`
- `final_consensus_file: null`

The four remaining blockers are correctly enumerated:
1. Final Claude v2.0 release-gate review missing.
2. Final Gemini v2.0 release-gate review missing.
3. Final v2.0 3-AI release consensus missing.
4. Explicit user-requested release action missing.

This review (Goal2320) satisfies blocker 1. Goal2072 will remain blocked
until Gemini review (Goal2321), 3-AI consensus, and user release action follow.

### 6. Public Claim Boundaries

**Pass.** All prohibited claim flags are `false` in both Goal2068 and Goal2069
JSON artifacts:
- `package_install_claim_authorized: false`
- `arbitrary_partner_program_acceleration_authorized: false`
- `broad_rt_core_speedup_claim_authorized: false`
- `whole_app_speedup_claim_authorized: false`
- `v2_0_release_authorized: false`

Goal2319 report explicitly lists "Still Not Allowed" items that are consistent
with the above: no PyPI/package-install, no arbitrary PyTorch/CuPy
acceleration, no broad RT-core speedup, no whole-app speedup, no arbitrary
polygon overlay, no RTDL-beats-RayJoin claim.

Goal2318 2-AI consensus (`accept-with-boundary`) and Goal2315 RayJoin closure
(`closed-for-v2.0-with-boundary`) are internally consistent with these
prohibitions. The 15-16x performance gap between RTDL's generic prepared route
and RayJoin's specialized C++/CUDA/OptiX query phase is correctly documented
as research context, not a public win/loss benchmark.

Embree rows: Several Embree CPU rows show ratios at or slightly above 1.0
(e.g., `graph_analytics: 1.0005`, `service_coverage_gaps: 1.0054`,
`hausdorff_distance: 1.0271`). This is correctly handled — the Embree table is
a CPU same-contract evidence surface, not the headline GPU partner-speedup
claim. Goal2085 and Goal2088 explicitly bound this interpretation. No Embree
CPU speedup is claimed.

### 7. v2.1+ Tuning Debt Deferred, Not Blocking v2.0

**Pass.** Goal2319 "v2.1 And Later" section correctly lists the deferred items:
deeper RayJoin reproduction, exact Hausdorff/X-HD tuning, device-resident
row-stream continuations, reusable graph partner primitives, broader polygon
overlay, Triton/Numba partner exploration, v3.0 custom extensions. None of
these are asserted as v2.0 deliverables.

Goal2315 likewise writes the remaining RayJoin to-do list to
`docs/research/future_version_to_do_list.md` and marks the v2.0 lane closed.

---

## Evidence Quality Notes

The streaming witness update (`segment_polygon_anyhit_rows`: ratio 0.00075)
resolves the only previously-mixed row cleanly. The GoAL2083/Goal2085 evidence
chain is reviewed by Gemini (Goal2084, Goal2087) and internally consistent
with the expanded scale runs in Goal2086.

The bounded rows' comparison caveats (partner-backend asymmetry, not
absolutely fair) are documented consistently in both the matrix JSON
`analysis_hint` fields and the human-readable release-prep report. This is
the correct handling: document the caveat, do not claim a comparison the
evidence does not support.

The RayJoin closure is handled well: exact parity on the 100k-query imported
streams, honest documentation of the 15-16x gap to specialized code, future
work deferred.

---

## Acceptance Boundaries

This acceptance is bounded by the following:

1. **Not a release authorization.** v2.0 is not released by this review.
   The explicit user-requested release action has not occurred.

2. **3-AI consensus not complete.** This is one of three required review
   inputs. Gemini review (Goal2321) and the final 3-AI consensus file are
   still required before release.

3. **Bounded rows carry documented caveats.** The four `bounded-implemented`
   rows (`database_analytics`, `graph_analytics`, `polygon_pair_overlap_area_rows`,
   `polygon_set_jaccard`) have partner-backend asymmetry documented and must
   not be cited as absolutely-fair comparisons.

4. **Embree rows are CPU same-contract evidence only.** The several Embree
   rows at or above parity are not a v2.0 claim surface; they fill the evidence
   table without contributing to the headline GPU partner-speedup claim.

5. **RayJoin claim boundary applies.** RTDL does not beat RayJoin; the
   current prepared route is approximately 15-16x slower than RayJoin's
   specialized query phase. This boundary must be preserved in any external
   communication about v2.0.

6. **No package-install, no broad RT-core, no arbitrary acceleration claims.**
   These remain outside v2.0 scope.

---

## Summary

The Goal2319 cleanup packet is coherent and correct. All 7 verification items
pass on direct artifact inspection. The native scan position is clean (9
false-positive constants, 0 real app-shaped symbols), the diagnostic
environment strings are app-agnostic, the release matrix is post-streaming
evidence complete, the pre-release gate is green but not release
authorization, Goal2072 correctly remains blocked pending this and the Gemini
review, and all prohibited claim flags are false.

The repository is ready for the Gemini final v2.0 release review (Goal2321)
and subsequent 3-AI consensus. It is not yet released.
