# Goal2957: Claude Review — Goal2955 Zero-Target v2.5 Packet

**Date:** 2026-06-01
**Reviewer:** Claude (independent read-only)
**Verdict:** `accept-with-boundary`
**Scope:** Goal2948 → Goal2950 → Goal2952 → Goal2954 → Goal2955 chain

---

## Summary

The five-goal chain produces a current v2.5 canonical packet with zero
performance targets in the triage output. Both route-tuning changes that
achieved this (Hausdorff target-8192 default and RTNN CUDA graph replay) are
technically sound and generic. All claim boundaries are explicitly maintained
throughout the chain. The verdict is `accept-with-boundary`: the internal
engineering conclusion is supported, but multiple release-blocking conditions
remain in force.

---

## Q1 — Does the evidence support zero performance targets?

**Finding: yes, with one margin note.**

The triage JSON (`goal2955_triage.json`) records `"performance_targets": []`
and `"top_priority": null`. The triage logic in
`scripts/goal2902_v2_5_current_packet_perf_triage.py` classifies an app as a
`performance_target` only when `str(app.get("performance_status")).startswith("performance_target")`.
All seven live packet apps report non-target statuses:

| App | Performance status |
| --- | --- |
| `triangle_counting` | `current_path_acceptable` |
| `librts_spatial_index` | `tier_c_no_regression` |
| `spatial_rayjoin` | `current_path_acceptable_but_rows_overlay_deferred` |
| `rtnn` | `current_path_acceptable` |
| `hausdorff_xhd` | `current_path_acceptable` |
| `rt_dbscan` | `current_path_acceptable` |
| `barnes_hut` | `current_path_acceptable_with_measured_partner_selection` |

The `rtnn` entry reports `min_cupy_over_rtdl_ratio: 1.147` across three
distributions (`uniform: 1.147`, `clustered: 2.722`, `shell: 7.503`) with
`weak_distributions: []`. The near-parity floor is `0.95` in the triage
script (`goal2902_v2_5_current_packet_perf_triage.py:113`). The uniform
distribution at `1.147x` is comfortably above that floor.

**Margin note (source-backed):** The uniform distribution at `1.147x` is not
a large margin. The Goal2954 clean harness confirmation recorded `1.104x`
on the same distribution, and the sweep recorded `1.091x` at repeat=13. The
result is stable across repeated runs but remains distribution-dependent.
This is correctly characterized in the triage as
`"next_action": "keep current ranked-summary route green"`, not as a
permanently resolved performance class boundary.

---

## Q2 — Are the route choices technically sound and generic?

**Finding: yes for both changes.**

**RTNN (Goal2954, `scripts/goal2800_rtnn_v25_live_ranked_summary_harness.py:90`):**
The route change is a single `result_mode` argument change:
`"ranked-summary-aggregate-prepared-query-batch-graph-float32"`. This uses an
existing RTDL generic prepared-query CUDA graph replay primitive; no new
native code was added. The sweep tested five route modes on the problematic
uniform distribution and the graph replay path won clearly (`0.000126s` vs
the prior `prepared-query aggregate` at `0.000155s`). CUDA graph replay for
repeated fixed-radius queries is a standard generic optimization: it amortizes
kernel launch overhead across repeated same-shape executions without
introducing RTNN-specific ABI customization. The `CLAIM_BOUNDARY` dict in the
harness records `"native_engine_customization": False`.

**Hausdorff (Goal2952, `scripts/goal2801_hausdorff_xhd_v25_canonical_entrypoint.py:32`):**
The change is `DEFAULT_REDUCED_TARGET_POINTS_PER_GROUP = 8192`. This is a
parameter change to an existing RT grouped nearest-witness reduction; no new
native code path was introduced. The parameter controls how many target points
are grouped before RT traversal, which is a generic grouping heuristic. The
`CLAIM_BOUNDARY` dict records `"native_engine_customization": False`.

Both changes follow the pattern the reports describe: prefer an existing
generic RTDL route before adding new primitives.

---

## Q3 — Are claim boundaries preserved?

**Finding: yes, boundaries are consistently maintained across the chain.**

All five goal reports carry explicit boundary paragraphs. The
`goal2855_summary.json` records `"claim_boundary_violations": {}` and
confirms every artifact flag. Key checks:

