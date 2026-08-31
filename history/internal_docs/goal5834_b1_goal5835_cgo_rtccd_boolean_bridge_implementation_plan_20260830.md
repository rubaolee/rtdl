# Goal5834-B1 / Goal5835 implementation plan: bounded RT-CCD Boolean core for CGO

Date: 2026-08-30  
Status: `GOAL5834_B1_PREACTION__GOAL5835_REMAINS_UNAUTHORIZED`  
External review: not requested or authorized  
Performance measurement: forbidden in this plan

## 0. Controlling correction

The immediate objective is **not** to turn RTDL into a production collision
library or to prove that the closed-source OptiX built-in-curve provider is an
exact capsule solver for every floating-point input.

The immediate objective is to add one scientifically honest, understandable
CGO application:

> A sphere-approximated robot follows a piecewise-linear path. RTDL encodes the
> swept spheres as OptiX round-linear curves, traces obstacle-mesh edges, and
> returns whether any registered edge crosses the swept volume.

Goal5834's general First Contact status remains controlled by
`goal5834_final_adversarial_self_review_result_20260830.json`:

```text
INCOMPLETE__POSITIVE_PROVIDER_EVENT_PATH__CAPSULE_NUMERIC_DOMAIN_NOT_ESTABLISHED
```

This plan does not relabel that result. Instead, it introduces a narrower
bridge whose application output is only a Boolean. That is the output required
by the selected RT-CCD core and does not depend on exact time of impact or on
which equal/near-equal primitive wins.

This is a **CGO research-prototype plan**, not a product roadmap. The work is
split into one prerequisite and one conditionally authorized goal:

1. **Goal5834-B1 — bounded Boolean collision bridge.** Reuse the existing
   public built-in round-linear-curve lifecycle on canonical normalized,
   margin-separated fixtures and consume only per-edge hit/miss bits plus an
   aggregate collision Boolean.
2. **Goal5835 — Sui-derived RT-CCD edge-crossing case study.** This remains
   unauthorized until a separate controlling Goal5834-B1 result closes B1 and
   explicitly authorizes the registered-fixture mapping. If authorized, it
   encodes piecewise-linear swept robot spheres and obstacle edges using the
   bridge, validates them against an independent CPU predicate, and reports a
   finite research case study rather than a complete paper reproduction.

No B1 implementation or successful test implicitly authorizes Goal5835. The
authorization transition must be literal and append-only in the B1 closure.

## 1. Why this is the right CGO-sized target

The paper does not need a universal geometry theorem. It needs evidence that
RTDL's whole-callback-protocol mechanism can express a non-rendering workload
that was not among the original custom-AABB/triangle applications, while
retaining public lifecycle, physical identity, status-before-output, and an
independent application oracle.

The Boolean collision question removes two findings that are fatal to First
Contact but irrelevant to this application:

| Goal5834 counterexample | First Contact consequence | Boolean collision consequence |
|---|---|---|
| provider `t` differs by 725 float32 bit steps | exact TOI claim fails | both outputs are HIT; irrelevant |
| near-coincident capsules select different application IDs | stable nearest-ID claim fails | both outputs are HIT; irrelevant |
| float32 tie changes winner ID | ordering must be repaired | both outputs are HIT; irrelevant |
| large translation changes HIT to MISS | semantic failure | still fatal; must be neutralized by canonical normalization and tested |

The plan therefore attacks only what can change the RT-CCD Boolean. It does not
spend the remaining submission time proving unused TOI/ID properties.

## 2. Exact research scope

### 2.1 Reference predicate and executable semantics

For each robot sphere and each consecutive pair of trajectory samples, form a
closed capsule:

```text
Capsule(path_start, path_end, sphere_radius)
```

For each registered obstacle triangle edge, form a finite directed segment:

```text
Edge(edge_start, edge_end), t in [0,1]
```

The independent reference predicate on each registered fixture is:

```text
edge_hit[e] = OR over swept capsules c of intersects(Edge[e], Capsule[c])
collision   = OR over edges e of edge_hit[e]
```

The public B1 runtime makes the narrower executable promise
`provider_any_contact_bit`: it reports whether the pinned OptiX built-in curve
provider invoked closest-hit for each query. It does **not** claim that this bit
is a sound and complete mathematical capsule predicate for arbitrary inputs.
Only the frozen, independently qualified fixtures are compared with the
segment-capsule reference predicate. This distinction is essential because a
black-box provider plus a non-geometric admission path cannot establish a
universal capsule theorem.

