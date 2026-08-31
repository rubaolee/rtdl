# Owner replan: Goals 5833--5836 built-in sphere, built-in curve, and RT-CCD

Date: 2026-08-30  
Status: controlling owner-directed implementation plan  
External review: not requested and not authorized by this document  
Performance measurement: not part of these four goals

## 0. Controlling decision

The owner selects the following four-goal route:

1. **Goal5833:** add an app-neutral public OptiX built-in-sphere route and a
   small `First Contact` application with an independent CPU oracle.
2. **Goal5834:** add an app-neutral public OptiX built-in round-linear-curve
   route and validate swept-sphere/capsule semantics.
3. **Goal5835:** implement the piecewise-linear core of Sui, Sentis, and
   Bylard's RT-CCD: encode a sphere-approximated robot's swept motion as
   curves, trace directed obstacle-mesh edges, and return collision booleans.
4. **Goal5836:** add paper/source provenance, a same-input author-code
   comparison, and modern-GPU functional evidence; upgrade the result to a
   Paper App only if every gate below passes.

This plan append-only supersedes the earlier numbering in which Goal5833 was
reserved for a generic `FamilySchema` compiler and Goal5834 for a provider ABI.
That genericity programme remains scientifically valuable, but it is not the
controlling definition of Goals5833--5836 after this owner direction.

The partially created files `src/rtdsl/v4_family_schema.py` and
`tests/goal5833_family_schema_compilation_plan_test.py` are classified as an
**unfinished, noncontrolling generic-core prototype**. Fourteen isolated tests
currently pass, but the prototype is not integrated into a GPU route, is not a
Goal5833 result, is not generalization evidence, and is not a prerequisite for
the four goals below. It may be resumed under a separately named later goal.

## 1. Why this route is scientifically useful

The pinned OptiX-9 surface has four leaf-primitive kinds in the project's
current taxonomy:

1. custom primitives;
2. built-in triangles;
3. built-in curves; and
4. built-in spheres.

RTDL currently has public GPU evidence for two of those four kinds: custom
primitives and built-in triangles. Sphere and curve are therefore not arbitrary
feature additions. They close the two missing leaf-kind-presence cells and,
more importantly, force the callback-protocol mechanism across two new
platform-produced intersection interfaces.

The claims must remain precise:

- completing Goal5833 may establish built-in-sphere public-path support;
- completing Goal5834 may establish the tested round-linear subset of the
  built-in-curve class and kind-presence coverage of 4/4 leaf classes;
- completing Goal5835 may establish one paper-derived RT-CCD kernel;
- completing Goal5836 may establish a bounded Paper App;
- none of these alone establishes arbitrary Callback IR, arbitrary OptiX
  topology, arbitrary curve variants, prospective unseen-app generalization,
  external-user usability, or performance parity.

## 2. Goal5833 -- public built-in sphere plus First Contact

### 2.1 Objective

Implement a stable public lifecycle for static OptiX built-in spheres:

```text
verify source -> compile protocol -> materialize -> prepare -> execute* -> close
```

The route must be app-neutral. `src/rtdsl/**` and `src/native/**` may know
about sphere centers, radii, primitive identity, typed hit channels, metadata,
and lifecycle, but must not contain Sui-, robot-, trajectory-, or collision-
paper-specific dispatch.

### 2.2 Public static input and query contract

Static scene:

```text
Sphere {
    center: vec3f32;
    radius: f32;          // finite and strictly positive
    application_id: u32; // unique in one static scene
}
```

Query:

```text
MotionSegment {
    start: vec3f32;
    end: vec3f32;
}
```

The normalized ray is `origin=start`, `direction=end-start`, `tmin=0`, and
`tmax=1`. The formal Goal5833 domain requires finite inputs, a nonzero motion
direction, and a start point strictly outside every sphere. Initial penetration
is deliberately excluded because OptiX's hollow/back-face behavior requires a
separate policy rather than an accidental convention.

Public output:

```text
FirstContact {
    hit: u32;             // 0 or 1
    toi_bits: u32;        // IEEE-754 binary32 bits, miss sentinel = 1.0f
    application_id: u32; // miss sentinel = U32_MAX
}
```

For multiple candidates the required order is the lexicographic minimum of
`(ordered_float32(t), application_id, primitive_index)`. This avoids relying on
an unspecified equal-distance traversal order. The compiler-owned wrapper may
enumerate candidates with any-hit, retain the canonical minimum, and invoke
the verified closest-hit or miss role exactly once.

### 2.3 Physical requirements

The native receipt must prove all of the following from actual runtime facts:

