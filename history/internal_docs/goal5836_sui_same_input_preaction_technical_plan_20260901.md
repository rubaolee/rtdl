# Goal5836 Sui same-input functional preaction

Date frozen: 2026-09-01  
Scope: preaction and gate definition only  
Authority: `goal5836_sui_same_input_preaction_authority_20260901.json`  
Performance: forbidden  
External review: not requested or authorized

## 1. Decision and present boundary

This preaction implements the only action authorized by the completed Mac
hostile review:

```text
GO__AUTHOR_GOAL5836_PREACTION_ONLY
```

It does not start Goal5836. It does not authorize source acquisition, an
author checkout, author build or execution, RTDL execution, product mutation,
a POD/GPU worker, timing, Paper-App promotion, public claims, or external
review. Its machine status is:

```text
READY_FOR_OWNER_GATE__SOURCE_ACQUISITION_ONLY__NO_GOAL5836_EXECUTION
```

The current scientific labels remain exact:

```text
paper_app_status: NOT_A_PAPER_APP
source_relation: SUI_DERIVED_MAPPING__AUTHOR_DESIGNED_FIXTURES
generalization_exam_count: 0
registered_performance_timing_count: 0
Goal5836 functional executions: 0
```

The preaction is bound to predecessor commit
`56ba0219c4cf58f27c78da978257caad39ebbf18`, branch
`codex/cgo-goal5836-handoff`, checkpoint
`d0bb938170cd227a33a5237cf5b7e48102cb5c7e`, the completed Mac review, and
the five controlling Goal5834/5835 evidence files by repository-relative path,
byte count, and SHA-256.

## 2. Source planning claims, not observations

The controlling handoff names this planned source:

```text
paper: Sizhe Sui, Luis Sentis, and Andrew Bylard,
       Hardware-Accelerated Ray Tracing for Discrete and Continuous
       Collision Detection on GPUs, ICRA 2025, 16133--16139
repository: https://github.com/Ssz990220/RTCollisionDetection
planned commit: bacbf77a612bba3e6e8f7a464fa0fa2c67298ac7
planned license: MIT
```

Every value above remains a planning claim. No paper PDF, author Git object,
author tree, selected source file, license byte, source hash, or author output
was acquired or observed while freezing this preaction. A returned object may
not cause the planned pin to be rewritten. Missing or mismatching bytes are a
negative outcome, not permission to choose a convenient replacement.

## 3. Serial stages and owner gates

Every stage starts locked. Passing one stage does not authorize the next; a
separate owner decision is required at each execution boundary.

### A0: exact source acquisition and hashing

The immediate next owner decision may authorize only A0. A0 may download and
hash the exact paper PDF, fetch and verify the planned Git commit, capture the
complete source-tree identity, capture and hash the license bytes, and preserve
network/fetch receipts. It may not build or run author code.

A0 passes only if the planned paper, commit, source tree, and license are all
available with unambiguous exact identities and no pin was changed. Missing
commit objects, source drift, a license mismatch, incomplete receipts, or hash
ambiguity stop the transaction.

### A1: author-source fidelity classification

A1 may begin only after a valid A0 authority and another owner decision. It
must identify the exact author path that defines:

- obstacle mesh extraction and edge direction;
- robot/sphere trajectory representation;
- curve width or radius convention;
- the returned collision Boolean;
- discrete endpoint, pose, initial-overlap, and face-interior checks;
- any composition between the edge test and those checks.

The classification must be exactly one of:

```text
MATCH_SELECTED_EDGE_PREDICATE
MATERIAL_PREDICATE_DIFFERENCE
UNRESOLVED
```

Only `MATCH_SELECTED_EDGE_PREDICATE` can support later input selection.
`MATERIAL_PREDICATE_DIFFERENCE` refuses the Goal5836 promotion mapping;
`UNRESOLVED` stops. The implementation may not narrow or expand the predicate
after observing an output.

### A2: same-input and output-contract freeze

A2 may begin only after A1 matches and another owner decision. Geometry must
be selected from paper/source semantics independently of author, RTDL, and
oracle output. The frozen corpus must contain at least:

- one complete mesh-derived robust positive edge crossing, which Goal5835
  does not currently contain;
- the existing face-interior-only negative boundary, kept visibly outside the
  edge predicate;