The GPU produces the raw per-edge hit vector through the public curve
lifecycle. That vector is copied to the host and sealed before evaluation. The
host then performs the transparent aggregation
`collision = OR(per_edge_hit)`. The aggregate is therefore *derived from GPU
bits*, not claimed to be a GPU-produced reduction. The CPU oracle runs in a
separate evaluation process after the raw GPU receipt is sealed; it must never
enter the application worker or substitute its answer for a GPU bit.

Before execution, an evaluation-only preaction builder computes and seals the
expected fixture Booleans, but those bytes are not passed to the application
worker. After the raw GPU receipt is sealed, a fresh evaluator independently
recomputes them. Thus “expected before execution” and “oracle absent from the
worker” are both mechanically true.

### 2.2 Deliberately excluded cases

This first core is restricted to **edge-crossing collision**:

- both endpoints of every registered obstacle edge are outside every swept
  capsule by the frozen margin;
- every hit crosses a capsule boundary with a nondegenerate margin;
- every miss has a nondegenerate clearance margin;
- the offline evaluator establishes that the query is not axial/near-parallel
  to a contacted capsule centerline;
- the offline evaluator establishes that entry is separated from `t=0` and
  `t=1` by the frozen endpoint margin;
- face-interior containment with no registered edge crossing is outside scope;
- an edge starting inside a swept capsule is outside scope;
- initial robot/obstacle overlap is outside scope;
- exact tangency is outside scope.

These exclusions must appear next to the positive result. They are not bugs to
hide and are not silently repaired by a CPU collision check.

The start-inside exclusion is especially important. The old First Contact
route rejects it through pairwise geometry, whereas the new shape-only Boolean
worker deliberately does not compute that predicate. The offline evaluator
therefore marks such a row `INELIGIBLE` and emits zero B1 worker for it. A
complete collision detector would normally treat it as a collision or invoke a
separate initial-overlap predicate. Goal5835 implements only the
endpoint-disjoint edge-crossing core; a later complete Paper App may add a
separately named initial-overlap path.

### 2.3 Not claimed

This plan does not authorize:

- exact or approximate time-of-impact claims;
- stable collided-primitive identity claims;
- arbitrary capsule or curve correctness;
- full robot collision detection;
- complete Sui et al. reproduction;
- performance, acceleration, or CUDA/OptiX parity;
- third-party usability or prospective generalization;
- feature-complete support for OptiX curves.

## 3. Goal5834-B1 contract

### 3.1 Add one pure-Boolean specialization without a generic rewrite

Do not redesign the generic curve compiler, but do not disguise First Contact
as a Boolean protocol by returning `(hit,t,id)` and merely ignoring two fields.
Add one small app-neutral fixed specialization, for example:

```python
curve_any_contact_boolean_source()
```

Its semantic output is only one hit bit per query. Its roles are:

```text
make_ray    -> finite edge ray over t in [0,1]
closest_hit -> hit = 1
miss        -> hit = 0
finalize    -> status check, then Boolean commit
```

The implementation should reuse and factor the current First Contact compiler
components where their physical meaning is identical, including:

- the existing curve Callback-IR/code-generation infrastructure, without
  inheriting First Contact's `t`/ID result schema;
- `BuiltinCurveStaticInput`;
- `CurveMotionSegmentBatch`;
- the current public `compile -> materialize -> prepare -> execute* -> close`
  lifecycle;
- the built-in round-linear physical provider, target binding, GAS/SBT route,
  status-before-output logic, and receipt machinery.

The specialization must not carry provider `t` or primitive ID into the
application result. Those values may remain internal provider diagnostics, but
they are not protocol effects or result fields. A suitable app-neutral public
result is:

```python
V4CurveBooleanResult(
    per_query_hit: tuple[int, ...],
    any_hit: int,
    device_status: ...,
    physical_receipt: ...,
)
```

Goal5835 may label queries as obstacle edges and expose the transparent aliases
`per_edge_hit` and `collision`; the generic public path must not know robots or
edges.

The existing native `u32x3` carrier may be reused to avoid an irrelevant
runtime rewrite, but only slot 0 is application-semantic. Slots 1 and 2 must be
compiler-owned fixed diagnostics/sentinels, must be checked, and must not be
exposed as application `t` or ID. This is an implementation economy for a
research prototype, not evidence for a generic Boolean ABI.

