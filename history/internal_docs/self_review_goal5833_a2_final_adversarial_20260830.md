# Goal5833 A2 final adversarial self-review

Date: 2026-08-30  
Posture: reject whenever the exact evidence does not discharge the frozen gate  
Negative results: preserved  
External review: neither requested nor authorized  

## Final verdict

`P0=1 · P1=9 · P2=5 · P3=3`

`goal5833_complete_under_controlling_plan: false`

`public_restricted_callback_ir_semantics_preserved: false`

`exact_five_row_home_observation_preserved: true`

This A2 judgement supersedes both the original `P0=0/P1=0` self-review and
the A1 `P0=0/P1=5` judgement.  The immutable result, report, first self-review,
and A1 self-review must remain available: the correction is append-only.

The decisive change from A1 is a reproduced **silent compiler
mistranslation**.  This is a P0 for the public language path, even though the
frozen standard program happens to use the values hardcoded by the wrapper and
its five observed rows therefore survive.

## Independent review structure

The final pass used four read-only lines:

1. primary-agent gate-by-gate review;
2. independent Callback-IR/authority review;
3. independent numerical/oracle review; and
4. independent native/receipt/custody review.

The primary agent reproduced every new P0/P1 counterexample reported below.
No implementation byte was changed, no GPU was rerun, and no external review
was requested.

## P0 finding

### P0-1 — Accepted `TraceRequest.tmin/tmax` semantics are silently discarded

The public function `verify_builtin_sphere_callback_source` accepts restricted
four-role Callback IR beyond the one standard source.  A source derived from
the standard program by changing only

```text
tmax=ONE_F32  ->  tmax=ZERO_F32
```

is accepted and receives a distinct verified IR identity:

```text
mutated_source_accepted = true
mutated_ir_sha256       = 539d0b33928e6d483731fda43510c308f8d9f9e9ef9ec08db3770ea40940dba7
normalized IR contains  = tmax=ZERO_F32
```

The generated make-ray leaf exposes the returned trace-request fields, but the
trusted sphere wrapper ignores the returned `tmin` and `tmax`.  It always emits:

```cpp
optixTrace(..., 0.0f, 1.0f, 0.0f, ...);
```

Relevant implementation locations are
`src/rtdsl/v4_sphere_optix_wrapper_codegen.py:172-184` and `:242-254`.
Origin, direction, and payload are taken from the leaf; `tmin/tmax` are not.
The verifier in `src/rtdsl/v4_sphere_physical_schema.py:191-229` neither
requires those expressions to be the frozen zero/one values nor rejects other
accepted values.

This is not merely an untested leaf.  A verified source and the executed
program have different ray domains.  It is the same defect class as the
project's earlier inert-leaf failures, now inside the new sphere lowering.

**Impact.** The public claim that restricted accepted Callback IR is exactly
materialized is false.  The standard First Contact source itself returns
`tmin=0/tmax=1`, so this P0 does not alter its five stored outputs.  Closure
requires either lowering the returned fields or making the physical verifier
reject every noncanonical value before issuing authority, followed by an
exhaustive populated-leaf liveness sweep.

## P1 findings

### P1-1 — Authorized native and actually loaded DSO are not fail-closed bound

`PreparedBuiltinSphereOwner` obtains a process-global cached handle from
`optix_runtime._load_optix_library()`.  When an explicit target path is also
provided, `_native_path(library, explicit)` hashes only that explicit path and
does not compare it with the handle's actual loaded path or SHA.

A direct reproduction supplied a foreign `_name` with the authorized explicit
file and obtained:

```text
loaded library != hashed explicit path
mismatch accepted = true
```

The traversal receipt does carry the actual loaded provider SHA, but neither
the sphere runtime nor its independent verifier compares that value with the
authorized native SHA.  Thus a cached DSO A can execute while authority names
and hashes DSO B.

The final Home receipt happens to close this gap for that one observation:

```text
authorized native SHA = c0c2981f...bd45
actual provider SHA    = c0c2981f...bd45
```

So the five-row observation survives.  The public mechanism does not.

### P1-2 — Logical fields and concrete GPU inputs are not bound to the launch

Changing all six `BuiltinSphereFieldIds` changes the schema and plan identities
but leaves the ABI and generated wrapper byte-identical:

```text
schema_equal        false
plan_equal          false
abi_equal           true
wrapper_equal       true
wrapper_bytes_equal true
```

