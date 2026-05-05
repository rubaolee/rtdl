# Goal1321: Backend-Neutral Polygon Area Summary ABI

Date: 2026-05-05

## Scope

Goal1321 implements the backend-neutral native reduction ABI required by the
Goal1313 Jaccard device plan:

```c
int rtdl_native_reduce_polygon_pair_exact_area_summary(...);
```

This ABI is not app-named and does not expose a
`polygon_set_jaccard_fast` path. It reduces complete bounded polygon-pair
candidates into set-level area totals:

- `overlap_pair_count`
- unique `intersection_area`
- `left_area`
- `right_area`
- `union_area`

The Jaccard app computes the final ratio from this generic area summary.

## Changes

- Added `RtdlPolygonPairAreaSummary` to the native oracle ABI.
- Added exported native function
  `rtdl_native_reduce_polygon_pair_exact_area_summary`.
- Added Python ctypes wrapper
  `reduce_polygon_pair_exact_area_summary_for_candidates(...)`.
- Routed `polygon_set_jaccard` native scoring through the backend-neutral
  area-summary wrapper instead of the app-named
  `rtdl_oracle_refine_polygon_set_jaccard_for_pairs`.
- Updated Jaccard app metadata:
  `native_continuation_backend=native_polygon_pair_area_summary`.
- Updated Jaccard diagnostic contract:
  `exact_score_continuation=backend_neutral_native_polygon_pair_area_summary`.

## Local Evidence

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1321_v1_5_native_polygon_pair_area_summary_abi_test \
  tests.goal1320_v1_5_jaccard_generic_score_reduction_test \
  tests.goal1318_v1_5_jaccard_native_collection_routing_test \
  tests.goal948_polygon_native_continuation_test \
  tests.goal1280_v1_4_polygon_jaccard_diagnostic_contract_test
```

Result:

```text
Ran 19 tests in 0.034s
OK
```

Compile and whitespace gates passed:

```text
python3 -m py_compile src/rtdsl/oracle_runtime.py src/rtdsl/__init__.py src/rtdsl/polygon_primitives.py src/rtdsl/app_support_matrix.py examples/rtdl_polygon_set_jaccard.py tests/goal1321_v1_5_native_polygon_pair_area_summary_abi_test.py
git diff --check
```

Real Embree app-route run:

```text
RTDL_FORCE_EMBREE_REBUILD=1 PYTHONPATH=src:. python3 examples/rtdl_polygon_set_jaccard.py --backend embree --copies 2 --output-mode summary --collection-capacity 16
```

Observed:

- `collection.native_collection=true`
- `native_continuation_backend=native_polygon_pair_area_summary`
- `exact_score_continuation=backend_neutral_native_polygon_pair_area_summary`
- `score_reduction_primitive=POLYGON_SET_JACCARD_SCORE_REDUCTION`
- `score_reduction.integer_parity_values`: intersection `10`, left `26`,
  right `22`, union `38`
- final `jaccard_similarity=0.2631578947368421`

## Boundary

This removes the app-named native Jaccard continuation from the active app route
and replaces it with a backend-neutral native polygon-pair area summary. The
path remains diagnostic: no public Jaccard speedup wording, no fused GPU
Jaccard kernel claim, and no Vulkan/HIPRT/Apple RT work before v2.1.

Next required evidence is pod OptiX validation from GitHub state.