This is a fixed constructor, not a new arbitrary Callback-IR-to-GPU compiler.
It may factor the existing curve compiler internally, but it must not duplicate
the provider or use a private native escape.

The audited minimal implementation route is:

- `v4_builtin_curve_standard_library.py`: add a one-field Boolean
  payload/output source and manifest;
- `v4_curve_physical_schema.py`: add one exact Boolean template, field/output
  contract, and structural-only f32/nonzero-query verifier;
- `v4_curve_optix_wrapper_codegen.py`: dispatch the Boolean layout, preserve
  the existing eight payload registers with deterministic zero padding before
  the compiler-owned hidden slots, and write deterministic zeroes to physical
  output lanes 1 and 2;
- `v4_public_builtin_curve.py`: add the fixed compile/prepared Boolean surface
  and public commitment properties;
- `v4_curve_prepared_runtime.py`: add `V4CurveBooleanResult`, status-first
  execution, semantic digest over raw per-query bits, and explicitly host-side
  OR;
- `v4_curve.py`: export the fixed source and public surface.

No change is expected in `v4_curve_callback_abi.py`,
`v4_curve_callback_numba_codegen.py`, `v4_curve_optix_compiler.py`, or native
C++/CUDA. A pure Boolean Callback source already passes the current frontend,
role verification, ABI compiler, and all four formal Numba leaf generators;
the known failure is confined to the trusted wrapper's current
“exactly-three-fields” First Contact assumption. If implementation evidence
contradicts this file boundary, B1 stops for reassessment rather than growing
into a native rewrite.

The B1 application worker must use **shape/type-only admission**: finite vec3
values, nonzero query segments, valid indices/counts, positive finite radii,
and the frozen normalized envelope. It must not call the current
`verify_curve_motion_segments`, `_segment_segment_distance2`, `_capsule_entry`,
or any other query-by-primitive geometric predicate. Those routines perform
the O(QxP) collision geometry whose execution is being assigned to RT cores.
Margin/domain qualification belongs only to the independent evaluator and
cannot affect, replace, or filter a sealed GPU result.

### 3.2 Canonical scene normalization

The one Boolean-changing counterexample is caused by large absolute
translation before float32 provider execution. Goal5834-B1 therefore performs
one uniform affine normalization, determined solely by the **static swept-volume
scene**, before binary32 projection. Query batches never redefine the static
coordinate frame.

Inputs that define the transform:

- every swept-path endpoint;
- every sphere radius, included as radius-expanded bounds.

Frozen construction:

1. compute the finite binary64 axis-aligned bounds of all curve endpoints,
   expanded by their associated radii;
2. choose each midpoint with `min + (max - min) / 2` as the binary64 `origin`;
3. choose `scale` as the smallest positive power of two not smaller than the
   largest absolute centered coordinate or radius;
4. transform points with `(x - origin) / scale` and radii with `r / scale`;
5. only then project transformed scene values to canonical binary32 for
   RTDL/OptiX;
6. transform every query using the same scene `origin` and `scale`, then project
   it to canonical binary32;
7. reject nonfinite values, zero scale, overflow, underflowed/nonpositive
   normalized radii, or queries outside the frozen canonical envelope. Never
   rebuild the transform merely to admit a later query.

A uniform translation and positive scale preserve the ideal mathematical
segment-capsule collision Boolean. The **normative evaluation oracle** operates
on the exact canonical binary32 scene/query bytes consumed by the provider,
using binary64 only to evaluate those frozen binary32 values. The original
binary64 fixture oracle is retained as a metamorphic sanity check; equality
between original and canonical-oracle Booleans is required for every paper
fixture but is not inflated into a theorem over arbitrary real inputs.

The following must be retained in the result:

- exact binary64 bits of `origin` and `scale`;
- original-input digest;
- normalized-input digest;
- original-input oracle Boolean;
- canonical-binary32 oracle Boolean;
- equality of the two oracle Booleans.

The receipt runner must bind the exact transform bits plus original and
normalized scene/query digests to the public static-input and query
commitments. Commitment framing must be shared with the runtime rather than
reimplemented privately in the case study.

This normalization is `O(P+Q)` data preparation. The application worker may
not perform an `O(PQ)` CPU collision prepass and must not use either oracle to
manufacture or filter the GPU output.

