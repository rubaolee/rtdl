# Goal821 Public Docs RT-Core Claim Boundary Refresh

Date: 2026-04-23

## Verdict

ACCEPT. The public docs now consistently separate OptiX backend selection from
NVIDIA RT-core acceleration claims.

## Scope

This goal refreshed the user-facing documentation after Goals 813-820 added
app-level `--require-rt-core` gates. No runtime behavior changed in this goal.

Updated public docs:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md`
- `/Users/rl2025/rtdl_python_only/docs/application_catalog.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/db_workloads.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/graph_workloads.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/nearest_neighbor_workloads.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/segment_polygon_workloads.md`

## User-Facing Rule

`--backend optix` is a backend-selection flag. It is not, by itself, a NVIDIA
RT-core acceleration claim.

Claim-sensitive commands must use `--require-rt-core`. Apps reject that flag
unless the selected mode is a documented bounded OptiX traversal path with a
narrow claim scope.

## Current Accepted Partial Claim Modes

| App | Claim-sensitive command shape | Scope |
| --- | --- | --- |
| Unified DB app | `--backend optix --output-mode compact_summary --require-rt-core` | compact summary only |
| Service coverage gaps | `--backend optix --optix-summary-mode gap_summary_prepared --require-rt-core` | prepared uncovered-household summary |
| Event hotspot screening | `--backend optix --optix-summary-mode count_summary_prepared --require-rt-core` | prepared event count/hotspot summary |
| Outlier detection | `--backend optix --optix-summary-mode rt_count_threshold_prepared` | prepared fixed-radius density-threshold summary |
| DBSCAN clustering | `--backend optix --optix-summary-mode rt_core_flags_prepared` | prepared core-flag summary only |
| Robot collision screening | `--backend optix --optix-summary-mode prepared_count` or `prepared_pose_flags` | prepared any-hit count or pose flags |

## Current Rejected Families

These app families now remain explicitly non-claim paths in public docs:

- graph apps
- facility KNN
- polygon overlap/Jaccard
- segment/polygon apps
- Hausdorff
- ANN candidate search
- Barnes-Hut

They may still be useful compatibility or experimental paths, but they are not
public NVIDIA RT-core acceleration claims yet.

## Verification

Added `/Users/rl2025/rtdl_python_only/tests/goal821_public_docs_require_rt_core_test.py`.

The focused test checks that:

- `README.md`, `docs/quick_tutorial.md`, `docs/application_catalog.md`,
  `docs/release_facing_examples.md`, and `docs/rtdl_feature_guide.md` explain
  the OptiX-vs-RT-core distinction.
- public docs list the current claim-sensitive command shapes.
- graph, nearest-neighbor app, and segment/polygon tutorials document rejected
  `--require-rt-core` app families.

The public command truth audit was also refreshed so the two new
claim-sensitive service/hotspot commands are classified as
`goal821_require_rt_core_doc_gate_exact` rather than uncovered commands.
`scripts/goal515_public_command_truth_audit.py` now reports `valid: true` for
252 public commands.

This report preserves the release honesty boundary from
`/Users/rl2025/rtdl_python_only/docs/reports/goal818_rtx_app_claim_gate_summary_2026-04-23.md`.
