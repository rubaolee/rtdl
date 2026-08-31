# Goal5834 final adversarial self-review

Date: 2026-08-30  
Controlling result: `goal5834_final_adversarial_self_review_result_20260830.json`

## Verdict

**P0=1 / P1=0 / P2=2 / P3=1. Goal5834 is not complete at swept-sphere or mathematical capsule-semantic scope.**

The implementation does have a public, executable OptiX built-in round-linear
curve path. A fresh Home run on a GTX 1070 observes true OptiX traversal and
matches the separately implemented capsule reference on four fixed fixtures.
The exact-class liveness repair also closes all 40 populated physical and
numeric schema leaves.

That positive result does **not** establish the original claim. Four admitted
inputs reproduce three decisive differences between the mathematical capsule
reference and the OptiX provider: a 725-bit-step time difference, a competing
contact that changes the selected application ID, and a large-translation
capsule hit that the provider misses. Therefore the old
`COMPLETE_AT_BOUNDED_FUNCTIONAL_SCOPE` status and the phrase “exact capsule
semantics on the accepted numeric domain” are superseded.

The controlling status is:

> `INCOMPLETE__POSITIVE_PROVIDER_EVENT_PATH__CAPSULE_NUMERIC_DOMAIN_NOT_ESTABLISHED`

Goal5835 must not inherit the present curve numeric contract.

## Findings

### P0 — the admitted domain is not a sound capsule-equivalence domain

All four rows below enter through the public Python lifecycle, pass admission,
materialize independently, and produce an `optix_traversal_observed` receipt.
No timing is taken.

| Case | CPU closed-capsule reference | OptiX provider output | Consequence |
|---|---:|---:|---|
| Float32 tie repair | `(1,1056964604,1)` | `(1,1056964604,1)` | The repaired float32-before-ID order is live. |
| Ordinary scale | `(1,983336707,555)` | `(1,983337432,555)` | Same hit/ID, but 725 float32 bit steps separate the reported times; the old eight-ULP ceiling is false. |
| Near-coincident capsules | `(1,1030805664,1000)` | `(1,1030805698,1)` | Provider error changes the selected application ID, not merely an approximate time. |
| Large translation | `(1,1056833536,4)` | canonical miss | Public admission accepts a mathematical capsule hit that the provider misses. |

The exact evidence is
`goal5834_final_adversarial_self_review_20260830/NUMERIC_COUNTEREXAMPLES.json`
at SHA-256 `ce9c7daddf65c6a0d4686ff89841a365930d15eceeea6e1069528b842a28cfd3`.
Its v2 schema pins both sides of every row, not merely a broad relation class,
and retains the complete physical and traversal receipts.

This is not repaired by renaming the provider output “the semantics.” The
First Contact application and Goal5835 require a meaningful collision/earliest
contact contract. Provider-event ordering is an implementable observation, but
it is not proof of mathematical earliest time of impact.

### Closed P1 — eleven supposedly live leaves were previously inert

The prior 35-leaf test mutated eleven `buffers`/`hit_channels` projections by
creating a subclass of the physical schema. The verifier rejected the subclass
before inspecting the mutated leaf, so the test falsely reported those leaves
as decision-bearing.

The repair makes those eleven projections actual fields of the exact
`BuiltinCurvePhysicalSchema` and makes five numeric-policy values part of the
same authority. An independent exact-class sweep now reports:

```text
40 mutations / 40 REJECT / 0 ACCEPT
```

The rejection distribution is: schema identity 8, field identity 7, buffer
contract 7, GAS contract 5, numeric admission 5, hit-channel contract 4,
callback binding 2, and stable ordering 2. This closes the liveness defect; it
does not close the P0 numeric-semantic defect.

### Closed P1 — oracle ordering was internally inconsistent

The old oracle sorted binary64 roots and only then converted the chosen root to
float32. The public schema instead orders `(float32 t, application_id)`. The
oracle now projects every candidate time to float32 before ordering. The first
counterexample above proves the repair changes the answer from application ID
100 to application ID 1 and agrees exactly with the provider for that case.

### Closed P1 — numeric policy did not participate in authority identity

The previous final source allowed the near-parallel and other numeric thresholds
to change while retaining the same physical schema/plan identity. The current
schema carries five explicit normative values:

- policy ID `rtdl.v4.curve_numeric_admission.v2`;
- provider-time semantics
  `optix_provider_reported_float32__no_cpu_toi_accuracy_bound_v1`;
- three exponent-encoded conditioning thresholds, each currently `-12`.

Each value is separately mutation-tested and changes the admission verdict.

### Closed P1 — “public C ABI” was false

The native symbols do not independently execute the Python physical/numeric
admission logic. They are now classified as the **internal native provider ABI
used by the Python public lifecycle**, not a user-facing public C API. Calling
those symbols directly is outside the public RTDL contract and is not evidence
that the native entrypoints enforce the same admission rules.

### P2 — current admission duplicates geometric work on the CPU

