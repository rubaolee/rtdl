# RayJoin Sections 5.2 / 5.3 / 5.7 Reproduction Report

Date: 2026-07-03

Status: prepared for Claude review.

## Executive Summary

RTDL v2.14 now has a bounded RayJoin reproduction record across three paper
sections:

- **Section 5.2 LSI**: reproduced for the available tested pairs as scalar
  line-segment-intersection counts.
- **Section 5.3 PIP / point-location**: exact per-point closest-edge agreement
  on the two serious recovered US workloads, plus count-consistent representative
  evidence for Australia Lakes/Parks.
- **Section 5.7 polygon overlay**: bounded reproduction, consisting of two
  available paper-style full-stream pairs and two current-source Lakes/Parks
  representative pairs.

This is a correctness and reproduction report. It does **not** authorize:

- full hidden-input all-eight reproduction;
- broad RTDL speedup over RayJoin;
- Embree claims;
- Numba correctness-critical claims;
- treating current-source OSM representative data as the original hidden paper
  input;
- treating diagnostic timings as optimized performance.

## Comparator

The comparator used by this line is:

```text
AuthorOfficial = Author+RTDLContractPatch
```

This comparator is the author code with deterministic contract updates for the
ambiguous cases exposed during reproduction work:

- directed point-location / PIP equal-height tie handling;
- duplicate-half-edge deterministic face selection for overlay continuation.

These are treated as correctness-contract repairs, not as benchmark-specific
performance changes.

Important evidence boundary:

- The directed point-location / PIP equal-height rule is author-derived. It is
  supported by the author clarification and by the author source comment that
  query map 0 prefers the larger slope while query map 1 prefers the smaller
  slope, and that this priority must affect reported hit distance.
- The duplicate-half-edge canonicalization is RTDL-defined deterministic
  contract repair. It is applied to both the patched author comparator and the
  RTDL path. Results depending on this rule are therefore **deterministic
  contract consistency** results, not independent reproduction of the original
  unpatched author behavior.

This distinction matters. `AuthorOfficial` is the correct comparator for the
current bounded RTDL contract, but it must not be described as raw author output
or as proof that every ambiguous duplicate-half-edge case matches the original
unpatched binary.

## Public RTDL Model Used

The clean app-author model is:

```text
RTDL core:
  public planar-map line-segment intersection primitive
  public planar-map point-location / PIP primitive
  deterministic directed-overlay contracts

Application layer:
  CDB selection and loading
  author-compatible parameters
  output-chain construction and formatting
  exact-vs-representative labeling
```

The public primitive front doors are:

```python
from rtdsl import prepare_planar_map_lsi_2d_optix
from rtdsl import prepare_planar_map_point_location_2d_optix
```

The representative Section 5.7 route explicitly uses the public primitive
shape:

```text
public planar-map LSI
-> public planar-map point-location / PIP
-> Python application-level output-chain assembly
```

Numba is not on the correctness-critical route for the current 5.2/5.3/5.7
evidence. It remains a possible future partner for app-layer acceleration.

## Section 5.2: LSI

### Purpose

Section 5.2 checks line-segment-intersection count behavior. This section does
not test point-location, overlay output-chain construction, or performance.

### Route

RTDL route:

```python
prepare_planar_map_lsi_2d_optix(base).count(query)
```

No `rtdsl.rayjoin_overlay` evidence is used for the public RTDL route.

### Results

| Pair | Orientation | AuthorOfficial LSI count | RTDL public LSI count | Match | Classification |
| --- | --- | ---: | ---: | --- | --- |
| County x Zipcode | County base, Zipcode query | 961,165 | 961,165 | yes | exact count match |
| Block x Water | Block base, Water query | 649,605 | 649,605 | yes | exact count match |
| Australia Lakes x Parks representative | Lakes base, Parks query | 13,622 | 13,622 | yes | representative exact count match |

Important orientation note: the Australia Section 5.2 forward count `13,622`
is not the same as the opposite-oriented Section 5.7 LSI row count `13,452`.
That difference is expected and not a contradiction.