### 3.3 Margin-separated experimental domain

The independent oracle qualifies the frozen evaluation fixtures before GPU
output is inspected. For every canonical-binary32 edge/capsule pair it records:

- minimum segment-segment distance;
- capsule radius;
- the dimensionless decision separation
  `abs(distance_squared - radius_squared) /
  (distance_squared + radius_squared)`;
- whether both edge endpoints are outside the capsule;
- whether the offline equivalents of the frozen near-parallel and endpoint
  predicates qualify the row for the evaluation corpus.

The B1 evaluation margin is frozen here as **exactly `2^-10`**. It must not be
tuned after a mismatch. The evaluator also uses the already-published `2^-12`
direction-cross-ratio, contact-separation, and front-entry endpoint constants
to classify fixture eligibility; the shape-only public Boolean route does not
perform these pairwise tests. The stricter `2^-10` value is an independent
evaluation rule over the registered fixtures, not a new public admission
claim. A later mismatch or an evaluator rejection of an intended executable
fixture terminates B1; it does not authorize threshold shopping.

### 3.4 Ten author-designed fixture families, not a provider theorem

B1 deliberately uses a small, reader-auditable corpus appropriate to the CGO
case-study objective: exactly the ten named fixture families in Section 5.
The large-translation family contains two GPU executions, so the positive and
boundary fixture manifest must state the exact concrete execution and
evaluator-ineligible/malformed-prelaunch denominators rather than silently
count a pair as one.
There is no generated 128--512-row campaign in this goal.

Freeze the ten fixture families, all concrete canonical input bytes, expected
oracle Booleans, and target/provider identity before worker zero. The corpus is
author-designed convenience/adversarial evidence and is not representative.
The scientific requirement is zero accepted-row hit/miss mismatch on the
frozen concrete executions. Generalization-exam count remains exactly zero.

## 4. Goal5835 application layout

Only after Goal5834-B1 closure explicitly authorizes Goal5835, create:

```text
case_studies/sui_derived_edge_crossing_core/
    README.md
    bounded_piecewise_linear_core.py
    independent_edge_capsule_oracle.py
    fixtures.py
    run_functional_receipt.py
```

Recommended separation:

- `independent_edge_capsule_oracle.py`: stdlib-only segment-segment distance and
  Boolean aggregation over the exact canonical-binary32 input values, evaluated
  in binary64; must not import RTDL;
- `fixtures.py`: deterministic reader-checkable fixtures and normalization;
- `bounded_piecewise_linear_core.py`: paper-to-RTDL mapping and public lifecycle
  invocation;
- `run_functional_receipt.py`: functional execution and evidence serialization;
- `README.md`: source attribution, exact implemented subset, and exclusions.

The case-study manifest must freeze:

```text
paper_app_status: NOT_A_PAPER_APP
source_relation: SUI_DERIVED_MAPPING__AUTHOR_DESIGNED_FIXTURES
generalization_exam_count: 0
```

Only Goal5836 may reconsider Paper App status, and only after adding a
paper-source fixture, author-code same-input comparison, and modern-GPU
functional evidence. B1/Goal5835 success alone cannot promote it.

No Sui-, robot-, trajectory-, or obstacle-specific branch may be added to
`src/rtdsl/**` or `src/native/**`. Generic code may change only if a truly
app-neutral Boolean projection is both necessary and smaller than the app
adapter.

## 5. Mandatory fixtures

Freeze these before the first GPU result:

1. **single crossing hit** — one obstacle edge crosses one swept capsule;
2. **clear miss** — all registered edges have clearance larger than the frozen
   margin;
3. **round-endcap hit** — the edge crosses the rounded path endpoint but remains
   outside the cylindrical side region;
4. **piecewise-linear OR** — multiple path segments and multiple obstacle
   edges, exactly one robust crossing;
5. **multiple robust hits** — multiple provider candidates, application output
   remains only `collision=True`;
6. **large-translation metamorphic pair** — a base fixture and a translated /
   power-of-two-scaled copy normalize to the same registered input and must
   produce the same Boolean (two concrete GPU executions);
7. **face-interior-only boundary** — expected miss under the implemented
   edge-crossing predicate and explicitly identified as a method boundary;
8. **ordinary provider-`t` disagreement regression** — both routes are Boolean
   HIT although exact `t` differs;
9. **near-coincident ID disagreement regression** — Boolean HIT survives the
   unstable winner ID;