The public execute boundary evaluates query-by-primitive segment/capsule
geometry to decide whether the provider-stability exclusions apply. That is a
scientifically useful guard for this experiment, but it is not an acceptable
scalable execution path for RT-CCD. Goal5835 must not inherit an `O(QP)` CPU
collision prepass and then call the GPU as if the GPU supplied the acceleration.

### P2 — hardware scope is one behavioral OptiX target

The fresh result is from one GTX 1070 (compute capability 6.1, driver
580.173.02, OptiX 9.0.0, CUDA 12.0). It establishes behavioral true-OptiX
execution, not RT-core-silicon execution, Ada behavior, or a cross-GPU numeric
theorem.

### P3 — lineage and evidence hygiene

Old result/report/source variants remain immutable historical material. They
are not controlling. The new v8 source projection contains 20 exact source,
test, validation, verifier, and counterexample files; all are regular read-only
members with uid/gid/mtime zero. Its archive and independently rebuilt twin are
byte-identical at SHA-256
`e0edb530de776d815dd7055fc2fb553efea64082e04c4f2d3f8f9582bcbf6e51`.

The repository object database still reports `fatal: bad object HEAD` for
status operations. This review therefore makes no commit-identity claim.

## Fresh positive evidence that remains valid

The repaired source was copied to a new Home directory, rebuilt from source,
and executed. It did not reuse the old v7 result or DSO.

- native DSO:
  `d9bd98135f18b1545a0d55e72acb4d7ae4aa06a6e36c03415e02b7efe70f7531`;
- Home result:
  `67746c2141677df80dbdb62d396031a9d8f35d6343cb5283f7416c10a96e4b77`;
- RTDL-free consistency result:
  `1964438e1a2ba816bc6479e313312d0314e8c94da7db16dbf7817f2f9c947129`;
- executable:
  `7ec48faa40d4427d8c5ef34dcd7e49446b5f5e9d86c1277abd7ce37e606a3da7`;
- generated-artifact manifest:
  `837edb191e82b60ce7bcd587efc505cdc9f852fb8d0a384072da51b166c1188f`,
  13 members;
- four rows:
  `(1,1052770304,50)`, canonical miss,
  `(1,1044381696,900)`, `(1,1049699860,77)`;
- reversed second execution: exact;
- role counters: `[0,4,0,0,3,1,4]`;
- status-before-output: true;
- use-after-close: rejected;
- registered performance timings: zero.

The safe verifier statement is narrowly this:

> An RTDL-free consistency verifier rehashes the preserved DSO and thirteen
> generated artifacts, recomputes the four fixed fixture rows with the
> separately implemented capsule reference, and checks selected embedded
> descriptor and traversal-receipt invariants.

It does not rebuild the implementation, independently query the GPU,
reconstruct target or authority identities, or prove the source-to-IR-to-PTX
or native chain.

The original axial oracle-hit/provider-miss log was not preserved. It must not
be cited as a reproduced raw failure. The controlling evidence for semantic
failure is the newly preserved four-case counterexample result.

## Regression result

The combined Goal5833/Goal5834 local regression ran 82 tests with zero failure.
The focused Goal5834 suites ran 12 tests with zero failure on Windows and again
on Home Linux before GPU execution. These results prove the named bounded
mechanisms remain live; they do not cancel the GPU counterexamples.

## Exact claim boundary

Allowed:

- RTDL exposes a public lifecycle for an OptiX built-in round-linear curve
  provider.
- Four fixed fixtures execute true OptiX and equal the independent capsule
  reference exactly.
- All 40 populated physical/numeric schema leaves are decision-bearing.
- RTDL has public GPU **kind presence** for all four coarse OptiX leaf primitive
  classes.

Forbidden:

- exact capsule semantics over the admitted domain;
- a fixed provider-vs-CPU-root ULP guarantee;
- feature-complete curve or swept-sphere support;
- Goal5834 completion at the scope originally requested;
- prospective generalization, Paper App, external-user, performance, RT-core,
  or cross-GPU claims.

The 4/4 primitive statement is governed separately by
`goal5834_optix_leaf_primitive_kind_presence_authority_v2_20260830.json` and is
explicitly `KIND_PRESENCE_ONLY__NOT_FEATURE_COMPLETE`.

## Required successor before Goal5835

Create Goal5834-R1 (or an append-only equivalent) with a frozen, falsifiable
contract:

1. define and implement scene/query normalization and inverse result mapping;
2. define a competing-contact separation/ambiguity rule that prevents provider
   error from silently changing application identity;
3. choose whether the language returns provider event time or recomputes a
   mathematical time of impact after provider candidate generation;
4. freeze a differential corpus spanning scale, translation, side/endcap,
   near-parallel, near-tangent, endpoint, and competing-contact cases;
5. test at least Home and one RTX target and accept the result unconditionally,
   including a terminal negative result;
6. remove the `O(QP)` CPU geometric admission from the future accelerated path,
   or report it openly as CPU precomputation rather than RT acceleration.

Until that successor passes, Goal5835 is blocked for scientific reasons, not
for documentation or software-engineering polish.

No external review was requested or authorized for this self-review.
