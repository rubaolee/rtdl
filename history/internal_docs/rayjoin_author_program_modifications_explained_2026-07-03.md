# RayJoin Author Program Modifications Explained

Date: 2026-07-03

## Purpose

This document records what RTDL changed in the RayJoin author program during the
paper-reproduction effort, why each change was made, and what each change does
or does not authorize us to claim.

The key point is that the current comparator is not the raw historical author
binary:

```text
AuthorOfficial = Author + RTDLContractPatch
```

`AuthorOfficial` is the author source with deterministic contract updates and
modern build/debug support. It is the comparator used for the current bounded
RayJoin reproduction evidence.

## Why This Document Is Needed

The reproduction line exposed a subtle risk:

```text
If RTDL patches the author program and then matches that patched program, the
project must say exactly what was patched.
```

Otherwise "RTDL matches AuthorOfficial" could be misread as "RTDL matches the
raw unpatched historical author binary." Those are not the same statement.

This document prevents that ambiguity.

## Author Source Baseline

Underlying author-source HEAD recorded in the RayJoin reproduction notes:

```text
02bf6220d6d20b04af77ee20364eced75cc029c9
```

AuthorOfficial POD tree recorded in the project notes:

```text
/workspace/RayJoin_goal4834_patched_author
```

AuthorOfficial binary recorded in the project notes:

```text
/workspace/RayJoin_goal4834_patched_author/release/bin/polyover_exec
```

Binary SHA256 recorded in the project notes:

```text
7ef4d5ee62180df695191d92a8ccdffcb27443a95820f04d5d6d2bd672888f47
```

Modified author-tree files recorded in the AuthorOfficial definition:

```text
src/algo/rt_pip_custom.cu
src/app/map_overlay_rt.h
src/app/output_chain.h
src/map/map.h
src/run_query.cu
src/util/markers.h
```

The semantic patch artifacts saved in this repository are:

```text
history/internal_docs/goal4834_author_sos_t_reported.patch
history/internal_docs/goal4868_author_rtdl_contract_patch.diff
```

## Classification Summary

| Category | Files | Changes algorithm semantics? | Source of authority | Claim impact |
| --- | --- | --- | --- | --- |
| Build / environment compatibility | `src/util/markers.h` and related build-support edits | No | Modern CUDA/GCC/POD compatibility need | Does not change RayJoin semantics |
| Author-clarified PIP / SoS deterministic behavior | `src/algo/rt_pip_custom.cu` | Yes | Author clarification + author source comments | Supports "author intended deterministic point-location contract" |
| RTDL-defined duplicate-half-edge deterministic contract | `src/map/map.h`, `src/app/map_overlay_rt.h` | Yes | RTDL deterministic planar-map contract | Supports "deterministic-contract consistency"; not raw unpatched-author reproduction |
| Debug / output / comparison support | `src/app/output_chain.h`, `src/run_query.cu`, debug scripts | Mostly no; used for inspection/output | Reproduction harness need | Supports diagnosis and comparison, not a standalone algorithm claim |

## Category 1: Build / Environment Compatibility

### What changed

The author source needed limited compatibility edits to build and run in the
modern POD environment. The recorded modified files include:

```text
src/util/markers.h
```

The notes describe this as compatibility/debug support, such as disabling or
adapting profiling markers that were not portable to the current CUDA/GCC
environment.

### Why it was needed

The raw historical source did not build cleanly in the current environment.
Without this compatibility layer, there would be no executable author baseline.

### What it means

This category is not a RayJoin algorithm change. It exists to make the author
program runnable.

Allowed wording:

```text
The author source was built with compatibility edits required by the current
CUDA/GCC/POD environment.
```

Forbidden wording:

```text
The compatibility edits changed the RayJoin algorithm.
```

## Category 2: Author-Clarified PIP / SoS Determinism

### Files

```text
src/algo/rt_pip_custom.cu
```

Patch artifact:

```text
history/internal_docs/goal4834_author_sos_t_reported.patch
```

### What changed

The patch adds deterministic Simulation-of-Simplicity helper logic:

```text
rayjoin_pip_sos_tie_breaker(...)
rayjoin_pip_sos_report_t(...)
```

It changes the PIP intersection path so that when multiple vertical-ray
candidate edges have the same primary hit distance, the slope preference is
encoded into the reported hit distance:

```text
optixReportIntersection(t_reported, 0)
```

instead of reporting only the unmodified primary distance:

```text
optixReportIntersection(t, 0)
```

The intended behavior is:

