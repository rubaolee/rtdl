# Goal649 App Rewrite: Any-Hit And `reduce_rows`

Date: 2026-04-20

## Goal

Rewrite the existing RTDL-plus-Python apps that naturally benefit from the
v0.9.5 programming surface so they use `ray_triangle_any_hit` and
`rt.reduce_rows(...)` where appropriate, without changing RTDL language
internals and without claiming new native backend speedups.

## Changes

- `examples/rtdl_robot_collision_screening_app.py`
  - Replaced the old per-edge `ray_triangle_hit_count` kernel with
    `ray_triangle_any_hit`.
  - Added pose metadata enrichment and `rt.reduce_rows(..., op="any")` so edge
    any-hit rows become pose collision flags.
  - Kept Python-owned witness reporting for pose/link/edge summaries.
  - Switched the oracle from `rt.ray_triangle_hit_count_cpu` to
    `rt.ray_triangle_any_hit_cpu`.
- `examples/rtdl_hausdorff_distance_app.py`
  - Kept the RTDL `knn_rows(k=1)` primitive.
  - Added `rt.reduce_rows(..., op="max")` for directed Hausdorff distance
    reduction.
  - Kept Python-owned witness/tie-break and undirected-direction selection.
- `examples/rtdl_outlier_detection_app.py`
  - Kept the RTDL `fixed_radius_neighbors` primitive.
  - Replaced manual neighbor counting with `rt.reduce_rows(..., op="count")`.
  - Kept Python-owned thresholding into outlier labels.
- `examples/rtdl_dbscan_clustering_app.py`
  - Kept the RTDL `fixed_radius_neighbors` primitive.
  - Added `rt.reduce_rows(..., op="count")` for core-candidate counts.
  - Kept Python-owned DBSCAN cluster expansion, border labeling, and noise
    labeling.

## Public Docs Updated

- `README.md`
- `docs/README.md`
- `docs/current_architecture.md`
- `docs/tutorials/feature_quickstart_cookbook.md`
- `docs/tutorials/v0_8_app_building.md`
- `examples/README.md`
- `examples/rtdl_feature_quickstart_cookbook.py`

The docs now distinguish the current v0.9.5 app style from the older v0.8
hit-count/manual-reduction wording. They also preserve the honesty boundary:
`reduce_rows` is a Python standard-library helper over already emitted rows,
not a native RT backend reduction or speedup claim.

## Verification

Commands run from `/Users/rl2025/rtdl_python_only`:

```bash
PYTHONPATH=src:. python3 examples/rtdl_robot_collision_screening_app.py --backend cpu_python_reference
PYTHONPATH=src:. python3 examples/rtdl_hausdorff_distance_app.py --backend cpu_python_reference
PYTHONPATH=src:. python3 examples/rtdl_outlier_detection_app.py --backend cpu_python_reference
PYTHONPATH=src:. python3 examples/rtdl_dbscan_clustering_app.py --backend cpu_python_reference
PYTHONPATH=src:. python3 examples/rtdl_feature_quickstart_cookbook.py
PYTHONPATH=src:. python3 -m unittest tests.goal649_app_rewrite_anyhit_reduce_rows_test tests.goal515_public_command_truth_audit_test tests.goal512_public_doc_smoke_audit_test tests.goal646_public_front_page_doc_consistency_test -v
PYTHONPATH=src:. python3 -m unittest tests.goal506_public_entry_v08_alignment_test tests.goal649_app_rewrite_anyhit_reduce_rows_test tests.goal515_public_command_truth_audit_test tests.goal512_public_doc_smoke_audit_test tests.goal646_public_front_page_doc_consistency_test -v
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
```

Results:

- Four rewritten app examples ran on `cpu_python_reference` and matched their
  oracles.
- Goal649 app rewrite tests: 4 tests OK.
- Public-doc alignment/front-page/doc-smoke command tests: 14 tests OK in the
  combined run.
- Public command truth audit: `valid: true`, 248 public commands across 14
  public docs.

## Boundary

- This goal did not change RTDL kernel syntax, lowering internals, or native
  backend ABIs.
- This goal did not claim new speedups.
- Native any-hit acceleration remains limited to engines that already implement
  native early-exit any-hit: OptiX, Embree, and HIPRT.
- Vulkan and Apple RT remain documented as compatibility any-hit paths until
  dedicated native early-exit work is implemented and measured.

## Codex Verdict

ACCEPT. The rewrite makes the existing apps better reflect the current v0.9.5
programming model: RTDL owns candidate traversal/refinement/emitted rows,
`reduce_rows` handles common emitted-row aggregation, and Python keeps the
application-specific logic.

## External Consensus

- Claude review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal649_claude_review_2026-04-20.md`
  - Verdict: ACCEPT.
  - Key point: the four `reduce_rows` calls match their semantic intent and
    the robot app has no residual `hit_count` output.
- Gemini Flash review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal649_gemini_flash_review_2026-04-20.md`
  - Verdict: ACCEPT.
  - Key point: the rewritten apps use `ray_triangle_any_hit` and
    `rt.reduce_rows` without overclaiming native backend acceleration.

Final Goal649 closure: ACCEPT by Codex + Claude + Gemini Flash.
