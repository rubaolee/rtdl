# External Review: LibRTS Goals5492-5500

## Verdict

```text
approve_librts_goals5492_5500_honest_partial_evidence__range_intersects_mismatch_diagnosis_required
```

Goals5492-5499 are approved as bounded evidence. Goal5500 is approved as an
honest partial six-geometry batch result, not as a matched batch or a complete
range-intersects matrix.

## Verified Findings

- The official archive is bound to MD5
  `89e589f086038f1cd3af9e3ed67da8c8` and the selected members carry size and
  SHA-256 evidence.
- Goal5492 inventories `14` exact point-contains, `14` exact range-contains,
  `42` exact range-intersects, and no exact PIP or mutation pairs.
- Goal5493 matches exact range-contains `dtl_cnty` count `117314`.
- Goals5496, 5497, and 5499 match exact `dtl_cnty` range-intersects counts
  `1570285`, `242920`, and `239884`.
- Goal5500 attempts six exact geometry/query pairs: three matches, two count
  disagreements, and one author-side CUDA OOM. The batch result remains
  `matched=false` and `complete_range_intersects_matrix_claimed=false`.
- `range_intersects` is a generic AABB operation; no LibRTS-specific primitive
  was found in RTDL core/native.
- Goal5494 correctly keeps cache lifecycle app-owned because no second generic
  consumer and no generic lifecycle contract justify core promotion.
- Author internal query metrics and RTDL load/prepare/query phases remain
  different denominators; no performance ratio is authorized.
- Embree remains explicitly out of scope.

## Goal Decisions

```text
Goal5492: approve
Goal5493: approve
Goal5494: approve
Goal5495: approve
Goal5496: approve
Goal5497: approve
Goal5498: approve
Goal5499: approve
Goal5500: approve as honest partial evidence only
```

## Required Next Goal

The range-intersects line remains open. Before any broader range-intersects
claim or closeout, Goal5501 must diagnose the two count disagreements:

```text
parks_Europe: author 216977211, RTDL 216981002, delta +3791
lakes.bz2:    author 1113229623, RTDL 1113284318, delta +54695
```

The diagnostic must include a discriminating independent CPU AABB
intersection oracle on a feasible workload or synthetic reduction. It should
test the generic possibilities already identified by the evidence: float32
conversion, AABB padding, diagonal intersection semantics, and other
author/RTDL contract differences. It must not assume that either side is
wrong before the oracle or relation-level evidence says so.

The `parks.bz2` author CUDA OOM remains capacity evidence and is not a semantic
mismatch. Any retry requires a separately justified capacity/load-factor plan.

## Claim Boundary

The following remain closed:

```text
complete range-intersects matrix
pointwise relation equality for the count-only author binary
Figure 6 reproduction
full LibRTS paper reproduction
author performance parity or any author-vs-RTDL ratio
device zero-copy
Embree comparison
```

The strongest authorized summary is:

```text
LibRTS has exact archive provenance and a generic columnar AABB route. Across
Goals5492-5500, three exact range-intersects cases match author counts, two
larger cases disagree in count and require diagnosis, and one author case is
blocked by CUDA allocation failure. The range-intersects line remains open.
```

## Review Notes

No blocking findings or required amendments were identified. The external
review did not rerun the test suite; it verified the evidence JSON, per-case
flags, provenance, core genericity, and claim boundaries directly.
