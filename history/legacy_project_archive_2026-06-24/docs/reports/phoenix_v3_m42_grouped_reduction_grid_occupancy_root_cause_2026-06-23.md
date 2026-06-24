# Phoenix V3 M42 Grouped-Reduction Grid Occupancy Root Cause

Date: 2026-06-23

Status: `m42_root_cause_identified_shape_positive_not_release`

This report answers the M41 blocker: why the serious free-local grouped-reduction run at `262144` rows and `1024` groups produced a Numba low-occupancy warning (`grid size 4`) and stayed slower than the CPU hot control.

This is not a release authorization, not an all-app authorization, not paid-POD authorization, not public speedup wording, not V4, not embedding, and not true zero-copy evidence.

## Source Findings

The productized grouped-reduction path uses the Numba presegmented-offsets kernel:

- `src/rtdsl/numba_partner_continuation.py`
- `run_numba_grouped_vector_sum_f64x2_by_offsets`
- `run_numba_prepared_grouped_vector_sum_f64x2_by_offsets`
- `_numba_grouped_vector_sum_f64x2_offsets_kernel`

The launch shape is:

```text
grid = ceil(group_count / block_size)
block_size = 256
```

The kernel parallelism axis is `group_count`, not `row_count`. Each CUDA thread owns one group and loops serially over that group's contiguous row segment:

```text
group = cuda.grid(1)
start = row_offsets[group]
end = row_offsets[group + 1]
while index < end:
    local_x += values_x[index]
    local_y += values_y[index]
```

Therefore the M41 serious shape:

```text
row_count = 262144
group_count = 1024
block_size = 256
program_count = ceil(1024 / 256) = 4
rows_per_group_mean = 256
```

launches only `4` blocks. Increasing `row_count` while holding `group_count=1024` would not increase grid occupancy; it would only make each thread run a longer serial loop. Reducing `group_count` to `64` would make occupancy worse (`ceil(64 / 256) = 1` block). The code evidence therefore corrects the earlier speculative shape suggestions: the diagnostic shape must increase `group_count`.

## Instrumentation Added

M42 adds launch-shape metadata to the generic grouped-reduction prepared-session path:

- `v2_5_numba_offset_program_count`
- `v2_5_numba_threads_per_block`
- `v2_5_numba_launch_parallelism_axis`
- `v2_5_numba_rows_per_group_mean`
- `grouped_reduction_launch_shape`

This is generic runtime evidence instrumentation. It does not change kernel behavior and does not tune an app route.

Local validation:

```text
PYTHONPATH=src;. py -3 -m unittest tests.v3_phoenix_prepared_execution_session_runner_test -k grouped_vector_sum
3 tests OK

py -3 -m unittest tests.v3_phoenix_m41_grouped_reduction_harness_test
6 tests OK
```

## Bounded Free-Local Shape Experiment

Because root cause showed that occupancy depends on `group_count`, M42 ran exactly one free local Linux shape experiment on `192.168.1.20`, not paid POD:

```text
PYTHONPATH=src:. python3 scripts/v3_phoenix_grouped_reduction_m41_local_harness.py \
  --variant all \
  --row-count 262144 \
  --group-count 65536 \
  --seed 20260623 \
  --warmup 2 \
  --repeat 5
```

Copied evidence:

```text
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m42_lx1_shape_262144x65536_20260623_151852/
```

Key result:

| Metric | Value |
|---|---:|
| failed checks | `0` |
| correctness | `allclose=true` |
| step2 local runner contract candidate | `true` |
| runtime trunk executes end-to-end | `true` |
| internal device residency between RTDL phases | `true` |
| hot-path host materialization | `false` |
| program count | `256` |
| threads per block | `256` |
| rows per group mean | `4.0` |
| CPU hot median | `0.0017162379808723927 s` |
| legacy Numba hot median | `0.004982274957001209 s` |
| productized runner hot median | `0.0002663338091224432 s` |
| runner vs CPU hot | `6.443935850755532x` |
| runner vs legacy hot | `18.706881313407262x` |
| runner vs legacy wall | `25.558762196642736x` |

## Interpretation

M41's grouped-reduction failure was not proof that the productized execution trunk is ineffective. It was a launch-shape mismatch: the generic offsets kernel exposes parallelism over groups, while the M41 shape had too few groups and too much serial work per group.

The M42 shape-positive result proves that the same productized runner and same generic grouped-reduction primitive can become materially faster when the input has enough independent groups. This is real Step-2 evidence for generic grouped reduction, but it is shape-scoped evidence only.

The remaining technical question is not "does the runner ever work?" It does. The remaining question is whether grouped reduction should be:

1. accepted as a second Step-2 family with a documented shape envelope, or
2. redesigned with a row-parallel/tiled grouped-reduction kernel so low-group-count workloads also benefit.

## Non-Authorization

This report does not authorize:

- V3 release
- all-app run
- paid POD
- public speedup wording
- broad V3-over-V2 claim
- true zero-copy claim
- V4, embedding, or C ABI work

## Goal-Level Decision Audit

Decision: run one bounded free-local shape experiment at `262144` rows and `65536` groups after identifying the launch-shape root cause.

1. Was I foolish? No.
2. If yes, what actions made the decision foolish? The foolish path would have been to blindly run `1048576/1024` or `262144/64`, because source inspection showed both fail to increase launch occupancy.
3. Was there another path that would avoid being stuck? Yes. Directly abandon grouped reduction and switch Step-2 family, but that would discard a fixable, generic runtime signal before testing the actual launch hypothesis.
4. Can I now try a different path that actually solves the problem? Yes. M42 now supports either accepting a shape-scoped grouped-reduction envelope or implementing a row-parallel/tiled generic grouped-reduction kernel for low-group-count shapes. Paid POD remains blocked until external review authorizes a next step.

