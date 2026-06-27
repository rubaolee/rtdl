# Goal3149: v2.8 Front-Door Completion Packet

Date: 2026-06-03

Status: internal v2.8 preview packet complete; not a release authorization.

## What Changed

The v2.8 typed result-stream work now has a complete explicit partner-consumer front door for the current continuation operation set. The key change over the last burst is that fast lower-level Numba primitives are no longer reachable only through bespoke benchmark-app paths:

- Goal3143 exposed exact Hausdorff Numba continuation through `partner_exact, partner="numba"`.
- Goal3145 moved `segmented_min_f64` and `segmented_max_f64` into the segmented typed stream front door with canonical output compaction.
- Goal3147 moved `compact_mask_i64` into the front door as a stable candidate-stream filter.
- Goal3148 accepted the compact-mask promotion and cleaned the two informational code-quality notes from the review.

## Current Supported Operations

The v2.8 front door supports the full current typed-result continuation set:

| operation | front-door status | canonical output |
| --- | --- | --- |
| `segmented_count_i64` | supported | `counts` |
| `segmented_sum_f64` | supported | `sums` |
| `segmented_min_f64` | supported | `group_ids`, `mins`, `missing_group_ids` |
| `segmented_max_f64` | supported | `group_ids`, `maxes`, `missing_group_ids` |
| `grouped_vector_sum_f64x2` | supported | `sum_x`, `sum_y` |
| `grouped_argmin_f64` | supported | `group_ids`, `item_ids`, `scores`, `missing_group_ids` |
| `grouped_argmax_f64` | supported | `group_ids`, `item_ids`, `scores`, `missing_group_ids` |
| `grouped_topk_f64` | supported | `group_ids`, `item_ids`, `scores`, `ranks`, `row_offsets`, `missing_group_ids` |
| `bounded_collect_finalize_i64` | supported | `group_ids`, `item_ids`, `row_offsets` |
| `compact_mask_i64` | supported | `values`, `original_indices` |

`V2_8_SEGMENTED_TYPED_STREAM_PARTNER_CONSUMER_DEFERRED_OPERATIONS` is now empty. That means the current operation surface has no remaining deferred front-door entry. It does not mean v2.8 is release-ready.

## Evidence

Local focused suite:

```text
python -m unittest \
  tests.goal3105_v2_8_benchmark_runtime_gap_map_test \
  tests.goal3108_v2_8_typed_result_stream_contract_test \
  tests.goal3111_v2_8_segmented_typed_stream_adapter_test \
  tests.goal3143_hausdorff_partner_exact_numba_front_door_test \
  tests.goal3145_segmented_minmax_front_door_canonical_compaction_test \
  tests.goal3147_compact_mask_front_door_test \
  tests.goal3139_numba_kernel_cache_contract_test

Ran 46 tests
OK (skipped=2)
```

Pod focused suite on NVIDIA RTX 4000 Ada at commit `719cfc34`:

```text
Ran 46 tests in 0.885s
OK
```

Pod artifacts:

- `docs/reports/goal3143_pod_artifacts/hausdorff_partner_exact_numba_pod_probe_2026-06-03.json`
- `docs/reports/goal3145_pod_artifacts/segmented_minmax_front_door_pod_probe_2026-06-03.json`
- `docs/reports/goal3147_pod_artifacts/compact_mask_front_door_pod_probe_2026-06-03.json`

External review signals:

- `docs/reviews/goal3144_claude_review_goal3143_hausdorff_partner_exact_numba_front_door_2026-06-03.md` - `accept-with-boundary`
- `docs/reviews/goal3146_claude_review_goal3145_segmented_minmax_front_door_2026-06-03.md` - `accept-with-boundary`
- `docs/reviews/goal3148_claude_review_goal3147_compact_mask_front_door_2026-06-03.md` - `accept`

## Boundary

This packet proves front-door coverage and correctness evidence for the current internal v2.8 operation set. It does not authorize:

- v2.8 release;
- public speedup claims;
- broad RT-core speedup claims;
- true zero-copy or device-resident result-stream claims;
- hidden dispatch;
- automatic partner selection;
- app-specific native engine logic;
- user-defined shader injection.

The user still chooses the partner explicitly. The front door makes generic primitives discoverable and composable; it does not choose a partner for the user.

## Next Work

The next meaningful v2.8/v3.0-adjacent work is not another missing front-door operation. It is deeper runtime work:

- device-resident result streams instead of host-side canonical output shaping;
- stronger multi-partner conformance matrices for Torch/CuPy/Numba/Triton-shaped paths;
- larger same-contract benchmark packets that compare primitive-first and partner-continuation implementations without public speedup overclaim;
- eventual v3.0 user-defined shader or custom-kernel extension design, which remains out of scope here.
