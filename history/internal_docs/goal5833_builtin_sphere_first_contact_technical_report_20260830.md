# Goal5833 — OptiX built-in sphere public path and First Contact

## Outcome

Goal5833 is complete at its frozen bounded scope. RTDL now has a public
successor namespace, `rtdsl.v4_sphere`, that accepts restricted four-role
Callback IR, binds it to one static OptiX built-in-sphere GAS, compiles and
materializes the exact callback, prepares static sphere columns, executes one
or more motion-segment queries, checks device status before copying application
output, and closes the prepared owner.

This is functional evidence only. It contains zero registered performance
timings and authorizes no performance, prospective-generalization, Paper App,
curve, motion-blur, instancing, or RT-CCD claim.

## What was implemented

The public lifecycle is:

```python
from rtdsl.v4_sphere import (
    BuiltinSphereStaticInput, MotionSegmentBatch,
    V4SphereTarget, first_contact_source,
)
from rtdsl.v4 import V4Toolchain

source = first_contact_source()
program = source.compile(target=target)
materialized = program.materialize(toolchain=toolchain)
prepared = materialized.prepare(BuiltinSphereStaticInput(centers, radii, ids))
result = prepared.execute(MotionSegmentBatch(queries), expected_output=oracle_rows)
prepared.close()
```

`V4Toolchain` remains in the byte-frozen `rtdsl.v4` namespace; the sphere
successor deliberately does not modify that predecessor. Users do not supply
PTX, an intersection program, an SBT record, or a private loader.

The verified callback has exactly `make_ray`, `closest_hit`, `miss`, and
`finalize`. The compiler owns the any-hit enumerator needed to inspect all
sphere candidates. Its order is `(ordered-f32(t), application_id,
primitive_index)`, so equal-time traversal order cannot choose the result.
The application ID is a primitive-aligned compiler metadata column; it is not
smuggled through a user attribute slot.

The native provider uses `OPTIX_BUILD_INPUT_TYPE_SPHERES`, obtains the
intersection module through `optixBuiltinISModuleGet` with
`OPTIX_PRIMITIVE_TYPE_SPHERE`, binds no user intersection program, builds one
static GAS and one SBT record, and downloads status/counters before any output.
A query against a live prepared token returns these facts through a native
descriptor; the Python receipt no longer merely restates its expectations.

## First Contact validation

The independent oracle at
`examples/first_contact_sphere/first_contact_oracle.py` imports no RTDL module.
It solves segment-sphere intersection in binary64, selects by the frozen order,
and converts the selected time to binary32 only at the public output boundary.

Five reader-checkable fixtures were run:

| Fixture | Required behavior | Observed `(hit, f32(t)-bits, app-id)` |
|---|---|---|
| Equal-time coincident spheres | smaller application ID wins | `(1, 1056964608, 2)` |
| Transverse miss | miss sentinel | `(0, 1065353216, 4294967295)` |
| Two hits at different times | nearer time beats smaller later ID | `(1, 1048576000, 99)` |
| Exact tangent | tangent is a hit | `(1, 1048576000, 11)` |
| Intersection beyond segment end | miss sentinel | `(0, 1065353216, 4294967295)` |

All five GPU rows equal the independent oracle exactly. All five device status
records have zero first-error and zero error code. The role counters are
`[0,5,0,0,3,2,5]`: five make-ray/finalize calls, three closest-hit calls and
two miss calls. Use after close is rejected.

## Physical execution evidence

The final a5 execution ran on Home Linux `lx1`, GTX 1070 (CC 6.1), driver
580.126.09, CUDA 12.0 and OptiX 9.0.0. This is behavioral OptiX evidence on
Pascal, not evidence of RT-core silicon execution.

The traversal receipt reports one attempted and one successful launch, zero
failed or incomplete launches, one bound traversal context, five raygen
invocations, a nonzero traversable, and the expected sphere program bundle at
the receipt edge. Exact identities include:

- native: `c0c2981f2d1bf132d11abdf533de1d4ead1bbb80bd6624ec4f1b7b0681bfbd45`;
- Callback IR: `60314121a0d865dbd32efe92616bbd3784f11286cb0581eaed3aded0fbe0ae5d`;
- physical schema: `2ea5117c3a8da9a3ee5aa8edc78e0e02317766a79fde9c51109a768fb88d512e`;
- canonical plan: `d289f2c3b11e668ec90c194628dec305e9d99ae6a21eabd1b3de95216951d16d`;
- callback ABI: `8f63b85dbd792b817b330b821e28a6f9d82c5b4d48f65097b4deff3a8b149652`;
- composed PTX: `5653791d25b94a625a8d75df316fd38795c832c005ef74b33b023ce6a8020848`.

The raw result was independently recounted on Home and again on Windows by a
stdlib-only verifier. Their input identity is
`7ac21df6d89a6b5a22c0bd6c22bac63b78788aab5db1e03ba7d271c4eafa8e72`.

## Regression and custody

One broad local suite ran 178 tests spanning Callback IR, ABI, formal codegen,
typed physical schemas, triangle runtime/reduction, public import/lifecycle,
Goal5831/5832 custody, family-schema compilation, stable sort and Goal5833.
All 178 passed, followed by Python compilation of every new module and script.

Goal5833 does not widen three frozen predecessor files. Their current exact
identities remain:

- `v4_callback_abi.py`: `3f4be4d9…74fb5`;
- `v4_typed_physical_schema.py`: `f1b093da…c7e5d`;
- `rtdsl.v4`: `5800a381…7f582`.

The sphere successor has its own authority/ABI and Numba-leaf adapters. Public
import is compiler- and native-quiet; compiler/runtime modules load only at
materialize/prepare.

## What this changes for the CGO evidence

At the coarse OptiX primitive-geometry denominator—custom primitives,
triangles, spheres and curves—the executable public evidence moves from two of
four classes to three of four. More importantly, the third class is an OptiX
built-in primitive with no user intersection program. This shows that RTDL's
protocol-contract mechanism is not confined to custom intersections or
triangle attributes.

It does **not** prove a universal geometry-family compiler. Goal5833 added a
sphere-specific successor authority, wrapper and provider. Therefore this is a
third bounded instantiation and mechanistic portability evidence, not a
prospective new-application generalization exam. Curves remain the missing
fourth coarse class and are Goal5834.

## Evidence

- Machine-readable result:
  `history/internal_docs/goal5833_builtin_sphere_first_contact_result_20260830.json`
- Raw Home result:
  `history/internal_docs/goal5833_builtin_sphere_home_evidence_20260830/goal5833_home_result.json`
- Home recount:
  `history/internal_docs/goal5833_builtin_sphere_home_evidence_20260830/goal5833_home_recount.json`
- Local recount:
  `history/internal_docs/goal5833_builtin_sphere_home_evidence_20260830/goal5833_local_recount.json`
- Exact Home native:
  `history/internal_docs/goal5833_builtin_sphere_home_evidence_20260830/librtdl_optix_goal5833_sm61.so`

No external review was requested or performed.
