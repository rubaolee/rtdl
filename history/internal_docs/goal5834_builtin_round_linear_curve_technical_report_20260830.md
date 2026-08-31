# Goal5834 technical report: public OptiX round-linear curves

Date: 2026-08-30  
Status: **complete at the bounded functional scope**  
External review: not requested or authorized  
Performance measurements: zero

## Outcome

Goal5834 now provides an app-neutral public lifecycle for the tested static
OptiX built-in round-linear-curve subset:

```text
verify source -> compile protocol -> materialize -> prepare -> execute* -> close
```

The implementation uses `OPTIX_BUILD_INPUT_TYPE_CURVES`,
`OPTIX_PRIMITIVE_TYPE_ROUND_LINEAR`, positive float32 widths (radii), indexed
two-point segments, OptiX's default round endcaps for linear curves, one static
GAS, one SBT record, trace depth one, and no callable program, motion blur,
instancing, or user intersection program. Application-specific Sui/RT-CCD
logic is absent from `src/rtdsl/**` and `src/native/**`.

The result supports the controlling claim:

> RTDL supports the tested OptiX round-linear built-in-curve subset. Together
> with the existing custom, triangle, and sphere routes, this instantiates all
> four leaf-primitive classes in the pinned taxonomy; 4/4 means kind presence
> only.

It does not establish complete curve support, arbitrary Callback IR to GPU,
prospective unseen-app generalization, an RT-CCD Paper App, external usability,
performance parity, or RT-core silicon execution.

## What was implemented

- A four-role Callback IR program (`make_ray`, `closest_hit`, `miss`,
  `finalize`) and exact curve-specific ABI.
- A physical schema binding seven public fields: control points, widths,
  segment indices, application IDs, motion-segment queries, first-contact
  outputs, and device status.
- A trusted wrapper using compiler-owned any-hit enumeration to choose the
  lexicographic minimum `(float32 t, application_id, primitive_index)` before
  invoking the verified closest-hit or miss role once.
- A native built-in-curve GAS producer and public C ABI for
  prepare/execute/describe/destroy.
- Runtime receipts binding build input, primitive and flags, endcap policy,
  strides, counts, target versions, host/device content fingerprints, device
  pointers, traversable identity, generated PTX, native DSO, status-first D2H,
  and output D2H.
- A stdlib-only independent capsule oracle and a public First Contact fixture.

## Functional evidence

Home Linux rebuilt the current native producer against OptiX 9.0.0. The target
was GTX 1070 / compute capability 6.1, so this is true OptiX functional
traversal but not RT-core-silicon evidence.

| Fixture | Oracle and GPU result |
|---|---|
| Side hit with equal-time duplicate capsules | hit, `t=0.375`, stable ID `50` |
| Complete miss | canonical miss `(0, 1.0f bits, U32_MAX)` |
| Earlier contact versus smaller later ID | hit, `t=0.1875`, ID `900` |
| Nondegenerate round-endcap-only contact | hit, `t≈0.28349365`, ID `77` |

All four rows are bit-identical to the independent oracle. The same prepared
program ran a second reversed query batch exactly. Device role counters were
`[0,4,0,0,3,1,4]`: four make-ray, three closest-hit, one miss, and four
finalize invocations. The traversal receipt records one successful OptiX
launch, four raygen invocations, the expected curve program bundle, and a
nonzero traversable.

The static scene contains five primitives with radii `0.125`, `0.25`, and
`0.5`. Invalid cardinality, indices, zero-length segments, nonfinite values,
nonpositive widths, tapered segments, duplicate segment starts, and duplicate
application IDs fail before launch.

## The important negative result and repair

The first hardware endcap fixture used a ray exactly collinear with a capsule
axis. The independent closed-capsule oracle returned a hit, while the OptiX
built-in curve returned a miss. That input was initially admitted, so merely
changing the fixture would have left a correctness hole.

The final public numeric domain therefore adds an explicit, post-observation
guard: when a query could contact a primitive and the squared sine/cross ratio
between the query and curve axes is below `2^-12`, the query is rejected before
native launch with `near_parallel_curve_query`. The final evidence preserves
the closed-capsule oracle hit and proves that the repaired route performs no
third launch. A nondegenerate endcap-only fixture remains accepted and exact.

This is a domain restriction discovered from hardware, not a preregistered
rule and not evidence that OptiX generally lacks round endcaps.

## Liveness and regression evidence

- 611/611 populated serialized ABI scalar occurrences were independently
  mutated and resealed; none remained silently admissible.
- 35/35 physical-schema scalar occurrences were mutated; all were rejected.
- Six target leaves changed the authority identity or were rejected.
- Seven canonical-plan leaves changed identity and were rejected downstream.
- Goal5834 tests: 11/11 on Windows and 11/11 on Home Linux.
- Goal5833 regression: 70/70 local tests plus a fresh Home built-in-sphere
  hardware validation using the new native DSO.
- A standalone verifier importing no RTDL rehashed all 13 generated executable
  artifacts, reran the independent oracle, checked the native descriptor and
  target identities, and returned PASS.

## Attempt lineage

No failed attempt is relabelled as a successful result:

1. One run stopped before materialization because `/usr/local/cuda` was a
   dangling include path.
2. One run stopped before GPU execution because the system Python's isolated
   child could not import Numba; the existing pinned clean venv was then used.
3. The first GPU attempt exposed the axial endcap oracle/OptiX mismatch.
4. The repaired nondegenerate fixture passed GPU comparison, but strict JSON
   serialization rejected the miss-row NaN telemetry. Evidence serialization
   was changed to `null` plus exact float32 bits; execution was unchanged.
5. A pre-boundary result passed, then strict self-review identified that the
   axial input was still admitted. It is superseded by final v7.
6. Final v7 passed all positive, negative, lifecycle, identity, and independent
   verification gates.

## Evidence identities

- Final Home result: `562e4cb0d565f3b7a97e3c46ab14aaa27db31ea9a01cf04da530203e1bd5685a`
- Independent verification: `6081de60c3576d6ea63bf135a33b702a1cccfd99525b64ac1619f00104bf5c83`
- Native DSO: `7a9f38fe40f1fdea770e4e0d3aceb4f473c1434250e942003f359e108c86a46c`
- Exact executed-source projection: `a6d423001c01277f6bec3f7d252b0689a9a383c07a3efffcd9dbc923f5d5ca85`
- Final source archive v4: `5face185c176a3277a1a7860d35ddc04f96ac487549b71716fb6c595271f0f73`
- Goal5833 sphere regression: `924ba63c3fefb88b36a378af92ddafeafea4c193a230323a8658988f0fb762a8`

The local Git object database currently cannot resolve `HEAD` or several refs,
so no commit claim is made. Exact source and evidence are bound by the hashes
above; repairing Git storage is a separate repository-maintenance task.