- `OPTIX_BUILD_INPUT_TYPE_SPHERES` was used;
- center and radius buffers have the declared counts, strides, and identities;
- the primitive flag is sphere;
- the intersection module came from `optixBuiltinISModuleGet` for sphere;
- there is no user-authored sphere intersection program;
- motion blur is disabled in Goal5833;
- one static GAS and the declared SBT topology were used;
- callback, generated wrapper, native binary, GAS inputs, and output/status
  buffers are identity-bound;
- device status is copied and accepted before any output is consumed;
- prepare/execute/close ownership, replay, thread/process, and use-after-close
  rules match the public lifecycle.

### 2.4 First Contact illustrative application

The application is intentionally understandable without robotics background:
"A point moves along a straight segment among spherical obstacles; which
obstacle is hit first, and when?"

Minimum reader-checkable fixtures:

1. exact-root hit: a segment and sphere chosen so the entry `t` is exactly
   representable in binary32;
2. miss by transverse separation;
3. miss because contact lies beyond `tmax=1`;
4. two geometrically coincident spheres with different application IDs,
   proving the stable ID tie-break;
5. a nearer sphere with a numerically larger ID, proving time precedes ID;
6. different radii in one GAS;
7. tangent contact with a frozen tolerance policy;
8. malformed/nonfinite/zero-radius/duplicate-ID/inside-start inputs that fail
   before GPU launch.

### 2.5 Independent oracle

The CPU oracle must not import RTDL compiler, wrapper, native runtime, or
application output code. For each query/sphere pair it solves the standard
quadratic in binary64:

```text
m = start - center
d = end - start
a = dot(d,d)
b = 2*dot(m,d)
c = dot(m,m) - radius*radius
disc = b*b - 4*a*c
```

It selects the first root in `[0,1]`, then applies the same `(t,id,index)`
ordering. Exact-root fixtures require bit equality. General well-conditioned
fixtures use a preregistered binary32 ULP bound and a frozen separation margin;
near-degenerate values outside that domain are rejected rather than interpreted
after seeing the GPU result.

### 2.6 Goal5833 success gate

Goal5833 completes only if:

- the public Python path uses no private loader or manual PTX/SBT escape;
- the native built-in-sphere path and prepared lifecycle are implemented;
- all positive, negative, lifecycle, identity, and oracle tests pass;
- a clean local/Home Linux run provides behavioral true-OptiX evidence if the
  available SDK supports the exact frozen route;
- no performance sample is collected;
- the report states that this is an author-designed known qualification, not a
  prospective generalization exam.

If true-OptiX execution cannot be obtained locally, Goal5833 remains
implementation-complete but hardware-unqualified; it may not be called a
completed public GPU route until Goal5836 supplies the missing execution.

### 2.7 Goal5833 claim ceiling

Allowed after all gates pass:

> RTDL exposes a bounded public callback-protocol lifecycle for static OptiX
> built-in spheres and exactly executes a first-contact kernel against an
> independent oracle.

Forbidden:

- complete RT-CCD reproduction;
- curve support;
- arbitrary sphere workloads or degenerate geometry;
- a third-party user result;
- prospective/unseen generalization;
- performance, no-overhead, or CUDA/OptiX parity.

## 3. Goal5834 -- public built-in round-linear curves

### 3.1 Objective

Implement an app-neutral public route for the **round-linear subset** of OptiX
built-in curves. The provider contract must describe curve control points,
width/radius data, segment indices, endcap policy, primitive identity, and
typed hit channels without embedding RT-CCD application logic.

### 3.2 Supported physical subset

Goal5834 supports exactly:

- `OPTIX_BUILD_INPUT_TYPE_CURVES`;
- `OPTIX_PRIMITIVE_TYPE_ROUND_LINEAR`;
- finite piecewise-linear centerlines;
- strictly positive finite radius/width values;
- round endcaps;
- static GAS, trace depth one, callable depth zero;
- one ray type and the frozen SBT topology.

It does not imply flat-linear, quadratic, cubic, Catmull-Rom, Bézier, motion
blur, instancing, or multi-trace continuation support.

### 3.3 Reference semantics and oracle

A round-linear curve segment with radius `r` is treated as the capsule/swept
volume of a sphere of radius `r` moving along the segment. The primary oracle
computes the minimum squared distance between a query segment and every curve
centerline segment in binary64 and compares it with `r^2`, with a preregistered
margin for non-exact floating cases.

Mandatory fixtures:

1. side-wall hit;
2. complete miss;
3. hit only on a round endcap;
4. multiple curve segments with a unique earliest contact;
5. equal-contact candidates with a stable application-ID tie-break;
6. varying radii where supported by the frozen input representation;
7. invalid segment indices, zero-length geometry, nonfinite coordinates,
   nonpositive radii, and inconsistent counts, all rejected before launch.

### 3.4 Physical and liveness requirements

