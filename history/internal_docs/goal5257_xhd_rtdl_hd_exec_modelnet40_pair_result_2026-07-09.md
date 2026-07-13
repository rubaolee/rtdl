# Goal5257 - X-HD RTDL hd_exec Entrypoint on ModelNet40 OFF Pair

Date: 2026-07-09

## Objective

Move the new RTDL `hd_exec`-compatible entrypoint beyond bounded WKT smoke tests
by running it on a real public ModelNet40 OFF pair from the X-HD paper-branch
log index.

This goal validates the user-facing entrypoint on a representative public
3-D mesh workload. It is still not exact paper byte-input identity and not
Figure reproduction.

## Workload

Selected pair from the all-400 ModelNet40 evidence:

```text
case_name = 0000_airplane_0036__airplane_0515
input1 = ModelNet40/airplane/train/airplane_0036.off
input2 = ModelNet40/airplane/train/airplane_0515.off
source vertices = 370568
target vertices = 376741
author rerun HDResult = 0.09761668741703033
```

Preprocessing:

```text
normalize_each_input_to_author_float32_unit_box
```

This matches the ModelNet40 route contract used by Goals5252-5253.

## POD Commands

Exact-witness route:

```text
cd /tmp/rtdl_goal5236
export PYTHONPATH=src:.
export LD_LIBRARY_PATH=build:${LD_LIBRARY_PATH:-}
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py \
  -input1 /tmp/xhd-modelnet40/extracted/ModelNet40/airplane/train/airplane_0036.off \
  -input2 /tmp/xhd-modelnet40/extracted/ModelNet40/airplane/train/airplane_0515.off \
  -n_dims 3 \
  -input_type off \
  -variant rt \
  -execution gpu \
  -json /tmp/xhd_goal5257_modelnet40_airplane_0036_0515_exact_witness.json \
  --rtdl-route cell-mbr-exact-witness \
  --normalize-each-input-to-author-unit-box \
  --author-float32-normalization \
  --grid-shape 96,60,72
```

Fast-scalar route:

```text
cd /tmp/rtdl_goal5236
export PYTHONPATH=src:.
export LD_LIBRARY_PATH=build:${LD_LIBRARY_PATH:-}
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py \
  -input1 /tmp/xhd-modelnet40/extracted/ModelNet40/airplane/train/airplane_0036.off \
  -input2 /tmp/xhd-modelnet40/extracted/ModelNet40/airplane/train/airplane_0515.off \
  -n_dims 3 \
  -input_type off \
  -variant rt \
  -execution gpu \
  -json /tmp/xhd_goal5257_modelnet40_airplane_0036_0515_fast_scalar.json \
  --rtdl-route cell-mbr-fast-scalar \
  --normalize-each-input-to-author-unit-box \
  --author-float32-normalization \
  --grid-shape 96,60,72
```

## Evidence Artifacts

Downloaded POD JSON:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5257_modelnet40_airplane_0036_0515_exact_witness_hd_exec_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5257_modelnet40_airplane_0036_0515_fast_scalar_hd_exec_pod.json
```

## Results

Exact-witness route:

```text
HDResult = 0.09761668669590366
author_abs_diff = 7.211266722650933e-10
route_label = cell-mbr-exact-witness
per_source_witness_exact = true
Running.AvgTime = 706.7185416817665 ms
```

Fast-scalar route:

```text
HDResult = 0.09761668669590366
author_abs_diff = 7.211266722650933e-10
route_label = cell-mbr-fast-scalar
per_source_witness_exact = false
Running.AvgTime = 678.3381029963493 ms
```

Both routes match the author rerun value within the established 1e-6 tolerance.

The distinction is important:

```text
cell-mbr-fast-scalar:
  scalar HDResult route; per-source witness not exact on this ModelNet40 pair

cell-mbr-exact-witness:
  functionally fuller route; per-source witness exact under the selected route
```

## Validation

Artifact test:

```text
py -m unittest tests.goal5257_xhd_rtdl_hd_exec_modelnet40_pod_artifact_test
```

Assertions:

```text
HDResult matches author rerun tolerance
input_type = off
n_dims = 3
point counts = 370568 / 376741
preprocessing = normalize_each_input_to_author_float32_unit_box
route labels are distinct
per_source_witness_exact differs as expected
claim-boundary flags remain false
```

## Claim Boundary

Allowed claim:

```text
The RTDL hd_exec-compatible entrypoint ran a real public ModelNet40 OFF pair on
a live GPU POD and matched the corresponding author rerun HDResult for both the
fast scalar and exact-witness route labels.
```

Forbidden claims:

```text
this proves exact paper byte-input identity
this proves all ModelNet40 via the hd_exec-compatible entrypoint
this proves Figure reproduction
this proves author RT-core algorithm equivalence
this proves performance parity or speedup
```

## Status

```text
implemented_review_pending
```

## Next Recommended Work

1. Send Goal5257 with Goals5255-5256 for strict review as the current
   user-facing X-HD app entrypoint packet.
2. If accepted, decide whether to rerun all-400 through the `hd_exec`-compatible
   wrapper or treat Goals5252-5254 as the bulk evidence and Goal5257 as the user
   entrypoint bridge.
3. Continue performance/algorithm gap work separately from app-entrypoint work.