```text
query map 0: prefer larger slope
query map 1: prefer smaller slope
```

This slope-ordering polarity is author-derived. In the saved patch artifact,
the relevant source comment appears as pre-existing author context rather than
as an RTDL-added line:

```text
/* If im==0 we want the bigger slope, if im==1, the smaller. */
```

The more preferred candidate reports a slightly smaller `t_reported`, preventing
OptiX traversal pruning from discarding the intended candidate before
shader-side tie-breaking can observe it.

### Why it was needed

The raw author behavior could be nondeterministic when equal-height candidates
reported the same primary distance. Hardware traversal order could select one
candidate before the intended software-level tie-breaker had a chance to act.

The author clarification stated that deterministic slope-based ordering should
be encoded into the reported distance. Therefore this patch is treated as
author-intended deterministic behavior.

### What it means

This is a semantic change to the author program, but it has two parts:

- The slope-ordering rule is author-derived.
- The `t_reported` encoding is RTDL's engineering implementation of that
  author-derived rule so the preferred candidate survives OptiX traversal
  pruning. It is a faithful implementation of the intended deterministic
  contract, but the helper functions themselves were added by RTDL.

It is not a RTDL-invented overlay rule.

Allowed wording:

```text
AuthorOfficial includes the author-clarified deterministic PIP / SoS reported-
distance behavior.
```

Forbidden wording:

```text
RTDL invented the PIP slope rule.
```

Also avoid the opposite overstatement:

```text
The author source already contained RTDL's exact `t_reported` helper functions.
```

## Category 3: RTDL-Defined Duplicate-Half-Edge Deterministic Contract

### Files

```text
src/map/map.h
src/app/map_overlay_rt.h
```

Patch artifact:

```text
history/internal_docs/goal4868_author_rtdl_contract_patch.diff
```

### What changed

The patch adds canonical duplicate-half-edge handling to the author program.
The key newly introduced mechanisms are:

```text
BuildCanonicalDuplicateHalfEdges()
DuplicateKey
canonical_edge_id(...)
get_face_id_for_edge_id(...)
```

The rule groups duplicate or opposite half-edges by exact scaled unordered
endpoint pair. Within each group, it selects a stable canonical edge id. Overlay
face selection then uses the canonical edge id when resolving face ids.

Conceptually:

```text
same exact geometric edge, possibly reversed or duplicated
-> one deterministic canonical edge id
-> one deterministic face-id choice
```

### Why it was needed

Some CDB planar maps can contain identical or opposite half-edge witnesses.
Without an explicit deterministic contract, two geometrically valid witnesses
can imply different face ids. That can make overlay output depend on traversal
or input ordering rather than a stable planar-map rule.

### What it means

This is the most important claim boundary.

The duplicate-half-edge rule is defensible as a deterministic planar-map overlay
contract, but it was defined by RTDL and then applied to both sides:

```text
AuthorOfficial comparator: patched with RTDL-defined canonicalization
RTDL route: patched with the same canonicalization
```

Therefore, equality in cases affected by this rule means:

```text
RTDL matches the deterministic contract applied to both systems.
```

It does **not** mean:

```text
RTDL independently matches the raw unpatched author binary's behavior for every
ambiguous duplicate-half-edge case.
```

Allowed wording:

```text
The Block x Water and representative Section 5.7 overlay results are equality
against AuthorOfficial, including an RTDL-defined deterministic duplicate-
half-edge contract.
```

Forbidden wording:

```text
The duplicate-half-edge-affected results prove raw unpatched author-output
reproduction.
```

## Category 4: Debug / Output / Comparison Support

### Files

Recorded modified files include:

```text
src/app/output_chain.h
src/run_query.cu
```

There are also many saved debug scripts and artifact readers in
`history/internal_docs/`.

### What changed

These edits and scripts supported diagnosis:

- dumping candidate traces;
- comparing output-chain prefixes;
- exposing counts / hashes / first-diff positions;
- building exact comparison artifacts;
- separating raw author behavior, AuthorPatch behavior, AuthorOfficial
  behavior, bundled helper behavior, and public RTDL primitive behavior.

### Why it was needed

Full overlay output is huge. A small missing chain can shift millions of later
lines. The project needed targeted introspection to reduce the problem to
specific contracts:

- PIP / SoS reported-distance tie behavior;
- midpoint face state;
- rational midpoint construction;
- LSI row materialization;
- duplicate-half-edge canonicalization.

### What it means

