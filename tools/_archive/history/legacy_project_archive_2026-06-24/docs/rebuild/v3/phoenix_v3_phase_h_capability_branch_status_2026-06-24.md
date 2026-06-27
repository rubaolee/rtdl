# Phoenix V3 Phase H Capability/Quality Branch Status

Date: 2026-06-24
Status: `phase_h_capability_quality_branch_not_release`

## Bottom Line

Phoenix V3 no longer has an active high-performance release path. Phase A
tested the trunk-first performance hypothesis and did not move named
scorecard-bound blockers to the required bar. Claude and Antigravity both
accepted the No-Go verdict.

V3 continues as a capability/quality branch: a Python-hosted RTDL runtime with
a productized prepared-execution trunk, explicit backend/partner boundaries,
serious row-scoped evidence, and clean tutorials/docs. It must not claim broad
V3-over-V2 speed superiority.

## Controlling Evidence

- Phase A consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_phase_a_performance_source_consensus_2026-06-24.md`
- Barnes-Hut evidence:
  `docs/rebuild/v3/evidence/phoenix_v3_m72_barnes_hut_native_leafdfs_t2_20260624_101218/`
- RTNN reselected-family evidence:
  `docs/rebuild/v3/evidence/phoenix_v3_phaseA_rtnn_clustered262144_20260624_110456/summary.json`
- V2.14 vs Phoenix V3 paired benchmark:
  `docs/rebuild/v3/v2_14_vs_v3_same_rt_hardware_paired_benchmark_2026-06-20.md`
- Current exact-row evidence catalog:
  `docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.md`

## What V3 Can Still Be

V3 can be completed as:

- a source-tree Python-hosted RTDL runtime branch;
- a clearer app-author programming surface than the V2.x research archive;
- a prepared-execution/session-runner capability branch;
- a row-scoped evidence catalog for selected workloads;
- a polished tutorial/example path with strict claim boundaries.

## What V3 Cannot Be

V3 cannot be described as:

- broadly faster than V2.x;
- a high-performance major release;
- proof that OptiX/RT cores automatically speed up these apps;
- a whole-app benchmark victory across all benchmark apps;
- a V4 embedding, C ABI, external device-buffer, or true-zero-copy release.

## Remaining Phase H/G Work

1. **Front-door docs:** keep README, docs index, tutorials, examples, and claim
   boundaries aligned to capability/quality wording.
2. **Evidence wording:** keep exact-row performance statements, negative rows,
   hot/query/wall boundaries, and artifact paths visible.
3. **Version truth:** keep `VERSION` and package metadata as branch markers, not
   release markers.
4. **History fencing:** keep old V3/V4 release/tutorial material out of the user
   path and audit-only under history.
5. **Sanity gates:** run wording/tutorial/public-doc gates and source-tree
   sanity checks before any external Phase H release review.
6. **External review:** after H/G edits are complete, send the final capability
   branch to Claude and Antigravity for release-readiness review.

## Current Gates

Passed locally after the Phase H/G front-door, blocker-ledger, and gate-note
updates:

```text
py -3 -m unittest tests.v3_release_wording_gate_test tests.v3_public_docs_rebuild_surface_test tests.v3_rebuild_tutorial_surface_test
23 tests OK

py -3 -m unittest tests.v3_release_wording_gate_test tests.v3_public_docs_rebuild_surface_test tests.v3_rebuild_tutorial_surface_test tests.v3_phoenix_release_readiness_gate_test tests.v3_phoenix_major_performance_mandate_gate_test tests.v3_rebuild_reset_test tests.goal4278_source_tree_doctor_test
39 tests OK

py -3 scripts/v3_release_wording_gate.py --pretty
status: pass
violations: []

py -3 scripts/rtdl_source_tree_doctor.py --json --run-smoke
ok: true
status: v3_capability_branch_ready
required_failures: []

py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 148
tests: 754
status: OK
```

## External Review Status

- Claude first review:
  `docs/reviews/claude_phoenix_v3_phase_h_g_capability_completion_candidate_review_2026-06-24.md`
  returned `accept_with_required_amendments`.
- Required amendments P0-A, P0-B, P1-A, P1-B, and P1-C were applied.
- Claude amendment review:
  `docs/reviews/claude_phoenix_v3_phase_h_g_capability_completion_candidate_amendment_review_2026-06-24.md`
  returned `accept_phase_h_g_capability_release_ready`.
- Antigravity CLI stdout was blocked because the CLI exited with code `0` but
  returned no substantive stdout, even for a trivial prompt. The substantive
  review was recovered from Antigravity's local transcript store and returned
  `accept_phase_h_g_capability_release_ready`:
  `docs/reviews/antigravity_phoenix_v3_phase_h_g_capability_completion_candidate_review_2026-06-24.md`.
- The CLI stdout defect record is:
  `docs/reviews/antigravity_blocked_phoenix_v3_phase_h_g_capability_completion_candidate_2026-06-24.md`.

This status is not release-owner authorization.

## Non-Authorization

This status file authorizes no V3 release, no all-app benchmark, no public
speedup wording, no broad V3-over-V2 wording, no V4, no embedding, no C ABI,
and no external zero-copy claim.
