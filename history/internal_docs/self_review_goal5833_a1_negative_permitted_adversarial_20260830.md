# Goal5833 A1 adversarial self-review — negative results permitted

Date: 2026-08-30  
Review posture: attempt to reject the completion claim; preserve negative results  
External review: not requested or authorized  

## Revised verdict

`P0=0 · P1=5 · P2=5 · P3=2`

`goal5833_complete_under_controlling_plan: false`

`fixed_five_query_home_observation_survives: true`

The earlier `P0=0 / P1=0` self-review and the structured result's
`COMPLETE_AT_BOUNDED_STATIC_BUILTIN_SPHERE_SCOPE` status are superseded as
completion judgements.  Their immutable bytes remain useful evidence of what
was actually run; they must not be rewritten to conceal this correction.

The final Home run still establishes a real, useful lower result: the exact
native used OptiX successfully, the generated route used the sphere build-input
and built-in-sphere IS construction in the reviewed source, and the five frozen
queries matched the independent analytic calculation.  No finding below
changes those five observed rows.  The findings instead show that the frozen
Goal5833 completion gate and the broader physical-authority claim were not
fully discharged.

## Checks performed in this pass

1. Re-read the controlling Goal5833--5836 plan, public Python lifecycle,
   physical schema, wrapper, prepared runtime, native prepare/execute path,
   Home runner, independent recount, result, technical report, and first
   self-review.
2. Re-ran the nine Goal5833-specific unit tests: `9/9 PASS`.
3. Rehashed the existing manifest: `26/26` named payloads still match.
4. Compared two compiled sphere authorities that differed only in all six
   `BuiltinSphereFieldIds`.
5. Constructed a target profile with the exact native but the literal
   `NOT_AN_OPTIX_VERSION`.
6. Compared the independent oracle on one accepted input before and after the
   public route's mandatory binary32 normalization.
7. Recounted the formal Home inputs: five queries and only one distinct radius.

These are post-result adversarial diagnostics, not preregistered experiments.
They may refute a claim, but must not be presented as prospective evidence.

## P1 findings

### P1-1 — Claimed field and buffer identities do not reach the execution edge

All six logical field identifiers were changed from their defaults to
`C2/R2/I2/Q2/O2/S2`.  The schema and plan identities changed, but both the ABI
and generated wrapper remained byte-identical:

```text
schema_equal        false
plan_equal          false
abi_equal           true
wrapper_equal       true
wrapper_bytes_equal true
```

The runtime receipt contains the authority nonce, native/PTX hashes, a native
descriptor, symbolic enum names, and `status_before_output`; it contains no
field identifiers and no digest of centers, radii, application IDs, queries,
status buffers, or output buffers.  The traversal semantic digest likewise
omits those data identities.  The independent recount recomputes an oracle
from the inputs written into the same JSON result, but it cannot establish that
those exact bytes populated the GPU buffers.

Therefore the current chain binds an authority label to an executable, but
does not bind the declared logical fields or concrete execution inputs to the
actual launch.  This directly misses the controlling plan's requirements that
center/radius buffers have identities and that GAS inputs plus output/status
buffers are identity-bound.  The six field-ID leaves are identity-bearing in
the certificate but non-bearing in the lowering and runtime receipt.

**Claim consequence:** withdraw any statement that Goal5833 proves complete
physical input/buffer identity.  The five-row result remains a source-traced
execution observation.

### P1-2 — A mandatory different-radius hardware fixture was never run

The controlling plan lists “different radii in one GAS” among the minimum
reader-checkable fixtures.  The final Home scene is:

```text
radii = [1.0, 1.0, 1.0, 1.0, 1.0]
distinct radius count = 1
```

The native descriptor reports `single_radius: false` and the native builder
uploads a radius array, which demonstrates representation and implementation
intent.  It does not demonstrate that heterogeneous radius values were
executed correctly.  No Goal5833 unit test supplies two different radii to the
GPU route.

**Claim consequence:** the exact frozen success gate is unmet.  This alone is
sufficient to retract the completion verdict, even if every other finding were
closed.

### P1-3 — Oracle and GPU do not share the accepted input projection

The public static/query validators first round centers, radii, starts, and ends
to target binary32.  The independent oracle instead performs its binary64
quadratic on the original Python values and rounds only the selected `t` at the
output boundary.  The five Home fixtures use exactly representable values, so
they are unaffected.  The mismatch is observable on an ordinary accepted,
non-degenerate axial hit:

```text
start  = (0, 0, 0)
end    = (1, 0, 0)
center = (0.20030000007, 0, 0)
radius = 0.00110000018

oracle on original values:   toi_bits = 1045166870
oracle on RTDL-f32 inputs:    toi_bits = 1045166869
```

The controlling plan also requires a frozen ULP bound and separation margin
for general well-conditioned fixtures, and rejection of near-degenerate values
outside that domain.  Neither policy is implemented or tested.  The public
validator accepts the wider finite domain.

**Claim consequence:** “exact against the oracle” is valid only for the five
frozen exact fixtures, not for the current accepted public input domain.

### P1-4 — The target SDK identity is a caller assertion, not a verified fact

