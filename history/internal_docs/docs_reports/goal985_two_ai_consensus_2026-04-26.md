# Goal985 Two-AI Consensus

Date: 2026-04-26

Goal: replace graph `visibility_edges` OptiX summary row materialization with prepared ray/triangle any-hit count, while preserving row-returning semantics and public claim boundaries.

## Local Dev AI Verdict

ACCEPT.

The implementation is bounded to `examples/rtdl_graph_analytics_app.py` for `backend="optix"`, `scenario="visibility_edges"`, and `output_mode="summary"`. It builds the same explicit candidate-edge rays, prepares blocker triangles and rays, calls `prepared_scene.count(prepared_rays)`, and derives visible/blocked counts without calling `rt.visibility_pair_rows(...)`.

The row-returning path remains unchanged for non-summary modes and non-OptiX backends. The change is an interface/materialization reduction, not a new graph-system speedup claim.

## External AI Verdict

Gemini CLI reviewed the goal and wrote `docs/reports/goal985_gemini_review_2026-04-26.md` with verdict ACCEPT.

Gemini specifically accepted:

- Correct use of `rt.prepare_optix_ray_triangle_any_hit_2d(...)`, `rt.prepare_optix_rays_2d(...)`, and `prepared_scene.count(...)` for blocked-edge counts.
- Correct visible-edge derivation from candidate-edge count minus blocked count.
- Preservation of `rt.visibility_pair_rows(...)` row-returning semantics outside OptiX summary mode.
- Consistent docs and manifest updates.
- No public RTX speedup authorization.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal814_graph_optix_rt_core_honesty_gate_test \
  tests.goal889_graph_visibility_optix_gate_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal914_rtx_targeted_graph_jaccard_rerun_test
```

Result:

```text
Ran 31 tests in 0.390s
OK
```

Additional checks:

```text
python3 -m py_compile examples/rtdl_graph_analytics_app.py scripts/goal759_rtx_cloud_benchmark_manifest.py src/rtdsl/app_support_matrix.py
git diff --check
```

Both passed.

## Consensus Decision

ACCEPT.

Goal985 is closed as a correct bounded optimization and documentation update. It improves the next RTX graph rerun path by avoiding summary row materialization, but graph remains under the existing Goal978 claim boundary until a fresh RTX artifact beats the same-scale non-OptiX baseline and passes separate claim review.
