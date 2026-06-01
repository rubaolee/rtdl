# Goal2961: Claude Review — Goal2958/Goal2959 RTNN Chunking and Current Packet

**Date:** 2026-06-01
**Reviewer:** Claude (independent read-only)
**Verdict:** `accept-with-boundary`
**Scope:** Goal2954 → Goal2955 → Goal2958 → Goal2959 chain
**Source commit reviewed:** `8deb21be` (HEAD at review time)

---

## Summary

The two-goal increment (Goal2958 + Goal2959) adds a graph-safe default query
batching policy to the RTNN harness and confirms the 7-app canonical packet
still has zero performance targets after that fix. The chunking implementation
is a Python-harness policy change — no native engine code was modified.
The 131,072-point pod artifact provides concrete scale evidence that the batch
cap works correctly. All claim boundaries carried forward from Goal2955/Goal2957
are intact. The verdict is `accept-with-boundary`: the implementation and
evidence are sound, but release and public-claim gates remain explicitly blocked.

---

## Q1 — Does Goal2958 solve the RTNN graph replay usability failure in a generic Python-harness policy rather than adding app-specific native engine code?

**Finding: yes.**

The fix is entirely within
`scripts/goal2800_rtnn_v25_live_ranked_summary_harness.py` (lines 64–68):

```python
batch_size = int(
    query_batch_size
    if query_batch_size is not None
    else min(int(point_count), GOAL2800_GRAPH_REPLAY_QUERY_BATCH_LIMIT)
)
```

`GOAL2800_GRAPH_REPLAY_QUERY_BATCH_LIMIT = 65536` is a module-level constant
(line 26). When `query_batch_size` is not provided by the caller, the harness
automatically clips to this limit. For a 131,072-point run the harness produces
`batch_size = 65536`, which means `point_count / batch_size = 2` batches.

No new native ABI names, kernel signatures, or RTNN-specific OptiX code paths
were introduced. The `CLAIM_BOUNDARY` dict (lines 27–38) records
`"native_engine_customization": False`. The report confirms: "This fixes a
graph-replay batching policy in the Python benchmark harness. It does not add
RTNN-specific native engine code."

The fix also preserves backward compatibility: callers who supply an explicit
`--query-batch-size` argument retain full control (line 65), so the automatic
cap applies only to the unset default case.

---

## Q2 — Is the 65536 chunk boundary adequately disclosed as an implementation cap, and are larger runs covered by the clean 131,072-point pod artifact?

**Finding: yes.**

The cap is disclosed at three levels:

1. **Source constant** — `GOAL2800_GRAPH_REPLAY_QUERY_BATCH_LIMIT = 65536`
   (harness line 26) is a named module-level constant rather than a magic
   literal.
2. **Report** — `docs/reports/goal2958_rtnn_graph_replay_scale_chunking_2026-06-01.md`
   reproduces the constant in a code block and explains: "the OptiX graph replay
   implementation currently supports `query_count <= 65536` per prepared graph."
3. **Test** — `tests/goal2958_rtnn_graph_replay_scale_chunking_test.py` line 17
   asserts `self.assertEqual(65536, harness.GOAL2800_GRAPH_REPLAY_QUERY_BATCH_LIMIT)`
   and line 29 asserts `self.assertEqual(2, row["rtdl_phase_summary"]["batch_count"])`,
   binding the disclosure to the concrete pod artifact.

The 131,072-point pod artifact
(`docs/reports/goal2958_rtnn_graph_replay_scale_pod/goal2958_rtnn_graph_131k.json`)
covers all three canonical distributions:

| Distribution | Batches | RTDL median sec | CuPy median sec | CuPy/RTDL ratio |
| --- | ---: | ---: | ---: | ---: |
| uniform | 2 | 0.000325 (7-run) | 0.000556 | 1.711x |
| clustered | 2 | 0.062053 (7-run) | 0.151121 | 2.435x |
| shell | 2 | 0.002321 (7-run) | 0.028535 | 12.296x |

All three rows confirm:
- `candidate_count_delta == 0` (exact bounded-neighbor-count match with CuPy)
- `ranked_aggregate_matches_cupy_grid == true` (nearest/kth checksums match;
  sum-distance within float32 tolerance)
