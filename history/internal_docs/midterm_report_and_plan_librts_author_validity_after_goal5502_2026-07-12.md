# LibRTS Paper-App Midterm Report And Completion Plan

Date: 2026-07-12

## Executive Conclusion

The LibRTS paper-app campaign has already produced a useful generic RTDL
system result, but it has not completed full paper reproduction.

The current evidence says:

```text
RTDL generic AABB route == selected independent float32 contract: 5/5 prefixes
author == selected independent float32 contract: 1/5 prefixes
author diverges from that contract: 4/5 prefixes
full parks.bz2 author run: CUDA allocation failure
```

This is not enough to declare the author program globally wrong. It is enough
to make the current engineering decision: do not change RTDL core and do not
copy an author-specific divergence into RTDL. A future full-input oracle must
decide whether exact reproduction requires a generic RTDL fix or whether the
author result is the divergent implementation.

## Project Objective

LibRTS is the fifth paper-reproduction application used to pressure-test RTDL.
The project has four purposes:

1. Reproduce author results on identical inputs where the author contract is
   available.
2. Test generic RTDL AABB, prepared-index, columnar, mutation, and OptiX
   capabilities against a real spatial application.
3. Separate count equality, relation equality, numerical semantics, capacity,
   and performance instead of treating them as one result.
4. Extract only reusable system capabilities; keep WKT loading, author
   compatibility, provenance, cache policy, and paper claims in the app.

Embree is excluded from this entire campaign.

## What Has Been Completed

### Provenance and execution environment

- The official PPoPPAE archive was downloaded and verified by published MD5.
- Selected archive members have recorded member path, size, and SHA-256.
- The pinned RTSpatial/SpatialQueryBenchmark author environment builds and runs
  on the RTX 4000 Ada POD.
- Exact selected members were passed unchanged to author and RTDL gates.

### Generic RTDL capabilities exercised

- `Aabb2DColumns` and prepared columnar AABB input.
- Generic point-contains, range-contains, and range-intersects operations.
- Native OptiX AABB preparation and query paths.
- Generic mutable AABB lifecycle with stable IDs.
- Native sparse-slot refit for fixed-cardinality updates.
- Atomic snapshot rebuild for cardinality-changing mutations.
- Rollback recovery and fail-closed poisoning after injected native failure.
- App-owned hash-bound AABB cache for repeated exact inputs.

### Paper-app evidence

- Exact point-contains count matrix: 6/6 matched.
- Exact range-contains count evidence: matched on the selected exact member.
- Exact range-intersects batch: 3 matches, 2 count disagreements, 1 author
  CUDA OOM.
- Goal5501 independent prefixes: CPU float64, CPU float32, and padding
  variants were measured separately.
- Goal5502 author-validity gate: five prefixes were classified against the
  selected generic inclusive float32 contract.

### Goal5502 evidence matrix

| case | geometry prefix | author | RTDL | CPU FP32 | decision |
|---|---:|---:|---:|---:|---|
| parks_Europe | 100K | 13,695,048 | 13,695,053 | 13,695,053 | preserve RTDL |
| lakes.bz2 | 100K | 12,596,850 | 12,596,850 | 12,596,850 | both agree |
| parks_Europe | 250K | 34,240,217 | 34,240,244 | 34,240,244 | preserve RTDL |
| lakes.bz2 | 250K | 34,581,812 | 34,586,817 | 34,586,817 | preserve RTDL |
| parks.bz2 | 100K | 11,815,394 | 11,815,398 | 11,815,398 | preserve RTDL |

CPU FP64 was also measured. It does not consistently match either side, so
it is a numerical diagnostic rather than the selected contract. Padding also
does not explain the parks differences.

## Current Architecture Assessment

The architecture is still correctly split:

```text
RTDL core:
  generic AABB columns, prepared indexes, predicates, native backends,
  mutation lifecycle, stable-ID refit, fail-closed state

LibRTS app:
  WKT parsing, author build and flags, archive provenance, cache policy,
  count parser, oracle selection, comparison, and paper claim boundaries
```

