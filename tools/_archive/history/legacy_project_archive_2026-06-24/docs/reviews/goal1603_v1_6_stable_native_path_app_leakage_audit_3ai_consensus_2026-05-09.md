# 3-AI Consensus: Goal 1603 v1.6 Stable Native-Path App-Leakage Audit

## Verdict

Accepted as a valid `v1.6` closure gate artifact.

Codex, Claude, and Gemini agree that the stable `v1.6` Python+RTDL public
surface can be described as app-generic at the RTDL primitive-contract level,
while the current native engine tree must still be described as not fully
app-agnostic internally.

This does not block the `v1.6` architecture-anchor path. It does block any
public claim that native internals are fully app-agnostic or that all native
exports are app-name-free.

## Consensus Findings

The accepted stable primitive boundary remains:

- `ANY_HIT`
- `COUNT_HITS`
- `REDUCE_FLOAT(MIN|MAX|SUM)`
- `REDUCE_INT(COUNT|SUM)`

Representative Embree and OptiX primitive exports exist for the stable surface,
including ray any-hit, ray hit-count, grouped count/sum, and fixed-radius count
threshold paths.

The native tree still contains app-shaped, workload-shaped, or proof-oriented
entry points. Examples include GIS/polygon, database, graph, directed
Hausdorff, robot/pose, and candidate-collection paths. These may remain as
compatibility, internal, historical, or proof surfaces, but they are not part of
the stable public primitive claim.

`COLLECT_K_BOUNDED` remains pending and experimental. The presence of generic
native bounded-collection exports does not promote it into the stable `v1.6`
surface.

## Fixes Applied After Review

Claude identified one traceability cleanup: the test asserted
`rtdl_embree_run_directed_hausdorff_2d`, but the report did not explicitly list
that symbol. The report now includes the directed-Hausdorff path in the
app-shaped compatibility/proof enumeration.

Claude also recommended clarifying the test meaning of "excluded". The test now
states that exclusion refers to the public `v1.6` claim boundary, not removal
from historical/proof native compatibility code.

Gemini found no required fixes.

## Blocked Claims

This consensus does not authorize:

- `v1.6` release or tag action;
- public speedup wording;
- broad RTX/GPU acceleration wording;
- true zero-copy wording;
- partner tensor handoff claims;
- whole-application speedup claims;
- package-install claims;
- stable `COLLECT_K_BOUNDED` promotion;
- claims that native internals are fully app-agnostic.

## Recommendation

Proceed with the remaining `v1.6` closure gates while keeping the public claim
boundary narrow:

```text
The v1.6 Python+RTDL release surface is app-generic at the stable RTDL
primitive-contract level for the listed supported primitives.
```

Do not publish `v1.6` yet.
