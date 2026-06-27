# Goal3898 RT-DBSCAN Segmented-Count Signature Path

## Purpose

Goal3898 improves the current RT-DBSCAN Numba grouped-stream column-signature
path without changing the native engine. The previous column-signature path
copied point ids, component labels, and core flags to host, then sorted and
densified in Python. For the current clustered all-core scale row, that was
unnecessary work.

The new path uses the generic Numba `segmented_count_i64` partner primitive on
the device component-label column when the grouped-stream metadata proves all
core flags are true. It then copies one count vector and densifies only the
nonzero label counts on host.

This is an app-layer continuation optimization over a generic partner
primitive. It does not add DBSCAN vocabulary or behavior to the native engine.

## What Changed

Updated:

- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`

Added:

- `tests/goal3898_rt_dbscan_numba_segmented_count_signature_test.py`

The grouped-stream Numba column-signature mode now records:

- `column_signature_strategy: numba_segmented_count_all_core_labels`
- `column_signature_uses_numba_segmented_count: true`
- `column_signature_materializes_point_ids: false`
- `column_signature_materializes_core_flags: false`

## A5000 Evidence

Pod:

`ssh root@69.30.85.203 -p 22057 -i id_ed25519_rtdl_codex`

Fresh pod clone:

`/root/rtdl_goal3898_rt_dbscan_signature_1780900970`

Source commit:

`59d0225d`

GPU:

`NVIDIA RTX A5000, 580.126.09`

Artifact:

`docs/reports/goal3898_rt_dbscan_segmented_count_signature_a5000/rt_dbscan_segmented_count_signature_65k.json`

Command:

```bash
python3 examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py \
  --mode optix_rt_core_grouped_stream_numba_column_signature_3d \
  --dataset clustered3d \
  --point-count 65536 \
  --repeat 3 \
  --warmup 1 \
  --no-validation
```

## Result

The new output signature matches the previous clean Goal3894 RT-DBSCAN output.

| Metric | Previous Goal3894 path | Goal3898 path | Ratio |
| --- | ---: | ---: | ---: |
| App hot elapsed sec | `0.115497` | `0.080245` | `1.439x` faster |
| Column-signature sec | `0.041711` | `0.006625` | `6.296x` faster |
| Native grouped-union sec | `0.072997` | `0.073411` | unchanged |

The important diagnostic is that the native grouped-union time did not change:
Goal3898 optimizes the partner/app signature continuation, not the RT traversal
primitive.

It optimizes the partner/app signature continuation, not the RT traversal primitive.

## Boundary

Goal3898 does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, RT-DBSCAN paper-reproduction
wording, true-zero-copy wording, automatic partner selection, or app-specific
native-engine logic.

The accepted internal claim is narrower: for the current A5000 clustered
65,536-point RT-DBSCAN scale row, the explicit user-selected Numba grouped
stream path now computes the all-core signature through a generic segmented
count primitive and avoids host materialization of point ids and core flags.

## Validation

Local validation:

```text
py -3 -m unittest tests.goal3898_rt_dbscan_numba_segmented_count_signature_test tests.goal3859_rt_dbscan_numba_grouped_stream_test tests.goal2469_rt_dbscan_column_signature_mode_test
```

Result:

`13 tests OK`