### Evidence Files

- `history/internal_docs/goal4877_section52_lsi_authorofficial_revalidation_2026-07-02.md`
- `history/internal_docs/goal4877_section52_lsi_authorofficial_revalidation_summary.json`
- `history/internal_docs/antigravity_goal4877_section52_lsi_authorofficial_revalidation_review_2026-07-02.md`

External review verdict:

```text
approve_goal4877_section52_lsi_authorofficial_revalidated
```

### Boundary

Section 5.2 proves available-pair LSI count agreement only. It does not prove
PIP, overlay, all-eight hidden-input reproduction, Numba, Embree, or speedup.

## Section 5.3: PIP / Point-Location

### Purpose

Section 5.3 checks point-in-polygon / point-location behavior. This section is
affected by the updated deterministic point-location contract, so it required
fresh AuthorOfficial comparison rather than simple reclassification of older
evidence.

### Correct Comparator

The correct author comparator is:

```text
query_exec -query=pip
```

During the work, an earlier harness mistake was caught: `polyover_exec` can run
PIP-shaped smoke workloads, but it is not the correct Section 5.3 per-point
closest-edge comparator.

### Route

RTDL route:

```python
prepare_planar_map_point_location_2d_optix(...)
```

Comparison contract:

```text
author: closest_eids != DONTKNOW and FNV64 over closest edge ids
RTDL:   segment_id != DONTKNOW and FNV64 over (segment_id - 1)
```

The `-1` normalization is required because RTDL reports 1-based segment ids
while the author comparator reports 0-based closest edge ids.

### Results

| Pair | Query points | AuthorOfficial positives | RTDL found segments | Count match | Author hash | RTDL normalized hash | Hash match | Classification |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- | --- |
| County x Zipcode | 47,862,092 | 47,327,744 | 47,327,744 | yes | 17,585,803,063,680,255,704 | 17,585,803,063,680,255,704 | yes | exact per-point closest-edge match |
| Block x Water | 44,863,618 | 44,841,020 | 44,841,020 | yes | 13,878,963,590,670,293,968 | 13,878,963,590,670,293,968 | yes | exact per-point closest-edge match |
| Australia Lakes x Parks representative | 992,505 | 958,981 | 958,981 | yes | 13,434,159,047,986,799,888 | 8,149,910,373,246,904,473 | no | count-consistent only |

### Evidence Files

- `history/internal_docs/goal4878_section53_pip_authorofficial_reproduction_2026-07-02.md`
- `history/internal_docs/goal4878_section53_pip_authorofficial_summary.json`
- `history/internal_docs/antigravity_goal4878_section53_pip_authorofficial_reproduction_review_2026-07-02.md`

External review verdict:

```text
approve_goal4878_section53_authorofficial_two_serious_exact_one_representative_count_only
```

### Boundary

County x Zipcode and Block x Water are exact per-point closest-edge matches.
Australia representative is count-consistent only and must not be described as
exact per-point equivalent.

Section 5.3 does not prove Section 5.7 overlay output equality or performance.

## Section 5.7: Polygon Overlay

### Purpose

Section 5.7 is the full polygon-overlay workload. It composes lower-level
geometry operations such as LSI and PIP with overlay continuation/output-chain
construction.

### Proven Claim

The approved bounded claim is:

```text
RTDL reproduces Section 5.7 polygon-overlay behavior on two available
full-stream pairs and two current-source Lakes/Parks representative pairs.
```

This is not a full old hidden-input eight-pair reproduction.

### Evidence Matrix

