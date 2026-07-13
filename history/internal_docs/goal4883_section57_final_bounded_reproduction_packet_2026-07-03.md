# Goal4883: RayJoin Section 5.7 Final Bounded Reproduction Packet

Date: 2026-07-03

## Executive Verdict

RTDL has a bounded, honest Section 5.7 polygon-overlay reproduction package.

The proven claim is:

```text
RTDL reproduces Section 5.7 polygon-overlay behavior on two available full-stream pairs
and two current-source Lakes/Parks representative pairs.
```

This is a correctness reproduction packet, not a broad performance claim and not a full exact old eight-pair paper-input claim.

## Comparator

The comparator is:

```text
AuthorOfficial = Author+RTDLContractPatch
```

This is the official updated comparator for the current line. It incorporates the deterministic point-location and duplicate-half-edge contracts exposed during the reproduction work.

Why this is necessary:

- the old author behavior was unstable on equal-height / duplicate-half-edge cases;
- the user/author explicitly allowed the patched comparator as the official updated baseline;
- RTDL's core fixes are product-level deterministic planar-map/overlay contract repairs, not hidden RayJoin-only shortcuts.

## Evidence Matrix

| Pair | Evidence type | Input label | Comparator | Route | Result | Allowed claim |
| --- | --- | --- | --- | --- | --- | --- |
| County x Zipcode | full-stream overlay | available paper-style pair | author-intended baseline | RTDL Section 5.7 route after core contract repairs | exact stream match | bounded available-pair Section 5.7 reproduction |
| Block x Water | full-stream overlay | available paper-style pair | AuthorOfficial | RTDL Section 5.7 route after duplicate-half-edge repair | exact stream match | bounded available-pair Section 5.7 reproduction |
| Australia Lakes x Parks | full overlay output | representative current-source OSM | AuthorOfficial | public RTDL LSI + public RTDL PIP + app output writer | byte-equal | representative current-source public-primitives reproduction |
| South America Lakes x Parks | full overlay output on bounded slice | representative current-source OSM bounded slice | AuthorOfficial | public RTDL LSI + public RTDL PIP + app output writer | byte-equal | bounded representative current-source public-primitives reproduction |

## Pair Evidence

### County x Zipcode

Source:

```text
history/internal_docs/goal4873_section57_two_pair_bounded_closure_2026-07-02.md
```

Result:

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

Claim:

```text
full-stream exact match on the available County x Zipcode pair
```

### Block x Water

Source:

```text
history/internal_docs/goal4873_section57_two_pair_bounded_closure_2026-07-02.md
```

Result:

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

Claim:

```text
full-stream exact match on the available Block x Water pair under AuthorOfficial
```

### Australia Lakes x Parks

Source:

```text
history/internal_docs/goal4875_section57_au_representative_public_primitive_closure_2026-07-02.md
```

Result:

```text
sha256: a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e
lines: 276320
bytes: 6189260
byte_equal_to_author: true
```

Route:

```text
public prepare_planar_map_lsi_2d_optix
public prepare_planar_map_point_location_2d_optix
Python application-level output-chain assembly
no rtdsl.rayjoin_overlay import
```

Claim:

```text
representative current-source Australia Lakes/Parks byte-equal public-primitives reproduction
```

### South America Lakes x Parks

Source:

```text
history/internal_docs/goal4881_section57_south_america_representative_public_primitives_2026-07-03.md
```

Result:

```text
sha256: 8b4e80a50fedb77120781e8bf39c9f2db1df3a1f823716f7dab9c1f9eed1862d
lines: 97893
bytes: 2096449
byte_equal_to_author: true
```

Route:

```text
public prepare_planar_map_lsi_2d_optix
public prepare_planar_map_point_location_2d_optix
Python application-level output-chain assembly
no rtdsl.rayjoin_overlay import
```

Claim:

```text
bounded representative current-source South America Lakes/Parks byte-equal public-primitives reproduction
```

The South America full current-source CDB was generated but not accepted as the run target because the current-source data was substantially larger than the old paper LKSA scale and first-load text-CDB staging became the dominant operational issue. The bounded slice was chosen to keep the experiment controlled.

## Relation To Section 5.2 And 5.3

This packet should be read with the earlier single-operation closures:

