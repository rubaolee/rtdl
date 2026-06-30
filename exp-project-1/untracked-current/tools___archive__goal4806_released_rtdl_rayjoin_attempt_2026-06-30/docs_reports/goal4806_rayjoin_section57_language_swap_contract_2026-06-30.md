# Goal4806 RayJoin Section 5.7 Language-Swap Contract

Date: 2026-06-30

## Verdict

Yes. For a fair RayJoin Section 5.7 reproduction, the intended change is the
implementation stack:

- author: C++ / CUDA / OptiX
- RTDL reproduction: Python / RTDL / Numba where appropriate / RTDL native OptiX

Everything else that defines the workload should stay the same unless a
difference is explicitly documented and disqualifies the row from a direct
performance comparison.

## What Must Stay The Same

The paper and author code define the polygon overlay workload as:

1. Same CDB inputs and same pair selection.
2. Same Section 5.7 real-world overlay workload.
3. Same runtime parameters:
   - `grid_size=15000`
   - `mode=rt`
   - `xsect_factor=0.1`
   - `enlarge=3.5`
   - `fau`
   - same serialized topology prefix when author code uses one.
4. Same algorithmic stages:
   - load planar graph / CDB maps
   - load packed map data to device
   - build RT index / BVH from base-map line segments
   - run LSI
   - run PIP / point-location for both maps
   - compute output polygon chains
   - write the overlay output
5. Same RT formulation:
   - LSI: query line segment becomes a ray over `[tmin, tmax] = [0, 1]`.
   - PIP: query point casts a vertical ray upward and selects the closest
     boundary hit.
6. Same precision contract:
   - fixed-point scaled coordinates for exact arithmetic;
   - line coefficients precomputed from scaled endpoints;
   - LSI intersection points represented as rationals before materialization;
   - conservative AABBs for FP32 RT traversal so high-precision geometry is not
     falsely missed;
   - Simulation of Simplicity for degeneracies.
7. Same output contract:
   - author-format overlay text;
   - same chain ordering;
   - same face ids;
   - same coordinate materialization and six-decimal output formatting;
   - byte-equal output is the strongest correctness target.

## Paper Evidence Read

The ICS 2024 RayJoin paper states that polygon overlay is built by combining
LSI and PIP. LSI is formulated as ray tracing by casting each query segment as a
ray and collecting intersections through the RT traversal. PIP is formulated by
shooting a vertical ray from the query point and selecting the closest boundary
segment, then using chain left/right face metadata to determine the containing
face.

Section 3.2 and the implementation notes add the precision contract:

- OptiX uses FP32 ray-tracing primitives for performance.
- RayJoin preserves exact results by storing map coordinates in scaled integer
  form and by using a conservative representation for the low-precision AABBs
  handed to RT traversal.
- The conservative AABB rule expands FP32 bounds by mantissa-step adjustment so
  the high-precision line segment remains enclosed after downcast.
- Degenerate cases are handled by Simulation of Simplicity.
- The implementation combines callback logic into the intersection shader to
  reduce AnyHit / ClosestHit invocation overhead.

## Author Code Evidence Read

The clean author-code path is:

- `src/run_overlay.cu`
  - `Read map 0`
  - `Read map 1`
  - `Create App`
  - `Load Data`
  - `Init`
  - `Build Index`
  - `Intersection edges`
  - `Map 0/1: Locate vertices in other map`
  - `Computer output polygons`
  - optional `Check result`
  - optional `Write to file`

- `src/app/map_overlay_rt.h`
  - constructs `LSIRT` and `PIPRT`;
  - builds RT acceleration structures from grouped AABB primitives;
  - runs LSI against the opposite map;
  - runs PIP against the opposite map;
  - computes midpoint point-location for output polygon chains;
  - emits output through `WriteOutputChain`.

- `src/algo/rt_pip_custom.cu`
  - casts vertical rays;
  - tests each candidate edge in the hit AABB range;
  - applies SoS boundary decisions;
  - selects the closest boundary hit;
  - stores the closest edge id used later to derive the polygon face id.

- `src/app/output_chain.h`
  - groups intersections by edge;
  - walks planar graph chains;
  - splits chains at intersection points;
  - removes only exact consecutive duplicate points;
  - assigns output face ids;
  - writes author-format chains.

- `src/rt/primitive.h`
  - constructs conservative OptiX AABBs;
  - supports grouped primitive ranges for adaptive grouping.

The author working tree on the POD contains temporary Goal4806 debug
instrumentation, so the authoritative source for author behavior is
`git show HEAD:<file>` in `/workspace/RayJoin_fresh`, not the modified working
copy.

