# Goal876 Polygon Overlap OptiX Native-Assisted App Surface

- date: `2026-04-24`
- apps: `polygon_pair_overlap_area_rows`, `polygon_set_jaccard`
- status: `local_app_surface_complete`

## Work Completed

Goal876 adds OptiX native-assisted app surfaces to the two polygon-overlap
apps.

Before this goal, these apps exposed CPU and Embree native-assisted paths at
the public app layer. They did not expose OptiX. After this goal:

- `examples/rtdl_polygon_pair_overlap_area_rows.py --backend optix` is accepted.
- `examples/rtdl_polygon_set_jaccard.py --backend optix` is accepted.
- OptiX mode uses native OptiX LSI/PIP positive candidate discovery.
- CPU/Python still performs exact grid-cell area or Jaccard refinement.
- JSON payloads keep `rt_core_accelerated: false` because the whole app is not
  accelerated end to end; they expose `rt_core_candidate_discovery_active: true`
  for successful OptiX native-assisted candidate discovery.

## Boundary

This is native-assisted traversal filtering, not a fully native polygon-area
or Jaccard kernel.

Allowed statement:

- RTDL can use OptiX traversal to discover candidate polygon overlaps for these
  apps.

Forbidden statement:

- Do not claim a full polygon-area/Jaccard RTX speedup.
- Do not claim exact area/Jaccard refinement is native OptiX.
- Do not interpret `--require-rt-core` as a whole-app speedup claim for these
  apps; it only requires the OptiX candidate-discovery surface.

## Matrix Refresh

Updated:

- `src/rtdsl/app_support_matrix.py`
- `docs/app_engine_support_matrix.md`
- `scripts/goal759_rtx_cloud_benchmark_manifest.py`
- regenerated `docs/reports/goal759_rtx_cloud_benchmark_manifest_2026-04-22.json`

Current status:

- app support: `direct_cli_native_assisted` for OptiX
- OptiX performance class: `python_interface_dominated`
- benchmark readiness: `needs_interface_tuning`
- RT-core maturity: `rt_core_partial_ready`

## Docs Updated

- `examples/README.md`
- `docs/application_catalog.md`
- `docs/features/polygon_pair_overlap_area_rows/README.md`
- `docs/features/polygon_set_jaccard/README.md`
- `docs/tutorials/segment_polygon_workloads.md`
- `docs/release_facing_examples.md`

## Verification

```text
PYTHONPATH=src:. python3 -m unittest tests.goal713_polygon_overlap_embree_app_test tests.goal816_polygon_overlap_rt_core_boundary_test tests.goal705_optix_app_benchmark_readiness_test tests.goal687_app_engine_support_matrix_test tests.goal803_rt_core_app_maturity_contract_test tests.goal759_rtx_cloud_benchmark_manifest_test tests.goal822_rtx_cloud_manifest_claim_boundary_test tests.goal512_public_doc_smoke_audit_test
```

Result: `48 tests OK`.

```text
PYTHONPATH=src:. python3 -m py_compile examples/rtdl_polygon_pair_overlap_area_rows.py examples/rtdl_polygon_set_jaccard.py src/rtdsl/app_support_matrix.py tests/goal713_polygon_overlap_embree_app_test.py tests/goal816_polygon_overlap_rt_core_boundary_test.py scripts/goal759_rtx_cloud_benchmark_manifest.py
git diff --check
```

Result: both passed.

Smoke:

```text
PYTHONPATH=src:. python3 examples/rtdl_polygon_pair_overlap_area_rows.py --backend cpu_python_reference --output-mode summary
PYTHONPATH=src:. python3 examples/rtdl_polygon_set_jaccard.py --backend cpu_python_reference
```

Result: both produced valid JSON.