- `upload_sec == 0.0` (no host-device upload in the native phase)
- `source_dirty == []`, `source_commit == f880bf024f072e4e2dd143c845b2d10c30494f9a`

The artifact shows ratios at 131k that are the same order as or better than the
65k canonical results, which is consistent with the larger input providing more
GPU parallelism for the graph replay path.

**Margin note (source-backed):** The uniform distribution at 131k yields 1.711x,
which is materially higher than the canonical 65k result (~1.145x in Goal2959).
The improvement is expected: at 131k the RTDL graph path amortises fixed graph
launch cost over twice as many query points. This is not a regression artifact.

---

## Q3 — Does Goal2959 preserve the current packet's zero performance targets, 7/7 artifact pass status, clean source labels, and empty claim-boundary violations?

**Finding: yes, verified against pod artifacts.**

From `docs/reports/goal2959_current_packet_after_rtnn_chunk_pod/goal2855_summary.json`:

| Field | Value |
| --- | --- |
| `status` | `pass` |
| `all_pass` | `true` |
| `artifact_count` | `7` |
| `expected_artifact_count` | `7` |
| `returncode_ok` | `true` |
| `artifact_status_ok` | `true` |
| `source_commit_consistent` | `true` |
| `dirty_artifacts` | `{}` |
| `claim_boundary_violations` | `{}` |
| `elapsed_sec` | `427.193s` |

All 7 artifacts (`goal2797` through `goal2803`) report:
- `status: pass`
- `source_commit: b4b8d7a6c6554b84870d9a5e67ffd16ebb8b76e8` (consistent)
- `source_dirty: []` (clean)
- `gpu: NVIDIA RTX A5000, 570.211.01` (consistent pod identity)
- `claim_boundary_violations: {}` (no violations)

From `docs/reports/goal2959_current_packet_after_rtnn_chunk_pod/goal2959_triage.json`:

| Field | Value |
| --- | --- |
| `status` | `pass` |
| `performance_targets` | `[]` |
| `top_priority` | `null` |
| App count triaged | 10 |

All 7 live-packet apps show non-target performance statuses:

| App | Performance status | Key metric |
| --- | --- | --- |
| `triangle_counting` | `current_path_acceptable` | max 0.413ms |
| `librts_spatial_index` | `tier_c_no_regression` | CPU/query 1345x |
| `spatial_rayjoin` | `current_path_acceptable_but_rows_overlay_deferred` | max 0.161ms |
| `rtnn` | `current_path_acceptable` | min CuPy/RTDL 1.145x |
| `hausdorff_xhd` | `current_path_acceptable` | RTDL/CuPy 0.898x |
| `rt_dbscan` | `current_path_acceptable` | speedup 3.687x–5.09x |
| `barnes_hut` | `current_path_acceptable_with_measured_partner_selection` | membership 158.977x |

The RTNN `weak_distributions` list is `[]` and `near_parity_distributions` is
`[]`. All three distributions (uniform 1.145x, clustered 2.726x, shell 7.652x)
are above the 0.95 near-parity floor. The triage script
(`goal2902_v2_5_current_packet_perf_triage.py:113`) only classifies `weak` if
ratio < 0.95; all three distributions are at or above 1.0. Correct.

The `goal2855_summary.json` `claim_boundary` section confirms:
`"v2_5_release_authorized": false` and all other release/speedup flags false.

The test `tests/goal2959_current_packet_after_rtnn_chunking_test.py` hard-codes
`EXPECTED_COMMIT = "b4b8d7a6c6554b84870d9a5e67ffd16ebb8b76e8"` and calls
`rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)`, asserting
`validation["status"] == "accept"`. This means the full readiness packet
validation — including all core validations, required report presence, and
required external review presence — passes at the current HEAD (`8deb21be`).

---

## Q4 — Is it acceptable for readiness to index Goal2956/Goal2957 as chain-level review evidence for Goal2948–Goal2955, while treating Goal2961 as the follow-up for Goal2958/Goal2959?

**Finding: yes, the division of review scope is coherent.**

