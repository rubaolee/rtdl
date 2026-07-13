# Goal5156 - X-HD Route Phase Median Profile Result

## Verdict

`completed_seeded_route_repeat_phase_median_profile`

## What Changed

Goal5156 strengthens the Goal5155 route profile from last-run-only timings to
repeat-level phase evidence. The performance matrix now records, for each case
and each directed route:

```text
phase_timings_sec_runs
phase_timings_sec_median
```

for the existing route phases:

```text
source_columns
target_columns
grid_cell_mbrs
initial_state_seed
radius_selection
frontier_rows
nearest_continuation
max_nearest_reduction
direction_total
```

This makes bottleneck selection median-based across repeats rather than dependent
on whichever run happens to be last.

## Files Changed

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_production_author_only_median_profile_pod.json
Paper-reproduction-apps/x-hd-paper/data/manifest.json
tests/goal5156_xhd_route_phase_median_profile_test.py
```

## POD Command

```text
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py \
  --author-bin /tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec \
  --cases sample256,sample1024 \
  --backend optix \
  --grid-shape 8,8,8 \
  --rtdl-repeat-count 5 \
  --validation-mode author-only \
  --summary Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_production_author_only_median_profile_pod.json
```

POD:

```text
host = 213.173.108.24
port = 13502
gpu = NVIDIA RTX 4000 Ada Generation, 550.127.05
```

## Evidence File

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_production_author_only_median_profile_pod.json
```

## Results

### sample256

```text
matched = true
author Running.AvgTime = 4.155 ms
RTDL route median = 0.0379673168063164 s
RTDL total median = 0.0399764478206635 s
validation_mode = author-only
ratios_authorized = false
```

Median route profile:

```text
A->B seed = 0.00638055056333542 s
A->B frontier = 0.00451542437076569 s
A->B nearest continuation = 0.00802277773618698 s
A->B direction total = 0.0215792879462242 s

B->A seed = 0.00627332180738449 s
B->A frontier = 0.00265301018953323 s
B->A nearest continuation = 0.00486644357442856 s
B->A direction total = 0.0163432210683823 s
```

### sample1024

```text
matched = true
author Running.AvgTime = 4.046 ms
RTDL route median = 0.288512669503689 s
RTDL total median = 0.296023562550545 s
validation_mode = author-only
ratios_authorized = false
```

Median route profile:

```text
A->B seed = 0.0491514652967453 s
A->B frontier = 0.0380633175373077 s
A->B nearest continuation = 0.0801987573504448 s
A->B direction total = 0.174023665487766 s

B->A seed = 0.0427372008562088 s
B->A frontier = 0.0118727460503578 s
B->A nearest continuation = 0.0552233085036278 s
B->A direction total = 0.114369101822376 s
```

## Interpretation

The median profile changes the next-target decision:

```text
sample1024 continuation median total ~= 0.1354 s
sample1024 seed median total         ~= 0.0919 s
sample1024 frontier median total     ~= 0.0499 s
```

So the largest remaining route cost is not the native OptiX frontier producer.
It is the partner-side nearest continuation, followed by the nearest-cell-MBR
seed selection. The native frontier is still nontrivial, but it is the third
largest measured phase in this route.

This means the next performance work should target one of:

1. a more compiled/device-resident nearest-witness continuation over frontier
   rows;
2. a more compiled/device-resident nearest-cell-MBR seed;
3. a route design that avoids producing/consuming so many frontier rows before
   nearest continuation.

## Validation

Local:

```text
py -m json.tool Paper-reproduction-apps/x-hd-paper/data/manifest.json
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_production_author_only_median_profile_pod.json
py -m unittest tests.goal5156_xhd_route_phase_median_profile_test \
  tests.goal5155_xhd_production_validation_and_route_profile_test \
  tests.goal5154_xhd_seeded_performance_matrix_test
Ran 7 tests OK
```

POD:

```text
python3 -m unittest tests.goal5156_xhd_route_phase_median_profile_test \
  tests.goal5155_xhd_production_validation_and_route_profile_test
Ran 5 tests OK (skipped=1 before artifact generation)
```

## Claim Boundary

This goal does not claim:

- exact paper dataset reproduction;
- full X-HD paper reproduction;
- author `Running.AvgTime` parity;
- speedup;
- denominator-aligned author-vs-RTDL ratio;
- that median profiling alone improves runtime.

It provides stable bottleneck evidence for the current representative seeded
RTDL route.
