# Goal1311: v1.5 Jaccard Generic Fail-Closed Collection Wrapper

Date: 2026-05-05

## Decision

Goal1311 adds a Python/generic `COLLECT_K_BOUNDED` wrapper for `polygon_set_jaccard`. This is not a native device-level implementation and does not promote Jaccard to a public speedup claim. It closes the Python-layer gap from Goal1310: Jaccard score reduction now runs only after bounded candidate collection proves complete coverage.

## What Changed

- `collect_k_bounded_candidate_pairs(candidate_pairs, k=...)` normalizes candidate-pair IDs into stable `(left_id, right_id)` order.
- If `k` is too small, the wrapper raises `RuntimeError` with `failure_mode=fail_closed_overflow` before returning candidate pairs.
- `run_generic_polygon_set_jaccard_summary(...)` calls the bounded collection wrapper before invoking exact score reduction.
- `examples/rtdl_polygon_set_jaccard.py` now routes Embree and OptiX native-assisted Jaccard scoring through the generic wrapper and exposes optional `--collection-capacity`.

## Boundary

This is still diagnostic:

| Area | Status |
|---|---|
| Python/generic fail-closed collection | done |
| Native device-level fail-closed collection | not done |
| Native device-level Jaccard score reduction | not done |
| OptiX slower-than-Embree explanation | still required |
| Public NVIDIA speedup wording | blocked |

The inventory remains `diagnostic_blocked` because the fail-closed guarantee is not yet enforced inside native Embree/OptiX device-level collection, and because the OptiX performance explanation is still open.

## Validation

Local gate:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1311_v1_5_jaccard_generic_fail_closed_collection_test \
  tests.goal1310_v1_5_jaccard_collect_k_bounded_contract_test \
  tests.goal1280_v1_4_polygon_jaccard_diagnostic_contract_test \
  tests.goal1304_v1_5_generic_migration_inventory_test
python3 -m py_compile \
  src/rtdsl/generic_polygon_primitives.py \
  examples/rtdl_polygon_set_jaccard.py \
  src/rtdsl/v1_5_migration_inventory.py \
  src/rtdsl/__init__.py
git diff --check
```

Result: passed on 2026-05-05.

## Pod Diagnostic

Pod workspace: `/workspace/rtdl_goal1311_min`

OptiX library: `/workspace/rtdl_goal1292/build/librtdl_optix.so`

Compact artifact:

- `docs/reports/goal1311_v1_5_jaccard_generic_fail_closed_collection_pod_results/compact_summary.json`

Commands:

```bash
export RTDL_OPTIX_LIB=/workspace/rtdl_goal1292/build/librtdl_optix.so
PYTHONPATH=src:. python3 examples/rtdl_polygon_set_jaccard.py \
  --backend embree --copies 128 --output-mode summary --collection-capacity 512
PYTHONPATH=src:. python3 examples/rtdl_polygon_set_jaccard.py \
  --backend optix --copies 128 --output-mode summary --collection-capacity 512 --require-rt-core
PYTHONPATH=src:. python3 examples/rtdl_polygon_set_jaccard.py \
  --backend embree --copies 128 --output-mode summary --collection-capacity 1
```

Result:

| Check | Result |
|---|---|
| Embree candidate pairs | 384 |
| OptiX candidate pairs | 256 |
| Embree Jaccard summary | intersection `640`, union `2432`, similarity `0.2631578947368421` |
| OptiX Jaccard summary | intersection `640`, union `2432`, similarity `0.2631578947368421` |
| OptiX RT-core candidate discovery | active |
| Capacity 1 overflow | exit `1`, `COLLECT_K_BOUNDED overflowed capacity 1; emitted 384; failure_mode=fail_closed_overflow` |

The Embree/OptiX candidate counts differ because the candidate-discovery subpaths can emit different positive-candidate supersets, but both produce the same exact Jaccard score after native exact scoring. This remains diagnostic because native device-level bounded collection and native score reduction are not implemented.