Receipts must prove the curve build input, round-linear primitive type, round
endcap setting, built-in intersection module, input-buffer identities, and
absence of a custom curve IS. Every populated curve-specific contract leaf
must be mutated once; the admission verdict must change or the leaf must be
explicitly classified non-decision-bearing before the result is reported.

### 3.5 Goal5834 success gate and claim ceiling

The same public lifecycle, status-before-output, identity, ownership, and
clean-Linux requirements as Goal5833 apply.

Allowed claim:

> RTDL supports the tested OptiX round-linear built-in-curve subset and the
> project's public GPU routes now instantiate all four leaf-primitive classes
> in the pinned taxonomy.

The phrase `4/4` means **kind presence only**. It must always be accompanied by
the explicit round-linear subset and must never be expanded to complete support
for every curve primitive, build-input kind, topology, or RT application.

## 4. Goal5835 -- Sui RT-CCD piecewise-linear core

### 4.1 Source authority

Primary paper:

Sizhe Sui, Luis Sentis, and Andrew Bylard. 2025. *Hardware-Accelerated Ray
Tracing for Discrete and Continuous Collision Detection on GPUs*. ICRA 2025,
16133--16139.

Primary author implementation:

```text
repository: https://github.com/Ssz990220/RTCollisionDetection
commit:     bacbf77a612bba3e6e8f7a464fa0fa2c67298ac7
license:    MIT
```

Both the paper bytes and the source commit/license must be pinned and hashed in
the Goal5835 manifest before application result inspection.

### 4.2 Exact implemented research subset

Goal5835 implements the paper's **piecewise-linear edge-intersection core**:

1. represent one or more robot-link spheres along a finite piecewise-linear
   trajectory;
2. encode each sphere's swept volume as round-linear built-in curves/capsules;
3. obtain directed finite rays from the obstacle triangle mesh's edges;
4. trace those edge rays against the swept-volume GAS;
5. aggregate a query-local collision boolean with explicit device status;
6. stop at the paper's actual edge-intersection predicate.

The app may use the Goal5833 sphere route for discrete endpoint/pose checks and
the Goal5834 curve route for continuous sweep checks, but the two results must
remain separately observable. No Sui- or robot-specific branch may enter
`src/rtdsl/**` or `src/native/**`; those semantics belong under
`Paper-reproduction-apps/**`.

### 4.3 Explicit exclusions

Goal5835 is not initially a complete Franka/62-sphere reproduction. It excludes
unless separately implemented and evidenced:

- full URDF ingestion and robot forward kinematics;
- the paper's complete batching/stream/compaction system;
- quadratic/cubic B-spline trajectories;
- every paper environment and scale;
- a proof of exact sphere-versus-triangle continuous collision;
- the paper's reported speedups;
- collision configurations detected only through triangle-face interior with
  no edge/swept-volume intersection.

### 4.4 Independent oracle and mandatory boundary example

For each obstacle edge and each piecewise-linear sphere path segment, the
oracle evaluates whether the segment--segment minimum distance is at most the
sphere radius. Query collision is the OR of these exact registered predicates.

Mandatory cases:

- an obstacle edge crossing the capsule: expected hit;
- complete separation: expected miss;
- contact only at the rounded path endpoint: expected hit;
- multiple path segments and obstacle edges: expected exact aggregate boolean;
- a face-interior-only penetration that touches no registered edge: expected
  miss under the implemented paper predicate, published as a method boundary
  rather than silently rescued.

### 4.5 Goal5835 success gate

- Goal5833 and Goal5834 public routes are used without private escape;
- the app mapping is frozen before GPU output is observed;
- paper-derived algorithm ownership is separated from generic RTDL code;
- every registered fixture matches the independent predicate oracle;
- no core special case is introduced to make a fixture pass;
- no performance result or full-paper claim is made;
- the result is named `paper-derived piecewise-linear RT-CCD core` until
  Goal5836 upgrades it.

## 5. Goal5836 -- same-input author comparison and Paper-App gate

### 5.1 Objective

Turn the Goal5835 paper-derived core into a bounded Paper App only if the
author implementation, RTDL route, and independent oracle can consume an
exactly defined common input on a modern NVIDIA GPU.

### 5.2 Preexecution freeze

Before worker zero, freeze:

- paper PDF, author repository commit, license, and selected source files;
- exact common input bytes and provenance;
- mapping from common input to author structures and RTDL structures;
- expected output predicate and comparison rule;
- GPU/driver/CUDA/OptiX/toolchain identities;
- exact source trees, generated sources, native binaries, and public entrypoint;
- worker count and rule that no failing case is replaced or dropped;
- claim branches for match, mismatch, author-build failure, mapping failure,
  infrastructure failure, and unsupported capability.

### 5.3 Modern-GPU execution

