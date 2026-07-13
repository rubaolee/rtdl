# Goal5161 - Numba Nearest-Cell-MBR Seed Result

## Verdict

`completed_numba_nearest_cell_mbr_seed_executor`

## What Changed

Goal5161 adds a generic executor option to:

```text
seed_nearest_witness_from_nearest_cell_mbr_numpy_columns(...)
```

The helper now accepts:

```text
executor: "auto" | "numpy" | "numba" = "auto"
```

Behavior:

- `executor="numpy"` preserves the Goal5158 vectorized NumPy path.
- `executor="numba"` uses a Numba-compiled loop that preserves the same
  nearest-cell and nearest-point tie-breaks.
- `executor="auto"` uses Numba when available and falls back to NumPy otherwise.

The helper remains app-neutral. It does not contain X-HD, paper, author, or
Hausdorff semantics. It computes a generic nearest-state upper bound from each
query point to one point in its nearest non-empty cell MBR.

## Why This Was The Next Target

After Goal5160, the native frontier phase was no longer dominant:

```text
Goal5160 sample1024:
  RTDL route median ~= 0.079s
  seed combined     ~= 0.0585s
  frontier combined ~= 0.0051s
  continuation      ~= 0.0065s
```

So the measured route bottleneck moved back to the nearest-cell-MBR seed.

## Semantics

The Numba executor preserves the existing deterministic layers:

```text
1. choose the cell MBR with smallest lower-bound distance;
2. if tied, choose lower cell_id;
3. inside that chosen cell, choose the closest target point;
4. if tied, choose lower target point id.
```

The existing NumPy path remains available and is used as a parity oracle in the
Goal5161 tests.

## Files Changed

```text
src/rtdsl/partner_continuations.py
tests/goal5158_vectorized_nearest_cell_mbr_seed_test.py
tests/goal5161_numba_nearest_cell_mbr_seed_test.py
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_numba_seed_profile_pod.json
Paper-reproduction-apps/x-hd-paper/data/manifest.json
scripts/current_pod_ssh.py
```

`scripts/current_pod_ssh.py` also gained `upload` and `download` subcommands so
POD file transfer uses the same pinned key and `IdentitiesOnly=yes` discipline
as POD exec/preflight.

## POD Command

```text
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py \
  --author-bin /tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec \
  --cases sample256,sample1024 \
  --backend optix \
  --grid-shape 8,8,8 \
  --rtdl-repeat-count 5 \
  --validation-mode author-only \
  --summary Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_numba_seed_profile_pod.json
```

POD:

```text
host = 213.173.108.24
port = 13502
gpu = NVIDIA RTX 4000 Ada Generation
```

## Evidence File

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_numba_seed_profile_pod.json
```

## Results

### sample256

```text
matched = true
author Running.AvgTime = 4.024 ms
RTDL route median = 0.009549818933010101 s
RTDL total median = 0.011600740253925323 s
validation_mode = author-only
ratios_authorized = false
```

Seed phase:

```text
A->B seed median = 0.00038952380418777466 s
B->A seed median = 0.0003375411033630371 s
selection = numba_loop_min_distance_then_cell_id
```

### sample1024

```text
matched = true
author Running.AvgTime = 4.416 ms
RTDL route median = 0.02210059016942978 s
RTDL total median = 0.028866872191429138 s
validation_mode = author-only
ratios_authorized = false
```

Seed phase:

```text
A->B seed median = 0.0016798824071884155 s
B->A seed median = 0.0013452470302581787 s
selection = numba_loop_min_distance_then_cell_id
```

## Before / After Against Goal5160

The comparable Goal5160 production matrix reported:

```text
sample256 RTDL route median = 0.013508938252925873 s
sample1024 RTDL route median = 0.07889240980148315 s
```

Goal5161 reports:

```text
sample256 RTDL route median = 0.009549818933010101 s
sample1024 RTDL route median = 0.02210059016942978 s
```

So, for the RTDL route itself:

```text
sample256 route improvement ~= 1.41x vs Goal5160
sample1024 route improvement ~= 3.57x vs Goal5160
```

Across the recent production-route optimization line:

```text
Goal5155 sample1024 production route ~= 0.301 s
Goal5157 after continuation vectorization ~= 0.170 s
Goal5158 after seed vectorization ~= 0.114 s
Goal5159 after row-table-only split avoidance ~= 0.108 s
Goal5160 after active-row native emission ~= 0.079 s
Goal5161 after Numba seed executor ~= 0.022 s
```

This is about a 13.6x RTDL-route improvement from Goal5155 to Goal5161 on the
same representative sample1024 route family.

## Interpretation

Goal5161 shows that the post-5160 seed bottleneck was mostly NumPy allocation and
sorting overhead, not unavoidable geometry work. A compiled generic loop can
preserve the deterministic seed semantics while avoiding the large
query-by-cell matrix and expand/lexsort intermediate arrays.

The remaining measured route cost on sample1024 is now dominated by grid
cell-MBR construction plus nearest continuation/frontier work rather than the
seed itself.

This result still does not authorize author-performance parity or a
denominator-aligned speedup ratio. The author `Running.AvgTime`, author process
wall, RTDL route time, and RTDL total time remain different phase boundaries.

## Validation

Local:

```text
py -m unittest tests.goal5161_numba_nearest_cell_mbr_seed_test \
  tests.goal5158_vectorized_nearest_cell_mbr_seed_test \
  tests.goal5152_nearest_cell_mbr_seed_pruning_test
Ran 11 tests OK (skipped=1)
```

POD:

```text
python3 -m unittest tests.goal5161_numba_nearest_cell_mbr_seed_test \
  tests.goal5158_vectorized_nearest_cell_mbr_seed_test \
  tests.goal5152_nearest_cell_mbr_seed_pruning_test
Ran 11 tests OK (skipped=1)
```

## Claim Boundary

This goal does not claim:

- exact paper dataset reproduction;
- full X-HD paper reproduction;
- author `Running.AvgTime` parity;
- denominator-aligned author-vs-RTDL speedup;
- native fused X-HD RT-core equivalence;
- whole-program performance reproduction.

It claims only a generic Numba executor for nearest-cell-MBR seed construction
and measured RTDL-route phase reduction on representative same-source fixtures.