| Pair | Evidence type | Input label | Comparator | Route | Result | Allowed claim |
| --- | --- | --- | --- | --- | --- | --- |
| County x Zipcode | full-stream overlay | available paper-style pair | AuthorOfficial, with no observed output change from the duplicate-half-edge contract on this pair | RTDL Section 5.7 route after core contract repairs | exact stream match | bounded available-pair reproduction under the deterministic author-contract comparator |
| Block x Water | full-stream overlay | available paper-style pair | AuthorOfficial, including RTDL-defined duplicate-half-edge canonicalization | RTDL Section 5.7 route after duplicate-half-edge repair | exact stream match | bounded deterministic-contract consistency on an available pair |
| Australia Lakes x Parks | full overlay output | representative current-source OSM | AuthorOfficial, including deterministic-contract updates | public RTDL LSI + public RTDL PIP + app output writer | byte-equal | representative current-source deterministic-contract consistency through public primitives |
| South America Lakes x Parks | full overlay output on bounded slice | representative current-source OSM bounded slice | AuthorOfficial, including deterministic-contract updates | public RTDL LSI + public RTDL PIP + app output writer | byte-equal | bounded representative deterministic-contract consistency through public primitives |

### Pair Details

#### County x Zipcode

```json
{
  "stream_match": true,
  "first_diff": null,
  "streamed_line_count": 87758114,
  "streamed_chain_count": 29253961,
  "streamed_point_count": 58504153,
  "streamed_face_count": 115515
}
```

#### Block x Water

```json
{
  "stream_match": true,
  "first_diff": null,
  "streamed_line_count": 138674679,
  "streamed_chain_count": 46224916,
  "streamed_point_count": 92449763,
  "streamed_face_count": 2581495
}
```

#### Australia Lakes x Parks

```text
sha256: a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e
lines: 276,320
bytes: 6,189,260
byte_equal_to_author: true
```

#### South America Lakes x Parks

```text
sha256: 8b4e80a50fedb77120781e8bf39c9f2db1df3a1f823716f7dab9c1f9eed1862d
lines: 97,893
bytes: 2,096,449
byte_equal_to_author: true
```

South America is intentionally bounded. The full current-source extract is much
larger than the old paper LKSA scale in the current public OSM snapshot, and
first-load text-CDB staging dominates the experiment. The bounded slice keeps
the correctness test controlled.

### Evidence Files

- `history/internal_docs/goal4883_section57_final_bounded_reproduction_packet_2026-07-03.md`
- `history/internal_docs/antigravity_goal4883_section57_final_bounded_reproduction_packet_review_2026-07-03.md`
- `docs/release_reports/v2_14/rayjoin_section57_bounded_reproduction.md`
- `history/internal_docs/antigravity_goal4884_reader_facing_section57_page_review_2026-07-03.md`

External review verdicts:

```text
approve_goal4883_final_bounded_section57_packet
approve_goal4884_reader_facing_section57_page
```

### Boundary

Section 5.7 is reproduced in a bounded form. Do not claim:

- full exact old eight-pair Section 5.7 reproduction;
- exact old hidden paper CDB reproduction for continent Lakes/Parks pairs;
- raw unpatched-author byte equality for duplicate-half-edge ambiguous cases;
- broad RTDL speedup over the author implementation;
- that Numba is on the correctness-critical path;
- that representative current-source data equals old paper input;
- that Africa, Asia, Europe, or North America have been reproduced;
- that Python output-chain assembly is performance-optimal.

### Comparator Strength And Patch Impact

The evidence should be read in tiers:

1. **Strongest non-circular evidence**: Section 5.3 County x Zipcode and Block x
   Water match raw author `query_exec -query=pip` per-point closest-edge hashes.
   This does not depend on the duplicate-half-edge comparator patch.
2. **Deterministic author-contract evidence**: Section 5.7 overlay rows match
   `AuthorOfficial`, which is author code plus deterministic contract repairs.
   This is the right comparator for the current RTDL contract, but it is weaker
   than raw author-output equality where the RTDL-defined duplicate-half-edge
   rule is involved.
3. **Representative evidence**: Australia and South America use current-source
   representative OSM inputs, not hidden old paper-preprocessed CDB inputs.

Patch impact is only partially quantified:

