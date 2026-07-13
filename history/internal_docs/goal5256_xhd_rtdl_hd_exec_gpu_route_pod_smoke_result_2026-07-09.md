# Goal5256 - X-HD RTDL hd_exec Entrypoint GPU Route POD Smoke

Date: 2026-07-09

## Objective

Validate that the Goal5255 user-facing RTDL `hd_exec`-compatible entrypoint is
not merely a CPU/reference wrapper. It must run the actual 3-D GPU RTDL route
labels through the same author-style CLI and produce author-shaped JSON.

This is a smoke/execution proof, not a performance claim.

## POD

Preflight:

```text
POD_OK
45c502cfccb5
NVIDIA RTX 4000 Ada Generation, 550.127.05
```

Remote worktree:

```text
/tmp/rtdl_goal5236
```

The remote worktree already had `build/librtdl_optix.so`. A minimal tarball was
uploaded containing the new runner, current X-HD app scripts, and bounded
fixtures.

## Commands

Exact-witness route:

```text
cd /tmp/rtdl_goal5236
export PYTHONPATH=src:.
export LD_LIBRARY_PATH=build:${LD_LIBRARY_PATH:-}
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py \
  -input1 Paper-reproduction-apps/x-hd-paper/data/fixtures/bounded3d_a.wkt \
  -input2 Paper-reproduction-apps/x-hd-paper/data/fixtures/bounded3d_b.wkt \
  -n_dims 3 \
  -input_type wkt \
  -variant rt \
  -execution gpu \
  -json /tmp/xhd_goal5256_bounded3d_exact_witness.json \
  --rtdl-route cell-mbr-exact-witness \
  --grid-shape 2,1,1
```

Fast-scalar route:

```text
cd /tmp/rtdl_goal5236
export PYTHONPATH=src:.
export LD_LIBRARY_PATH=build:${LD_LIBRARY_PATH:-}
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py \
  -input1 Paper-reproduction-apps/x-hd-paper/data/fixtures/bounded3d_a.wkt \
  -input2 Paper-reproduction-apps/x-hd-paper/data/fixtures/bounded3d_b.wkt \
  -n_dims 3 \
  -input_type wkt \
  -variant rt \
  -execution gpu \
  -json /tmp/xhd_goal5256_bounded3d_fast_scalar.json \
  --rtdl-route cell-mbr-fast-scalar \
  --grid-shape 2,1,1
```

## Evidence Artifacts

Downloaded POD JSON:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5256_rtdl_hd_exec_bounded3d_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5256_rtdl_hd_exec_bounded3d_fast_scalar_pod.json
```

Summary:

```text
exact-witness:
  HDResult = 2.0
  RTDL.route_label = cell-mbr-exact-witness
  RTDL.route.per_source_witness_exact = true
  Running.Algorithm = RTDL-cell-mbr-exact-witness
  Running.AvgTime = 274.77584034204483 ms

fast-scalar:
  HDResult = 2.0
  RTDL.route_label = cell-mbr-fast-scalar
  RTDL.route.per_source_witness_exact = true on this tiny bounded fixture
  Running.Algorithm = RTDL-cell-mbr-fast-scalar
  Running.AvgTime = 384.3530938029289 ms
```

The fast-scalar route reports exact witnesses on this tiny fixture, but that is
not a general route property. The route label remains the authority:

```text
cell-mbr-fast-scalar != cell-mbr-exact-witness
```

## Validation

Local artifact tests:

```text
py -m unittest tests.goal5256_xhd_rtdl_hd_exec_pod_artifact_test
```

Expected assertions:

```text
HDResult fields are present
Running.Algorithm route labels are present
RTDL.route_label values are distinct
claim-boundary flags remain false
```

Broader related validation after Goal5255:

```text
py -m unittest \
  tests.goal5255_xhd_rtdl_hd_exec_entrypoint_test \
  tests.goal5115_xhd_rtdl_route_gate_test \
  tests.goal5118_xhd_bounded3d_rtdl_route_gate_test \
  tests.goal5223_modelnet40_algorithm_aware_comparator_test
```

Result:

```text
Ran 20 tests
OK
```

## Claim Boundary

Allowed claim:

```text
The RTDL hd_exec-compatible X-HD entrypoint runs both bounded 3-D GPU route
labels on a POD and writes author-shaped HDResult / Running JSON with explicit
RTDL route metadata.
```

Forbidden claims:

```text
full X-HD paper reproduction is complete
the author RT-core algorithm has been reimplemented
the POD timings prove performance parity or speedup
the tiny bounded fixture represents ModelNet40 or full public paper data
cell-mbr-fast-scalar is generally exact-witness just because this tiny fixture
reported per_source_witness_exact=true
```

## Status

```text
implemented_review_pending
```

## Next Recommended Work

1. Send Goal5255 and Goal5256 together for strict review.
2. If accepted, use `run_xhd_rtdl_hd_exec.py` as the public X-HD paper app
   entrypoint while keeping route labels mandatory.
3. Continue algorithm/performance work separately under the route-label matrix.
