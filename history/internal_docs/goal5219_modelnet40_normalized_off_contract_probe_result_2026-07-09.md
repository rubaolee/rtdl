# Goal5219 ModelNet40 Normalized OFF Contract Probe Result

Date: 2026-07-09

## Verdict

```text
completed_modelnet40_normalized_off_contract_probe__one_pair_matches_paper_log_and_rtdl_route
```

## Purpose

Goal5218 proved that the official public ModelNet40 raw OFF files are
count-compatible with one author paper-branch pair, but raw coordinates do not
match the paper log:

```text
paper-branch HDResult                  = 0.22594279050827026
author hd_exec on public raw OFF        = 1115.2059326171875
```

The Goal5218 next recommendation was to inspect the author preprocessing
contract. The paper-branch log for the selected pair recorded
`Input.Normalize=true`, while the raw probe had used the default
`Normalize=false`.

Goal5219 tests whether:

```text
official public raw ModelNet40 OFF + author NormalizePoints transform
```

reproduces the author paper-branch log for the selected pair, and whether the
RTDL generic route can consume the same app-owned normalized OFF input.

## Selected Pair

From the paper-branch log index:

```text
category = ModelNet40
input1 = /local/storage/shared/HDDatasets/ModelNet40/glass_box/train/glass_box_0115.off
input2 = /local/storage/shared/HDDatasets/ModelNet40/glass_box/train/glass_box_0081.off
paper-branch point counts = [1107, 1200]
paper-branch HDResult = 0.22594279050827026
paper-branch Input.Normalize = true
paper-branch Input.Translate = 0.0
paper-branch Input.Type = Float
```

Public files from the official Princeton archive:

```text
ModelNet40/glass_box/train/glass_box_0115.off
ModelNet40/glass_box/train/glass_box_0081.off
```

Raw public file hashes, from Goal5218:

```text
glass_box_0115.off SHA256 = 6a6d23cb9619c32f0c6a17082b450452f13facade3a998ed676de948c53a1b5f
glass_box_0081.off SHA256 = d35c49cc061f73ec0211bd65c69177599a269300d1b915db1f9a36e523405048
```

The archive remains POD-local only:

```text
/tmp/xhd-modelnet40/ModelNet40.zip
```

It is not committed into the repository.

## Author Normalize Contract

The author binary exposes an official gflags option:

```text
-normalize (Normalize points to [0, 1]) type: bool default: false
```

Source inspection:

```text
src/flags.cc: DEFINE_bool(normalize, false, "Normalize points to [0, 1]");
src/main.cpp: config.normalize = FLAGS_normalize;
src/run_hausdorff_distance.cu: if (config.normalize) NormalizePoints(points_a); NormalizePoints(points_b);
```

The transform in `src/loaders/translate_points.h` is:

```text
for each input independently:
  lower = per-axis lower bound
  max_extent = max(axis extents)
  point[axis] = (point[axis] - lower[axis]) / max_extent
```

This is not a generic RTDL core primitive. For the RTDL route, it is implemented
as app-owned input provenance handling in:

```text
Paper-reproduction-apps/x-hd-paper/scripts/xhd_input_loader.py
```

## Author Normalized Probe

Command shape:

```text
hd_exec
  -input1 /tmp/xhd-modelnet40/extracted/ModelNet40/glass_box/train/glass_box_0115.off
  -input2 /tmp/xhd-modelnet40/extracted/ModelNet40/glass_box/train/glass_box_0081.off
  -n_dims 3
  -input_type off
  -variant rt
  -execution gpu
  -normalize=true
  -json ...
  -overwrite=true
  -check=false
  -repeat=1
```

Downloaded author artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5219_modelnet40_glass_box_author_normalized_probe_2026-07-09.json
```

Observed:

```text
author normalized HDResult = 0.22594279050827026
author Running.AvgTime = 4.292 ms
Input.Normalize = true
Input.Type = Float
Input.Translate = 0.0
Input counts = [1107, 1200]
```

Comparison:

```text
paper-branch log HDResult      = 0.22594279050827026
author normalized HDResult     = 0.22594279050827026
absolute difference            = 0.0
```

Normalized MBRs also match the paper-branch log values:

```text
file1:
  x [0.0, 0.5865572094917297]
  y [0.0, 1.0]
  z [0.0, 0.27818214893341064]