- any source-required discrete endpoint/pose case as a separate composition,
  not silently folded into edge crossing.

The adapter must reject ambiguous input before freeze: assigned device-visible
IDs are finite integral u32 values, path IDs are globally deterministic,
triangle identities are unique, and triangles are finite and nondegenerate.
The exact input bytes, Boolean output predicate, normalization, margins,
statuses, and no-replacement rule then become immutable.

The bounded application output is an edge Boolean vector followed by host OR
to a collision Boolean. This is not automatically complete sphere-triangle
CCD or complete robot collision detection.

### A3: local three-route materialization

A3 may begin only after the A2 bytes are frozen and another owner decision.
It creates three separately implemented routes over the exact same input:

1. an author-source adapter;
2. an RTDL public-lifecycle adapter;
3. a stdlib-only CPU oracle that imports neither RTDL nor the author runtime.

The author and RTDL worker packages contain no expected output and no CPU
geometry oracle. Raw author and RTDL outputs are sealed before evaluation.
Only a separate post-seal evaluator loads the oracle and compares the three
routes. A3 is limited to source, schema, hostile, and materializer tests on
macOS. It may not simulate OptiX or run the author binary.

### A4: modern-RTX functional execution

A4 requires a separately frozen A3 execution bundle, a new owner gate, and a
zero-worker preflight. The preflight must bind the exact GPU, driver, CUDA,
OptiX, paper/source authority, author and RTDL source, generated source, native
binary, input, worker, and evaluator hashes before worker zero.

Only then may one modern NVIDIA RTX Linux target run the author route, RTDL
public route, and independent recount over the exact common input. True-OptiX
receipts must prove the claimed built-in sphere/round-linear-curve route.
Functional fields only are allowed; timing fields and performance inference
remain forbidden.

### A5: Paper-App decision

A5 requires another explicit decision. Paper-App status is allowed only if all
of the following pass:

1. exact paper and author-source provenance;
2. a faithful frozen same-input mapping;
3. successful author execution;
4. RTDL public-lifecycle execution;
5. author/RTDL/oracle agreement, or a scientifically resolved difference that
   does not change the frozen rule;
6. independently recountable identity and custody;
7. visible limitations and negative cases;
8. zero performance inference.

Partial passage does not authorize promotion. The result must retain the
strongest lower status instead of repairing the wording.

## 4. Unconditional outcomes

All result branches are accepted before output exists:

| Event | Frozen outcome |
|---|---|
| All three routes match | Functional match; the Paper-App gate may be evaluated |
| Functional mismatch | Terminal scientific mismatch; preserve input and outputs |
| Author build/run fails | Author execution unavailable; no Paper-App promotion |
| Source predicate materially differs | Refuse the mapping; retain Goal5835 scope |
| Source semantics remain unresolved | Stop with unresolved source relation |
| Mapping fails | Terminal mapping failure; no input replacement |
| Capability is unsupported | Report unsupported capability; do not rewrite scope |
| Infrastructure is invalid | Evidence is invalid; make no scientific inference |

No branch permits replacement inputs, changed margins, changed thresholds,
changed output predicates, a different commit, or a relabelled failure.

## 5. Custody and evidence independence

All new identity-bearing paths are repository-relative POSIX paths plus
content hashes. Absolute paths may appear only in explicitly non-identity
diagnostics. This avoids repeating Goal5835's cross-machine path-dependent
whole-file receipt defect.

The exact input identity is verified before every worker. Worker packages are
free of expected output and oracle geometry. Raw outputs are sealed before
evaluation. Old Goal5834-B3 launches remain inherited evidence and cannot be
counted as Goal5836 application runs.

## 6. Verification and next gate

The authority is deterministic and self-sealed. Its generator verifies the
Mac hostile review and five controlling evidence pins before construction.
The stored authority is checked by:

```text
python3 scripts/goal5836_build_sui_same_input_preaction.py --verify-stored
python3 -m unittest tests.goal5836_sui_same_input_preaction_test -v
```

The only next requested owner decision is:

```text
AUTHORIZE_STAGE_A0_SOURCE_ACQUISITION_AND_HASHING_ONLY
```

Even if approved, author build/execution, Goal5836 functional execution,
product mutation, POD/GPU use, timing, Paper-App promotion, external review,
and public claims remain forbidden.
