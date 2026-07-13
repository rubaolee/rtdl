# Goal5154 - X-HD Seeded Performance Matrix Result

## Verdict

`completed_seeded_sample256_1024_performance_matrix_phase_separated`

## What Changed

Goal5154 adds a same-POD performance matrix runner:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py
```

It runs, for each case:

1. author `hd_exec -variant rt -execution gpu`;
2. RTDL seeded cell-MBR frontier route with `backend=optix`;
3. three RTDL route repeats;
4. phase-separated output:
   - author `Running.AvgTime`;
   - author process wall time;
   - author iteration RT/CUDA summaries;
   - RTDL load input time;
   - RTDL exact-reference check time;
   - RTDL route time;
   - RTDL total time.

It intentionally does **not** report a speedup/parity ratio, because these phase
boundaries are not identical.

## POD Command

```text
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py \
  --author-bin /tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec \
  --cases sample256,sample1024 \
  --backend optix \
  --grid-shape 8,8,8 \
  --rtdl-repeat-count 3 \
  --summary Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_performance_matrix_pod.json
```

POD:

```text
host = 213.173.108.24
port = 13502
gpu = NVIDIA RTX 4000 Ada Generation, 550.127.05
```

## Evidence File

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_performance_matrix_pod.json
```

## Results

### sample256

Correctness:

```text
matched = true
author HDResult = 0.11612465232610703
RTDL directed A->B = 0.11612464969699586
author_abs_diff = 2.6291111648868437e-09
```

Author:

```text
Running.AvgTime = 4.024 ms
process_wall_sec = 1.1215357333421707
iteration_count = 2
RTTime sum = 2.454 ms
CUDATime sum = 0.112 ms
```

RTDL seeded OptiX route:

```text
route_sec runs = [0.36351171135902405, 0.03888532519340515, 0.03848829120397568]
route_sec median = 0.03888532519340515
load_input_sec median = 0.0016872510313987732
exact_reference_sec median = 0.10457136482000351
total_sec median = 0.14549384266138077
frontier_native_symbol = rtdl_optix_collect_cell_mbr_nearest_frontier_3d
A->B total candidate distance evaluations = 1201
B->A total candidate distance evaluations = 1237
```

### sample1024

Correctness:

```text
matched = true
author HDResult = 0.1215052381157875
RTDL directed A->B = 0.12150523439597159
author_abs_diff = 3.7198159136275777e-09
```

Author:

```text
Running.AvgTime = 4.059 ms
process_wall_sec = 1.075897328555584
iteration_count = 2
RTTime sum = 2.407 ms
CUDATime sum = 0.116 ms
```

RTDL seeded OptiX route:

```text
route_sec runs = [0.31465598940849304, 0.3040360137820244, 0.30438121408224106]
route_sec median = 0.30438121408224106
load_input_sec median = 0.014543220400810242
exact_reference_sec median = 1.6646058484911919
total_sec median = 1.9755493998527527
frontier_native_symbol = rtdl_optix_collect_cell_mbr_nearest_frontier_3d
A->B total candidate distance evaluations = 20256
B->A total candidate distance evaluations = 18971
```

## Interpretation

The matrix is useful precisely because it avoids pretending all timing fields
share a denominator:

- Author `Running.AvgTime` is an internal author algorithm time in milliseconds.
- Author process wall is a full subprocess run around `hd_exec`.
- RTDL `route_sec` is the seeded in-process route.
- RTDL `total_sec` currently includes load/preprocess and exact-reference
  validation.

Therefore no speedup/parity ratio is authorized in this goal.

The performance gap is still large against author `Running.AvgTime`, especially
on sample1024. The current RTDL route is correctness-preserving and work-reduced,
but it still has Python/NumPy seed/continuation components and is not the
author fused RT-core algorithm.

## Validation

Local test:

```text
py -m unittest tests.goal5154_xhd_seeded_performance_matrix_test
```

The test validates:

- schema;
- both cases present;
- both cases matched;
- ratios are null;
- phase fields exist;
- native symbol is the generic cell-MBR frontier symbol.

## Claim Boundary

This goal does not claim:

- exact paper dataset reproduction;
- full X-HD paper reproduction;
- performance parity;
- speedup;
- denominator-aligned author-vs-RTDL ratio.

It provides the first phase-separated representative performance matrix for the
current seeded RTDL route.
