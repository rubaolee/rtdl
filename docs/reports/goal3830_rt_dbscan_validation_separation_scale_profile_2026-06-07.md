# Goal3830 RT-DBSCAN Validation Separation For Scale Profiles

Date: 2026-06-07

Status: implemented and A5000-validated.

## Purpose

Goal3827 corrected stdout-pipe backpressure, but the RT-DBSCAN 65k row still
timed out because the command included CPU reference validation. That is not the
same thing as timing the RTDL/OptiX + Numba execution path.

Goal3830 separates the two concerns:

- correctness validation remains available on smaller rows,
- large scale-profile timing uses `--no-validation`, and
- the current scale-profile registry promotes the 65k RT-DBSCAN performance row
  instead of the previous 8192-point validation-inclusive row.

## Probe Result

Manual A5000 probe before the registry refresh:

```bash
PYTHONPATH=.pydeps_goal3788_numba:src:. \
RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
python examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py \
  --mode optix_rt_core_flags_numba_prepared_grid_components_3d \
  --dataset clustered3d \
  --point-count 65536 \
  --repeat 3 \
  --warmup 1 \
  --no-validation
```

Result: pass, `elapsed_sec=2.429`, `numba_component_continuation_sec=0.983`,
`optix_rt_count_threshold_sec=0.750`, `matches_reference=null`.

## Scale-Profile Refresh

The refreshed scale-profile artifact is:

`docs/reports/goal3828_current_benchmark_scale_profiles_a5000/summary.json`

The full Goal3828 runner now records
`rt_dbscan_optix_numba_scale_default_65536_no_validation` as a passing row:

- `elapsed_sec=3.503`
- `stdout_bytes=4798`
- `json_pass_count=10` across the complete scale-profile packet
- zero forbidden true claim flags

## Boundary

This is a benchmark methodology correction. It does not weaken correctness
requirements; it separates small correctness validation from large performance
timing. It does not authorize release action, public speedup wording, broad
RT-core wording, paper-reproduction wording, true-zero-copy wording, automatic
partner selection, or app-specific native-engine logic.