| Boundary flag | Status in artifacts and triage |
| --- | --- |
| `v2_5_release_authorized` | `false` everywhere |
| `public_speedup_claim_authorized` | `false` everywhere |
| `whole_app_speedup_claim_authorized` | `false` everywhere |
| `broad_rt_core_speedup_claim_authorized` | `false` everywhere |
| `paper_reproduction_claim_authorized` | `false` everywhere |
| `true_zero_copy_claim_authorized` | `false` everywhere |
| `native_engine_customization` | `false` in both changed harnesses |
| `rtdl_beats_cupy_grid_claim_authorized` | `false` in RTNN harness |
| `rtdl_beats_xhd_claim_authorized` | `false` in Hausdorff harness |
| `rtdl_beats_rtnn_claim_authorized` | `false` in RTNN harness |
| `triton_speedup_claim_authorized` | `false` in RTNN harness |

The `v2_5_internal_readiness.py` `V2_5_INTERNAL_READINESS_BLOCKED_ACTIONS`
tuple (lines 217–226) hard-codes all these blocked categories at the
readiness-packet level. The `validate_v2_5_internal_readiness_packet` function
enforces all flags programmatically (lines 506–522). No claim slip is
detectable in the reviewed artifacts.

---

## Q4 — Does the RayDB planner guard correctly prefer primitive-first?

**Finding: yes. The evidence is unambiguous.**

Goal2950 (`docs/reports/goal2950_raydb_payload_grouped_sum_front_door_probe_2026-06-01.md`)
measures the payload hit-stream front door against the primitive-first fused
grouped reduction on RayDB `count` and `sum` workloads:

| Mode | Payload front door sec | Primitive-first sec | Slowdown |
| --- | ---: | ---: | ---: |
| `count` 250K | `0.009484` | `0.000345` | `27x` |
| `sum` 250K | `0.291365` | `0.000938` | `311x` |
| `count` 1M | `0.006293` | `0.000287` | `22x` |
| `sum` 1M | `0.309383` | `0.001589` | `195x` |

The one-to-three-order-of-magnitude performance gap means the planner rule —
use primitive-first for operations already expressible as a fused RTDL
primitive — is well justified by the evidence.

The report notes the planner guard
`rt.plan_v2_5_ray_triangle_payload_grouped_reduction_execution` is intended
to explain to users when primitive-first is the correct selection. The triage
output records `raydb_style` as `"covered_by_goal2896_external_gate"`, meaning
it is not in the live 7-app packet but has its own decision gate. The Goal2950
evidence reinforces the existing Goal2896 gate decision without creating a new
promotion path.

---

## Q5 — Does the Hausdorff target-8192 default evidence justify the change?

**Finding: yes, with a density-condition note.**

The sweep in Goal2952 tested the `reduced` method at four target group sizes
on the exact 8192×8192 canonical fixture:

| Target points/group | RTDL sec | Ratio vs CuPy |
| ---: | ---: | ---: |
| `1024` | `0.007963` | `0.958x` |
| `2048` | `0.007830` | `0.942x` |
| `4096` | `0.007881` | `0.948x` |
| `8192` | `0.007006` | `0.843x` |

Target 8192 wins by a 10–12% margin over the previous defaults. The 16K
confirmation (`ratio: 0.873x`) and the clean default confirmation at commit
`f246ca5e` (`ratio: 0.856x`) are consistent. All runs preserve zero distance
error against the CuPy baseline.

**Density-condition note (source-backed):** The sweep is performed on a dense
canonical fixture only. The report correctly notes: "seeded/pruned variant is
slower on this dense canonical fixture and remains a workload-specific option,
not the default." The default change is therefore evidence-justified for the
existing canonical fixture. Sparse workloads are not covered. This is
consistent with what the entrypoint is advertised to measure.

No X-HD reproduction claim is made; `rtdl_beats_xhd_claim_authorized: false`
is confirmed in the Hausdorff `CLAIM_BOUNDARY`.

---

## Q6 — Does the RTNN graph replay route evidence justify the canonical harness change?

**Finding: yes. The sweep is comprehensive and the result is stable.**

Goal2954 ran a 5-mode route sweep on the uniform 65,536-point distribution
(the distribution that was a performance target before this goal). The graph
replay path wins on all three distributions in the subsequent multi-distribution
confirmation and the clean harness run:

| Distribution | Clean harness RTDL sec | CuPy sec | Ratio |
| --- | ---: | ---: | ---: |
| `uniform` | `0.000124` | `0.000137` | `1.104x` |
| `clustered` | `0.017253` | `0.046959` | `2.722x` |
| `shell` | `0.000354` | `0.002723` | `7.684x` |

