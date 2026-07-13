# RayJoin 5.2 / 5.3 / 5.7 Claude Amendment Response

Date: 2026-07-03

## Context

Claude reviewed the RayJoin reproduction summary and correctness postmortem and
returned:

```text
approve_with_required_amendments
```

The central criticism was correct: the reports used `AuthorOfficial =
Author+RTDLContractPatch` without sufficiently separating author-derived
contract repairs from RTDL-defined deterministic contract repairs.

This response records the amendments applied.

## Files Updated

- `history/internal_docs/rayjoin_sections_52_53_57_reproduction_report_2026-07-03.md`
- `history/internal_docs/rayjoin_correctness_problem_root_cause_and_resolution_2026-07-03.md`
- `docs/release_reports/v2_14/rayjoin_section57_bounded_reproduction.md`

## Amendment Mapping

### AM1: Separate author-derived vs RTDL-defined contract elements

Status: addressed.

The reports now distinguish:

- Author-derived directed point-location / PIP SoS behavior:
  query map 0 prefers larger slope, query map 1 prefers smaller slope, and the
  priority is encoded into reported hit distance.
- RTDL-defined duplicate-half-edge canonicalization:
  a deterministic planar-map overlay contract applied to both comparator and
  RTDL.

The documents now state that duplicate-half-edge-dependent equality is
deterministic-contract consistency, not raw unpatched-author reproduction.

### AM2: Quantify patch impact

Status: partially addressed, with explicit remaining limit.

Known quantified / bounded facts now recorded:

- County x Zipcode retained the same checked full-stream output after duplicate
  contract revalidation: `0 / 87,758,114` output lines changed in that stream.
- Block x Water has targeted witness evidence that at least two probed
  duplicate-half-edge cases changed semantics under the canonicalization rule.
- A full old-comparator-vs-new-comparator impact count for Block x Water has
  not yet been produced, so Block x Water remains classified as
  deterministic-contract consistency rather than raw author reproduction.

### AM3: Resolve Australia 5.3 vs 5.7 evidence tension

Status: addressed.

The Section 5.2/5.3/5.7 report now states:

- Australia 5.3 closest-edge hash is compared to raw `query_exec` and remains
  count-consistent only.
- Australia 5.7 byte equality is compared to `AuthorOfficial`.
- This is not a contradiction; it means the two rows use different evidence
  tiers.

### AM4: Rank evidence strength by comparator

Status: addressed.

The documents now rank evidence:

1. Strongest non-circular evidence: US Section 5.3 raw `query_exec` per-point
   closest-edge hash matches.
2. Valid deterministic-contract evidence: Section 5.7 equality against
   `AuthorOfficial`.
3. Representative evidence: current-source representative OSM rows, not hidden
   old paper-input rows.

### AM5: Public wording must name the comparator

Status: addressed.

The public RayJoin Section 5.7 page now says equality is against the
deterministic author-contract comparator and explicitly warns that
duplicate-half-edge ambiguous cases should not be read as raw unpatched
historical author-binary equality.

### AM6: Clarify map-id-dependent SoS generality

Status: addressed.

The correctness postmortem now describes the SoS rule as a directed two-map
planar-overlay point-location contract. It no longer implies that the exact
map0/map1 policy is a universal standalone PIP semantic outside the directed
overlay setting.

## Remaining Honest Limits

- Full old-vs-new duplicate-contract impact has not been quantified for every
  pair.
- Representative current-source rows are not old hidden paper-preprocessed CDB
  reproduction.
- Section 5.7 equality is correctness evidence, not speedup evidence.
- Numba is not on the correctness-critical path for this reproduction record.

## Requested Re-Review

Please re-review the amended files and decide whether the AM1-AM6 concerns are
resolved enough to accept the two reports as bounded, honest reproduction
records.

Preferred verdict labels:

- `approve_amended_rayjoin_52_53_57_reports`
- `approve_with_remaining_minor_amendments`
- `block_until_comparator_boundary_fixed`