`src/rtdsl/v2_5_internal_readiness.py` already lists Goal2956 and Goal2957 in
`V2_5_INTERNAL_READINESS_REQUIRED_EXTERNAL_REVIEW_PATHS` (lines 216–217).
Goal2957 independently reviewed the Goal2948–Goal2955 chain with an
`accept-with-boundary` verdict that covered RTNN graph replay route tuning
(Goal2954) and the first zero-target packet (Goal2955).

Goal2958 and Goal2959 are a forward increment: Goal2958 adds the batch-cap
safety net needed for runs above 65k, and Goal2959 re-verifies the canonical
packet after that addition. Neither changes the route chosen in Goal2954 nor
reopens any of the claims addressed in Goal2957. Goal2961 (this review) is
therefore appropriately scoped as the follow-up that covers only the chunking
safety net and its packet non-regression.

The `V2_5_INTERNAL_READINESS_ALLOWED_NEXT_ACTIONS` list (lines 287–288) already
includes `keep_goal2958_rtnn_graph_replay_scale_chunking_green` and
`keep_goal2959_current_packet_after_rtnn_chunking_green`, and line 289 includes
`triage_goal2956_2957_zero_target_packet_reviews_before_release_packet`.

**Note:** Goal2961 (this review file) is not yet listed in
`V2_5_INTERNAL_READINESS_REQUIRED_EXTERNAL_REVIEW_PATHS`. That path
(`docs/reviews/goal2961_claude_review_goal2958_2959_rtnn_chunk_packet_2026-06-01.md`)
should be added to that tuple when this review is indexed so that
`validate_v2_5_internal_readiness_packet` can require it at the packet level.

---

## Q5 — Are all claim boundaries preserved?

**Finding: yes, no claim slip detected anywhere in the chain.**

**Source-backed claim boundary audit:**

| Boundary flag | RTNN harness (goal2800) | Goal2959 summary | Goal2959 triage | Readiness packet |
| --- | --- | --- | --- | --- |
| `v2_5_release_authorized` | — | `false` | `release_authorized: false` | `False` |
| `public_speedup_claim_authorized` | `false` | `false` | `false` | `False` |
| `whole_app_speedup_claim_authorized` | `false` | `false` | `false` | `False` |
| `broad_rt_core_speedup_claim_authorized` | `false` | `false` | — | `False` |
| `paper_reproduction_claim_authorized` | `false` | — | `false` | — |
| `true_zero_copy_claim_authorized` | — | `false` | `false` | `False` |
| `native_engine_customization` | `false` | — | — | `False` |
| `rtdl_beats_cupy_grid_claim_authorized` | `false` | — | — | — |
| `rtdl_beats_rtnn_claim_authorized` | `false` | — | — | — |
| `triton_speedup_claim_authorized` | `false` | — | — | — |
| `compiler_fairness_claim_authorized` | — | `false` (toolchain) | — | — |
| `multivendor_claim_authorized` | — | `false` (toolchain) | — | — |

The goal2958 report boundary section explicitly lists: no public speedup, broad
RT-core, whole-app speedup, RTNN-paper reproduction, package install, true
zero-copy, Triton auto-selection, or v2.5 release claims.

The goal2959 report boundary section repeats all of the above.

`V2_5_INTERNAL_READINESS_BLOCKED_ACTIONS` (lines 220–229 of
`v2_5_internal_readiness.py`) hard-codes `v2_5_release`, `release_tag_action`,
`public_speedup_wording`, `broad_rt_core_speedup_wording`,
`whole_app_speedup_wording`, `true_zero_copy_wording`,
`package_install_wording`, `triton_preview_auto_selection`, and
`native_app_specific_engine_logic` as blocked. The `validate_v2_5_internal_readiness_packet`
function (lines 506–522) enforces every claim-authorization flag is `False` via
iteration and raises an error on any violation. The packet-level validate
function passes at the current HEAD.

---

## Q6 — What should remain blocked before a user-requested v2.5 release packet and fresh 3-AI release consensus?

**Source-backed blockers:**

1. **v2.5 release and release tag action.** Both are in
   `V2_5_INTERNAL_READINESS_BLOCKED_ACTIONS` and all `_authorized` flags are
   explicitly `False` in the readiness packet. These are not lifted by Goal2958
   or Goal2959.

