# Goal1320: Jaccard Generic Score-Reduction Surface

Date: 2026-05-05

## Scope

`polygon_set_jaccard` now has an explicit generic score-reduction wrapper that
runs only after `COLLECT_K_BOUNDED` reports complete candidate coverage.

New API:

- `run_generic_polygon_set_jaccard_score_reduction(...)`

This is a metadata and routing surface around the current native exact
continuation. It is not a fused GPU Jaccard kernel and does not authorize public
speedup wording.

## Behavior

- Requires `collection.primitive=COLLECT_K_BOUNDED`.
- Requires backend match.
- Rejects overflow before calling the score function.
- Rejects incomplete candidate coverage before calling the score function.
- Emits `primitive=POLYGON_SET_JACCARD_SCORE_REDUCTION`.
- Emits `summary_primitive=REDUCE_FLOAT(SUM)`.
- Preserves exact integer parity fields for the current integer-grid oracle.
- `run_generic_polygon_set_jaccard_summary()` now embeds
  `score_reduction_primitive` and `score_reduction` metadata.

## Local Evidence

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1320_v1_5_jaccard_generic_score_reduction_test \
  tests.goal1318_v1_5_jaccard_native_collection_routing_test \
  tests.goal1311_v1_5_jaccard_generic_fail_closed_collection_test \
  tests.goal1310_v1_5_jaccard_collect_k_bounded_contract_test \
  tests.goal1280_v1_4_polygon_jaccard_diagnostic_contract_test
```

Result:

```text
Ran 23 tests in 0.032s
OK
```

Compile and whitespace gates passed:

```text
python3 -m py_compile src/rtdsl/generic_polygon_primitives.py src/rtdsl/__init__.py tests/goal1320_v1_5_jaccard_generic_score_reduction_test.py
git diff --check
```

Real Embree app route:

```text
RTDL_FORCE_EMBREE_REBUILD=1 PYTHONPATH=src:. python3 examples/rtdl_polygon_set_jaccard.py --backend embree --copies 2 --output-mode summary --collection-capacity 16
```

Observed:

- `collection.native_collection=true`
- `score_reduction_primitive=POLYGON_SET_JACCARD_SCORE_REDUCTION`
- `score_reduction.summary_primitive=REDUCE_FLOAT(SUM)`
- `score_reduction.result_layout=summary_float64_sums_plus_ratio`
- `score_reduction.integer_parity_values`: intersection `10`, left `26`,
  right `22`, union `38`
- final `jaccard_similarity=0.2631578947368421`

## Boundary

This narrows the Jaccard path further, but remains diagnostic. The current
score-reduction wrapper may call the native oracle continuation underneath; it
does not claim a new device-side fused reduction and does not promote public
NVIDIA speedup wording.

Next required evidence is pod OptiX app-route validation from GitHub state.
