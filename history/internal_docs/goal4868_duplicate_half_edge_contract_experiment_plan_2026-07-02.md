# Goal4868: RTDL Duplicate Half-Edge Contract Experiment

## Purpose

While waiting for the author to clarify the intended same-height / same-slope duplicate-half-edge SoS rule, define and test one RTDL-owned deterministic contract that can be applied to both:

- RTDL directed planar-map point-location; and
- an explicitly labeled `Author+RTDLContractPatch` baseline.

This is **not** a claim that the original AuthorPatch output is reproduced. It is a contract experiment to replace traversal-order dependence with explicit language/runtime semantics.

## Candidate Contract

For directed planar-map point-location, if multiple half-edges represent the same geometric segment in opposite directions, they form one duplicate-half-edge group.

Group key:

- scaled endpoint pair, unordered:
  `min((sx0, sy0), (sx1, sy1)), max((sx0, sy0), (sx1, sy1))`

Canonical member:

- the member with the smallest stable source edge/segment id.

Point-location normalization:

- the native PIP route may let OptiX traversal select any member of the duplicate group;
- after `closest_eid` is produced, normalize it to the canonical member of its duplicate group;
- the resulting face is `get_face_id(canonical_edge)`, using the same directed face convention already used by RayJoin / RTDL:
  - if `x0 < x1`, use right face;
  - otherwise use left face.

## Why This Is A Generic Rule

This rule is not RayJoin-output-specific. It is a deterministic contract for a common planar-map degeneracy:

- two directed half-edges encode the same geometric boundary;
- OptiX traversal order is not a valid language semantic;
- source-order canonicalization makes the result stable and testable.

It does **not** hard-code:

- a dataset,
- a point id,
- a face id,
- "prefer nonzero face",
- "prefer exterior",
- "prefer reverse edge",
- "prefer larger/smaller slope".

Those heuristics were already shown to overfit and conflict across witnesses.

## Expected Consequence

This may differ from the original AuthorPatch output in cases where the original program's same-line duplicate winner was a traversal artifact.

Therefore claims must be split:

- Allowed: `RTDL deterministic duplicate-half-edge contract matches Author+RTDLContractPatch`.
- Not allowed unless separately proven: `RTDL byte-reproduces original AuthorPatch Section 5.7`.

## Minimal Experiments

1. Extend the duplicate-half-edge micro probe to compute canonical duplicate groups and show that both input orders normalize to the same canonical segment.
2. Implement the normalization in RTDL point-location output for the RayJoin CDB / directed planar-map route.
3. Patch the author program with the same post-PIP closest-edge canonicalization and label it `Author+RTDLContractPatch`.
4. Run small synthetic Author+RTDLContractPatch vs RTDL.
5. Run focused Block x Water witness probes.
6. Only then run bounded streaming compare.

## Review Questions Before Full Section 5.7 Claim

1. Is source-edge canonicalization an acceptable generic contract for duplicate half-edges?
2. Is post-PIP closest-edge normalization acceptable, or must the rule be encoded into `t_reported`?
3. If the old AuthorPatch output differs from Author+RTDLContractPatch, should exact original-author reproduction be marked blocked by undefined traversal artifact?
4. What regression suite is required before keeping this as a core RTDL behavior?