2. **3-AI release consensus.** The allowed next actions list
   `request_fresh_3ai_release_review_only_if_user_requests_release`, making
   this user-triggered. No automated path to release exists.

3. **Release conformance.** The partner conformance snapshot recorded via
   `_partner_conformance_snapshot()` keeps `release_conformance_complete: False`
   while `preview_runtime_conformance_complete: True`. The conformance matrix
   cell count is 52. Release-grade conformance is not yet complete and is not
   within the scope of Goal2958 or Goal2959.

4. **Goal2896 compiler/second-arch cautions.** The triage records
   `raydb_style` as `covered_by_goal2896_external_gate` with
   `"next_action": "keep Goal2896 gate current; external review and
   compiler/second-arch cautions remain"`. The allowed next actions include
   `track_goal2897_compiler_flag_alignment_before_release_packet` and
   `track_goal2897_multivendor_or_second_arch_perf_check_before_release_packet`.
   Neither is resolved by this chain.

5. **Goal2961 review indexing.** This review (goal2961) is not yet present in
   `V2_5_INTERNAL_READINESS_REQUIRED_EXTERNAL_REVIEW_PATHS`. Before a release
   packet is prepared, this path should be added to that tuple and
   `validate_v2_5_internal_readiness_packet` should be re-run to confirm all
   external review requirements are met.

6. **All public-claim wording.** Public speedup wording, whole-app speedup
   wording, broad RT-core wording, true zero-copy wording, package-install
   wording, and Triton preview auto-selection remain in
   `V2_5_INTERNAL_READINESS_BLOCKED_ACTIONS`.

7. **Native app-specific engine logic.** Also explicitly blocked. Both Goal2958
   and the prior Goal2954 confirm `native_engine_customization: False`.

---

## File-Level Findings

### `scripts/goal2800_rtnn_v25_live_ranked_summary_harness.py`

- **Line 26:** `GOAL2800_GRAPH_REPLAY_QUERY_BATCH_LIMIT = 65536` — constant is
  named and module-level, making the cap discoverable.
- **Lines 64–68:** Default batch-size calculation correctly uses `min` when
  `query_batch_size is None`. The `int()` cast guards against non-integer
  `point_count` values.
- **Line 95:** `query_batch_size=batch_size` passes the resolved batch size into
  the RTDL runner. Correct.
- **Lines 27–38:** `CLAIM_BOUNDARY` dict is complete; `native_engine_customization`
  and all speedup/paper flags are `False`. No issues.
- **Line 21:** Harness version string `v8.scale65536_repeat9_graph_replay`
  correctly documents the canonical default scale and the route. No change was
  needed here since the version already reflects Goal2954.

**Minor observation (not a defect):** The constant name
`GOAL2800_GRAPH_REPLAY_QUERY_BATCH_LIMIT` prefixes with `GOAL2800_`, which ties
the cap to this harness file specifically. This is appropriate since the cap
documents the OptiX implementation detail for this harness version, not a
general RTDL API limit.

### `tests/goal2958_rtnn_graph_replay_scale_chunking_test.py`

- **Line 17:** `self.assertEqual(65536, harness.GOAL2800_GRAPH_REPLAY_QUERY_BATCH_LIMIT)`
  — binds the constant to its expected value; will catch accidental constant changes.
- **Line 27:** `self.assertEqual(131072, payload["point_count"])` and
  `self.assertEqual(65536, payload["query_batch_size"])` — confirms the artifact
  was run at exactly double the cap.
- **Line 29:** `self.assertEqual(2, row["rtdl_phase_summary"]["batch_count"])` for
  each distribution — confirms the chunking actually produced two batches.
- **Line 31:** `self.assertTrue(row["ranked_aggregate_matches_cupy_grid"])` — confirms
  correctness across both chunks.
- **Line 32:** `self.assertGreater(float(row["cupy_grid_over_rtdl_elapsed_ratio"]), 1.0)`
  — confirms RTDL is faster than CuPy at 131k across all distributions.
