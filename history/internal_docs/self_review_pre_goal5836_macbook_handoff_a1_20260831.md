# Internal hostile self-review -- pre-Goal5836 Mac handoff A1

Date completed: 2026-09-01  
Task: `PRE-GOAL5836-A1__HOSTILE_REVIEW_AND_PREACTION_DECISION`  
Review type: internal self-review, not external review and not a call for review  
Performance: not measured or authorized  
Product source mutation during review: none

## 1. Verdict

```text
P0 = 0
P1 = 0 (one acceptance-gate P1 found and closed during this task)
P2 = 4
P3 = 2

PREACTION DECISION:
GO__AUTHOR_GOAL5836_PREACTION_ONLY
```

Goal5836 execution remains locked. Author-source acquisition, a POD/GPU
worker, performance collection, Paper-App promotion and external review remain
unauthorized.

The scientific Goal5833--5835 payload is recoverable and its controlling
hashes and tests pass. The first review pass found that the new Git-native
acceptance gate could not pass in the exact fresh-clone environment required by
the handoff. The bounded repair in Section 5 closed that P1 without changing
product source or Goal5834/5835 evidence. The evidence now supports authoring a
Goal5836 preaction only. It does not predetermine that the Sui paper/source
mapping is faithful and does not authorize acquiring or executing the author
implementation.

## 2. Mac receipt

### 2.1 Repository and capsule

```text
repo: /Users/rl2025/rtdl_v4_restricted_python_design
remote: https://github.com/rubaolee/rtdl
branch: codex/cgo-goal5836-handoff
HEAD: 7a60890588ab562d06a9c762e9a97b52a36ebddb
minimum checkpoint: d0bb938170cd227a33a5237cf5b7e48102cb5c7e
checkpoint_is_ancestor: true
tracked_git_status_before_report: clean
```

The only commit after the minimum checkpoint is `7a60890`,
`docs(cgo): add Git-native Mac Goal5836 handoff`. It changes only
`CAPSULE_MANIFEST.json`, `START_HERE.md`, the outer handoff tar and the copied
handoff document.

The current `HEAD` passes from a clean `git archive` extraction:

```json
{"payload_bytes": 77141642, "payload_count": 5357,
 "status": "PASS__GOAL5836_MACBOOK_CAPSULE"}
```

An ordinary fresh clone does not pass `python3 VERIFY_CAPSULE.py`. The verifier
uses `root.rglob("*")` and does not exclude `.git/**`, so it reports the Git
metadata as extra payload. After the baseline tests, it also reports generated
`__pycache__` files. In addition, both Git-native handoff copies still say that
the verifier must report the minimum checkpoint's old `payload_bytes` value
`77137824`, while the current manifest correctly reports `77141642`.

This is not a Goal5835 payload mismatch: the 3818-byte difference is exactly
the two handoff copies growing by 1909 bytes each in `7a60890`, and the current
archive manifest is internally consistent. It is nevertheless a real failure
of the handoff's mandatory fresh-clone gate.

### 2.2 Controlling hashes

All five transferred controlling hashes match:

```text
0f13ab8a7408c253114c56a51645c015d0e5e36ca96a4290c9dd1a2ba700adad  FIXTURE_AUTHORITY.json
55eeff377c93c32fed8cc326ad975cb9d2437df85812e30b9d916b3e7cc581a4  WORKER_INPUTS.json
b50043e81713aacf6a70986a6e334789cbfeef17342ae97a8ae401ab1507f513  RAW_GPU_RECEIPT_B3.json
786ebd4970dadf842c57aa6c08539694d0cdbe8a6b2f6672932029b5f19be02a  INDEPENDENT_EVALUATION_B3.json
ae370da1ca5ac96562d0956438e7c6c8eee39fddf2d9894953db8e956c47ccff  Goal5835 result
```

The Goal5835 result and separately generated recount are byte-identical at
`ae370da1...ccff`.

### 2.3 Environment and test denominator

```text
macOS: 26.3, build 25D125
Python: 3.14.4
NumPy: 2.5.2
environment: /Users/rl2025/.venvs/rtdl-goal5836-mac
command: python -m unittest discover -s tests -p 'goal583[3-5]*_test.py' -v
result: Ran 102 tests; OK
```

Python 3.14 emits one future-compatibility `SyntaxWarning` for the test regex
string `"hit\+zero\+zero"`; it does not change the 102/102 outcome.

The controlling Goal5835 labels also remain exact:

```text
paper_app_status: NOT_A_PAPER_APP
source_relation: SUI_DERIVED_MAPPING__AUTHOR_DESIGNED_FIXTURES
generalization_exam_count: 0
registered_performance_timing_count: 0
new_goal5835_gpu_launch_count: 0
inherited_b3_true_optix_launch_count: 33
goal5836_authorized: false
```

## 3. Findings

### Closed P1-1 -- The Git-native acceptance gate was impossible as written

`VERIFY_CAPSULE.py` treats `.git/**` as capsule payload, while Section 1.1 of
both handoff copies requires running that verifier inside an ordinary Git
clone. The same section requires `payload_bytes=77137824`, but current `HEAD`
and its manifest contain `77141642`. Section 9 then says never to continue from
a checkout that fails this gate.

This is a reproducible acceptance-gate contradiction, not a speculative style
issue. The archive pass and exact hashes recover the intended state, but this
review cannot silently waive a mandatory fail-closed rule.

Required bounded repair:

1. Exclude repository metadata such as `.git/**` from capsule path-set
   enumeration without weakening checks over tracked payload files.
2. Make both handoff copies state the post-repair manifest's exact current
   payload count and byte total.
3. Regenerate the manifest and optional outer capsule as needed.
4. Prove the repaired branch in both a fresh clone and a `git archive`
   extraction, then rerun the five hashes and the 102-test denominator.

This repair is handoff infrastructure. It must not modify product source,
Goal5834/5835 evidence, fixtures, labels or scientific outcomes.

The repair is closed in Section 5. This finding is retained for audit history
but is not counted as an open P1 in the final verdict.

### P2-1 -- Exact Sui paper/source fidelity is unresolved

The workspace contains planning metadata for the Sui/Sentis/Bylard paper and
repository, but it contains no pinned paper PDF, author Git object, selected
source bytes or license bytes. Therefore the statement that the author route
uses the same directed mesh-edge versus swept-sphere/capsule predicate is not
yet verified. It is inferred from the project plan and deliberately remains
`SUI_DERIVED_MAPPING__AUTHOR_DESIGNED_FIXTURES`.

A later owner-authorized preaction must make paper/source acquisition and hash
pinning its first fail-closed stage. It must inspect the exact author geometry,
edge direction, curve-width/radius convention, trajectory representation,
Boolean reduction and any discrete endpoint/pose checks before selecting a
common input. If the exact source implements a materially different predicate,
Goal5836 must refuse promotion rather than adapting the claim after output is
seen.

### P2-2 -- There is no complete mesh-derived positive edge-crossing fixture

The Goal5835 result has ten positive/mixed registered-edge executions, but all
positive query rows have empty `source_triangle_ids`. The only execution whose
queries all reconstruct a complete triangle is
`face_interior_only_boundary`, and its collision bit is zero. This confirms the
handoff's lead with direct result inspection.

A robust paper/source-derived complete triangle or mesh containing a positive
edge crossing is mandatory before any Goal5836 worker. It must be frozen before
author or RTDL output is observed and cannot replace the current negative
face-interior boundary.

### P2-3 -- Edge crossing is not complete sphere-triangle CCD

The implemented predicate detects a collision only when at least one
registered finite triangle edge intersects at least one swept-sphere capsule
in the qualified domain. Round endcaps allow a registered edge to detect
contact at a path endpoint, but the current corpus and admission intentionally
exclude edge endpoints starting inside a capsule, initial overlap, tangency and
near-parallel contact.

The method cannot detect collision confined to triangle-face interior with no
edge/capsule intersection. The frozen `face_interior_only_boundary` is an
explicit counterexample. Discrete endpoint/pose checks are not composed into
Goal5835. Goal5836 must determine from exact author source whether those checks
are separate author stages, outside the selected paper core, or necessary for
a faithful same-input result. The edge result must remain separately
observable and must never be renamed complete robot or sphere-triangle CCD.

### P2-4 -- Goal5835 whole-file identity is path-dependent

`run_functional_receipt.py` serializes resolved absolute source paths. The
frozen result therefore contains Windows paths and cannot be regenerated
byte-identically on this Mac even when source hashes and semantic fields are
identical. The original result and recount remain valid frozen Windows
artifacts; they must not be rewritten.

Every new Goal5836 identity must use repository-relative logical paths plus
content hashes. An absolute execution path may appear only in a separately
labelled non-identity diagnostic field.

### P3-1 -- App-level ID type guards are permissive but fail closed downstream

`SweptSphereSegment` accepts non-integral numeric `sphere_id` and
`path_segment_id` values if they compare inside the u32 range. A reproduced
`path_segment_id=2.5` is later rejected by `BuiltinCurveStaticInput` as not a
u32; a non-integral `sphere_id` can remain only in the application identity
projection because it is not device-visible.