10. **float32 tie-ID disagreement regression** — Boolean HIT survives the
    unstable tie winner.

Three boundary tests are frozen outside the ten executed fixture families.
Start-inside and near-tangent/near-parallel are classified `INELIGIBLE` by the
offline evaluator and launch zero B1 worker. Malformed shape/type input is the
only one required to fail in the public route before launch. All are reported
as unsupported, and none may be converted into a CPU-produced result. Provider
`t`/ID differences in fixture families 8--10 are expected and must not be
rewritten as exact agreement.

## 6. Tests that matter for the paper

Do not spend the implementation window on production-quality API polish. The
minimum high-value test set is:

### 6.1 Mapping correctness

- each robot sphere/path segment becomes exactly one registered curve capsule;
- each obstacle triangle contributes the declared directed edge set with a
  deterministic deduplication rule;
- query-to-edge and curve-to-path identities remain reconstructable;
- Boolean aggregation is OR over per-edge GPU hit bits.

### 6.2 Oracle independence and non-ceremonial GPU work

- the oracle source contains no RTDL import or native call;
- the application worker contains no pairwise CPU geometry predicate and does
  not call `verify_curve_motion_segments`;
- the raw per-edge GPU vector is sealed before the independent oracle process
  starts;
- original and normalized oracle Booleans match;
- every frozen fixture has an exact expected Boolean before GPU execution;
- margin and endpoint-disjoint qualifications are serialized.

### 6.3 Protocol evidence

Do not rerun the complete old 40/40 campaign, but do not assume that a new
Boolean constructor is live merely because the First Contact constructor was.

1. Prove every inherited ABI leaf is byte-identical to the old authority.
2. Enumerate every new or changed Boolean delta leaf.
3. Mutate each delta leaf separately and require a decision or output change.
4. At minimum, closest-hit bit, miss bit, final Boolean commit, buffer binding,
   and status-before-output must all be decision-bearing.

### 6.4 Functional GPU gate

- public lifecycle only;
- built-in `OPTIX_PRIMITIVE_TYPE_ROUND_LINEAR`, no custom intersection;
- true OptiX traversal receipt;
- raw per-edge GPU vector preserved before host OR and before oracle launch;
- every frozen fixture host-OR Boolean equals the independent oracle Boolean;
- repeated execution and reversed query order preserve the aggregate result;
- zero performance samples.

Home GTX 1070 is sufficient for the first functional gate because the same
native built-in curve provider already ran there. The main execution risks are
wrong payload-register positions, uninitialized physical padding lanes,
remaining hard-coded First Contact shape checks, and a genuine provider
Boolean mismatch. A paid RTX POD is not needed until Goal5836's same-input
author comparison or a later modern-GPU functional check.

## 7. Execution order and time budget

This is a research-app sprint, not a new runtime programme.

### Phase A — contract, oracle, fixtures (about 2–3 hours)

1. Bind the workspace path and record the broken Git object state; make no
   commit-identity claim.
2. Implement the app-neutral Boolean source, independent oracle, and batch
   normalizer without creating the Goal5835 case-study directory.
3. Freeze the ten reader-checkable fixture families, exact concrete
   denominators, exact `2^-10` evaluation margin, expected Booleans,
   target/provider identity, and the outcome branches below.
4. Prove inherited-leaf identity and run the Boolean-delta leaf mutations.
5. Run CPU-only and admission tests.

### Phase B — public RTDL integration (about 3–5 hours)

1. Map normalized generic capsules to `BuiltinCurveStaticInput`.
2. Map normalized generic queries to the new shape-only Boolean batch; do not
   reuse `CurveMotionSegmentBatch` if it invokes pairwise geometry.
3. Execute through the new `curve_any_contact_boolean_source()` public fixed
   constructor; do not project a First Contact tuple in the application layer.
4. Seal the raw per-edge GPU vector, then perform transparent host OR.
5. Launch the independent evaluator only after the raw receipt is sealed.

### Phase C — local/Home functional closure (about 2–4 hours)

1. Run Goal5833/5834 regressions plus the new app tests.
2. Build a fresh Home native from the exact source projection.
3. Execute the frozen fixtures once; no replacement or threshold change.
4. Recount results without importing the RTDL execution route.
5. Write one B1 result, one strict self-review, and an explicit authorization
   or refusal for the registered-fixture Goal5835 mapping.