No LibRTS-specific primitive has been added to RTDL core during this campaign.
The current mismatch does not justify changing that boundary.

## Open Problems

### 1. Full-input numerical contract

The prefix oracle shows a persistent RTDL/author difference on four of five
samples, but the full-input author contract is not independently adjudicated.
Possible causes include float conversion, boundary semantics, indexing behavior,
or an author implementation detail. No single cause is authorized yet.

### 2. Full-input capacity

The full `parks.bz2` author execution fails with CUDA allocation failure. The
100K capacity prefix is not a solution. A larger GPU, load-factor policy, or
query batching may be required.

### 3. Relation-level output

The standard author binary exposes counts rather than pair rows. Equal counts
cannot prove equal relations. A pair-row comparator or independently accepted
relation oracle is required for relation-level reproduction.

### 4. Performance

No author/RTDL performance ratio is authorized. Author internal query time,
author process wall, RTDL WKT load, index preparation, query wall, and native
primitive time are different denominators.

## Decision Rule

Every future case must enter one of four states:

```text
author == oracle and RTDL == oracle
  -> no semantic fix required

author == oracle and RTDL != oracle
  -> fix generic RTDL before exact reproduction claim

RTDL == oracle and author != oracle
  -> preserve generic RTDL; do not copy author divergence

author != oracle and RTDL != oracle
  -> unresolved; collect stronger contract or relation evidence
```

The count difference alone never proves that the author is wrong. The selected
oracle and its semantics must be stated for every decision.

## Planned Goals After Review

### Goal5503: Author contract source audit

Audit the pinned author source and build configuration for coordinate types,
intersection inclusivity, conversion points, and any documented padding or
epsilon. Deliver a source-backed contract matrix, not a code change.

Exit labels:

```text
author_float32_inclusive_contract_supported
author_contract_ambiguous_requires_relation_evidence
```

### Goal5504: Discriminating numerical semantics fixtures

Build app-owned fixtures that independently distinguish inclusive/strict
boundaries, float32/float64 conversion, signed zero, near-touching boxes, and
padding. Run author, RTDL, and CPU references where possible. Do not add a
LibRTS-specific mode to RTDL before the genericity decision.

### Goal5505: Scalable independent oracle

Extend the independent oracle beyond 250K prefixes using a documented memory
budget and deterministic samples. The oracle must report counts and, where
feasible, canonical relation rows. It must fail closed rather than silently
downsample an alleged full-input result.

### Goal5506: Full-input capacity campaign

On a sufficiently large POD, test the author and RTDL full inputs with explicit
load-factor, batching, and prepared-index policies. Keep capacity and semantic
results separate. A failure remains a capacity boundary.

### Goal5507: Full-input author-validity decision

Combine Goal5503-5506 into the three-way author/oracle/RTDL decision. This goal
must decide whether a generic RTDL fix is required, author divergence can be
ignored for RTDL correctness, or evidence remains unresolved.

### Goal5508: Exact reproduction or bounded closeout

If the author is validated and RTDL is fixed, require exact same-input
reproduction. If the author diverges from the independent contract, close the
RTDL line with explicit author incompatibility. If unresolved, close only at
the bounded evidence boundary and do not claim full paper reproduction.

## Resource Plan

- Local Windows/Linux: source audit, fixtures, tests, schema, and report work.
- Current RTX 4000 Ada POD: suitable for prefix and most exact AABB gates.
- Full `parks.bz2`: likely needs a larger-memory GPU or an accepted batching
  strategy; the current 20 GiB class device has already exposed an author OOM.
- No Embree installation or resource is required.

## Success Criteria

The project is complete only when one of these evidence-backed outcomes is
reached:

1. Author and RTDL are both validated against the same independent contract,
   and exact reproduction passes on the authorized full inputs.
2. RTDL is validated against the generic contract while the author diverges;
   the author discrepancy is explicitly closed without changing RTDL core.
3. The remaining full-input evidence is genuinely unavailable or ambiguous;
   the project closes honestly at bounded evidence without full-paper claims.

No outcome permits author-performance parity, complete paper reproduction,
zero-copy, or Embree claims without separate evidence.