Debug/output changes are evidence tools. They should not be counted as RayJoin
algorithm improvements unless a specific file also changes semantic behavior.

There are two subcases:

- Pure diagnostics, such as environment-gated trace dumps, should not enter the
  compared output stream. They help locate a mismatch but do not define the
  comparator.
- Any change that affects the bytes being compared must be treated as part of
  the `AuthorOfficial` comparator boundary. It cannot be presented as raw
  unpatched-author output.

The current reproduction documents treat `output_chain.h` and `run_query.cu`
as compatibility/debug modifications, not as the semantic reason for changing
the comparison contract. If later evidence shows that one of these files
changed the compared output format, that result must carry the same explicit
comparator caveat as the duplicate-half-edge contract.

Allowed wording:

```text
The author tree contains output/debug support edits used to produce comparison
artifacts.
```

Forbidden wording:

```text
Every modified author file changes the RayJoin algorithm.
```

Also forbidden:

```text
Output/debug edits can be ignored even if they change the compared bytes.
```

## What AuthorOfficial Means

The precise meaning is:

```text
AuthorOfficial =
  author source
  + modern build/debug compatibility edits
  + author-derived PIP / SoS reported-distance deterministic behavior
  + RTDL-defined duplicate-half-edge deterministic planar-map contract
```

The project may use `AuthorOfficial` as a fair deterministic comparator only if
the reports name it clearly.

## What AuthorOfficial Does Not Mean

It does not mean:

- raw unpatched author binary;
- the exact historical nondeterministic traversal order;
- proof that RTDL matches every old output file produced before the
  deterministic contract was defined;
- proof that the RTDL-defined duplicate-half-edge rule came from the original
  author source.

## Impact On Current Section 5.2 / 5.3 / 5.7 Claims

### Section 5.2 LSI

Section 5.2 LSI count results are not directly affected by the PIP/SoS or
duplicate-half-edge overlay contract changes.

Allowed claim:

```text
RTDL public planar-map LSI matches the available AuthorOfficial counts for the
tested pairs.
```

### Section 5.3 PIP

The strongest current non-circular evidence is the raw `query_exec -query=pip`
per-point closest-edge hash match on the two serious US workloads.

Allowed claim:

```text
RTDL public planar-map point-location/PIP matches the raw author per-point
closest-edge hashes on County x Zipcode and Block x Water.
```

Australia representative remains count-consistent only for 5.3 because its raw
closest-edge hash does not match.

### Section 5.7 Overlay

Section 5.7 equality is against `AuthorOfficial`.

Allowed claim:

```text
RTDL matches the deterministic AuthorOfficial comparator on two available
full-stream pairs and two current-source representative pairs.
```

Required caveat:

```text
Where duplicate-half-edge ambiguity is involved, this is deterministic-contract
consistency under an RTDL-defined rule applied to both sides, not raw
unpatched-author reproduction.
```

## Claim Rules

### Allowed

- "AuthorOfficial baseline"
- "AuthorOfficial = Author + RTDLContractPatch"
- "deterministic author-contract comparator"
- "author-derived PIP / SoS reported-distance patch"
- "RTDL-defined duplicate-half-edge deterministic contract"
- "bounded Section 5.7 reproduction against AuthorOfficial"
- "deterministic-contract consistency"

### Not Allowed

- "raw author output reproduced" for duplicate-half-edge affected rows;
- "unpatched author binary reproduced" for AuthorOfficial comparisons;
- "the author originally implemented duplicate-half-edge canonicalization";
- "full all-eight hidden-input Section 5.7 reproduction";
- "broad RayJoin speedup";
- "Numba is correctness-critical" for the current Section 5.2 / 5.3 / 5.7
  evidence.

## Open Honesty Items

1. Full old-comparator-vs-new-comparator impact has not been quantified for
   every pair.
2. County x Zipcode currently has recorded zero output-line change after
   duplicate contract revalidation in the checked stream.
3. Block x Water has targeted witness evidence that duplicate-half-edge
   semantics changed, but no full impact count is recorded.
4. Representative current-source OSM rows are not old hidden paper-preprocessed
   CDB inputs.

## Bottom Line

We changed the author program in two semantically important ways:

1. A **PIP / SoS reported-distance patch** that follows the author-clarified
   intended deterministic behavior.
2. A **duplicate-half-edge canonicalization patch** that RTDL defines as a
   deterministic planar-map overlay contract and applies to both AuthorOfficial
   and RTDL.

The first is author-derived. The second is RTDL-defined. Reports must keep this
distinction visible.