Expected total: one focused implementation day plus up to one additional day
for the clean Home closure. If the work begins to require a generic curve
compiler rewrite, arbitrary numerical proof, or performance infrastructure,
the implementation has left the authorized scope and must stop.

## 8. Predeclared outcome branches

### Branch A — positive registered-fixture evaluation

All frozen GPU Booleans equal the independent oracle, including the normalized
large-translation metamorphic pair.

Allowed B1 status:

```text
GOAL5834_B1_COMPLETE_REGISTERED_FIXTURE_EVALUATION
```

Allowed paper sentence:

> On one pinned OptiX provider, RTDL's public round-linear-curve lifecycle
> produced per-edge hit vectors whose host-OR collision results matched an
> independent canonical-float32 segment-capsule oracle on every pre-frozen
> executed fixture. The small author-designed corpus is a case study, not a
> representative sample or a generalization test.

The B1 closure may then explicitly authorize Goal5835's registered-fixture
Sui-derived mapping. It may not call B1 itself a completed robot application.

### Branch B — provider Boolean mismatch

Any normalized, in-domain fixture differs from the CPU oracle.

Required status:

```text
TERMINAL_NEGATIVE__BUILTIN_CURVE_BOOLEAN_UNRELIABLE_FOR_REGISTERED_CORE
```

Do not change the margin, drop the fixture, or add a fixture-specific branch.
For the submission, retain curve kind-presence evidence and omit the RT-CCD app
claim. A later goal may implement the same capsule predicate through RTDL's
custom-primitive route, where the intersection algorithm is controlled by the
project.

### Branch C — B1 admission/evaluator failure

If any of the ten intended executable fixture families fails the frozen
offline qualification, is rejected by the Boolean route after qualification,
or disagrees with the independent oracle, B1 ends with:

```text
TERMINAL_NEGATIVE__B1_REGISTERED_FIXTURE_NOT_EXECUTABLE_AS_FROZEN
```

Do not repair and continue within B1. Any B2 repair must inherit the exact same
immutable fixtures and accept its result unconditionally. Do not bypass the
public API or call the native provider directly.

## 9. Claim impact for CGO

If Branch A passes and a later Goal5835 mapping also passes, the case study
strengthens exactly one weak part of the current submission:

- before: four leaf kinds are present, but sphere/curve examples are entirely
  author-designed qualification tasks;
- after: the curve route has executed and checked a Sui-derived, non-rendering
  robotics mapping on a small frozen set with an independently checkable
  application Boolean.

It does **not** produce prospective generalization or external-user evidence.
Its contribution is a bounded case study showing that the protocol mechanism
can be instantiated with a materially different Boolean callback/output shape
and a concrete repurposed-RT mapping on those frozen instances. It does not
establish support for an input class or for unseen robot applications.

The paper must still say:

- author implemented all RTDL apps;
- the RT-CCD result is a bounded edge-crossing core, not full collision
  detection;
- inputs are normalized and margin-separated;
- exact TOI/ID, performance, and general curve correctness are not evaluated;
- First Contact's general capsule-semantic goal remains incomplete.

## 10. Instructions for the next Extra High model

**Mode decision:** Extra High is appropriate. The task crosses Callback source,
physical schema, trusted wrapper layout, public lifecycle, evidence separation,
and claim boundaries; a locally plausible change can silently misalign payload
registers or let the CPU precompute the answer. The mode is being used for
cross-layer correctness, not to broaden the prototype into production work.

Read, in order:

1. this plan;
2. `goal5834_final_adversarial_self_review_result_20260830.json`;
3. `self_review_goal5834_final_adversarial_20260830.md`;
4. `goal5833_goal5836_sphere_curve_rtccd_owner_replan_20260830.md`, only for
   the paper/source mapping and Goal5836 promotion rule;
5. the current `v4_curve` public implementation and the four preserved numeric
   counterexamples.

Then begin with Phase A. Do not create the Goal5835 case-study directory until
B1 is closed and explicitly authorizes it. Do not reopen universal First
Contact semantics, collect performance data, build general software
infrastructure, or send anything for external review without explicit owner
approval.

The first checkpoint should occur only after the CPU oracle, normalization,
fixtures, expected Booleans, and outcome branches are frozen and their tests
pass. At that checkpoint the implementation should be ready to connect to the
existing public curve lifecycle without a design decision remaining.
