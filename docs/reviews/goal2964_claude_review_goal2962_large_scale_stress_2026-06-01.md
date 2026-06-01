# Goal2964: Independent Review of Goal2962 Large-Scale v2.5 Stress Probe

**Reviewer:** Claude (Sonnet 4.6), independent read-only pass  
**Review date:** 2026-06-01  
**Source commit reviewed:** `28bcf380` (current HEAD)  
**Pod artifact source commit:** `8deb21be` (Goal2959 recording)  
**Verdict:** `accept-with-boundary`

---

## Scope

This review covers the three high-risk v2.5 stress paths introduced by Goal2962:

- RTNN ranked summaries at 262,144 query/search points
- Exact Hausdorff/X-HD at 16,384 × 16,384 points
- RT-DBSCAN grouped-stream continuation at 262,144 points

Primary files examined (read-only):

- `docs/reports/goal2962_large_scale_v2_5_stress_probe_2026-06-01.md`
- `tests/goal2962_large_scale_v2_5_stress_probe_test.py`
- `docs/reports/goal2962_large_scale_stress_pod/goal2962_rtnn_262k.json`
- `docs/reports/goal2962_large_scale_stress_pod/goal2962_hausdorff_16k.json`
- `docs/reports/goal2962_large_scale_stress_pod/goal2962_rt_dbscan_262k.json`
- `src/rtdsl/v2_5_internal_readiness.py`

---

## Commit Provenance

Commit `28bcf380` adds exclusively: the three JSON artifacts, the stress probe report, a handoff document, two external reviews (Goal2960/2961), five index additions to `v2_5_internal_readiness.py`, and the test file. The git diff between `8deb21be` and `28bcf380` contains no changes to any computational RTDL source. The `v2_5_internal_readiness.py` change is a pure index update (adding Goal2962 to `V2_5_INTERNAL_READINESS_REQUIRED_REPORTS` and `V2_5_INTERNAL_READINESS_ALLOWED_NEXT_ACTIONS`). Pod artifacts were produced from `8deb21be` before the index update, which is the correct production order. Artifact validity is unaffected by the subsequent index commit.

---

## Q1: Artifact Status, Source Cleanliness, and Commit

All three artifacts are verified clean:

| Artifact | `status` | `source_commit` | `source_dirty` |
|---|---|---|---|
| `goal2962_rtnn_262k.json` | `pass` | `8deb21bea3930830ad03d3d7410356c786af5479` | `[]` |
| `goal2962_hausdorff_16k.json` | `pass` | `8deb21bea3930830ad03d3d7410356c786af5479` | `[]` |
| `goal2962_rt_dbscan_262k.json` | `pass` | `8deb21bea3930830ad03d3d7410356c786af5479` | `[]` |

The commit short-form `8deb21be` matches the full SHA in all three artifacts. All GPU identity fields record `NVIDIA RTX A5000, 570.211.01`, consistent across artifacts. The report acknowledges a trailing `NameError` from the SSH wrapper here-doc after all three JSON payloads had already been written; this is not reflected in any artifact field and does not affect artifact integrity.

---

## Q2: RTNN — Four 65,536-Query Graph Chunks at 262K, Same-Contract Opponent Match

**Chunking:** The artifact records `"query_batch_size": 65536` and `"point_count": 262144`. Division confirms exactly 4 batches (262,144 / 65,536 = 4). Each of the three distribution rows confirms `"batch_count": 4` in `rtdl_phase_summary`. All four mode strings per row are `prepared_query_uniform_cell_ranked_summary_aggregate_f32_batch_cuda_graph_replay`, confirming graph replay is active throughout.

**Same-contract opponent:** Each row declares `"same_contract_opponent": "cupy_grid_exact_ranked_summary_3d"`. All rows report `"cupy_grid_ok": true`, `"rtdl_ok": true`, and `"ranked_aggregate_matches_cupy_grid": true`. Candidate counts delta is 0 for all three distributions (well within their respective tolerances of 2, 12, and 11).

