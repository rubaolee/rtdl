# Goal5164 - X-HD Post-Goal5163 Three-Sample Matrix Result

## Verdict

`completed_post_goal5163_three_sample_matrix`

## What Changed

Goal5164 records a single same-POD matrix for the current post-Goal5163 route
across the available Stanford graphics representative samples:

```text
sample256
sample1024
sample2048
```

This is a performance/profile evidence goal, not a new algorithmic change.

## POD Command

```text
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py \
  --author-bin /tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec \
  --cases sample256,sample1024,sample2048 \
  --backend optix \
  --grid-shape 8,8,8 \
  --rtdl-repeat-count 5 \
  --validation-mode author-only \
  --summary Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_2048_post_goal5163_matrix_pod.json
```

## Evidence File

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_2048_post_goal5163_matrix_pod.json
```

## Results

```text
sample256:
  matched = true
  author Running.AvgTime = 3.991 ms
  RTDL route median = 0.009128741919994354 s
  RTDL total median = 0.011155426502227783 s

sample1024:
  matched = true
  author Running.AvgTime = 4.032 ms
  RTDL route median = 0.025217324495315552 s
  RTDL total median = 0.039307110011577606 s

sample2048:
  matched = true
  author Running.AvgTime = 4.13 ms
  RTDL route median = 0.025157354772090912 s
  RTDL total median = 0.03893127292394638 s
```

All cases use:

```text
validation_mode = author-only
ratios_authorized = false
```

## Phase Notes

The current route is now balanced enough that no single old bottleneck should be
assumed without fresh measurement. In this run:

```text
sample2048 A->B:
  grid = 0.004825495183467865 s
  seed = 0.0033776387572288513 s
  frontier = 0.0030123665928840637 s
  continuation = 0.001191161572933197 s

sample2048 B->A:
  grid = 0.004387497901916504 s
  seed = 0.0028305351734161377 s
  frontier = 0.0026656687259674072 s
  continuation = 0.0011254101991653442 s
```

## Interpretation

Goal5164 is the current route-performance lock point after the Goal5157-5163
optimization sequence. It confirms the current route remains author-matched on
sample256/sample1024/sample2048, and it preserves the phase-boundary discipline:
the matrix does not report author-vs-RTDL speedup or parity ratios.

## Claim Boundary

This goal does not claim:

- exact paper dataset reproduction;
- full X-HD paper reproduction;
- author `Running.AvgTime` parity;
- denominator-aligned author-vs-RTDL speedup;
- native fused X-HD RT-core equivalence;
- whole-program performance reproduction.

It claims only a same-POD representative performance/profile matrix for the
current post-Goal5163 RTDL route.
