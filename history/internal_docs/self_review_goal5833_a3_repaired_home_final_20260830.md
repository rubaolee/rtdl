# Strict self-review — Goal5833 A3 repaired Home final

Date: 2026-08-30  
Posture: negative results are acceptable; unsupported completion is not  
External review: not requested and not authorized

## Verdict

`P0=0 · P1=0 · P2=4 · P3=2`

`goal5833_complete_at_bounded_static_builtin_sphere_scope: true`

`goal5833_complete_as_general_family_compiler: false`

`prospective_generalization_evidence_added: false`

`performance_or_usability_evidence_added: false`

The technical implementation and Home functional evidence contain no remaining
known P0/P1 at the exact claim scope below. One review P1 about independent
verification is closed by refusing the overclaim: the stdlib verifier
reconstructs archived projections, member identities, receipts and the oracle,
but does not independently parse the public Callback DSL into IR or prove the
compiler semantically correct. A product-compiler replay demonstrates exact
reproducibility, not independent correctness.

## What was independently attacked

Three read-only adversarial lines were run against the exact v8 candidate:

1. exact-Fraction and high-precision numerical/domain reconstruction;
2. native, physical, traversal, generated-artifact and compiler-inventory
   reconstruction, including coordinated mutation attacks; and
3. source-capsule, evidence-custody, claim and supersession review.

The numerical line did not import RTDL's oracle. It reproduced all five GPU
rows, the exact tangent, exact-`tmax`, and just-outside-`tmax` roots. It also
checked the sign algebra in the square-root-free front-entry comparator.

The native line independently rehashed accepted and hostile manifests and
reconstructed both executable records. It also proved an important negative:
coordinately rewriting bytes and all author-controlled projections can still
produce an internally valid inventory. Therefore content hashes cannot be
presented as an independent compiler-provenance proof.

The custody line rechecked all 377 source members, all 120 final evidence
members, every size/hash, the formerly missing Goal5749 dependencies, all test
logs and the failure lineage.

## P2 limitations

### P2-1 — The source capsule is not a hermetic environment

The 377-member archive is source-complete under the declared Home environment.
It still relies on the external Python/Numba/NumPy environment, CUDA/NVRTC,
OptiX SDK, compiler, system headers and system libraries. “Source-complete”
must not become “offline hermetic reproduction.”

### P2-2 — The numerical domain is outcome-informed

The original hardware run exposed an exact-tangent MISS. A later hostile audit
then exposed exact/near trace-endpoint ambiguity. The final exact-tangent,
discriminant and endpoint guards are repairs made after those observations.
They are legitimate bounded engineering repairs, not a preregistered
generalization experiment. The failures and ordering are disclosed.

### P2-3 — `2^-12` is not a cross-device theorem

The discriminant and endpoint margins are conservative frozen admission
limits. They establish the tested public domain and make ambiguous inputs fail
closed. They do not prove that every OptiX version or GPU agrees numerically
throughout the remaining domain. Only one GTX 1070/OptiX 9 qualification is
available.

### P2-4 — The evaluation is author-designed and bounded

The five main rows, three repeated rows, hostile device-status program and all
unit tests were designed by the authors. They establish mechanism liveness and
the bounded First Contact path. They do not establish defect prevalence,
prospective generalization, third-party usability, or application coverage.

## P3 limitations

### P3-1 — Git custody is unavailable

The repository currently reports `bad object HEAD`. No commit identity is
claimed. The sole controlling source authority is the exact source archive at
`861a5d39...b01d` plus its member list and critical file pins.

### P3-2 — Compiler reproduction is not independently implemented

The second materialization used the product parser/compiler, same declared
toolchain and exact native. It regenerated accepted and hostile artifacts
byte-identically and is useful reproducibility evidence. It has neither a
separate compiler implementation nor a complete hermetic environment packet.

## Gates that now pass

### Public lifecycle and ownership

- public source verification, compilation, materialization, preparation,
  repeated execution and close are exercised;
- serialization, cross-thread use, use-after-close and double-close reject;
- an exception after a native launch closes the owner; and
- the earlier process-exit libnvoptix segfault is traced to an unclosed owner
  and does not recur with context-managed cleanup.

### Callback and physical liveness