- County x Zipcode retained the same full-stream output under the duplicate
  half-edge contract revalidation: `0 / 87,758,114` output lines changed in the
  checked stream.
- Block x Water has targeted witness evidence that at least two probed
  duplicate-half-edge cases changed semantics under the new canonicalization
  rule. A full old-comparator-vs-new-comparator impact count has not yet been
  produced, so its Section 5.7 result must remain classified as
  deterministic-contract consistency.
- Australia 5.3 and Australia 5.7 use different evidence comparators. The 5.3
  closest-edge hash is against raw `query_exec` and is count-consistent only;
  the 5.7 byte-equality is against `AuthorOfficial`. This is not a
  contradiction. It shows that raw closest-edge identity and the patched
  deterministic overlay comparator are different evidence tiers.

## Relationship Across 5.2, 5.3, And 5.7

Section 5.2 and 5.3 are lower-level operation checks. Section 5.7 is stronger
because it checks full overlay output equality on the listed pairs.

Current state:

| Section | What is checked | Strongest current result | Main limit |
| --- | --- | --- | --- |
| 5.2 | LSI count | exact count match on County x Zipcode, Block x Water, and Australia representative forward direction | not all hidden old pairs |
| 5.3 | PIP / point-location closest-edge result | exact per-point closest-edge match on County x Zipcode and Block x Water | Australia representative is count-consistent only |
| 5.7 | full polygon-overlay output | two full-stream available pairs plus two byte-equal representative public-primitives pairs | not full hidden-input all-eight reproduction |

## Performance Interpretation

Do not treat this report as performance evidence.

The reproduction line showed that successful representative runs are dominated
by:

- text-CDB loading and parsing;
- CDB packing/staging;
- Python output-chain assembly;
- diagnostic hashing and output comparison where enabled.

The RT-core LSI/PIP kernels are correctness-critical, but they are not the
dominant wall-time cost in the representative Section 5.7 runs.

Future performance work should target:

1. durable binary CDB staging and cache reuse;
2. public dataset loader improvements;
3. app-layer output-chain assembly acceleration;
4. optional Numba/CuPy partner acceleration where it genuinely removes
   Python-side bottlenecks.

## Final Proposed Status

Recommended status:

```text
rayjoin_sections_52_53_57_bounded_reproduction_supported
```

Recommended public wording:

```text
RTDL v2.14 has a bounded RayJoin reproduction record: Section 5.2 LSI matches
available counts; Section 5.3 PIP matches exact closest-edge results on the two
serious recovered US workloads; and Section 5.7 polygon overlay matches two
available full-stream pairs plus two current-source representative Lakes/Parks
pairs against the deterministic author-contract comparator. Some ambiguous
duplicate-half-edge cases use an RTDL-defined deterministic contract applied to
both comparator and RTDL, so those rows are deterministic-contract consistency
evidence, not raw unpatched-author output equality. This is bounded correctness
evidence, not a full hidden-input all-eight reproduction or a broad speedup
claim.
```

## Reviewer Questions

1. Is the Section 5.2 LSI revalidation correctly scoped to counts and not
   overextended into PIP, overlay, or performance?
2. Is the Section 5.3 PIP result correctly classified as two exact US workloads
   plus one count-consistent representative workload?
3. Is the Section 5.7 result correctly described as bounded reproduction, not
   full hidden-input all-eight reproduction?
4. Does the report preserve the distinction between available paper-style pairs
   and current-source representative pairs?
5. Does the report avoid bundled-helper laundering for the public representative
   route?
6. Is it correct that Numba is not on the correctness-critical path for the
   current evidence?
7. Are the performance boundaries strict enough?
8. Should this report be accepted as the project-level RayJoin 5.2/5.3/5.7
   reproduction summary?
9. Does the amended comparator section now correctly separate author-derived
   SoS behavior from RTDL-defined duplicate-half-edge deterministic behavior?
10. Is the evidence-strength tiering strict enough to prevent over-reading
    `AuthorOfficial` equality as raw unpatched-author reproduction?