This does not alter the frozen Goal5835 rows and is not load-bearing for a
Boolean-only Goal5836 fixture whose adapter assigns explicit integer IDs. The
preaction must freeze exact integer ID construction and test it. Do not broaden
this into general API cleanup unless the selected source fixture exploits it.

### P3-2 -- Mesh identity/degeneracy guards are incomplete but not yet
load-bearing

Two disjoint `ObstacleTriangle` objects with the same `triangle_id` are
accepted and yield ambiguous source provenance; a collinear three-vertex
triangle is also accepted. Distinct vertex IDs at coincident positions fail
later when a zero-length `ObstacleEdge` is constructed. None of these cases is
present in the frozen Goal5835 inputs, and the result is Boolean rather than a
triangle-identity output.

The future common-input adapter must reject duplicate triangle identities,
non-finite/non-u32 assigned IDs as applicable, and geometrically degenerate
triangles before commitments are frozen. A product-source change is not
justified during this review without an exact author fixture that reaches one
of these cases.

## 4. Required hostile questions

### 4.1 Paper fidelity

**Unresolved.** No exact author bytes are present, so current evidence cannot
establish that the selected predicate is the author's exact directed
mesh-edge/swept-sphere predicate. This is a hard first-stage question for the
future preaction, not a fact to infer from the paper title or planning prose.

### 4.2 Width semantics

**Resolved for the executed RTDL route.** The official NVIDIA OptiX 9.0 API
describes `OptixBuildInputCurveArray::widthBuffers` as one float per vertex
specifying curve width **(radius)**. It also defines default endcaps as round
for linear curves:

- [NVIDIA OptiX 9.0 API, OptixBuildInputCurveArray](https://raytracing-docs.nvidia.com/optix9/api/OptiX_API_Reference.pdf)
- [NVIDIA OptiX 9 type definitions](https://raytracing-docs.nvidia.com/optix9/api/group__optix__types.html)

The exact native source in the executed B3 projection has SHA-256
`ad86fb096e3b70b0826c17cff8fa22e6c273676dd0c4814ede0a4a44126eb154`.
It copies each public f32 width unchanged into `normalized_widths`, uploads
that array, sets `curveArray.widthBuffers` to it with four-byte stride, chooses
`OPTIX_PRIMITIVE_TYPE_ROUND_LINEAR`, and uses
`OPTIX_CURVE_ENDCAP_DEFAULT`. The B3 receipt records compiled OptiX version
`90000`, width stride 4, built-in IS present, no user intersection program, and
matching host/device static-input fingerprints. The CPU capsule radius and the
executed provider radius therefore use the same physical convention; there is
no radius/diameter factor-of-two gap in this route.

### 4.3 Mesh completeness

**Bounded and incomplete by design.** Robust registered edge/capsule crossing
is detected. Registered-edge contact at a round path endpoint is represented.
Initial overlap, start-inside edge rays, near-tangent/near-parallel contact and
face-interior-only collision are not supported. Discrete sphere/pose checks
are not currently composed with the edge route. The claim must remain an edge
predicate unless exact author evidence defines and validates a larger
composition.

### 4.4 Evidence independence

**Passes at the declared finite-corpus scope.** `WORKER_INPUTS.json` explicitly
contains neither expected output nor pairwise geometry. The B3 worker rejects
expected keys and does not import/call the oracle. The raw receipt is labelled
`RAW_GPU_BITS_SEALED__UNEVALUATED`; the post-result evaluator checks its hash
before loading the stdlib-only primary oracle. Goal5835's active-set distance
enumeration imports no RTDL and is algorithmically different from the primary
Goal5834 closest-segment implementation.

The Goal5835 active-set code is substantially the same second algorithm used
by the B3 cross-check test. It therefore counts as the second CPU geometry
calculation, not as an additional third independent algorithm. Existing
wording claiming two CPU calculations remains supportable.

### 4.5 Composition validity

**Passes for Goal5835's bounded mapping claim.** Public static commitments hash
all f32 control-point/width bits and all u32 segment/application IDs; query
commitments hash every f32 start/end bit with schema framing. For each of 11
rows, Goal5835 reconstructs these public objects and refuses any commitment or
byte mismatch before binding the exact sealed B3 vector. That is sufficient to
prove that the application mapping denotes the same static/query bytes that B3
executed.

It is not new hardware evidence. The result correctly reports 0 new Goal5835
launches and 33 inherited B3 launches. Goal5836 still needs an actual
case-study-front-door execution on the separately frozen modern-RTX target.

### 4.6 Frozen-input relevance

**Insufficient for Goal5836 promotion.** No positive execution reconstructs a
complete mesh. The future preaction must freeze at least one complete
paper/source-derived positive edge-crossing mesh before worker zero, while
retaining the negative face-interior boundary.

### 4.7 Type and identity boundaries

**No current P0/P1 scientific exploit found.** The permissive ID and duplicate/
degenerate triangle counterexamples are real but do not change any frozen
Goal5835 public commitment or Boolean result. The single-u32 physical identity
is adequate because Goal5835 exposes no collided primitive identity and uses
globally unique path-segment IDs. Goal5836 must freeze deterministic global
u32 IDs and valid unique mesh identities; only a selected exact fixture that
violates this condition would justify a product fix.

### 4.8 Cross-machine custody

**Passes after the bounded gate repair, with one historical result defect.**
Git commit/checkpoint identity,
source hashes, controlling evidence hashes and semantic labels are
path-independent. The frozen Goal5835 whole-file result is not because it
contains absolute Windows paths. Preserve it as-is and use relative logical
paths plus hashes in all Goal5836 identities. The Git-native verifier defect is
closed in Section 5.

### 4.9 Strongest claim if the author build fails or disagrees

The following remains true even if a later author build is unavailable or its
result disagrees:

> RTDL has public app-neutral built-in sphere and round-linear-curve callback
> protocol routes. On eleven author-designed registered executions, an exact
> bounded application mapping represents piecewise-linear sphere motion as
> round-linear capsules and queries finite obstacle edges; sealed OptiX Boolean
> vectors agree with a primary independent CPU capsule oracle and a second
> active-set calculation. This is not a Sui Paper App, complete RT-CCD,
> prospective generalization result, modern-RTX application result, or
> performance result.

If the exact author source uses a different predicate, the phrase
`SUI_DERIVED_MAPPING` must not be strengthened and Goal5836 promotion must be
refused. If the mapping is faithful but the author binary cannot build, the
strongest additional status is only
`same-input mapping established but author execution unavailable`. If the
author executes and disagrees, report `functional mismatch observed` under the
frozen rule; do not replace the input or comparator.

## 5. P1 repair closure and exact preaction gate

The bounded handoff repair changed only:

- `VERIFY_CAPSULE.py` and its capsule-builder source;
- the exact expected verifier byte receipt in both handoff copies;
- the generated capsule manifest and optional outer capsule; and
- this internal self-review.

The verifier now excludes only environment artifacts (`.git`, the prescribed
`.venv-goal5836`, Python/pytest caches, editable-install `.egg-info` and
`.DS_Store`) from path-set enumeration. Every manifest-listed payload is still
read and rehashed, and every other extra path still fails closed. The repaired
archive/fresh-clone-equivalent receipt is:

```text
status: PASS__GOAL5836_MACBOOK_CAPSULE
payload_count: 5358
payload_bytes: 77164522
five controlling hashes: match
Goal5833--5835 tests: 102/102 OK
```

The verifier passed both the actual Git working tree and an independent outer-
capsule extraction after injected `.git`, prescribed venv, cache, `.egg-info`
and `.DS_Store` artifacts. Injecting an ordinary unlisted
`UNEXPECTED_PAYLOAD.txt` still failed with a path-set mismatch, proving that
the repair did not turn path checking into an allow-all rule.

No `src/**`, `case_studies/**`, frozen evidence, fixture, label or scientific
outcome changed. The bounded repair closes P1-1 and authorizes only:

```text
GO__AUTHOR_GOAL5836_PREACTION_ONLY
```

That preaction must freeze, before any result inspection:

1. exact paper PDF, author commit, license and selected source hashes;
2. a source-backed statement of the author's actual edge, curve-width,
   trajectory, Boolean and discrete-check semantics;
3. one complete mesh-derived robust positive edge crossing plus retained
   negative boundaries;
4. three separately implemented adapters/routes: author, RTDL public lifecycle
   and stdlib-only oracle;
5. deterministic integer identity assignment and mesh validity rules;
6. repository-relative identity paths and content hashes;
7. unconditional match, mismatch, author-build failure, mapping failure,
   unsupported-capability and infrastructure-invalid branches;
8. a separate owner gate before any acquisition or worker, as required by the
   controlling handoff.

Nothing in this report authorizes a POD, GPU execution, timing field,
performance wording, Paper-App label, public release or external review.