- `tmin/tmax` from `make_ray` are decision-bearing;
- every populated role-effect leaf has a downstream sink;
- ABI, physical schema, target and plan leaves have exhaustive mutation
  coverage at their declared layers;
- application IDs are unique and stable selection uses only
  `(ordered_float32(t), application_id)`; and
- static/query/output/status/counter contents reach independent commitments
  and device-side fingerprints.

### Real OptiX path

- the loaded and authorized native paths agree for the original execution;
- the preserved native independently rehashes to the recorded SHA;
- the descriptor reports the exact OptiX 9 sphere enum/flag values;
- a built-in sphere module is used and no user intersection program exists;
- two positive launches complete with 5 and 3 raygen invocations; and
- one hostile launch fails in device status before any application-output D2H.

### Numerical boundary

- all inputs are evaluated after exact binary32 projection;
- starts inside or on any sphere reject;
- exact tangent and near-degenerate discriminants reject;
- front entries within `2^-12` of `t=0` or `t=1` reject;
- an interior hit and a far exterior miss remain accepted; and
- all five executed qualification rows use exact-bit output policies.

The public code contains a four-ULP policy for admitted nonexact roots, but the
Home five-row GPU fixture does not exercise it. Only its unit-level behavior is
established; no hardware claim is made for that subcase.

### Evidence and tests

- 56 controlling sphere/public/runtime/verifier tests pass;
- 14 noncontrolling `FamilySchema` prototype tests pass and are reported
  separately;
- 46 adjacent Callback regressions pass from the self-contained source
  capsule;
- accepted and hostile inventories each preserve 14 generated members;
- the Linux isolated recount is byte-identical; and
- the Windows recount is JSON-identical, with only CRLF/LF raw-byte variance.

## Claim audit

The following sentence is authorized:

> Under the project's frozen OptiX 9 taxonomy, public GPU routes instantiate
> three of four leaf-primitive classes—custom primitives, built-in triangles,
> and the bounded built-in-sphere route—while curves remain absent.

It must immediately be qualified as kind-presence implementation coverage. At
the build-input enum denominator the count is three of six. Neither count is a
percentage of OptiX features, a complete sphere implementation, a generic
family compiler, or a new-application generalization result.

The sphere path is limited to static non-motion single-GAS spheres, trace depth
1, callable depth 0, fixed `u32/f32/u32` First Contact output, unique
application IDs, starts strictly outside every sphere, discriminant separation
at least `2^-12`, and front-entry distance greater than `2^-12` from both trace
endpoints. Exact tangency and endpoint contacts fail closed.

Forbidden statements include:

- full or universal sphere support;
- 75% OptiX or geometry coverage;
- arbitrary Callback IR to GPU;
- prospective/generalization exam success;
- Paper App or RT-CCD completion;
- modern RTX or RT-core execution;
- cross-GPU numerical correctness;
- ease-of-use, productivity or external-user evidence;
- performance or no-overhead evidence; and
- independent source-to-executable/compiler-correctness proof.

## Supersession and failure lineage

The final machine result and technical report explicitly supersede the old
result/report/self-reviews, attempts 1–6, `final_home_pass_v6`, and the obsolete
85-member v8 evidence manifest.

The controlling record preserves, rather than conceals:

- the initial false exact-tangent description and unsound oracle;
- the silent `tmin/tmax` lowering defect;
- two zero-GPU environment failures;
- the real tangent MISS and leaked-owner teardown crash;
- the consumed-executable cleanup-test error;
- the GPU-pass/NaN-evidence failure;
- the v6 endpoint/capsule/verifier defects; and
- the first endpoint-repaired GPU pass whose verifier rejected conflated
  source identities.

## Final judgement

Goal5833 materially improves the CGO evidence because it extends the protocol
mechanism to a built-in primitive that has no user intersection program and
demonstrates status-before-output on a real hostile launch. It does not solve
the paper's generalization or usability deficits.

Within the exact bounded sphere domain, the implementation, qualification and
evidence are complete. The next scientific goal remains built-in curves and
then the RT-CCD core; reopening Goal5833 for performance, a generic family
compiler, or broader numerical claims would be scope drift.

No CFR was written and no external review was initiated.