**Ratio results:**

| Distribution | CuPy/RTDL ratio | Exceeds 2.0x |
|---|---:|---|
| uniform | 3.359x | yes |
| clustered | 2.071x | yes (weakest case) |
| shell | 4.608x | yes |

The clustered distribution is the stress case; even at 262K with heavy neighbor density (12.7M bounded neighbors), the ratio remains above 2.0x. This is consistent with the triage finding that the clustered distribution is distribution-dependent but not a weak-row artifact.

**Upload:** All three rows record `"upload_sec": 0.0`, confirming no re-upload cost in the native phase at 262K scale.

**Claim boundary:** Each row carries `"rtdl_beats_cupy_grid_claim_authorized": false` and all broader speedup flags false. The `"tier_b_same_contract_opponent": true` flag correctly identifies the opponent scope.

**Finding:** RTNN stress evidence is sound. The four-chunk graph replay route holds at 262K scale with >2.0x CuPy/RTDL ratio across all three distributions.

---

## Q3: Hausdorff 16K — Exact RT-Core Path, Zero Distance Error, CuPy Opponent

**RT-core identity:** The artifact records `"rtdl.uses_rt_cores": true`, `"rtdl.result.backend": "optix"`, `"rtdl.result.rt_core_accelerated": true`. The entrypoint is `rtdl.goal2801.hausdorff_xhd_v2_5_canonical_entrypoint.v3.reduced_target8192`.

**Exactness and distance error:**
- `"distance_error": 0.0`
- `"matches_exact_baseline": true`
- `"rtdl.result.exact_value": true`
- `"baseline.exact_value": true`

Both RTDL and CuPy return distance `0.11858844621300667` with source_index `13024`. RTDL target_index is `8210`, CuPy target_index is `462`. The differing target indices are consistent with multiple equidistant nearest neighbors from source point 13024 — both implementations find a valid nearest neighbor at the same distance, which is the correctness criterion for directed Hausdorff. The `distance_error: 0.0` confirms this.

**Timing:**

| Method | Median sec |
|---|---:|
| RTDL / OptiX reduced nearest witness | 0.014730 |
| CuPy grouped grid rawkernel | 0.015727 |

`rtdl_over_cupy_grid_elapsed_ratio: 0.9366` (< 1.0, RTDL is faster at this scale). This is stronger than the 0.898x ratio recorded at smaller scale in the Goal2902 triage, consistent with expected RT-core scaling behavior at larger problem sizes.

**Claim boundary:** `"rtdl_beats_xhd_claim_authorized": false`, `"rtdl_beats_cupy_grid_claim_authorized": false`. The report correctly states this does not authorize a claim to beat X-HD or an optimized CUDA implementation in general.

**Finding:** Hausdorff 16K evidence is sound. The exact RT-core path is confirmed, zero distance error is verified, and the timing is competitive. Overclaiming is correctly blocked.

---

## Q4: RT-DBSCAN 262K — Grouped-Stream RT-Core, Compact, Signature-Matching, Faster Than Prepared CuPy Grid

**RT-core status:** `"grouped_stream_rt_core_accelerated": true`.

**Compactness:** `"grouped_stream_avoids_neighbor_rows_and_full_adjacency_stream": true`. The artifact also records `"grouped_stream_materializes_directed_adjacency_stream": false` and `"grouped_stream_materializes_neighbor_rows": false` at the row level. The field `"planned_continuation_full_stream_fits_budget": false` explains why: at 262K points, the estimated directed edge count is 8,658,654,069 — the full adjacency stream does not fit budget, making the grouped stream the correct engineering choice at this scale.

**Signature matching:** `"signatures_match": true`. At the row level, `"grouped_stream_signature_match": true` and `"prepared_cupy_signature_match": true` and `"rt_count_signature_match": true`.

**Timing comparison (tail median):**

