# Strict self-review — Goal5833 built-in sphere / First Contact

## Verdict

`P0=0 · P1=0 · P2=4 · P3=2`

Goal5833 is complete at the owner-frozen bounded scope. The result is suitable
as functional evidence that the RTDL protocol mechanism can be instantiated
over a third OptiX primitive-geometry class. It is not suitable as evidence of
prospective generalization, broad usability, RT-core performance, or RT-CCD.

## Hostile questions and answers

### Is this secretly a custom-AABB sphere implementation?

No. The final native was built against OptiX 9 headers and executed
successfully. The live prepared-token descriptor reports the sphere build-input
and primitive enums, a built-in IS module, no user intersection program, one
static GAS and one SBT record. The native source calls
`optixBuiltinISModuleGet` and sets `OPTIX_BUILD_INPUT_TYPE_SPHERES`. The
traversal receipt observes the expected program bundle and a nonzero bound
traversable at the successful `optixLaunch` edge.

### Can traversal order silently change an equal-time answer?

The compiler-owned any-hit enumerator ignores every candidate after updating a
payload-held minimum under `(ordered-f32(t), application_id, primitive_index)`.
The raygen wrapper invokes the verified closest-hit role only after traversal.
Two coincident spheres with IDs 9 and 2 returned ID 2 on hardware. This is one
fixture, not a proof of all floating-point edge cases, but it executes the exact
tie mechanism claimed.

### Is the oracle circular?

No. The oracle imports no RTDL module and independently solves the quadratic in
binary64. The result is also recomputed a second time inside a stdlib-only
recount script rather than trusting the oracle's output bytes. All five roots
used for exact comparison are reader-checkable binary32 values.

### Did this repair mutate frozen predecessors?

An intermediate implementation did, and the broad custody test caught it. The
final implementation restores all three predecessor identities exactly and
places the sphere ABI/codegen bridge in successor modules. The current hashes
match Goal5831/5832. The old Goal5758 test contained a stale pre-optimization
hash that contradicted the newer Goal5831 authority; only that test assertion
was updated, and the immutable Goal5758 result artifact was not rewritten.

### Is the public import actually public and quiet?

Users import `rtdsl.v4_sphere`. A fresh-process test replaces `ctypes.CDLL` and
`subprocess.Popen` with failing sentinels, imports the namespace and verifies
the standard First Contact source, while requiring that Numba codegen, the
OptiX compiler, prepared runtime and CuPy remain unloaded. Materialize and
prepare are the only transitions that load those layers. The namespace is
separate because changing byte-frozen `rtdsl.v4` would invalidate current
custody evidence.

## P2 limitations

1. **Third bounded instantiation, not prospective generalization.** The sphere
   route has a sphere-specific physical authority, wrapper, compiler adapter
   and native provider. It establishes that the mechanism can be ported to an
   OptiX built-in primitive, but it does not establish that an unseen family
   can be admitted without new core work. The separate provider-neutral
   `FamilySchema` plan is tested but does not itself lower this sphere program
   to GPU.

2. **One old GPU and no RT-core claim.** Functional evidence is from a GTX
   1070 (Pascal). OptiX traversal is real and fully bound, but the result says
   nothing about dedicated RT-core execution or modern RTX compatibility.

3. **Five author-designed exact fixtures.** Hit, miss, nearest, tie, tangent and
   tmax behavior are covered, but there is no randomized numerical campaign,
   wide-radius stress set, third-party input or external author. The exact
   output claim is limited to these five fixtures.

4. **No user or performance evidence.** The lifecycle is executable, but no
   external person authored an app through it and no timing was registered.
   It cannot support “easy,” “productive,” “faster,” “performance-neutral,” or
   “no overhead.”

## P3 limitations

1. The successor ABI and leaf adapters reuse private helpers from frozen
   compiler modules so those modules remain byte-identical. This is an explicit
   maintenance/TCB tradeoff, not evidence of a clean long-term extension API.

2. The exact successful native and source hashes are preserved, but the a3
   native build stdout was not captured into the final evidence directory.
   Rehashing and execution prove the binary used; build-log reproduction would
   improve artifact ergonomics but would not change the functional result.

## Failure lineage

- Initial runner attempts stopped before GPU on the Home CUDA include layout
  and on Numba's user-site exclusion. The final run retained isolation by using
  a temporary explicit Python prefix; it did not relax `python -s`.
- a1 passed before native-descriptor hardening and is nonfinal.
- a2 failed compilation with zero execution because of an unnecessary early C
  prototype. It was removed.
- a3 passed with the live descriptor but preceded custody repair and is
  nonfinal.
- a4 failed materialization with zero launch because the successor leaf adapter
  omitted three required evidence fields. The frozen return shape was copied
  exactly.
- a5 is the sole final result.

## Next scientific action

Goal5834 should add the fourth coarse class—built-in round-linear curves—and
use swept-sphere/capsule semantics. Its primary question is not whether another
enum can be added; it is whether the same payload/status/identity mechanism
survives curve endcaps, primitive parameterization and earliest-contact
selection without weakening the claim boundary. Goal5835/5836 remain blocked
until that curve path exists and is independently validated.

No CFR was created and no external review was requested, per owner direction.