The physical/traversal receipts contain no canonical digest of centers,
radii, application IDs, queries, status buffers, or output buffers.  Their
input fields are not carried to the execution edge.  `params_mix` and an output
digest do not establish the contents of the pointee buffers.

Therefore Goal5833 does not satisfy the frozen requirement for identity-bound
GAS inputs and output/status resources.  The field names currently reseal an
authority without changing or checking the physical mapping.

### P1-3 — Two mandatory hardware fixtures are absent, and one is mislabeled

The frozen plan requires heterogeneous radii and an exact tangent.

The Home scene has:

```text
radii = [1.0, 1.0, 1.0, 1.0, 1.0]
distinct radius count = 1
```

It therefore never executes different radii in one GAS.

The row named `exact_tangent` uses center `(2,8,0)`, radius `1`, and segment
`(0,8,0)->(4,8,0)`.  The segment passes through the center:

```text
minimum axis distance = 0
radius                = 1
entry t               = 0.25
tangent                = false
```

The observed bits `1048576000` are exactly `0.25f`.  A true tangent exists only
in a CPU-oracle unit test, not in the GPU run.  Hence the technical report's
“tangent is a hit” row is false as a description of the executed geometry.

### P1-4 — The oracle is unsound over the accepted numerical domain

Two independent defects are reproduced.

First, public execution rounds inputs to binary32 before use, while the oracle
solves on the original Python values.  A regular axial hit changes by one ULP:

```text
center = 0.20030000007
radius = 0.00110000018
raw-value oracle toi_bits   = 1045166870
RTDL-f32 oracle toi_bits    = 1045166869
```

Second, even exact binary32 inputs can defeat the naive discriminant through
catastrophic cancellation:

```text
start  = (0,0,0)
end    = (200000,0,0)
center = (100000,1.0000001192092896,0)
radius = 1

binary64 implementation discriminant = 0.0
high-precision discriminant           = -38146.974945736756...
current oracle result                 = false tangent hit at 0.5f
mathematical result                    = miss
```

The frozen separation/conditioning policy and near-degenerate rejection rule
were never implemented.  The exact claim is therefore restricted to the
specific simple fixtures; it cannot cover the public accepted domain.

### P1-5 — Malformed query rows are silently truncated

`MotionSegmentBatch.__post_init__` constructs each row from `row[0]` and
`row[1]` without requiring `len(row)==2`.  A reproduced three-item row

```text
(start, end, unwanted_third_item)
```

is accepted and silently normalized to `(start,end)`.  The later owner check
cannot observe the discarded field.  This violates the frozen
malformed-input-fails-before-launch gate.

### P1-6 — Target SDK/device identity remains caller-asserted

The exact final native combined with the literal `NOT_AN_OPTIX_VERSION` is
accepted by `V4SphereTarget` and sphere compilation.  The false label changes
the target/plan identity while leaving ABI and wrapper unchanged.  Compute
capability is checked for textual agreement with the compiler request, not
derived from the executing device; the OptiX SDK label is not matched to a
pinned header or loaded API authority.

The Home environment may be reported as an independently observed execution
fact.  The public target certificate cannot yet be treated as mechanically
verified environment identity.

### P1-7 — Advertised lifecycle rules are not executed evidence

The Home result exercises prepare, one execute, close, and one use-after-close
rejection.  It does not exercise repeated execution with different data,
cross-thread/process use, serialization, concurrent reentry, close during
execution, or double-close.  The code contains guards, but the receipt's
`process_bound/thread_bound/nonserializable/nonreentrant` booleans are claims,
not the results of those hostile transitions.

### P1-8 — Physical and status receipts mostly restate implementation constants

The native descriptor serializes compile-time constants and one live primitive
count.  The traversal audit observes a successful launch, a nonzero traversable
and a program-bundle identifier; it does not introspect `OptixBuildInput.type`,
the built-in IS options/module, actual center/radius buffer contents, or the
hitgroup's IS module.  Python adds symbolic names and
`status_before_output: true` as constants.

The reviewed source does implement the sphere build input and built-in IS, so
source-traced evidence survives.  The report sentence claiming that the
receipt “no longer merely restates its expectations” does not.

The source order for status-before-output is also correct, but every Home row
has success status.  No injected device failure demonstrates that application
output is withheld on failure.  Therefore only source-order evidence—not an
executed failure-path property—is available.

### P1-9 — Exact executed callback chain is not independently reconstructable

