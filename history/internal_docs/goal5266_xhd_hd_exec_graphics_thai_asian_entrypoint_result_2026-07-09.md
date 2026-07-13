# Goal5266 - X-HD hd_exec Graphics ThaiStatuette -> AsianDragon Entrypoint Result

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

## Goal

Extend the user-facing RTDL `hd_exec`-compatible X-HD entrypoint evidence to the
remaining Stanford Graphics representative pair:

```text
ThaiStatuette scaled 1e-3 -> AsianDragon scaled 1e-3
```

This goal is intentionally bounded. It does not claim exact paper byte-input
identity, full paper reproduction, author RT-core algorithm equivalence, or
performance parity.

## Inputs

```text
input1 = Paper-reproduction-apps/x-hd-paper/data/external/stanford/thai_statuette_scaled_1e-3.ply
input2 = Paper-reproduction-apps/x-hd-paper/data/external/stanford/asian_dragon_scaled_1e-3.ply
n_dims = 3
input_type = ply
variant = rt
execution = gpu
preprocessing = translate_each_input_to_min_bound
```

The ThaiStatuette scaled source was prepared in Goal5265 from the public
Stanford XYZRGB source with an app-owned `1e-3` scale factor. AsianDragon scaled
1e-3 was prepared earlier in the Dragon -> AsianDragon line.

## Author hd_exec Rerun

Command, on POD:

```bash
/tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec \
  -input1 Paper-reproduction-apps/x-hd-paper/data/external/stanford/thai_statuette_scaled_1e-3.ply \
  -input2 Paper-reproduction-apps/x-hd-paper/data/external/stanford/asian_dragon_scaled_1e-3.ply \
  -n_dims 3 -input_type ply -variant rt -execution gpu \
  -json /tmp/xhd_goal5266_author_thai_asian_scaled_rt_gpu.json \
  -overwrite=true -check=false
```

Result:

```text
author HDResult = 0.28763842582702637
author Running.AvgTime = 18.864 ms
point_count_a = 4999996
point_count_b = 3609600
```

Paper-branch log target:

```text
paper log HDResult = 0.28763845562934875
abs(author rerun - paper log) ~= 2.98e-8
```

This close author-rerun/paper-log agreement supports the same-source/scaled
candidate interpretation. It still does not prove byte-identical paper inputs.

## RTDL hd_exec-Compatible Entrypoint

Command, on POD:

```bash
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py \
  -input1 Paper-reproduction-apps/x-hd-paper/data/external/stanford/thai_statuette_scaled_1e-3.ply \
  -input2 Paper-reproduction-apps/x-hd-paper/data/external/stanford/asian_dragon_scaled_1e-3.ply \
  -n_dims 3 -input_type ply -variant rt -execution gpu \
  -json /tmp/xhd_goal5266_thai_asian_hd_exec_exact_witness.json \
  --rtdl-route cell-mbr-exact-witness \
  --grid-shape 32,32,32 \
  --max-inline-points 512 \
  --translate-each-input-to-min-bound
```

Result:

```text
RTDL HDResult = 0.2876384148709406
abs(RTDL - author rerun) ~= 1.10e-8
abs(RTDL - paper log) ~= 4.08e-8
per_source_witness_exact = true
RTDL route wall = 10770.015 ms
RTDL entrypoint total wall = 11779.664 ms
```

Dominant recorded phases:

```text
load_input_sec = 0.4693
rtdl_route_sec = 10.7700
total_sec = 11.7779
```

The route is exact-witness and matches the author rerun within the existing
1e-6 X-HD bounded tolerance. The route wall is not comparable to author
`Running.AvgTime` as a performance parity claim because RTDL is running a
generic exact-witness route, not the author's fused X-HD RT-core algorithm.

## Artifacts

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5266_author_thai_asian_scaled_rt_gpu_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5266_thai_asian_hd_exec_exact_witness_pod.json
```

## Files Updated

```text
tests/goal5266_xhd_hd_exec_graphics_thai_asian_pod_artifact_test.py
Paper-reproduction-apps/x-hd-paper/README.md
Paper-reproduction-apps/x-hd-paper/data/manifest.json
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
history/internal_docs/xhd_current_status_after_goal5266_2026-07-09.md
```

## Claim Boundary

Authorized:

```text
Goal5266 adds a same-source/scaled Stanford Graphics ThaiStatuette ->
AsianDragon gate through the RTDL hd_exec-compatible entrypoint. The RTDL
cell-mbr-exact-witness route matches the author rerun HDResult within 1e-6 and
preserves per_source_witness_exact=true.
```

Not authorized:

```text
full X-HD paper reproduction
exact paper byte-input identity
author RT-core algorithm equivalence
author performance parity or speedup
paper Figure 5-11 reproduction
claiming scaled public candidates are the exact paper inputs
```

## Next Recommended Work

At the entrypoint-evidence level, the immediate graphics representative set now
covers Dragon -> HappyBuddha, Dragon -> AsianDragon, ThaiStatuette ->
HappyBuddha, and ThaiStatuette -> AsianDragon. The next major full-paper
blocker is no longer another wrapper gate, but the harder gap:

```text
author RT-core algorithm equivalence and fair full-paper performance/figure
reproduction under exact dataset provenance.
```