## What We Have Already Proven

On the County x Zipcode Section 5.7 pair, RTDL native OptiX output is now
byte-equal to the author output:

- line count: `87,758,310` for both files
- chain count: `29,254,027`
- face count: `115,490`
- RTDL total time: `459.2447640225291s`
- RTDL compute-without-load/pack time: `403.3002147451043s`

RTDL output artifact:

`/workspace/rtdl_goal4806_fast_min/artifacts/section57_same_source_county_zipcode_output_after_no_zero_length_correction_full/section57_overlay_county_zipcode_rtdl_after_no_zero_length_correction_full_optix.txt`

Author output artifact:

`/workspace/rtdl_goal4806_fast_min/artifacts/section57_author_output_debug/author_overlay_debug.overlay.txt`

This proves the algorithmic reproduction is possible when the contract is
followed. It does not prove a high-performance Numba partner result.

## Current Performance Truth

For the full County x Zipcode overlay output, RTDL is correct but slower than
the author code. The current RTDL time is dominated by output-chain assembly and
writing, not by the core RT queries alone.

Therefore the honest status is:

- correctness: strong, byte-equal for County x Zipcode;
- author-code performance parity: not achieved;
- V4+Numba high-performance selected primitive path: still blocked;
- public claim: no high-performance claim for Section 5.7 yet.

## Numba Partner Blocker

The initial V4+Numba candidate probe failed before measurement because Numba
used the system CUDA 12.8 NVVM and emitted PTX version 8.7 while the POD driver
accepted PTX up to 8.4:

`CUDA_ERROR_UNSUPPORTED_PTX_VERSION`

This was a toolchain blocker, not a proof that the RayJoin algorithm cannot be
implemented with RTDL/Numba. The temporary POD environment was repaired by
installing CUDA 12.4 NVCC/runtime Python packages into the venv and running
Numba with:

```bash
export CUDA_HOME=/tmp/rtdl_goal4806_venv/lib/python3.12/site-packages/nvidia/cuda_nvcc
export LD_LIBRARY_PATH=$CUDA_HOME/nvvm/lib64:$LD_LIBRARY_PATH
```

A minimal Numba CUDA kernel then emitted PTX 8.4 and executed successfully.

## V4+Numba Candidate Probe After Toolchain Repair

After the CUDA 12.4 NVVM repair, the Section 5.7 County x Zipcode V4+Numba
candidate probe completed on the POD:

```bash
python scripts/rayjoin_section57_numba_candidate_probe.py \
  --dataset-root /workspace/rayjoin_section57_same_source_cdb \
  --pairs county_zipcode \
  --warmup 1 \
  --repeat 3 \
  --topology-geometry-hash-match-confirmed \
  --output-json artifacts/goal4806_v4_numba_candidate_probe_after_byte_equal_cuda124/candidates_warmup1_repeat3.json
```

Remote artifact:

`/workspace/rtdl_goal4806_fast_min/artifacts/goal4806_v4_numba_candidate_probe_after_byte_equal_cuda124/candidates_warmup1_repeat3.json`

Measured rows:

| Candidate | Correctness | Hot-path host materialization | Steady-state sec | Notes |
|---|---:|---:|---:|---|
| `v4_numba_post_traversal_segmented_counts` | pass | false | `0.01628301292657852` | Selector-eligible candidate-stage row. |
| `v4_numba_post_traversal_mask_compact` | pass | true | `0.006718732416629791` | Faster but not selector-eligible because it uses host prefix-sum materialization. |
| `v4_numba_post_traversal_lsi_stream_digest` | pass | false | `0.13609668612480164` | Selector-eligible but slower. |

All three rows use the device-column route and match the expected LSI count:

- candidate row count: `965,844`
- expected LSI count: `965,844`
- topology/geometry hash match: confirmed by precondition
- GPU: NVIDIA RTX 4000 Ada Generation

The best selector-eligible V4+Numba candidate at this stage is:

`v4_numba_post_traversal_segmented_counts`

This is evidence for a post-traversal Numba continuation candidate. It is not
evidence that the full polygon overlay is faster than the author code.

## Rule For The Next Implementation

The RTDL/Numba implementation may change language and ownership of kernels, but
it may not change:

- dataset;
- query semantics;
- CDB/topology interpretation;
- SoS boundary policy;
- exact coordinate materialization;
- LSI/PIP/midpoint/output-chain decomposition;
- output equivalence target;
- benchmark timing scope.

If any of those change, the result is a new workload, not a fair RayJoin
Section 5.7 reproduction.