- **Line 33:** `self.assertEqual(0.0, float(row["rtdl_phase_summary"]["upload_sec"]))`
  — confirms no upload regression from chunking.
- **Line 34:** `self.assertFalse(row["claim_boundary"]["rtdl_beats_cupy_grid_claim_authorized"])`
  — correctly tests the boundary flag at row level.
- The report-content test (lines 36–48) checks that the markdown report contains
  all ratio values and the boundary statement. Comprehensive.

### `tests/goal2959_current_packet_after_rtnn_chunking_test.py`

- **Line 15:** `EXPECTED_COMMIT = "b4b8d7a6c6554b84870d9a5e67ffd16ebb8b76e8"` —
  hard-coded expected commit. This is correct: the pod ran at b4b8d7a6 (after the
  Goal2958 implementation was committed at f880bf02 and the Goal2958 scale artifact
  was recorded at b4b8d7a6). The test will fail if someone re-runs the packet at a
  different commit without updating this value, which is the intended behavior.
- **Lines 19–30:** Packet summary checks cover all critical fields: status,
  commit, artifact count, boundary violations, dirty artifacts, and the
  `v2_5_release_authorized` flag.
- **Lines 33–38:** Triage zero-target check: `assertEqual("pass", ...)`,
  `assertEqual([], triage["performance_targets"])`, `assertIsNone(top_priority)`,
  `assertEqual(10, len(triage["apps"]))`. Correct and complete.
- **Lines 41–51:** Readiness integration test: calls
  `rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)` and asserts
  `"accept"`. This is a strong integration assertion that the entire readiness
  packet machinery accepts the current state. Also asserts
  `"goal2959_current_packet_after_rtnn_chunk_pod"` in the runner summary path and
  that `v2_5_release_authorized` is False.

### `src/rtdsl/v2_5_internal_readiness.py`

- **Lines 143–144:** Goal2958 and Goal2959 reports are appended to
  `V2_5_INTERNAL_READINESS_REQUIRED_REPORTS`. Correct.
- **Lines 179:** `V2_5_INTERNAL_READINESS_CURRENT_CANONICAL_RUNNER_SUMMARY` now
  points to `goal2959_current_packet_after_rtnn_chunk_pod/goal2855_summary.json`.
  Correct.
- **Lines 181–183:** `V2_5_INTERNAL_READINESS_CURRENT_PACKET_PERF_TRIAGE` points to
  `goal2959_current_packet_after_rtnn_chunk_pod/goal2959_triage.json`. Correct.
- **Lines 287–289:** New allowed next actions `keep_goal2958_rtnn_graph_replay_scale_chunking_green`,
  `keep_goal2959_current_packet_after_rtnn_chunking_green`, and
  `triage_goal2956_2957_zero_target_packet_reviews_before_release_packet` added.
  All three are appropriate.
- **Line 216–217:** Goal2956 and Goal2957 reviews are already listed in
  `V2_5_INTERNAL_READINESS_REQUIRED_EXTERNAL_REVIEW_PATHS`. Goal2961 is not yet
  listed. This is expected (the review was not written until this session).

### `docs/reports/goal2958_rtnn_graph_replay_scale_pod/goal2958_rtnn_graph_131k.json`

- GPU: `NVIDIA RTX A5000, 570.211.01` — consistent pod identity.
- `source_commit: f880bf024f072e4e2dd143c845b2d10c30494f9a` — the commit that
  introduced the chunking implementation. Correct.
- `source_dirty: []` — clean run.
- `harness_version: rtdl.goal2800.rtnn_v2_5_live_ranked_summary_harness.v8.scale65536_repeat9_graph_replay`
  — carries forward from Goal2954 without change.
- All claim boundary flags confirmed `false` at both the top-level payload and
  each row.
- Each row's `rtdl_phase_summary.modes` array contains two entries, both
  `prepared_query_uniform_cell_ranked_summary_aggregate_f32_batch_cuda_graph_replay`,
  confirming the graph replay mode is used for both batches across all distributions.

### `docs/reports/goal2959_current_packet_after_rtnn_chunk_pod/goal2855_summary.json`

