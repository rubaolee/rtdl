# Goal2115: X-HD-Guided Hausdorff Pre-Pod Design Review

Date: 2026-05-16

Status: reviewed, with one pre-pod diagnostic improvement added.

## Review Verdict

`accept-with-boundary`

The current Hausdorff application is a valid RTDL v2.0 language test:

- exact Hausdorff can be written in Python+partner+RTDL;
- exact results match OpenMP, CUDA C++, CuPy, and RTDL+CuPy baselines;
- the new `rtdl_rt_nearest_witness` path really uses RTDL/OptiX traversal;
- the native engine remains app-agnostic.

But it is not yet an X-HD-level performance implementation. The current RT path
uses point AABBs plus fixed-radius decision/witness passes. X-HD's core
performance idea is not merely "use RT cores"; it is structured bounding,
grouping, estimator pruning, and CUDA fallback for heavy cells.

## Findings

| Priority | Finding | Impact before pod | Status |
| --- | --- | --- | --- |
| P1 | The RT path still performs many full fixed-radius decision launches before exact witness traversal. | Pod timing will include repeated decision-pass overhead; this is honest for the current user algorithm but not an X-HD best case. | Keep as measured path; add diagnostics. |
| P1 | The prepared OptiX primitive builds AABBs around individual points using a global radius bound, not X-HD grouped cells. | Traversal can visit too many candidates, especially when the radius is loose or data is dense. | Requires future generic grouped-cell primitive/user library. |
| P1 | No estimator / early-break layer exists. | The RT path cannot avoid work once enough evidence identifies the HD witness. | Future app-level algorithm work. |
| P2 | No heavy-cell CUDA/CuPy fallback exists. | Dense regions can punish RT traversal instead of falling back to partner kernels. | Future app-level algorithm work. |
| P2 | Native nearest-witness distance uses float payloads and Python recomputes the selected witness distance in double precision. | Distance value is corrected, but near-tie witness identity can differ from double baselines on adversarial data. | Accept for current generated data; add adversarial tests later. |
| P2 | Current pod lab uses generated ring-like point sets only. | It may not expose the same behavior as X-HD's intended spatial-cell workloads. | Pod should include clustered and dense-cell variants later. |
| P3 | A stale slower helper existed after Goal2114. | Future maintainers could accidentally benchmark the old fresh-prepare route. | Removed in this goal. |

## Changes Made In This Review

### Removed stale helper

The old `_directed_rt_nearest_witness` helper in
`examples/rtdl_hausdorff_v2_function.py` was no longer referenced after the
Goal2114 prepare-reuse path. It prepared a fresh scene for witness traversal and
could confuse future benchmark work. It has been removed.

### Added oracle-radius diagnostic

New language-lab method:

`rtdl_rt_nearest_witness_oracle_radius`

This is not a user-facing speedup claim. It is a diagnostic lower-bound probe:

- compute an exact reference first, usually with CUDA C++;
- use `exact_reference_distance + oracle_radius_slack` as the witness radius;
- skip threshold search;
- run exact RTDL/OptiX nearest-witness traversal.

This approximates the question:

> If an X-HD-style estimator gave us a nearly perfect radius bound, how fast is
> the current RT witness traversal layer?

Local GTX 1070 smoke result at 8192 x 8192:

| Method | Elapsed | Exact match? | Notes |
| --- | ---: | --- | --- |
| `cuda_cpp` | 0.010040 s | yes | exact reference |
| `rtdl_rt_nearest_witness_oracle_radius` | 1.056037 s | yes | diagnostic, threshold iterations = 0 |

Artifact:

- `docs/reports/hausdorff_v2_language_lab_local_optix_8192_oracle_radius.json`

## Design Review Against X-HD

| X-HD idea | Current RTDL HD state | Assessment |
| --- | --- | --- |
| BVH/RT traversal for spatial pruning | Present through fixed-radius OptiX AABBs and nearest-witness rows. | Correct foundation. |
| Group target points into spatial cells/AABBs | Not present; one primitive per point with a global radius. | Main missing performance layer. |
| Estimator-driven lower/upper bounds | Only binary threshold search over a global bound. | Correct but too blunt. |
| Early break once HD witness is determined | Not present. | Major missing algorithmic optimization. |
| Heavy-cell fallback to CUDA | Not present. | Needed for dense/clustered inputs. |
| Exact witness correctness | Present for tested cases via Python double recomputation of returned witness. | Good, with near-tie caveat. |
| App-agnostic native engine | Preserved. Native primitive is fixed-radius nearest witness, not Hausdorff. | Correct architecture. |

## Pod Run Recommendation

Use the pod to answer three separate questions, not one vague "is RTDL fast?"
question:

1. **Language usefulness:** Does `rtdl_v2_user_cuda` stay close to CUDA/CuPy
   baselines at larger sizes?
2. **Current RT-core exact path:** How does `rtdl_rt_nearest_witness` scale on
   modern RTX hardware when it includes threshold seeding?
3. **X-HD gap decomposition:** How much of the RT cost remains even with
   `rtdl_rt_nearest_witness_oracle_radius`?

Suggested method set:

```bash
python3 examples/rtdl_hausdorff_v2_language_lab.py \
  --points-a <N> --points-b <N> \
  --method cuda_cpp \
  --method cupy_rawkernel \
  --method rtdl_v2_user_cuda \
  --method rtdl_rt_threshold_search \
  --method rtdl_rt_nearest_witness \
  --method rtdl_rt_nearest_witness_oracle_radius \
  --rt-tolerance 1e-4 \
  --json-out docs/reports/<pod-artifact>.json
```

Run at several sizes that take seconds on the pod, for example 8192, 32768, and
65536 if memory/time allows. Use timeouts and progress logging.

## Claim Boundary

After this review, the honest claim is:

> RTDL v2.0 can implement exact Hausdorff Distance and validate it against
> independent C++/CUDA/CuPy baselines. It now has an exact RTDL/OptiX
> nearest-witness path, plus diagnostics that help measure the gap between the
> current implementation and an X-HD-style algorithm.

The review does not authorize:

- broad RT-core Hausdorff speedup claims;
- claims that RTDL currently matches X-HD;
- v2.0 release claims based on this lab alone.

Those require pod-scale evidence and additional X-HD-style algorithmic work.
