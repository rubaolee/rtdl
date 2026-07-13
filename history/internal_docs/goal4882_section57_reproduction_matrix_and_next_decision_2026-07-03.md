# Goal4882: Section 5.7 Reproduction Matrix And Next Decision

Date: 2026-07-03

## Purpose

After Goal4881, stop and consolidate the Section 5.7 evidence before launching another large continent run.

The goal is to answer:

1. What exactly is now reproduced?
2. Which results are exact/available pairs and which are representative current-source pairs?
3. Does another immediate Africa run add necessary evidence, or would it mostly repeat the same proof at higher resource cost?
4. What should the next goal be?

## Current Section 5.7 Evidence Matrix

| Paper pair | Evidence status | Input label | Comparator | RTDL route | Result | Claim allowed |
| --- | --- | --- | --- | --- | --- | --- |
| County x Zipcode | completed | available paper-style pair | Author-intended baseline | RTDL Section 5.7 route after core contract repairs | full-stream exact match | bounded exact/available pair reproduction |
| Block x Water | completed | available paper-style pair | AuthorOfficial (`Author+RTDLContractPatch`) | RTDL Section 5.7 route after duplicate-half-edge contract repair | full-stream exact match | bounded exact/available pair reproduction |
| LKAU x PKAU | completed | representative current-source Australia/Oceania OSM | AuthorOfficial | public RTDL planar-map LSI + public point-location/PIP + app-layer output writer | byte-equal output | representative current-source public-primitives reproduction |
| LKSA x PKSA | completed | representative current-source South America OSM bounded slice | AuthorOfficial | public RTDL planar-map LSI + public point-location/PIP + app-layer output writer | byte-equal output | representative current-source bounded public-primitives reproduction |
| LKAF x PKAF | not run in current closure | exact old paper input missing | n/a | n/a | n/a | candidate future representative if more breadth is required |
| LKAS x PKAS | not run in current closure | exact old paper input missing | n/a | n/a | n/a | deferred; high resource cost |
| LKEU x PKEU | not run in current closure | exact old paper input missing | n/a | n/a | n/a | deferred; very high resource cost |
| LKNA x PKNA | not run in current closure | exact old paper input missing | n/a | n/a | n/a | deferred; high resource cost |

## Evidence Details

### County x Zipcode

Source report:

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

### Block x Water

Source report:

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

### Australia Lakes x Parks

Source report:

```text
history/internal_docs/goal4875_section57_au_representative_public_primitive_closure_2026-07-02.md
```

Result:

```text
a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e  author_contract_au_overlay.txt
a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e  rtdl_public_overlay.txt

276320 lines
6189260 bytes
```

Route:

- public `prepare_planar_map_lsi_2d_optix`;
- public `prepare_planar_map_point_location_2d_optix`;
- Python application-level output-chain assembly;
- no import of `rtdsl.rayjoin_overlay`;
- no Embree;
- no V3/V4 dependency.

### South America Lakes x Parks

Source report:

```text
history/internal_docs/goal4881_section57_south_america_representative_public_primitives_2026-07-03.md
```

Result:

```text
8b4e80a50fedb77120781e8bf39c9f2db1df3a1f823716f7dab9c1f9eed1862d  author_official_sa_bounded_overlay.txt
8b4e80a50fedb77120781e8bf39c9f2db1df3a1f823716f7dab9c1f9eed1862d  rtdl_public_sa_bounded_overlay.txt

97893 lines
2096449 bytes
```

Route:

- public planar-map LSI;
- public planar-map point-location/PIP;
- Python application-level output-chain writer;
- no import of bundled `rtdsl.rayjoin_overlay`;
- no exact hidden-paper input claim;
- no full eight-pair claim.

## What Is Now Proven

The current evidence proves two important facts:

1. RTDL can reproduce two serious available Section 5.7 full-output pairs with exact stream equality.
2. The public RTDL planar-map primitives can support the Lakes/Parks overlay workflow on two independent current-source representatives, Australia and South America, with byte-for-byte equality to AuthorOfficial.

This is no longer only a bundled-helper result. The representative route is:

```text
public planar-map LSI
-> public planar-map point-location/PIP
-> application-level output-chain assembly
```

That is the intended RTDL app-implementation shape.

## What Is Not Proven

Not proven:

- exact old hidden-paper inputs for all eight Section 5.7 pairs;
- exact old hidden-paper LKAF/LKAS/LKAU/LKEU/LKNA/LKSA CDB reproduction;
- broad RTDL performance superiority over the author implementation;
- that Numba is on the correctness-critical path;
- that the public Python output-chain writer is performance-optimal;
- that full current-source continent-scale text CDB first-load is operationally clean without better staging/cache tooling.

## Should We Immediately Run Africa?

Recommendation: not as the next goal.

Reason:

- Africa would add breadth, but it would not test a new semantic mechanism. It would reuse the same public LSI/PIP/output-writer route already validated on Australia and South America.
- Goal4881 exposed the real operational bottleneck: current-source continent data staging and text-CDB first-load, not overlay correctness.
- Running Africa next risks becoming a resource-heavy repetition unless the goal is specifically "more representative breadth."

Africa should be run only if the release/reproduction bar explicitly requires a third Lakes/Parks representative. If it is run, it should start from bounded slicing and durable staging, not a full-continent first-load attempt.

## Recommended Next Goal

Goal4883 should be:

```text
Goal4883: Section 5.7 Bounded Final Reproduction Packet
```

Purpose:

- combine the two available exact/full-stream pairs and the two representative public-primitives Lakes/Parks pairs;
- state exactly what is claimed and not claimed;
- separate correctness evidence from performance evidence;
- identify engineering debt for future work:
  - durable dataset staging/cache;
  - public app examples;
  - optional Numba acceleration for app-side output/compaction;
  - optional Africa representative breadth run.

Goal4883 should not run another large dataset unless the review of this matrix says the evidence is insufficient without one.

## Decision Audit

1. Would it be stupid to launch Africa immediately?
   - Potentially yes. If the question is semantic correctness of the public-primitives route, Africa is likely repetitive. The current missing piece is a final bounded packet, not another expensive run.

2. What action would make the decision stupid?
   - Downloading another multi-GB continent and forcing full text-CDB parse just to look busy, after Goal4881 already showed the operational bottleneck.

3. Is there another path that avoids that?
   - Yes. Close the current evidence into a final Section 5.7 bounded reproduction packet and let review decide whether more breadth is required.

4. Can we solve the real problem now?
   - Yes. The real problem is claim clarity and reproduction closure. Goal4883 should turn the current evidence into a clear final packet.

## Exit Label

Recommended exit label:

```text
completed_section57_matrix_after_goal4881__recommend_final_bounded_packet_before_more_continents
```