- GPU identity consistent across all 7 artifacts: `NVIDIA RTX A5000, 570.211.01`.
- Toolchain metadata present with
  `metadata_version: rtdl.goal2916.toolchain_provenance.v1`,
  `rtdl_optix_ptx_compiler: nvcc`, `rtdl_optix_library_exists: true`,
  `optix_header_exists: true`. All Goal2916 toolchain requirements satisfied.
- `compiler_fairness_claim_authorized: false` and
  `multivendor_claim_authorized: false` in toolchain claim boundary.
- Elapsed: `427.193s`. This is slightly shorter than the Goal2955 packet (459s).
  The reduction is expected: the canonical 65k RTNN run is the same size;
  the slight variance is normal across pod runs.

### `docs/reports/goal2959_current_packet_after_rtnn_chunk_pod/goal2959_triage.json`

- `"claim_boundary_violations": {}` — verified.
- RTNN entry: `"result_modes": ["ranked-summary-aggregate-prepared-query-batch-graph-float32"]`,
  `"weak_distributions": []`, `"near_parity_distributions": []`,
  `"min_cupy_over_rtdl_ratio": 1.145`. Correct.
- Barnes-Hut entry: `"selected_vector_sum_partner": "cupy"`, consistent with
  Goal2933 measured selection. Triton not auto-selected.
- Raydb: `"covered_by_goal2896_external_gate"` — not in live packet, per design.
- Contact manifold and robot collision: `"tier_c_not_in_seven_app_packet"` — per design.

---

## Observations (reviewer's own, not source-backed)

1. **Uniform distribution margin.** The uniform RTNN distribution at 1.145x is a
   thin margin relative to GPU scheduling noise. This was noted in Goal2957 as well
   and remains true after Goal2958/Goal2959. The chunking change does not
   materially alter the canonical 65k margin. This is not a new concern but should
   continue to be monitored across future pod runs.

2. **Cap disclosure scope.** The 65536 cap is documented as an implementation cap
   in the harness report and tested in the test suite. For a future user-facing
   documentation pass, it would be worth noting whether this cap is a hard OptiX
   API limit, a GPU memory constraint, or a graph recording heuristic, so users
   can reason about it for their own workloads. This is out of scope for the
   current engineering packet.

3. **Goal2961 indexing.** Adding this review's path to
   `V2_5_INTERNAL_READINESS_REQUIRED_EXTERNAL_REVIEW_PATHS` in
   `v2_5_internal_readiness.py` is the expected administrative follow-up before
   any release packet preparation. The readiness validate function currently passes
   without it (as the Goal2959 test confirms), so the test will need updating too
   when the indexing is done.

---

## Verdict

**`accept-with-boundary`**

The Goal2958/Goal2959 increment is internally coherent:

- Goal2958 solves the RTNN graph replay `query_count > 65536` usability failure
  with a single generic Python-harness default policy — no native engine code
  was added or modified.
- The `GOAL2800_GRAPH_REPLAY_QUERY_BATCH_LIMIT = 65536` cap is named, tested,
  and documented. The 131,072-point pod artifact provides direct evidence that
  the two-batch execution path produces correct results and maintains CuPy/RTDL
  ratios of 1.711x (uniform), 2.435x (clustered), and 12.296x (shell).
- Goal2959 confirms that the canonical 7-app packet has zero performance targets
  after the chunking addition, with all 7 artifacts passing clean at commit
  b4b8d7a6, consistent GPU identity, consistent source commits, and empty
  claim-boundary violations.
- All release, public-claim, true-zero-copy, paper-reproduction, and
  Triton auto-selection claims remain explicitly blocked at the source-tree level
  in `v2_5_internal_readiness.py` and are not lifted by this chain.
- The Goal2956/Goal2957 indexing as chain-level review evidence for the
  Goal2948–Goal2955 work is coherent; Goal2961 (this review) is the designated
  follow-up for Goal2958/Goal2959 and should be indexed before any release packet
  preparation.

The following must remain blocked before a user-requested v2.5 release packet
and fresh 3-AI release consensus: v2.5 release and release tag action, all
public-claim wording categories, Goal2896 compiler/second-arch caution
resolution, release conformance completion, Goal2961 indexing in the readiness
packet, and the user-triggered 3-AI release consensus.