All aggregate contract checks pass: bounded neighbor count, nearest/kth
checksums, sum-distance within float32 tolerance, and `upload: 0.0`. No
neighbor row materialization is added.

**Boundary note (source-backed):** The harness `CLAIM_BOUNDARY` dict records
`rtdl_beats_rtnn_claim_authorized: false` and
`paper_reproduction_claim_authorized: false`. The opponent is a same-contract
CuPy grid, not the published RTNN system. The harness version string
`v8.scale65536_repeat9_graph_replay` correctly documents the specific
canonical parameters so the route change is traceable.

---

## Q7 — What must remain blocked before any v2.5 release packet?

The following remain blocked by explicit source-tree enforcement
(`v2_5_internal_readiness.py:217–226` and `validate_v2_5_internal_readiness_packet`):

1. **v2.5 release or release tag action.** `v2_5_release_authorized: False`
   everywhere; `V2_5_INTERNAL_READINESS_BLOCKED_ACTIONS` lists both
   `v2_5_release` and `release_tag_action`.

2. **3-AI release consensus.** The allowed next actions list
   `request_fresh_3ai_release_review_only_if_user_requests_release`, making
   this user-triggered. No automated release gate exists; human authorization
   is required.

3. **Goal2896 external review cautions.** The triage records
   `raydb_style` as `covered_by_goal2896_external_gate` with
   `"next_action": "keep Goal2896 gate current; external review and
   compiler/second-arch cautions remain"`. The allowed next actions include
   `track_goal2897_compiler_flag_alignment_before_release_packet` and
   `track_goal2897_multivendor_or_second_arch_perf_check_before_release_packet`.
   Neither is resolved in this chain.

4. **Release conformance.** The conformance snapshot records
   `release_conformance_complete: False`. Preview runtime conformance is
   complete, but release-grade conformance requires additional steps not taken
   in this chain.

5. **Goal2957 external review indexing.** The current review (this file) is
   not yet listed in `V2_5_INTERNAL_READINESS_REQUIRED_EXTERNAL_REVIEW_PATHS`
   in `v2_5_internal_readiness.py`. Any release packet preparation would need
   to index this review as a required external review path and then re-validate.

6. **All public-claim wording.** Public speedup wording, broad RT-core
   speedup wording, whole-app speedup wording, true zero-copy wording,
   package-install wording, and Triton preview auto-selection remain in
   `V2_5_INTERNAL_READINESS_BLOCKED_ACTIONS`.

7. **Native app-specific engine logic.** Also explicitly blocked; both recent
   route changes confirm `native_engine_customization: False`.

---

## File-Level Findings

### `scripts/goal2800_rtnn_v25_live_ranked_summary_harness.py`

- Line 21: harness version correctly updated to
  `v8.scale65536_repeat9_graph_replay`.
- Line 91: `result_mode="ranked-summary-aggregate-prepared-query-batch-graph-float32"`
  is the only behavioral change. No new native code.
- Lines 25–36: `CLAIM_BOUNDARY` is complete and all release/speedup/paper
  flags are `False`. No issues found.

### `scripts/goal2801_hausdorff_xhd_v25_canonical_entrypoint.py`

- Line 24: version string updated to `v3.reduced_target8192`.
- Line 32: `DEFAULT_REDUCED_TARGET_POINTS_PER_GROUP = 8192` is the only
  behavioral change.
- Lines 34–44: `CLAIM_BOUNDARY` is complete and all flags are `False`.
- Line 251 (comment): `--reduced-seed-with-threshold` help text correctly
  notes this is "Disabled by default for dense exact HD", acknowledging the
  density condition.

### `scripts/goal2902_v2_5_current_packet_perf_triage.py`

- Lines 113–126: RTNN triage logic correctly classifies `near_parity` (0.95 ≤
  ratio < 1.0) separately from `weak` (ratio < 0.95). Since all distributions
  are now ≥ 1.0, neither condition applies and the status is
  `current_path_acceptable`. Logic is correct.
- Lines 153–154: Hausdorff triage uses `near_parity_limit = 1.10`. Current
  ratio is `0.901x`, so `performance_target` is `False`. Correct.
- Lines 222–244: `_raydb` handler correctly returns
  `covered_by_goal2896_external_gate` when no raydb gate path is supplied.
  No issue.

### `src/rtdsl/v2_5_internal_readiness.py`