file2:
  x [0.0, 0.8333333134651184]
  y [0.0, 1.0]
  z [0.0, 0.3683861196041107]
```

## RTDL Normalized OFF Route Probe

Goal5219 added app-owned OFF input support and the author-compatible normalize
transform to the X-HD paper app input bridge. RTDL core remains unchanged and
still consumes generic NumPy coordinate matrices.

Local tests:

```text
py -m unittest tests.goal5219_xhd_off_normalize_input_contract_test
Ran 4 tests OK

py -m unittest tests.goal5203_numpy_point_matrix_input_loader_test \
  tests.goal5205_fast_ascii_ply_matrix_loader_test \
  tests.goal5133_xhd_ply_input_bridge_test
Ran 14 tests OK
```

POD RTDL route artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5219_modelnet40_glass_box_rtdl_normalized_route_summary_2026-07-09.json
```

Route:

```text
input_type = off
reference_preprocessing = ["normalize_each_input_to_author_unit_box"]
backend = optix
direction_mode = directed-a-to-b
validation_mode = exact-and-author
tolerance = 1e-6
```

Observed:

```text
RTDL route directed_a_to_b = 0.22594284338858983
RTDL exact reference       = 0.22594284338858983
author normalized HDResult = 0.22594279050827026
RTDL exact abs diff        = 0.0
RTDL vs author abs diff    = 5.288031956762751e-08
matched                    = true
```

The small RTDL-vs-author difference is expected under the current route:
author runs with `Input.Type=Float`, while the RTDL app bridge stores the
normalized coordinate matrix as float64. The route uses the already established
`1e-6` bounded-comparison tolerance.

## Interpretation

Goal5219 overturns the raw-OFF negative hypothesis from Goal5218 in a precise
way:

```text
public raw OFF alone: does not match paper log
public raw OFF + author NormalizePoints: matches paper log for this pair
```

For this one selected ModelNet40 pair, the official public raw OFF files plus
the author `-normalize=true` preprocessing contract reproduce the paper-branch
HDResult and logged MBRs. The RTDL generic route also matches the normalized
author run within the float-author tolerance.

## What This Proves

```text
The author preprocessing contract for this ModelNet40 pair is now identified:
  -normalize=true, with per-input lower-bound subtraction and max-extent scale.

The official public ModelNet40 raw OFF files plus that transform reproduce
the paper-branch author HDResult for glass_box_0115 -> glass_box_0081.

The X-HD paper app can now load OFF vertices and apply the same app-owned
normalize transform before invoking generic RTDL nearest/frontier/reduction
APIs.

The RTDL route matches the transformed author run for this one pair under the
existing float-author tolerance.
```

## What This Does Not Prove

```text
full X-HD paper reproduction;
all ModelNet40 paper pairs reproduced;
all ModelNet40 public raw OFF files are sufficient;
BraTS/geospatial/Stanford exact paper input identity;
author-vs-RTDL performance ratio;
author fused RT-core algorithm reproduction;
exact per-source witness equivalence beyond the route metadata;
byte-identical paper input files or hashes.
```

## Claim Boundary

Allowed:

```text
For one ModelNet40 paper-branch pair, official public raw OFF plus the author
NormalizePoints transform reproduces the author paper-branch HDResult and MBRs;
the RTDL generic route matches the same normalized author result within
float-author tolerance.
```

Not authorized:

```text
ModelNet40 full reproduction complete;
public raw OFF equals paper input without preprocessing;
all ModelNet40 pairs reproduce;
exact paper dataset identity proved;
author performance parity;
author-vs-RTDL ratio;
X-HD RT-core algorithm fully reproduced.
```

## Next Recommendation

The next step should validate this transform beyond one pair:

```text
Goal5220: run the same author-normalized + RTDL-normalized route gate over a
small representative batch of ModelNet40 paper-branch pairs, preferably across
multiple categories and including the same paper-log fields: HDResult, point
counts, Normalize flag, Type, Translate, and MBRs.
```

If the batch matches, ModelNet40 can be promoted from "raw public data mismatch"
to "public raw data plus author normalize contract is a strong Level-C
candidate." If it fails, keep ModelNet40 at "one pair reconstructed; broader
preprocessing/provenance still unresolved."
