# Goal3450 - Shape-Pair Relation Device-Column Content Correctness

## Status

Implemented and pod-validated on NVIDIA RTX A5000.

Goal3450 responds to the Goal3448 Claude review boundary: Goal3447 proved row counts but did not prove that the emitted resident `(left_id, right_id, flags)` content matches a host reference.

This goal adds a small sparse-id synthetic fixture and compares:

- host materialized active relation rows from the prepared shape-pair relation route
- resident relation device columns wrapped through CuPy

It also probes fail-closed overflow by rerunning the same fixture with `max_rows=1`.

## Scope

The fixture uses three left rectangles with sparse ids and four right rectangles. It includes:

- segment-intersection active pairs
- containment-only active pairs
- disjoint inactive pairs
- sparse ids to avoid silently relying on dense `0..N` row ordinals

The probe verifies sorted row content, not just counts:

- `left_id`
- `right_id`
- `requires_segment_intersection`
- `requires_point_containment`

## Claim Boundary

This goal does not authorize:

- v2.8 release
- public speedup wording
- RT-core speedup wording
- true-zero-copy wording
- RayJoin paper reproduction claims
- RTDL-beats-RayJoin claims
- full overlay relation-row, overlay-area, or witness completion claims

The intended claim is narrow: the generic resident relation-column stream emits the same active relation ids and dependency flags as the host materialized relation-row route on a small known fixture, and its overflow behavior fails closed.

## Pod Evidence

Artifact:

- `docs/reports/goal3450_shape_pair_relation_device_column_content_pod_2026-06-05.json`
- `docs/reports/goal3450_shape_pair_relation_device_column_content_pod_2026-06-05.stdout`

Pod:

- GPU: NVIDIA RTX A5000, driver 580.126.09
- Commit: `299bbe267d0817b7ee104ec275993921606b6a61`
- Library: `/root/rtdl/build/librtdl_optix.so`

The host materialized active rows and device-resident relation columns matched exactly:

| left_id | right_id | requires_segment_intersection | requires_point_containment |
| ---: | ---: | ---: | ---: |
| 3 | 10 | 1 | 0 |
| 3 | 11 | 0 | 1 |
| 20 | 13 | 0 | 1 |

Observed checks:

- `rows_match: true`
- `host_row_count: 3`
- `device_row_count: 3`
- `metadata_schema_id: shape_pair_relation_flags_2d_device_columns`
- `metadata_device_resident_output_stream_proven: true`

Overflow behavior was also validated with `max_rows=1`:

- `overflow: true`
- `row_count: 0`
- `active_relation_count: 3`
- `retry_capacity_hint: 3`
- `partial_result_returned: false`

## Validation

Local validation:

- `py -3 -m py_compile scripts\goal3450_shape_pair_relation_device_column_content_probe.py tests\goal3450_shape_pair_relation_device_column_content_test.py`
- `py -3 -m unittest tests.goal3450_shape_pair_relation_device_column_content_test`

Pod validation:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so \
python scripts/goal3450_shape_pair_relation_device_column_content_probe.py \
  --output docs/reports/goal3450_shape_pair_relation_device_column_content_pod_2026-06-05.json
```

- `PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so python -m unittest tests.goal3450_shape_pair_relation_device_column_content_test`
- all claim-boundary flags remained false

## Remaining Work

This closes the narrow content-correctness gap for the active relation stream on a small fixture. It still does not produce full overlay witnesses, polygon area, or RayJoin paper reproduction evidence.
