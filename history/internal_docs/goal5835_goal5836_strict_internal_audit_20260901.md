# Goal5835/Goal5836 strict internal audit

Date: 2026-09-01
Review class: internal hostile self-audit
External review: deferred by owner; count 0
GPU, pod, execution, or timing added by this audit: none

## 1. Findings

### P1: Goal5835 claim scope is broader than its executed evidence

Goal5835's receipt validly reconstructs application-shaped objects and proves
that their normalized static/query bytes equal the previously executed
Goal5834-B3 fixtures. It then composes the inherited B3 result. The receipt
source does not directly call `execute_registered_problem`,
`trajectory_to_swept_segments`, or `deduplicate_triangle_edges`; the fixture
loader invokes deduplication only to reconstruct the intentional complete-
triangle miss. It performs no Goal5835 GPU launch. The strongest supportable
class is:

```text
BOUNDED_APP_SEMANTIC_PROJECTION_WITH_INHERITED_TRUE_OPTIX_EVIDENCE
```

It is not an executed case-study front door, paper reproduction, Paper App, or
full RT-CCD result. This P1 is addressed for current readers by
`CURRENT_STATUS_AFTER_GOAL5836.md`; the hash-bound historical README and result
are intentionally unchanged.

### P2: Goal5835 has no positive complete-mesh fixture

The only row whose queries carry source-triangle identity is
`face_interior_only_boundary`, and that row is an intentional miss. Every
positive row has empty `source_triangle_ids`. Therefore the result does not
exercise positive triangle-to-directed-edge construction.

### P2: Frozen fixtures synthesize sphere identity

The fixture adapter sets `sphere_id=primitive_index`. In
`piecewise_linear_or`, two geometrically connected segments therefore carry
sphere IDs `[0, 1]`. The evidence runner never invokes the trajectory builder
that would preserve one sphere identity across segments.

### P2: The app result adapter does not fail closed

A hostile generic result with one bit for a three-edge problem and
`any_hit=0` while `OR(bits)=1` is accepted by `execute_registered_problem`.
The adapter aliases fields without validating cardinality or aggregate
consistency. This did not corrupt the frozen receipt because that runner never
called the front door, but it is a real successor-engineering defect.

### P2: Duplicate triangle IDs make directed output order-dependent

`deduplicate_triangle_edges` sorts only by `triangle_id`. Stable sorting leaves
caller order as a tie-break when IDs are duplicated. Two same-ID triangles
sharing an oppositely oriented edge produce `a -> b` in one caller order and
`b -> a` in the reverse order. Goal5836 established that direction is
predicate-significant, so duplicate IDs must eventually reject or use a fully
specified deterministic tie-break.

### P2: The historical receipt is path-dependent

Goal5835 serializes absolute source paths. Its result and recount are exactly
byte-identical on the originating environment, but a Mac regeneration has a
different whole-document hash. After removing only those path fields, the
regenerated document is exactly equal to the historical document. This is a
portability defect, not a semantic-result mismatch.

### P2: Goal5836 includes a human semantic judgment

A1 mechanically binds the exact paper, source capsule, selected Git blobs,
anchors, and transition policy. Its material-difference classification is a
human-reviewed semantic conclusion encoded in the builder; the tests do not
constitute a graph theorem or mechanical PDF interpretation. Exact PDF pages
5, 7, and 10 and the author call chain support the conclusion, but an eventual
external reviewer must inspect those semantics independently.

### P3: Numeric ID validation is permissive

`SweptSphereSegment` accepts non-integral numeric values such as `1.5` and
`2.5` when they fall inside the u32 numerical range. The path ID is rejected
later by physical input construction, while sphere ID may remain only in app
provenance. This is not load-bearing for the frozen result but violates the
declared integer contract.

## 2. Verdict

```text
P0 = 0
P1 = 1
P2 = 6
P3 = 1

Goal5835:
ACCEPT_ONLY_AFTER_CLAIM_NARROWING__NOT_AN_EXECUTED_PAPER_APP

Goal5836:
ACCEPT_TERMINAL_A1_NEGATIVE_OUTCOME__NO_A2__NO_POD_REQUIRED
```

The Goal5835 evidence is genuine within its narrower class. The audit does not
allege fabricated OptiX execution: it confirms 33 inherited B3 true-OptiX
launches and zero new Goal5835 launches. The error was scope, not custody.

Goal5836's core conclusion is accepted. The exact paper and author call chain
show that directed connectivity and inside-start handling are part of the
predicate. Goal5835 does not preserve them. Under the preregistered policy,
`MATERIAL_PREDICATE_DIFFERENCE` correctly terminates the transaction at A1.
A2--A5 remain unreachable; Paper App promotion did not succeed.

## 3. Evidence and method

The deterministic audit builder:

1. checks exact SHA-256 identities for the Goal5834 fixture authority, worker
   input, raw B3 receipt, B3 evaluation, Goal5835 result/recount and source,
   Goal5835 README, and Goal5836 A1 authority;
2. reruns the Goal5836 preaction, A0, and A1 stored verifiers;
3. rebuilds the Goal5835 receipt and proves exact semantic equality after
   removing only absolute source-path fields;
4. derives fixture coverage and call-presence facts;
5. executes deterministic hostile counterexamples for duplicate triangle IDs,
   malformed generic output, synthetic sphere identity, and permissive IDs;
6. binds the CGO manuscript inspected by this review; and
7. seals the exact finding set, severity denominator, claims, and deferred
   external-review state.

Authority:

```text
path:
history/internal_docs/goal5835_goal5836_strict_audit_20260901/
STRICT_AUDIT_AUTHORITY.json

whole-file SHA-256:
bb58e1f0fc247f01f4636e985cef93b117c574e75b60f16e845f0e080f5820a5

internal seal:
84f2e128aee140ed8e02665f5b869ca38d6cd1636a750272c7fa85f4e7739561
```

The seal is an integrity and policy-consistency check, not an independent
signature or external-review credential.

## 4. CGO manuscript impact

The inspected `paper/cgo2027/main.tex` has SHA-256
`d9cf2dc38f83e6545c4880efd6f101be27553c6729f41dcc7afe0e126c504716`.
It contains neither Goal5835 nor Goal5836 as a literal experiment. The Sui
paper appears in related-work/problem inventory. No experiment, performance
claim, or positive Paper-App result should be added from this negative
transaction.

## 5. Response and remediation

- Publish the current claim narrowing without changing frozen Goal5835 bytes.
- Preserve all eight counterevidence rows as hostile tests.
- Do not repair the historical app source in place because Goal5836 binds its
  exact hash.
- If the owner wants a repaired implementation, start a new preregistered goal
  with an app-neutral directed-orientation/connectivity contract, a real
  trajectory and positive complete-mesh fixture, fail-closed output validation,
  and fresh same-input author/RTDL/oracle evidence.
- Use a modern RTX pod only after that separate local gate passes. No pod can
  change the completed Goal5836 A1 result.

## 6. Verification

```text
strict-audit hostile tests: 20/20 PASS
Goal5833--Goal5836 historical regression: 148/148 PASS
Goal5836 preaction stored verifier: PASS
Goal5836 A0 stored verifier: PASS
Goal5836 A1 stored verifier: PASS
Goal5835 result/recount exact byte equality: PASS
Goal5835 semantic regeneration ignoring only absolute paths: PASS
working-tree capsule policy/hash verifier: PASS
independent capsule extraction verifier: PASS
independent extraction strict audit: 20/20 PASS
independent extraction historical regression: 148/148 PASS
```

External review was not requested. It is explicitly deferred until the owner
returns from travel, and no consensus claim is made.