### Section 5.2 LSI

Source:

```text
history/internal_docs/goal4853_section52_lsi_final_reproduction_closure_2026-07-01.md
```

Result:

| Pair | Expected | Public RTDL | Match |
| --- | ---: | ---: | --- |
| County x Zipcode | 961,165 | 961,165 | yes |
| Block x Water | 649,605 | 649,605 | yes |
| Australia representative | 13,622 | 13,622 | yes |

Boundary:

```text
LSI count-only, not overlay, not all-eight exact input.
```

### Section 5.3 PIP

Source:

```text
history/internal_docs/goal4878_section53_pip_authorofficial_reproduction_2026-07-02.md
```

Result:

| Pair | Count match | Closest-edge hash match | Classification |
| --- | --- | --- | --- |
| County x Zipcode | yes | yes | exact per-point closest-edge match |
| Block x Water | yes | yes | exact per-point closest-edge match |
| Australia representative | yes | no | count-consistent only |

Boundary:

```text
PIP/point-location only, not overlay, not all-eight exact input.
```

Section 5.7 goes beyond 5.2 and 5.3 by proving full output-chain equality on the listed overlay pairs.

## What We Can Say

Allowed public/internal reproduction wording:

```text
RTDL has a bounded RayJoin Section 5.7 reproduction: two available paper-style overlay pairs match full output streams, and two current-source Lakes/Parks representative pairs match AuthorOfficial byte-for-byte through public planar-map LSI and point-location primitives plus application-level output assembly.
```

Short version:

```text
Section 5.7 is reproduced in a bounded, evidence-backed form.
```

## What We Must Not Say

Do not claim:

- full exact old eight-pair Section 5.7 reproduction;
- exact hidden paper CDB reproduction for the continent Lakes/Parks pairs;
- broad RTDL speedup over the author implementation;
- that Numba is on the correctness-critical path;
- that representative current-source data equals old hidden paper input;
- that Africa/Asia/Europe/North America have been reproduced;
- that public Python output-chain assembly is performance-optimal.

## Performance Boundary

This packet is primarily correctness evidence.

Performance observations are diagnostic:

- AuthorOfficial spends substantial time in text-CDB read/deserialize on first load.
- Public RTDL representative runs spend substantial time in Python CDB load/pack and Python output-chain writing.
- RT-core LSI/PIP kernels are not the dominant cost in the successful representative runs.

Therefore, no broad performance claim is authorized from this packet.

Future performance work should target:

1. durable binary CDB staging/cache;
2. public dataset loader improvements;
3. app-layer output-chain assembly acceleration;
4. optional Numba/CuPy partner acceleration where it genuinely removes Python-side bottlenecks.

## Product Boundary

The clean RTDL app model for this line is:

```text
RTDL core:
  public planar-map LSI primitive
  public planar-map point-location/PIP primitive
  deterministic directed-overlay contracts

Application layer:
  paper-specific CDB selection/preprocessing
  AuthorOfficial-compatible parameters
  output-chain formatting
  representative-data labeling
```

The public representative route must not rely on importing bundled `rtdsl.rayjoin_overlay` as evidence of generic RTDL language capability.

## Remaining Engineering Debt

1. **Exact old input debt**
   - The exact old hidden CDBs/answers for the remaining Lakes/Parks continent pairs are not available in the current workspace/POD state.

2. **Dataset staging debt**
   - Full current-source continent routes can be dominated by text-CDB first-load and workspace quota pressure.

3. **Performance debt**
   - Public Python output-chain assembly and CDB packing need optimization before any broad performance claim.

4. **Partner debt**
   - Numba is not yet on the correctness-critical Section 5.7 path. It remains a plausible partner for output/compaction acceleration, but that is future work.

5. **Documentation debt**
   - If this packet becomes user-facing, representative vs exact-old-input labels must stay visible and simple.

## Final Decision

Recommended closure label:

```text
completed_section57_final_bounded_reproduction_packet__two_available_full_stream__two_representative_public_primitives__no_all8_or_perf_claim
```

Recommended next work after closure:

```text
Goal4884: decide whether to publish this bounded reproduction packet internally/publicly, and if public, produce a clean reader-facing RayJoin paper-reproduction page with the exact claim boundaries above.
```