| Path | Tail median sec | Speedup vs prepared CuPy |
|---|---:|---:|
| Prepared CuPy grid | 5.479164 | 1.0x (baseline) |
| RT count prepared grid | 3.066458 | 1.787x |
| RTDL grouped stream + CuPy components | 1.196323 | 4.580x |

`min_grouped_stream_speedup_vs_prepared_cupy_grid: 4.580004882573556`. The grouped stream is 2.56x faster than the RT count intermediate, confirming that the grouped-stream continuation adds substantial value beyond the RT counting step.

**Claim boundary:** `"paper_speedup_claim_authorized": false`. All other speedup and release flags are false. The `"pure_triton_components_claim_authorized": false` field is also present.

**Finding:** RT-DBSCAN stress evidence is sound. Grouped-stream continuation remains RT-core accelerated, compact, and signature-matching at 262K. The 4.580x speedup over the prepared CuPy grid baseline is well above the 4.0x threshold tested in the test file.

---

## Q5: Overclaiming Audit

The report's Boundary section explicitly blocks all nine required categories. Mapping against the handoff requirements:

| Required blocked category | Report wording | Present |
|---|---|---|
| v2.5 release or release tag action | "v2.5 release or release tag action" | yes |
| public speedup wording | "public speedup wording" | yes |
| broad RT-core speedup wording | "broad RT-core speedup wording" | yes |
| whole-app speedup wording | "whole-app speedup wording" | yes |
| true zero-copy wording | "true zero-copy wording" | yes |
| package-install wording | "package-install wording" | yes |
| Triton preview auto-selection | "Triton preview auto-selection" | yes |
| paper reproduction claims | "paper reproduction claims" | yes |
| app-specific native engine customization | "app-specific native engine customization" | yes |

The report's introductory framing — "This is stress evidence only. It is not a release authorization and it does not convert internal ratios into public speedup claims." — is appropriately conservative. Per-artifact claim_boundary fields enforce the same limits in machine-readable form.

The `v2_5_internal_readiness_packet` function's `claim_authorization` block continues to set `v2_5_release_authorized: False` and all six sibling flags False. The `V2_5_INTERNAL_READINESS_BLOCKED_ACTIONS` tuple is unchanged by the Goal2962 commit.

**Finding:** No overclaiming detected. All required boundary phrases are present in the report and enforced in the artifact claim_boundary fields.

---

## Q6: Framing as Stress Evidence Layered on Goal2959

Goal2959 established a zero-target canonical packet at the packet scale (the triage JSON records `"performance_targets": []`, `"top_priority": null`). Goal2962 extends this to three high-risk paths at scales significantly beyond the canonical packet:

- RTNN: 262,144 points vs. the ~65,536 canonical scale
- Hausdorff: 16,384 × 16,384 vs. the ~4,096 canonical scale
- RT-DBSCAN: 262,144 points vs. the canonical small-scale harness sizes

The layering is appropriate: Goal2959 confirms zero regression at packet scale; Goal2962 confirms the same paths do not degrade at large scale. The question "are these short-row wins?" is answered: all three paths hold at large scale.

The `V2_5_INTERNAL_READINESS_REQUIRED_REPORTS` tuple in `v2_5_internal_readiness.py:145` now includes `docs/reports/goal2962_large_scale_v2_5_stress_probe_2026-06-01.md`. The `V2_5_INTERNAL_READINESS_ALLOWED_NEXT_ACTIONS` tuple includes `keep_goal2962_large_scale_stress_probe_green`. Goal2962 is indexed correctly as stress evidence in the internal readiness structure without authorizing release.

**Finding:** The stress-evidence framing is appropriate. Goal2962 does not replace or supersede Goal2959; it supplements it with large-scale confidence. No reframing is needed.

---

## Test File Verification

`tests/goal2962_large_scale_v2_5_stress_probe_test.py` contains four test methods. All assertions were manually verified against artifact content:

