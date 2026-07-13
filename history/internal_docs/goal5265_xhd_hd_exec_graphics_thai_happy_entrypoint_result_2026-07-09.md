# Goal5265 - X-HD hd_exec Entrypoint Graphics ThaiStatuette/HappyBuddha Result

Date: 2026-07-09

## Objective

Extend the X-HD paper app's `hd_exec`-compatible RTDL entrypoint to another
paper graphics pair:

```text
ThaiStatuette -> HappyBuddha
```

This goal also acquires and scales the public Stanford XYZRGB ThaiStatuette
candidate so its coordinate scale matches the author paper-branch graphics logs.

## Source Acquisition And Scaling

Public source:

```text
url = https://graphics.stanford.edu/data/3Dscanrep/xyzrgb/xyzrgb_statuette.ply.gz
archive = Paper-reproduction-apps/x-hd-paper/data/external/stanford/xyzrgb_statuette.ply.gz
archive_bytes = 106051627
archive_sha256 = 1D867B6540C02935CAA777BD6746429A62D4A5D23F11C9BFDFEBBAA90C05CA8B
```

Extracted PLY:

```text
file = Paper-reproduction-apps/x-hd-paper/data/external/stanford/thai_statuette.ply
vertex_count = 4999996
face_count = 10000000
bytes = 190000131
sha256 = 01470DA9FC1241DCB4B075CC057FF6BF88D8DC721CE24B5847B9EFDFBB8C0345
```

The raw extracted coordinate extents are about `235 / 396 / 203`, while the
paper-branch author log for `thai_statuette.ply` records MBR upper bounds around
`0.235 / 0.396 / 0.203`. Goal5265 therefore prepares an app-owned scaled
candidate:

```text
script = Paper-reproduction-apps/x-hd-paper/scripts/prepare_xhd_scaled_ply_candidate.py
scale = 0.001
output = Paper-reproduction-apps/x-hd-paper/data/external/stanford/thai_statuette_scaled_1e-3.ply
output_bytes = 60000124
output_sha256 = 047024CF12FC541634D02612F0D72EA03EF9BABB8239F4CA6A1A6A9422DA272E
coordinate_extents_after_scale = [0.2352239456176758, 0.39604121398925785, 0.20316127014160157]
```

Scaling artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5265_thai_statuette_scaled_1e-3_candidate_summary_2026-07-09.json
```

## Author Comparator

Paper-branch log target:

```text
file_pair = thai_statuette.ply -> happy_buddha.ply
paper_log_HDResult = 0.21912434697151184
paper_log_counts = 4999996 / 543652
```

POD author run:

```text
author_bin = /tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec
input1 = thai_statuette_scaled_1e-3.ply
input2 = happy_recon/happy_vrip.ply
n_dims = 3
input_type = ply
variant = rt
execution = gpu
```

Author result:

```text
author_HDResult = 0.21912431716918945
author_abs_diff_vs_paper_log ~= 2.98e-8
author Running.AvgTime = 26.664 ms
author point counts = 4999996 / 543652
```

Author artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5265_author_thai_happy_scaled_rt_gpu_pod.json
```

## RTDL hd_exec-Compatible Route

Command:

```text
cd /tmp/rtdl_goal5236
export PYTHONPATH=src:.
export LD_LIBRARY_PATH=build:${LD_LIBRARY_PATH:-}
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py \
  -input1 Paper-reproduction-apps/x-hd-paper/data/external/stanford/thai_statuette_scaled_1e-3.ply \
  -input2 Paper-reproduction-apps/x-hd-paper/data/external/stanford/happy_recon/happy_vrip.ply \
  -n_dims 3 \
  -input_type ply \
  -variant rt \
  -execution gpu \
  -json /tmp/xhd_goal5265_thai_happy_hd_exec_exact_witness.json \
  --rtdl-route cell-mbr-exact-witness \
  --grid-shape 32,32,32 \
  --max-inline-points 512 \
  --translate-each-input-to-min-bound
```

Downloaded artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5265_thai_happy_hd_exec_exact_witness_pod.json
```

Result:

```text
RTDL HDResult = 0.2191243235042005
abs(RTDL - author rerun) ~= 6.34e-9
abs(RTDL - paper log) ~= 2.35e-8
matched author rerun within 1e-6 = true
point_count_a = 4999996
point_count_b = 543652
preprocessing = translate_each_input_to_min_bound
per_source_witness_exact = true
RTDL route wall = 5013.226099312305 ms
entrypoint total = 6.01855493336916 s
```

Dominant RTDL phase:

```text
initial_state_seed = 4.743512146174908 s
grid_cell_mbrs = 0.21363436430692673 s
nearest_continuation = 0.011145025491714478 s
max_nearest_reduction = 0.016311869025230408 s
```

## What This Proves

This proves that the RTDL `hd_exec`-compatible user entrypoint can run the
ThaiStatuette -> HappyBuddha graphics paper pair as a Level-B same-source /
scaled candidate and match both:

```text
author rerun HDResult within 1e-6
paper-branch log HDResult within 1e-6
```

It also proves the route is exact-witness for this gate:

```text
per_source_witness_exact = true
```

## What This Does Not Prove

This does not prove:

```text
exact paper byte-input identity
full X-HD paper reproduction
Figure 5-11 reproduction
author RT-core algorithm equivalence
author performance parity or speedup
same-source/scaled public candidate = exact paper dataset
```

The ThaiStatuette `1e-3` scaling is an app-owned Level-B reconstruction step.
It aligns the public source with the paper-log coordinate scale, but exact
paper identity would require author-provided bytes/hashes or a documented
deterministic conversion path.

## Validation

```text
py -m unittest tests.goal5265_xhd_hd_exec_graphics_thai_happy_pod_artifact_test
```

Expected assertions:

```text
scaled Thai candidate records source/output SHA, vertex count, and extents
author and RTDL HDResult match within 1e-6
RTDL exact-witness route reports per_source_witness_exact=true
README / manifest / Stanford data README record evidence without overclaim
claim-boundary flags remain false
```

## Status

```text
implemented_review_pending
```

## Next Recommended Work

1. Send Goal5265 for strict review, or fold it into the Goals5255-5265
   user-entrypoint review packet.
2. If accepted, the RTDL `hd_exec`-compatible entrypoint has now covered:
   ModelNet40 all-400, Dragon -> HappyBuddha, Dragon -> AsianDragon, and
   ThaiStatuette -> HappyBuddha.
3. Continue the remaining full-paper blockers: exact paper byte-input identity,
   remaining graphics/geospatial/MRI workloads, paper Figures 5-11, and author
   internal AvgTime algorithm gap.
