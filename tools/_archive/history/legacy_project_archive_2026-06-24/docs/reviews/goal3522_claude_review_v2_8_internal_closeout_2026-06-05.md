# Goal3522: Claude Review — v2.8 Internal Closeout Packet

Date: 2026-06-05

Reviewer: Claude (claude-sonnet-4-6)

Verdict: `accept-with-boundary`

## Scope

Independent read-only review of the Goal3522 v2.8 internal closeout packet and
its supporting chain: Goal3518 benchmark matrix, Goal3519 learner docs cleanup,
Goal3520 claim-boundary audit and 3-AI consensus, Goal3521 final validation
packet and test, and representative pod artifacts under
`docs/reports/goal3521_pod_artifacts/`.

## Validation Run

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal3521_v2_8_final_validation_packet_test \
  tests.goal3520_v2_8_claim_boundary_stale_audit_test \
  tests.goal3519_v2_8_learner_docs_cleanup_test \
  tests.goal3518_v2_8_benchmark_matrix_test

Ran 19 tests in 0.192s
OK
```

All four test modules pass.

## Authorization Phrase Scan

```text
rg -in "v2\.8 release authorized|public speedup claim.*true|true zero.copy authorized|
  rtdl beats rayjoin is authorized|full rayjoin reproduction is authorized|
  automatic partner selection is enabled|package-install supported|pip install -e \."
  docs/reports/goal3522_v2_8_internal_closeout_packet_2026-06-05.md
  README.md docs/README.md docs/learn docs/tutorials
  examples/v2_0/research_benchmarks
