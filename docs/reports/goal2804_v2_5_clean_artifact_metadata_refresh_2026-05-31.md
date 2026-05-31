# Goal2804 v2.5 Clean Artifact Metadata Refresh

Date: 2026-05-31

Status: implemented locally and pod validated.

Verdict: accept-with-boundary.

## Purpose

Goal2804 tightens the v2.5 evidence packet after Goal2803 filled the final
Tier B benchmark harness row. The issue was not algorithmic performance. It was
traceability:

- Goal2800 and Goal2801 clean artifacts did not record source commit, source
  dirty state, or GPU identity.
- Goal2802's clean artifact recorded a dirty stdout file because stdout had
  been created inside the repository before the harness captured `git status`.
- Goal2803 already had the stricter metadata after the clean rerun.

This goal refreshes the clean evidence metadata for Goal2800, Goal2801, and
Goal2802, and adds a single regression test that checks the current Tier B
clean artifacts as a group.

## Clean Artifact Metadata

| App | Artifact | Commit | source_dirty | GPU | Status |
| --- | --- | --- | --- | --- | --- |
| `rtnn` | `docs/reports/goal2800_pod_artifacts/rtnn_v25_live_ranked_summary_65536_clean_from_git.json` | `6ae202919c2af07ae8d8a9c662edd656ae77aa87` | `[]` | NVIDIA RTX A5000, 570.211.01 | pass |
| `hausdorff_xhd` | `docs/reports/goal2801_pod_artifacts/hausdorff_xhd_v25_canonical_entrypoint_4096_clean_from_git.json` | `6ae202919c2af07ae8d8a9c662edd656ae77aa87` | `[]` | NVIDIA RTX A5000, 570.211.01 | pass |
| `rt_dbscan` | `docs/reports/goal2802_pod_artifacts/rt_dbscan_v25_live_grouped_stream_32768_65536_131072_clean_from_git.json` | `6ae202919c2af07ae8d8a9c662edd656ae77aa87` | `[]` | NVIDIA RTX A5000, 570.211.01 | pass |
| `barnes_hut` | `docs/reports/goal2803_pod_artifacts/barnes_hut_v25_consolidated_harness_clean_from_git.json` | `60237c663c64b3322310817f0e0ece28e15e0f30` | `[]` | NVIDIA RTX A5000, 570.211.01 | pass |

The Goal2800-2802 refresh was run by writing the harness outputs to `/tmp`
after resetting the pod checkout for each harness. That avoids creating or
deleting tracked artifact files before the harness captures `git status`.

## v2.5 Manifest Position

The v2.5 tiered benchmark manifest now validates with 10 apps:

| Tier | Count | Apps |
| --- | ---: | --- |
| A | 3 | `raydb_style`, `triangle_counting`, `spatial_rayjoin` |
| B | 4 | `rt_dbscan`, `rtnn`, `barnes_hut`, `hausdorff_xhd` |
| C | 3 | `librts_spatial_index`, `contact_manifold`, `robot_collision` |

Every manifest row has a `ready...` canonical harness status. The manifest
still blocks public speedup and true-zero-copy claims.

## Boundary

This is a traceability and evidence-cleanliness goal. It is:

- not a release authorization;
- not a public speedup claim;
- not a whole-app speedup claim;
- not a true-zero-copy claim;
- not permission to auto-select a preview Triton path;
- not permission to add app-specific logic to the native engine.

## Validation

Local focused validation:

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest \
  tests.goal2800_rtnn_v25_live_ranked_summary_harness_test \
  tests.goal2801_hausdorff_xhd_v25_canonical_entrypoint_test \
  tests.goal2802_rt_dbscan_v25_live_grouped_stream_harness_test

Ran 15 tests in 0.038s
OK
```

Expanded local v2.5 metadata/boundary validation:

```text
tests.goal2804_v2_5_clean_artifact_metadata_refresh_test
tests.goal2800_rtnn_v25_live_ranked_summary_harness_test
tests.goal2801_hausdorff_xhd_v25_canonical_entrypoint_test
tests.goal2802_rt_dbscan_v25_live_grouped_stream_harness_test
tests.goal2803_barnes_hut_v25_consolidated_harness_test
tests.goal2723_v2_5_tiered_benchmark_manifest_test
tests.goal2789_neutral_buffer_torch_carrier_reconciliation_test
tests.goal2792_partner_selection_explain_plan_test
tests.goal2793_v2_5_partner_role_reconciliation_test
tests.goal2794_v2_5_determinism_policy_test
tests.goal2795_v2_5_tier_label_reconciliation_test

Ran 55 tests in 0.023s
OK
```

Clean pod validation after push:

```text
Host: root@69.30.85.171:22167
Commit: 8e322b0a
Command: python3 -m unittest [same 11-test-module slice]

Ran 55 tests in 0.008s
OK
```

External review:

```text
Gemini: accept-with-boundary
Review: docs/reviews/goal2804_gemini_review_v2_5_clean_artifact_metadata_refresh_2026-05-31.md
Consensus: docs/reports/goal2804_v2_5_clean_artifact_metadata_refresh_consensus_2026-05-31.md
```

Claude was attempted, but wrote no review output before the stuck process was
stopped; it is not counted for Goal2804 consensus.

This test verifies:

- all four Tier B clean artifacts are `pass`;
- all four record a 40-character source commit;
- all four record `source_dirty: []`;
- all four record the NVIDIA RTX A5000 pod GPU;
- public/whole-app speedup and native-customization claims remain false;
- the v2.5 manifest validates at 10 apps with Tier A/B/C counts of 3/4/3;
- continuation contract, preview gate, support matrix, selection guidance,
  determinism policy, and neutral seam boundaries still validate.
