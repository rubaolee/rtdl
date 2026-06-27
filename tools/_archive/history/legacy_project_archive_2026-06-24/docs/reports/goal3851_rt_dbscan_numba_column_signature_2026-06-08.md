# Goal3851: RT-DBSCAN Numba Column-Signature Prepared Repeat

Date: 2026-06-08

Status: implemented and A5000-validated

## Purpose

Goal3850 kept the ten promoted benchmark scale-profile rows green, but the
RT-DBSCAN row remained a clear high-cost target. The existing
`optix_rt_core_flags_numba_prepared_grid_components_3d` path had two issues:

- it accepted `--repeat` / `--warmup`, but still measured one cold prepared
  pass;
- even with `--no-validation`, it materialized Python row dictionaries to
  compute the result signature.

Goal3851 makes the OptiX + Numba RT-DBSCAN path behave like a prepared
resident benchmark route: prepare once, run the generic OptiX threshold-count
primitive and generic Numba component continuation repeatedly, then compute a
signature directly from partner columns without Python row dictionaries.

## Implementation

Touched files:

- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- `examples/v2_0/research_benchmarks/rt_dbscan/README.md`
- `src/rtdsl/current_benchmark_scale_profiles.py`

Key changes:

- Added explicit mode
  `optix_rt_core_flags_numba_prepared_grid_column_signature_3d`.
- The existing OptiX + Numba components mode now honors prepared
  `repeat` / `warmup` and records `prepared_query_repeat_protocol`.
- The new column-signature mode sets `materializes_python_rows=false` and
  `signature_source=partner_column_arrays_no_python_row_dicts`.
- The current benchmark scale-profile registry keeps the stable row id
  `rt_dbscan_optix_numba_scale_default_65536_no_validation`, but routes it to
  the column-signature mode.
- The one-time `prepare_sec` is recorded inside the repeat protocol and is not
  mixed into the per-iteration steady-state median.

The native engine ABI is unchanged. The path still composes generic primitives:

- OptiX writes threshold-capped fixed-radius counts and core flags into
  Numba-compatible device columns.
- Numba performs generic radius-graph component labeling over prepared point
  columns.
- The benchmark app computes a DBSCAN-style cluster signature outside the
  native engine.

This is an RTDL/OptiX + Numba composition path, not a DBSCAN-specific native
engine.

## A5000 Evidence

Artifact directory:

- `docs/reports/goal3851_rt_dbscan_numba_column_signature_a5000/`

Direct command:

```bash
PYTHONPATH=.pydeps_goal3788_numba:src:. \
RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so \
python examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py \
  --mode optix_rt_core_flags_numba_prepared_grid_column_signature_3d \
  --dataset clustered3d --point-count 65536 --repeat 3 --warmup 1 \
  --no-validation
```

Direct payload result:

| Metric | Value |
| --- | ---: |
| payload `elapsed_sec` | `0.284242913` |
| median OptiX threshold-count phase | `0.116409539` |
| median Numba component continuation phase | `0.130830898` |
| one-time prepare phase | `1.146791432` |
| measured iterations | `2` |
| materializes Python rows | `false` |

The file-backed scale-profile runner also passed the updated `rt_dbscan` row:

| Metric | Value |
| --- | ---: |
| runner status | `pass` |
| runner process elapsed | `3.752731372` |
| runner payload `elapsed_sec` | `0.266242804` |
| stdout JSON parseable | `true` |
| claim-boundary violations | `0` |

## Delta Versus Goal3850

Goal3850's RT-DBSCAN payload for the same 65k no-validation row was:

- `elapsed_sec=2.280521210`
- `optix_rt_count_threshold_sec=0.737919548`
- `numba_component_continuation_sec=0.966807261`
- `path=optix_rt_count_threshold_numba_prepared_grid_radius_graph_components_3d`

Goal3851's runner payload is:

- `elapsed_sec=0.266242804`
- `optix_rt_count_threshold_sec=0.102740549`
- `numba_component_continuation_sec=0.129611017`
- `path=optix_rt_count_threshold_numba_prepared_grid_radius_graph_column_signature_3d`

That is an `8.56x` prepared-payload improvement for the measured row. The
outer command-line process is not `8.56x` faster because process startup,
imports, Numba CUDA compilation, and one-time prepare work remain outside the
prepared steady-state payload. This is an important boundary, not a failure:
the improvement applies to resident/prepared application use.

## Boundary

This is not a public release claim, not a paper-reproduction claim, and not a
broad RT-core speedup claim. It is internal benchmark-app evidence that the
RTDL + OptiX + Numba route can avoid Python row materialization and measure a
prepared steady-state path honestly. It does not authorize release action,
public speedup wording, broad RT-core wording, or paper-reproduction wording.
