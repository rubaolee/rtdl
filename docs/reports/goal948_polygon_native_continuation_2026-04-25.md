# Goal948 Polygon Native Continuation

Date: 2026-04-25

## Purpose

Continue v1.0 app work after the RT candidate-discovery milestone by moving
one remaining app continuation stage out of Python loops.

This goal covers two polygon apps:

- `examples/rtdl_polygon_pair_overlap_area_rows.py`
- `examples/rtdl_polygon_set_jaccard.py`

## Change

Before this goal, Embree/OptiX app modes used native RT-assisted candidate
discovery through LSI/PIP kernels, then Python exact unit-cell refinement for
the final polygon-pair area rows or set-Jaccard row.

After this goal:

- Embree/OptiX still perform RT-assisted positive candidate discovery.
- Candidate pairs are passed into new native oracle C ABI entry points.
- Native C++ exact unit-cell continuation computes overlap-area rows and
  Jaccard rows.
- Public app payloads expose:
  - `native_continuation_active`
  - `native_continuation_backend: oracle_cpp`

This is intentionally not described as a monolithic GPU polygon overlay
kernel. The accurate claim is RT candidate discovery plus native C++
continuation.

## Files Changed

- `src/native/oracle/rtdl_oracle_abi.h`
- `src/native/oracle/rtdl_oracle_api.cpp`
- `src/rtdsl/oracle_runtime.py`
- `src/rtdsl/__init__.py`
- `examples/rtdl_polygon_pair_overlap_area_rows.py`
- `examples/rtdl_polygon_set_jaccard.py`
- `scripts/goal877_polygon_overlap_optix_phase_profiler.py`
- `scripts/goal759_rtx_cloud_benchmark_manifest.py`
- `docs/app_engine_support_matrix.md`
- `docs/application_catalog.md`
- `docs/features/polygon_pair_overlap_area_rows/README.md`
- `docs/features/polygon_set_jaccard/README.md`
- `examples/README.md`
- `tests/goal948_polygon_native_continuation_test.py`
- `tests/goal713_polygon_overlap_embree_app_test.py`

## Verification

Native ABI smoke:

```text
RTDL_FORCE_ORACLE_REBUILD=1 PYTHONPATH=src:. python3 - <<'PY'
... native pair/Jaccard refinement equals Python candidate refinement ...
PY
```

Focused test gate:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal948_polygon_native_continuation_test \
  tests.goal713_polygon_overlap_embree_app_test \
  tests.goal816_polygon_overlap_rt_core_boundary_test \
  tests.goal687_app_engine_support_matrix_test \
  tests.goal690_optix_performance_classification_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal877_polygon_overlap_optix_phase_profiler_test -v
```

Result:

```text
Ran 43 tests in 0.608s
OK
```

Additional compatibility check:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal603_apple_rt_native_contract_test -v
```

Result:

```text
Ran 4 tests in 0.000s
OK
```

Whitespace audit:

```text
git diff --check
```

Result: clean.

## Boundaries

- No new public speedup claim is authorized by this goal.
- This does not make polygon overlay a monolithic GPU kernel.
- Historical cloud artifacts that recorded `cpu_exact_refinement_sec` keep that
  field name for compatibility; the current profiler also emits
  `native_exact_continuation_sec` for the same continuation phase.
- Apple RT native-coverage wording is unchanged; this goal targets the public
  Embree/OptiX app surfaces.

## Peer Review Round 1

Peer verdict: BLOCK.

Finding: `docs/application_catalog.md` still described the two polygon
claim-review rows as candidate-discovery-only with exact refinement remaining
CPU/Python. That contradicted the new native C++ continuation path.

Resolution: the rows now say native-assisted LSI/PIP candidate discovery plus
native C++ exact area/Jaccard continuation, while preserving the no-monolithic
GPU speedup boundary.

## Next App Continuation Targets

The remaining high-value continuation work is still:

- graph analytics: move BFS/triangle-count postprocess/reduction farther into
  native graph-ray paths
- database analytics: reduce row materialization/copyback and prefer compact
  native outputs
- ANN/DBSCAN/Hausdorff/Barnes-Hut: move ranking, clustering flags, and force
  reduction into native or prepared backend summaries where semantics are
  bounded and testable