Use a modern RTX POD only after every local materializer, oracle, static,
hostile, lifecycle, and zero-worker preflight test is green. The POD run is
functional correctness only. No timing region or performance statistic is
authorized by this plan.

The execution must provide:

- actual author binary/result on the frozen common input;
- actual RTDL public-route sphere and/or curve result as declared;
- independent CPU oracle result;
- true-OptiX receipts proving built-in sphere/curve paths rather than custom
  intersection substitutions;
- exact status/output order and complete source/native/toolchain custody;
- an independent raw recount that imports neither executable route.

### 5.4 Paper-App promotion rule

Promote to a bounded Paper App only when all of these are true:

1. the paper and official author source are pinned;
2. the selected algorithm/input/output mapping is explicit and faithful;
3. the author route executes successfully on the same input;
4. the RTDL route uses only the public lifecycle;
5. author, RTDL, and independent oracle agree under the frozen rule, or any
   scientifically meaningful difference is explicitly resolved without
   changing inputs or rules after observation;
6. source, generated code, native code, primitive type, built-in IS, and result
   identities are bound and independently recounted;
7. limitations and negative cases remain visible;
8. no paper performance claim is inferred from functional execution.

If any item fails, retain the exact strongest lower status:

- `paper-derived core implemented`;
- `same-input mapping established but author execution unavailable`;
- `functional mismatch observed`;
- `infrastructure-invalid without replacement`;
- or `unsupported by current RTDL capability`.

No wording change may convert a failed promotion gate into a Paper App.

### 5.5 Goal5836 allowed final claim

If every promotion gate passes:

> RTDL reproduces a bounded, same-input piecewise-linear RT-CCD core from Sui
> et al. through its public built-in-curve/sphere protocol paths on a modern
> RTX GPU, with author-route and independent-oracle agreement.

This remains a bounded correctness claim. It is not full-paper reproduction,
performance reproduction, arbitrary-app generalization, or third-party
usability evidence.

## 6. Dependencies, parallelism, and estimated effort

Critical dependency chain:

```text
Goal5833 sphere provider
        |
        +------------------+
        |                  |
Goal5834 curve provider    |  Goal5835 app provenance/oracle scaffold
        |                  |
        +------------------+
                 |
              Goal5835 integration
                 |
              Goal5836 modern-GPU same-input gate
```

Parallel opportunities:

- while Goal5833 native/Python work proceeds, another line can pin Goal5835
  paper/source/license and build the independent segment--capsule oracle;
- Goal5834 native provider work can run in parallel with Goal5833 First Contact
  documentation/hostile fixtures after shared callback/hit records freeze;
- Goal5835 author-input adapter and RTDL app wrapper can run in parallel only
  after Goal5834 public input/output contracts freeze;
- Goal5836 bundle/materializer and independent recount can be prepared while
  local Goal5835 functional tests run, but no POD worker may start early.

Current realistic engineering estimates, excluding external review:

```text
Goal5833: 1--2 focused engineering days + local/Home functional run
Goal5834: 2--4 focused engineering days + local/Home functional run
Goal5835: 2--4 days for bounded app, oracle, fixtures, and integration
Goal5836: 1--2 days for freeze/bundle/author mapping + about half a POD day
```

The estimates are forecasts, not deadlines or claim evidence. Any requirement
to add an application-specific branch to generic source is a design failure,
not permission to hide the branch to meet the estimate.

## 7. Global honesty rules for all four goals

1. A third or fourth primitive path is implementation coverage, not by itself
   prospective generalization.
2. `4/4` always means leaf-kind presence in the pinned taxonomy, not complete
   category or application coverage.
3. A paper-derived kernel is not a Paper App until the Goal5836 promotion rule
   passes.
4. CPU oracle, RTDL route, and author route must remain independently
   implemented and independently identified.
5. Platform validation success does not prove application semantics; RTDL's
   contribution remains the whole-protocol contract and prelaunch rejection of
   mismatched intent/implementation.
6. Fail-closed inputs must be scoped to semantic/load-bearing facts; optional
   metadata may not terminate science unless the frozen contract says it is
   load-bearing.
7. No performance, ease-of-use, productivity, external-human, arbitrary-app,
   or full-paper claim is authorized by this plan.
8. External review remains owner-controlled. No review is sent without an
   explicit later owner command.

## 8. Immediate next action after the mode change

Resume Goal5833 at the implementation boundary:

1. inventory the existing built-in-triangle public lifecycle and native
   pipeline extension points;
2. freeze the `SphereHit`, static-input, query, output, tie-break, and receipt
   records;
3. implement Python/IR/schema/compiler and native sphere provider in separate
   file-ownership lanes;
4. implement the independent First Contact oracle and hostile fixtures;
5. integrate, run focused regressions, and stop only at a clean local/Home
   functional checkpoint or a concrete POD requirement.