- `test_rtnn_262k_uses_four_graph_chunks_and_beats_same_contract_cupy`: all assertions match artifact values — status, commit, dirty, point_count, query_batch_size, batch_count (4), ranked_aggregate_matches_cupy_grid, ratio >2.0, upload_sec 0.0, claim flag false.
- `test_hausdorff_16k_exact_rt_path_matches_cupy_baseline`: all assertions match — status, commit, dirty, points_a/b (16384), matches_exact_baseline, distance_error 0.0, uses_rt_cores, ratio <1.0, claim flag false.
- `test_rt_dbscan_262k_grouped_stream_stays_rt_accelerated_and_compact`: all assertions match — status, commit, dirty, point_counts ([262144]), signatures_match, grouped_stream_rt_core_accelerated, grouped_stream_avoids_neighbor_rows_and_full_adjacency_stream, speedup >4.0, claim flag false.
- `test_report_and_readiness_preserve_boundaries`: all six phrases verified in the report text; Goal2962 report path is at index 145 of `V2_5_INTERNAL_READINESS_REQUIRED_REPORTS`; `v2_5_release_authorized` is False.

No test asserts a performance ratio as an absolute truth claim — ratios are boundary-floored assertions (>2.0, >4.0, <1.0), not exact value locks. This is the correct test structure for non-reproducible hardware timing.

---

## Minor Observations (Non-Blocking)

1. **SSH wrapper NameError:** The report acknowledges this. It has no artifact-level impact. If the wrapper script is reused, the here-doc termination should be fixed to avoid confusion in future runs.

2. **RTNN harness goal field:** The artifact records `"goal": "Goal2800"`, referring to the base benchmark goal rather than Goal2962. This is consistent with reusing the established harness from Goal2800 and is not an error, but future reviewers may find it confusing when searching for "Goal2962" in artifact fields.

3. **Hausdorff target index divergence:** RTDL finds target_index 8210; CuPy finds target_index 462. Both report the identical distance. This is geometrically valid (equidistant nearest neighbors) and confirmed by `distance_error: 0.0`, but worth noting as expected behavior rather than a discrepancy.

4. **Review not yet in required external reviews:** The `V2_5_INTERNAL_READINESS_REQUIRED_EXTERNAL_REVIEW_PATHS` tuple does not yet include this review file (`docs/reviews/goal2964_claude_review_goal2962_large_scale_stress_2026-06-01.md`). This is expected since the review is being produced now; updating the index is the next step after this review is accepted.

---

## Boundary Preservation Summary

All release and claim boundaries are preserved:

- `v2_5_release_authorized: False` — confirmed in readiness packet
- `release_tag_action_authorized: False` — confirmed in readiness packet
- `public_speedup_claim_authorized: False` — confirmed in all three artifacts and readiness packet
- `broad_rt_core_speedup_claim_authorized: False` — confirmed in all three artifacts
- `whole_app_speedup_claim_authorized: False` — confirmed in all three artifacts and readiness packet
- `true_zero_copy_claim_authorized: False` — confirmed in readiness packet
- `package_install_claim_authorized: False` — confirmed in readiness packet
- `triton_preview_auto_selection_authorized: False` — confirmed in RTNN artifact and readiness packet
- `native_app_specific_engine_logic_authorized: False` — confirmed in readiness packet
- `paper_reproduction_claim_authorized: False` — confirmed in Hausdorff and RT-DBSCAN artifacts

---

## Verdict

**`accept-with-boundary`**

The stress evidence is sound. All three artifacts pass with clean source at commit `8deb21bea3930830ad03d3d7410356c786af5479`. RTNN correctly chunks into four 65,536-query graph batches with all distributions exceeding the 2.0x CuPy ratio floor. The Hausdorff 16K path is confirmed exact and RT-core accelerated with zero distance error and competitive timing. The RT-DBSCAN grouped-stream path remains RT-core accelerated, compact, and signature-matching at 262K with 4.580x speedup. The report avoids all prohibited overclaims. Goal2962 is appropriately framed as stress evidence layered on the Goal2959 zero-target packet, and the readiness module correctly indexes it without advancing any release gate.

Release authorization, public speedup claims, and all other blocked actions remain blocked.