The evidence preserves source generators, hashes and the final native, but not
the exact generated wrapper bytes, four compiled leaf PTX artifacts, composed
PTX bytes, NVRTC log, or a complete final Home source/build-command snapshot.
An independent holder can verify the reported hashes as strings but cannot
rebuild and inspect the exact PTX launched in the recorded transaction from the
packet alone.  The final native build stdout is also absent.

This does not refute the five rows.  It prevents the evidence packet from being
an independently reconstructable authority for the exact callback/native
chain.

## P2 findings

### P2-1 — The reported regression denominator overstates sphere coverage

The broad suite contains 178 tests, but Goal5833 itself has nine test methods,
one hardware launch and five queries.  The two counts must always be shown
separately.

### P2-2 — The route is a third hand-integrated template

Sphere-specific authority, ABI adapter, leaf adapter, wrapper, compiler,
prepared runtime, public lifecycle and native provider were added.  The
provider-neutral `FamilySchema` prototype does not lower this route.  This is
manual mechanistic portability, not prospective or automatic generalization.

### P2-3 — The advertised third stable-order key is unreachable

The schema declares `(t, application_id, primitive_index)`, but valid static
inputs require unique application IDs.  For two distinct primitives,
`application_id == current_id` is therefore impossible, so the
primitive-index branch cannot decide a legal tie.  It must be removed from the
semantic claim or explicitly classified non-decision-bearing.

The coincident-sphere GPU fixture also lacks an any-hit candidate counter and a
paired reversed-order run.  Its final ID 2 is consistent with the wrapper, but
does not alone prove order independence rather than favorable traversal order.

### P2-4 — Hardware scope is one Pascal configuration

The only final execution is GTX 1070 / CC 6.1.  It is behavioral OptiX
evidence, not dedicated RT-core, modern RTX, multi-driver or multi-SDK
evidence.

### P2-5 — No third-party use or performance result exists

All source and fixtures are project-authored.  No external developer,
usability study, matched PyOptiX/OWL task or registered timing exists.  The
result supports no ease, productivity, parity, no-overhead or speed statement.

## P3 findings

1. Successor adapters reuse private helpers from frozen compiler modules.
2. If native prepare succeeds but descriptor reading/validation fails, the
   Python constructor does not destroy the created token before raising.
3. The public output exposes raw `(u32, f32-bits, u32)` tuples rather than a
   typed FirstContact object, and the exact successful build log is absent.

## What remains valid after the final attack

The maximum safe result is:

> On one GTX 1070 configuration, the preserved native provider completed one
> five-query OptiX launch through source code that constructs a built-in sphere
> GAS and obtains a built-in sphere IS module.  The two miss rows and three
> ordinary sphere-entry rows match the project-authored analytic oracle for
> those exact simple inputs.  The actual provider SHA in that Home receipt
> equals the preserved authorized native SHA.

One of the three hits uses coincident spheres and returns the smaller
application ID, but order independence is not fully exercised.  None of the
five queries is a true tangent and none uses heterogeneous radii.

The result cannot support:

- exact semantic preservation for accepted sphere Callback IR;
- Goal5833 completion under the controlling plan;
- exactness over the accepted numerical domain;
- complete physical/runtime authority binding;
- exhaustive lifecycle or failure-path validation;
- generic-family, prospective-generalization, modern-RT-core, usability,
  performance, or Paper-App claims.

## Closure order

1. Repair or reject the ignored `tmin/tmax` semantics, then exhaustively mutate
   every populated Callback-IR, ABI and physical-schema leaf.
2. Load the exact target DSO explicitly or compare the cached handle's
   registered path/SHA against authority and the traversal receipt.
3. Carry canonical static/query/output/status projections to the native launch
   receipt and make field-ID rebinding observable and fail closed.
4. Normalize oracle inputs to the execution projection and replace the naive
   quadratic with a stable method plus a frozen conditioning/margin policy.
5. Replace the false tangent with a true hardware tangent, add heterogeneous
   radii, and add paired traversal-order fixtures without deleting old rows.
6. Reject extra query fields and complete malformed/nonfinite/range tests.
7. Exercise repeated lifecycle, cross-owner transitions and a real device
   status failure before output download.
8. Preserve exact generated wrapper/PTX/leaf/build artifacts and independently
   recount the repaired transaction.

These are Goal5833 repairs.  Goal5834 must not inherit Goal5833 as a closed
authority before P0 and P1 closure.  They require no performance measurement,
and Home Linux should be sufficient unless the repaired route cannot execute
there.