```

No matches. No accidentally-authorized public claim wording found in the active
doc surface.

## Question-by-Question Assessment

### 1. Is v2.8 ready to close as an internal version?

Yes. The evidence chain is complete and each step has been validated.

| Goal | Role | Status |
| --- | --- | --- |
| Goal3512/3515 | Established closeout plan and 3-AI agreement on goal order | Accepted |
| Goal3516 | Closed evidence bookkeeping for Goal3507/3509/3511 | Accepted |
| Goal3517 | Defined prepared-execution user pattern | Accepted |
| Goal3518 | Refreshed 12-row benchmark matrix; all cells explicit | Accepted |
| Goal3519 | Cleaned active learner docs to a single v2.8 story | Accepted |
| Goal3520 | Audited claim boundaries; quarantined versioned helper names | Accepted (3-AI) |
| Goal3521 | Fresh RTX A5000 pod validation at commit `9ad59f1e` | Accepted |

The full local gate (`Ran 112 tests, OK, skipped=5`) is recorded in the
Goal3521 packet and independently verified by the Goal3521 test above.

### 2. Does the packet preserve the app-agnostic engine boundary?

Yes. The engine-boundary flags are enforced at every artifact level:

- `contact_manifold_grid4096_optix.json`: `"native_collision_logic_allowed": false`
- `overlay_steady_state_read.json`: `"app_specific_engine_logic_allowed": false`
  appears in `active_shape_ordinal_metadata`, `bounds_positive_filter_metadata`,
  `executor_metadata`, and `prepared_execution_report`.
- `rt_dbscan_grouped_stream.json`: `"native_engine_customization": false`
- `robot_collision/summary.json`: all `_authorized` flags false except
  `internal_evidence_only: true`.

The Goal3518 matrix uses `primitive_only`, `partner_needed`, and
`prepared_execution_needed` rows without collapsing them or hardwiring a
backend selection into the matrix definition.

### 3. Does it keep partner choice explicit and avoid hidden dispatch?

Yes. The overlay artifact records `"automatic_partner_selection_allowed": false`
and `"explicit_partner_choice_required": true` in `prepared_execution_report`.
The partner field at every metadata level is `"cupy"` — an explicit user
declaration, not an inferred or hidden selection.

The RT-DBSCAN matrix row notes CuPy is the component continuation partner. The
Barnes-Hut row states "CuPy selected for vector sum by measured same-contract
timing", which is an explicit user decision preserved in the matrix, not a
runtime auto-selection.

The Goal3520 audit quarantined `v2_5`/`v2_6` helper/protocol names in five
Python files. These names survive in compatibility/schema identifiers (e.g.,
`"entrypoint_version": "rtdl.goal2802.rt_dbscan_v2_5_live_grouped_stream_harness.v1"`
in the RT-DBSCAN artifact). This is an internal schema identifier, not a
user-facing dispatch decision. The quarantine is correctly handled.

### 4. Are setup/cache/warmup/steady-state/continuation/validation phases separated clearly enough?

Yes, with two acknowledged gaps documented in the matrix.

**Strong separation (Goal3521 pod artifacts):**

- Overlay: 9 explicit phase entries in `prepared_execution_report.phase_timings`
  — prepare (`0.1756s`), cache_load (`0.1756s`), warmup three-repeat series
  (best `0.00710s`), steady_state_stream (`0.003780s`), candidate_filter
  (`0.04781s`), planner best-repeat (`0.04903s`), executor best-repeat
  (`0.01415s`), validation (`0.2705s`). Each phase is labeled with its role
  and `steady_state_candidate` / `validation_candidate` flags.
- Contact manifold: four-phase split in `v2_4_phase_timing.phases_sec` —
  scene_build (`0.573764s`), rt_traversal (`0.027931s`),
  partner_continuation/exact_app_refinement (`0.009865s`),
  materialization (`0.010726s`).
- Robot collision: tail-median phase breakdown across prepare_build
  (`0.139312s`), query_pack (`0.034758s`), traversal (`0.000078s`),
  output_postprocess (`0.000096s`); 2 warmup rows dropped.

**Known gaps (documented, not hidden):**

The Goal3518 matrix correctly records `legacy_total_only_from_goal2654` in the
`setup_sec/status` and `warmup_sec/status` cells for `robot_collision` and
`contact_manifold`. Goal3521 added fresh RTX pod rows for both apps; the
contact manifold artifact includes a phase split, and the robot collision
artifact reports a prepared tail median. The residual gap is that a fully
phase-separated setup/warmup aggregate is not yet available for robot
collision or RT-DBSCAN in the matrix format. This is recorded as the "Next
Pod Refresh" target in Goal3518 and does not block the internal closeout.

### 5. Are the benchmark claims correctly bounded?

Yes. Every artifact has explicit `claim_boundary` dicts with all positive
claims set to `false`. Only the appropriate internal-scope flags are true
(e.g., `internal_evidence_only: true` for robot collision;
`canonical_live_harness: true` for RT-DBSCAN).

One nuance worth noting for the consensus record: the RT-DBSCAN artifact
shows `rt_count_speedup_vs_prepared_cupy_grid` of **0.937x at 32K points** —
meaning the bare RT count path is marginally slower than prepared CuPy at
the smallest scale tested. Only the grouped-stream path achieves the
reported 4.0–4.9x speedup. The claim boundary correctly blocks any broad
DBSCAN speedup claim, and the packet reports the grouped-stream speedup with
scale labeling. This is correctly handled and does not require a correction,
but should be repeated in the 3-AI consensus to prevent any future
misreading of the `min_grouped_stream_speedup_vs_prepared_cupy_grid: 4.080`
figure as a universal RT speedup.

### 6. Is any public release or speedup wording accidentally authorized?

No. The authorization phrase scan returned zero matches across the active
doc surface, the closeout packet, and the main README. The Goal3520 test
recursively scans active Markdown and blocks literal `True` assignments for
all critical claim-boundary keys in benchmark Python. That guard passes.

The boundary list in the packet is complete and correctly states that the
following remain blocked: public v2.8 release, package-install/PyPI promise,
public speedup, broad RT-core speedup, true zero-copy, full RayJoin paper
reproduction, RTDL-beats-RayJoin, full overlay geometry/output claim, hidden
partner selection, and app-specific native-engine behavior.

### 7. Are any blockers before writing the final 3-AI closeout consensus?

No blockers. The identified residuals are deferred debt, not correctness gaps:

1. **Robot collision and RT-DBSCAN matrix phase gaps.** Setup and warmup cells
   use legacy total timing. This is documented and the next pod target is
   defined. The existing evidence is Tier-C/no-regression evidence, which is
   appropriate for these apps at internal closeout scope.
2. **Versioned Python helper names (`v2_5`, `v2_6`).** Five files contain
   these as compatibility/protocol names. They are quarantined and tracked in
   `docs/research/future_version_to_do_list.md`. A later alias/migration goal
   should handle them.
3. **Embree row error in Goal3521 pod.** The robot collision Embree row
   errored because no Embree library was configured on the pod. The RTX
   evidence is valid; Embree evidence remains from earlier accepted rows. This
   is correctly recorded in the packet and the test does not assert on the
   Embree row.

None of these prevent the 3-AI closeout consensus.

## Summary

The Goal3522 packet and its supporting chain are internally consistent and
correctly guarded. The engine boundary is preserved. Partner choice is
explicit at every artifact level. Phase separation is strong for the
highest-priority apps and the remaining gaps are documented with a clear
next-pod target. No public claim is accidentally authorized. All 19 test
cases pass.

The final 3-AI consensus should:

1. Repeat the full public-claim boundary verbatim (no release, no
   package-install, no speedup, no RT-core, no zero-copy, no RayJoin
   reproduction, no RTDL-beats-RayJoin, no hidden dispatch, no
   app-specific native-engine behavior).
2. Note the RT-DBSCAN 0.937x raw-count result at 32K so it is on record
   that the speedup claim applies only to the grouped-stream path.
3. Record the robot_collision/rt_dbscan phase-split gap as the first
   target for the next pod run.

## Verdict

`accept-with-boundary`

v2.8 is ready to close as an internal version. No additional pod run is
needed before the final consensus. The boundary conditions above must be
carried forward into the consensus document unchanged.
