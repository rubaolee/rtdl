# RTDL v2 Hausdorff RT-Acceleration Attempt

Date: 2026-05-15

Status: first RTDL/OptiX HD threshold-search implementation complete; exact CUDA
HD remains the fastest current user-facing exact value path.

## Question

The prior v2 user Hausdorff function computed exact HD with RTDL partner columns
plus a user-owned tiled CUDA continuation. That is a real HD function, but it
does not use RT cores.

The X-HD paper accelerates HD with RT cores by reformulating the nearest-neighbor
subproblem as ray/AABB traversal over grouped target points. RT cores accelerate
candidate-cell discovery; CUDA shaders/kernels compute point distances and handle
load balance.

This report records the first RTDL v2 implementation attempt in that direction.

## Implementation

The user-facing function file now has two HD paths:

```text
examples/rtdl_hausdorff_v2_function.py
```

Exact CUDA continuation:

```python
hausdorff_distance_2d(points_a, points_b, method="rtdl_v2_user_cuda")
```

RTDL/OptiX fixed-radius threshold search:

```python
hausdorff_distance_2d_rt_threshold_search(
    points_a,
    points_b,
    backend="optix",
    tolerance=1e-4,
)
```

The RT path uses the current v2 generic primitive:

```text
prepare_generic_fixed_radius_count_threshold_2d(..., backend="optix")
```

For a radius `r`, it asks:

```text
Is every source point within radius r of at least one target point?
```

That is a monotone decision form of directed HD:

```text
directed_H(A, B) <= r
```

Binary search over `r` gives a tight interval for HD.

## Local OptiX Smoke

Host:

```text
192.168.1.20
```

Checkout:

```text
/home/lestat/work/rtdl_hausdorff_v2_lab
```

OptiX backend built with:

```text
make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev
```

Command:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
  python3 examples/rtdl_hausdorff_v2_function.py \
  --points-a 512 --points-b 512 \
  --method rtdl_rt_threshold_search \
  --rt-backend optix \
  --rt-tolerance 1e-4 \
  --compare \
  --json-out docs/reports/hausdorff_v2_rt_threshold_search_local_optix_512.json
```

Artifact:

```text
docs/reports/hausdorff_v2_rt_threshold_search_local_optix_512.json
```

## Result

| Method | Time | Distance / interval | Correctness |
| --- | ---: | ---: | --- |
| RTDL/OptiX threshold search | 0.627886s | [0.146268446710, 0.146321137073] | contains exact |
| OpenMP CPU exact | 0.000696s | 0.146278731694 | matches interval |
| CUDA C++ exact | 0.000620s | 0.146278731694 | matches interval |
| CuPy RawKernel exact | 0.000539s | 0.146278731694 | matches interval |
| RTDL v2 user CUDA exact | 0.000555s | 0.146278731694 | matches interval |

The RT path reports:

```json
"rt_core_accelerated": true,
"exact_value": false
```

## Interpretation

This implementation does use RTDL/OptiX, hence RT-core BVH traversal, for the
fixed-radius HD decision subproblem. It is the closest X-HD-style formulation
available from the current public v2 primitive surface.

It is not yet the paper-level X-HD algorithm because the current primitive
returns only aggregate threshold coverage counts. It does not expose:

- nearest target identity for each source point;
- per-source minimum distance;
- grid-cell candidate lists;
- MBR lower/upper HD estimators;
- heavy-cell worklists;
- CUDA offload from RT shaders for imbalanced cells.

Therefore it can produce a tolerance-bounded HD interval by repeated RT
decision queries, but not a single-pass exact RT-HD value with witness.

## Design Lesson

For RTDL v2, the right lesson is:

```text
Current v2 can express RT-accelerated HD decision search.
Current v2 cannot yet express full X-HD exact nearest-witness traversal.
```

To make paper-level X-HD a first-class RTDL workload, the next generic primitive
would not be app-named `hausdorff`. It should be an app-agnostic nearest-distance
or candidate-cell primitive, for example:

```text
PREPARED_FIXED_RADIUS_NEAREST_WITNESS_2D
```

or:

```text
CELL_AABB_CANDIDATE_WITNESS_ROWS + REDUCE_FLOAT(MIN/MAX)
```

Those would let Python/partner code compute exact HD while preserving the
app-agnostic native-engine rule.

## Boundary

Do not claim this is faster than CUDA exact HD. On the local GTX 1070 smoke, it
is much slower because it performs many prepared fixed-radius decision queries.

Do claim:

- a real RTDL/OptiX RT-core HD decision-search path exists;
- it returns a correct tolerance-bounded HD interval;
- exact HD still works today through RTDL v2 partner columns plus user CUDA;
- paper-level X-HD needs one additional generic nearest-witness/candidate-cell
  primitive before it can be expressed efficiently in RTDL.