`V4SphereTarget.from_native` hashes the native file but accepts any nonempty
`optix_sdk` string.  With the exact final native, the literal
`NOT_AN_OPTIX_VERSION` passed verification and sphere compilation.  It changed
the target/plan identity but left the ABI and wrapper unchanged.  The compiler
checks that the requested compute-capability tuple matches the authority text;
it does not validate the OptiX version against the supplied headers or the
loaded library.

The native descriptor is useful source-coupled evidence—it emits the same
OptiX constants used by the implementation—but it is still a self-report.  The
Python verifier only requires enum/build/geometry values to be nonnegative
integers, and the independent recount does not compare their exact values
against a separately pinned SDK authority.

**Claim consequence:** the result may report the independently observed Home
environment, but the general target authority cannot yet claim that its OptiX
SDK label is mechanically established.

### P1-5 — The frozen lifecycle contract is implemented but not evidenced

The Home run exercises prepare, one execute, close, and one use-after-close
rejection.  It does not exercise the `execute*` part of the frozen lifecycle or
the advertised process-bound, thread-bound, nonserializable, and nonreentrant
rules.  There is no Goal5833 test for two executions with different batches,
cross-thread use, cross-process use, serialization, concurrent reentry,
double-close, or close-during-execute.  The implementation contains checks for
several of these conditions, but code inspection is not the same as a passed
lifecycle test.

**Claim consequence:** report only the lifecycle transitions actually run;
do not claim that all frozen ownership/replay rules were validated.

## P2 findings

### P2-1 — `178 tests` is a regression count, not Goal5833 coverage

Only nine test methods are Goal5833-specific, and the hardware result contains
five queries in one launch.  The other tests are valuable non-regression
evidence but do not enlarge the sphere input, numerical, lifecycle, or physical
identity coverage.  Future summaries must state both numbers separately.

### P2-2 — This is a third hand-integrated template, not a generic family result

The sphere physical schema, ABI adapter, leaf adapter, wrapper, compiler,
prepared runtime, public lifecycle, and native provider are all sphere-specific.
The unfinished provider-neutral `FamilySchema` prototype is not connected to
this GPU route.  Goal5833 shows that the mechanism can be manually instantiated
again; it does not show that a new provider or application can be admitted
without editing trusted core code.

### P2-3 — The physical qualification is one Pascal configuration

The sole final functional execution is GTX 1070 / compute capability 6.1.  It
is behavioral OptiX evidence, not dedicated RT-core evidence, modern-RTX
portability, or multi-version compatibility.

### P2-4 — No exhaustive new-leaf liveness sweep exists

The project history shows why rehash/recompile checks alone are insufficient:
one declaration leaf can remain decorative while every surrounding seal moves.
Goal5833 adds a new physical schema and adapters but does not mutate every
populated semantic leaf individually.  P1-1 already demonstrates one class of
non-lowering-bearing leaves.  A complete sweep must classify every populated
leaf as decision-bearing or explicitly non-decision-bearing.

### P2-5 — No external-user, usability, or performance evidence was produced

All source, fixtures, and tests were authored inside the project.  There is no
third-party application author, matched PyOptiX/OWL task, usability study, or
registered timing.  No easy/productive/faster/parity/no-overhead statement is
supported.

## P3 findings

1. Successor adapters import private helpers from byte-frozen predecessor
   compiler modules.  This preserves custody but enlarges maintenance risk and
   the trusted computing base.
2. Exact final native/source identities and execution evidence are preserved,
   but the successful final native build stdout is not included.  This is an
   artifact-reproduction weakness, not a functional refutation.

## What remains scientifically valid

The following bounded sentence survives this review:

> On one GTX 1070 configuration, RTDL's hand-integrated static built-in-sphere
> First Contact route executed one five-query OptiX launch, and all five exact
> author-designed outputs matched a separately implemented analytic oracle;
> the reviewed native source constructs an OptiX sphere build input and obtains
> a built-in sphere intersection module.

It does **not** yet justify:

- Goal5833 complete under the exact owner-frozen gate;
- exact execution for the whole accepted input domain;
- complete physical buffer/field identity;
- a generic sphere-family compiler or prospective generalization;
- 3/4 coverage as more than coarse kind-presence implementation;
- modern RT-core, performance, usability, or Paper-App evidence.

## Required closure sequence

1. **Authority-binding repair:** define canonical static-input and per-execute
   projections; bind their digests and the logical field mapping into the
   native launch receipt; independently verify status/output commitment and
   make every claimed field-ID mismatch reject rather than merely reseal.
2. **Target-identity repair:** derive and pin the actual OptiX header/API
   version and actual device capability; compare exact enum/build/geometry
   values against that authority instead of accepting arbitrary strings and
   nonnegative integers.
3. **Numerical-domain repair:** make the independent oracle consume the exact
   normalized binary32 input projection; freeze a ULP/separation policy or
   narrow the public domain; add near-boundary hostile cases.
4. **Fixture closure:** add a true heterogeneous-radius GAS plus all named
   malformed/nonfinite/range cases, preserving the current five rows rather
   than replacing them.
5. **Lifecycle and liveness closure:** exercise repeated execution and every
   advertised ownership rule; sweep every populated new contract/schema leaf.
6. Re-run one functional-only Home transaction and independent recount.  No
   performance measurement or POD is needed for these repairs unless Home
   cannot execute the repaired built-in-sphere route.

Until those gates pass, Goal5834 may be designed but should not inherit
Goal5833 as a completed authority.  No CFR or external-review request is
created by this self-review.
