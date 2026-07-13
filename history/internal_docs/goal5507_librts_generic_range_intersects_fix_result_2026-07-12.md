# Goal5507: Generic float32 `range_intersects` correction

## Status

`implemented__generic_native_fix__same_input_pod_verified__review_pending`

## Decision input

Goals5503-5506 established the pinned author's actual float32 contract and
then reproduced its bounded behavior on the POD. The pre-fix RTDL native
kernel differed on the one-ULP boundary case and on the scalable 8,192-pair
probe. The author source is the decision reference here; no LibRTS-specific
behavior was added to the system.

## Generic fix

`src/native/optix/rtdl_optix_workloads.cpp` now implements the generic
two-direction AABB intersection contract as follows:

1. Forward rays use the query anti-diagonal. A pair is accepted when that ray
   hits the indexed box and the indexed box main diagonal does not hit the
   query.
2. Backward rays use the indexed box main diagonal. A pair is accepted when
   that ray hits the query directly.
3. The segment slab interval uses the audited float32 upper endpoint
   `nextafterf(1.0f, +inf)` and the source-equivalent
   `1 + 2 * FLT_GAMMA(3)` far-bound expansion.

The source contains no `LibRTS`, `RTSpatial`, paper, or author-specific
identity. The candidate AABB pad remains the existing generic `1e-6f` value.
The dynamic NVRTC source uses explicit IEEE-754 float32 literals because its
minimal include environment does not provide host `<float.h>` macros.

## POD evidence

POD: `157.157.221.29:25039`, NVIDIA RTX 4000 Ada Generation, driver
`570.133.07`. The library was rebuilt from a clean `build5507pad1e6` directory
with CUDA 12.8 and the pinned OptiX SDK. The binary and kernel source hashes
are recorded in `goal5507_generic_range_intersects_fix_gate.json`.

The exact same input files were passed to the pinned author binary and RTDL:

```text
Goal5505 boundary fixture:  author 5, RTDL 5, RTDL rows 5, duplicates 0
Goal5506 8,192-pair probe: author 21, RTDL 21, RTDL rows 21, duplicates 0
```

The source-driven RayParams model is `5` and `21` respectively. RTDL rows
were collected separately from count-only execution; they contain no duplicate
pair rows in either probe. The pre-fix results remain preserved in the
Goal5505/5506 artifacts, so the correction is auditable rather than silently
rewriting history.

## What this proves

- The generic native AABB implementation can match the audited author float32
  contract on the five-case boundary fixture and the deterministic 8,192-pair
  probe.
- The mismatch was a real generic numerical/traversal contract gap, not a
  Python parser or author-output parsing issue.
- The fix is system-level and app-neutral: it changes the generic
  `range_intersects` kernel, not a LibRTS wrapper or comparator.

## What this does not prove

- It does not adjudicate the two large official-archive count disagreements.
- It does not prove official archive pair-row equality or full-input validity.
- It does not reproduce a paper figure, establish a performance ratio, or
  complete the LibRTS paper reproduction.
- It does not authorize Embree work; Embree remains out of scope.

Machine-readable evidence:

`Paper-reproduction-apps/librts-paper/results/goal5507_generic_range_intersects_fix_gate.json`