- Lines 141–143: Goal2955 report is correctly appended to
  `V2_5_INTERNAL_READINESS_REQUIRED_REPORTS`.
- Lines 176–180: `V2_5_INTERNAL_READINESS_CURRENT_CANONICAL_RUNNER_SUMMARY`
  and `V2_5_INTERNAL_READINESS_CURRENT_PACKET_PERF_TRIAGE` both point to the
  Goal2955 pod artifacts. Correct.
- Lines 279–282: `keep_goal2952_hausdorff_target8192_default_green`,
  `keep_goal2954_rtnn_graph_replay_route_green`, and
  `keep_goal2955_current_packet_zero_perf_targets_green` are added to
  `V2_5_INTERNAL_READINESS_ALLOWED_NEXT_ACTIONS`. Correct.
- Lines 460–462: `validate_v2_5_internal_readiness_packet` checks
  `performance_target_count == 0` and `top_priority is None`. These assertions
  are now met by the Goal2955 triage, meaning the readiness packet will accept
  at the current commit.

### `tests/goal2955_current_packet_after_rtnn_graph_replay_test.py`

- The test at line 50 asserts `rtnn["min_cupy_over_rtdl_ratio"] > 1.0`. This
  is tight relative to the `1.147x` result. If the uniform distribution
  regresses below `1.0x` in a future harness run, this test would fail (which
  is the correct behavior). The test correctly does not claim a fixed numeric
  floor beyond parity.
- Line 67 asserts `hausdorff["rtdl_over_cupy_grid_elapsed_ratio"] < 1.0` —
  confirms RTDL is faster than CuPy on this fixture.
- Line 79 asserts the readiness packet accepts and the current commit matches
  the expected sha. These are strong assertions that make the packet state
  machine machine-verifiable.

### `docs/reports/goal2955_current_packet_after_rtnn_graph_pod/goal2855_summary.json`

- GPU identity: `NVIDIA RTX A5000, 570.211.01` across all 7 artifacts.
- All artifacts have `source_commit: 747716c7141341b43a4bed37f66c53d0ff2bcc14`
  and `source_dirty: []`. Clean run.
- `claim_boundary_violations: {}` for all artifacts and the summary itself.
- Toolchain metadata present: `metadata_version: rtdl.goal2916.toolchain_provenance.v1`,
  `rtdl_optix_ptx_compiler: nvcc`, `rtdl_optix_library_exists: true`,
  `optix_header_exists: true`. All readiness validation gates for toolchain
  provenance are satisfied.
- `compiler_fairness_claim_authorized: false` and
  `multivendor_claim_authorized: false` in toolchain claim boundary. Correct.

---

## Observations (reviewer's own, not source-backed)

1. The uniform RTNN distribution at `1.147x` is a thin margin relative to
   GPU scheduling noise. It passes the current triage floor (`0.95x`) by a
   comfortable factor, but any future regression probe should monitor whether
   this margin is stable across different POD runs or CUDA driver updates.

2. The Hausdorff sweep covers a single fixture density (8192×8192 and its
   16K extension). The seeded/pruned path is explicitly kept as a
   workload-specific option. For the release packet, a note on when users
   should override the default for sparse fixtures would improve user-facing
   documentation, but this is out of scope for the current engineering packet.

3. Goal2957 (this review) is not yet indexed as a required external review in
   `V2_5_INTERNAL_READINESS_REQUIRED_EXTERNAL_REVIEW_PATHS`. Indexing this
   review there and re-running `validate_v2_5_internal_readiness_packet` is
   the expected next step after this review is written.

---

## Verdict

**`accept-with-boundary`**

The five-goal chain from Goal2948 to Goal2955 is internally coherent:

- Zero performance targets in the triage output is correctly derived from the
  evidence and triage logic.
- Both route changes are generic, evidence-backed, and bounded.
- No claim boundaries are violated anywhere in the chain.
- The planner guard for RayDB correctly steers count/sum workloads to
  primitive-first fused reduction.
- All release, public-speedup, true-zero-copy, paper-reproduction, and Triton
  auto-selection claims remain explicitly blocked.

The `accept-with-boundary` verdict is warranted because the internal
engineering evidence is sound but the following are not satisfied and must
remain blocked before any v2.5 release packet: 3-AI release consensus,
Goal2896 compiler/second-arch caution resolution, release conformance
completion, and Goal2957 review indexing in the internal readiness packet.
