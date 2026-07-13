# RayJoin Section 5.7 Bounded Reproduction

Status: current bounded reproduction evidence for RTDL v2.14.

This page explains what RTDL currently reproduces from the RayJoin polygon
overlay workload and what it does not claim. It is written for readers who want
the result, the boundary, and the programming model without project-internal
logs.

## Short Answer

RTDL has a bounded RayJoin Section 5.7 polygon-overlay reproduction:

- two available paper-style pairs match full output streams;
- two current-source Lakes/Parks representative pairs match the updated author
  comparator byte-for-byte through public RTDL planar-map primitives;
- this is correctness evidence, not a broad speedup claim.

It is not an all-eight exact hidden-input reproduction of the original paper
artifact package.

## Comparator

The comparator for this page is `AuthorOfficial`: the RayJoin author code with
the deterministic point-location and duplicate-half-edge contract updates used
for this reproduction line.

That comparator is needed because the original behavior can be ambiguous on
equal-height point-location candidates and duplicate half-edge witnesses. RTDL
uses a deterministic planar-map contract for those cases.

The comparator has two parts:

- The directed point-location tie rule is author-derived: for equal-height
  candidates, the two directed maps use opposite slope preferences and encode
  that priority into reported hit distance.
- The duplicate-half-edge rule is an RTDL-defined deterministic contract for
  identical or opposite half-edge witnesses. It is applied to both the
  comparator and RTDL so ambiguous overlay cases are reproducible.

Because of that second item, byte-for-byte equality here means equality against
the deterministic author-contract comparator. It should not be read as a claim
that every ambiguous duplicate-half-edge case matches an unpatched historical
author binary.

## Evidence Matrix

| Workload pair | Input label | RTDL route | Result | Claim |
| --- | --- | --- | --- | --- |
| County x Zipcode | available paper-style pair | RTDL Section 5.7 route after deterministic-contract repairs | full output stream exact match | bounded available-pair reproduction under the deterministic comparator |
| Block x Water | available paper-style pair | RTDL Section 5.7 route after duplicate-half-edge repair | full output stream exact match | bounded deterministic-contract consistency |
| Australia Lakes x Parks | current-source representative OSM pair | public planar-map LSI + public point-location/PIP + application output writer | byte-for-byte match | representative deterministic-contract consistency |
| South America Lakes x Parks | current-source bounded representative OSM slice | public planar-map LSI + public point-location/PIP + application output writer | byte-for-byte match | bounded representative deterministic-contract consistency |

The remaining continent Lakes/Parks pairs are not claimed here because the
exact old paper-preprocessed CDB inputs are not available in the current public
surface.

## Public RTDL Route

The representative Lakes/Parks route uses the intended app-author shape:

```text
public planar-map line-segment intersection
-> public planar-map point-location / PIP
-> Python application output-chain assembly
```

In code terms, the public primitive front doors are:

```python
from rtdsl import prepare_planar_map_lsi_2d_optix
from rtdsl import prepare_planar_map_point_location_2d_optix
```

The application layer owns:

- which CDB inputs to read;
- RayJoin-compatible command parameters;
- representative-vs-exact labeling;
- output-chain formatting.

The public representative route does not rely on importing the bundled
RayJoin compatibility helper as evidence for generic RTDL language capability.

## Result Sizes

| Pair | Output lines | Output bytes | Equality |
| --- | ---: | ---: | --- |
| County x Zipcode | 87,758,114 | not summarized here | full-stream exact |
| Block x Water | 138,674,679 | not summarized here | full-stream exact |
| Australia Lakes x Parks representative | 276,320 | 6,189,260 | byte-for-byte |
| South America Lakes x Parks bounded representative | 97,893 | 2,096,449 | byte-for-byte |

The South America row is intentionally bounded. The full current-source South
America extract is much larger than the historical paper LKSA scale in the
current public OSM snapshot, and first-load text-CDB staging dominates the
experiment. The bounded slice keeps the correctness test controlled.

## Relation To Sections 5.2 And 5.3

Section 5.7 polygon overlay depends on lower-level geometry operations.

Current supporting evidence:

- Section 5.2 LSI: public planar-map LSI reproduces the available counts for
  County x Zipcode, Block x Water, and the Australia representative pair.
- Section 5.3 PIP: public point-location/PIP gives exact per-point closest-edge
  matches on County x Zipcode and Block x Water; the Australia representative
  PIP row is count-consistent but not exact closest-edge hash equivalent.

Section 5.7 is stronger than the single-operation rows because it checks full
overlay output equality on the pairs listed above.

## Performance Boundary

Do not read this page as a speedup claim.

The successful representative runs show that the RTDL public primitives are
correct for this route. The measured elapsed time is dominated by CDB loading,
packing, and Python output-chain assembly. The RT-core LSI/PIP kernels are not
the dominant cost in the representative runs.

Future performance work should target:

- durable binary CDB staging and cache reuse;
- public dataset loader improvements;
- output-chain assembly acceleration;
- optional Numba or CuPy partner acceleration where it removes Python-side
  bottlenecks.

## What This Page Allows

Safe wording:

```text
RTDL v2.14 has a bounded RayJoin Section 5.7 reproduction: two available
paper-style pairs match full output streams, and two current-source
Lakes/Parks representative pairs match the updated author comparator
byte-for-byte through public planar-map primitives and application-level output
assembly. For duplicate-half-edge ambiguous cases, this is equality against a
deterministic contract applied to both comparator and RTDL, not a claim about
unpatched historical author-binary behavior.
```

## What This Page Does Not Allow

Do not claim:

- all-eight exact hidden-input Section 5.7 reproduction;
- exact old hidden paper CDB reproduction for the continent Lakes/Parks pairs;
- broad RTDL speedup over RayJoin;
- that Numba is on the correctness-critical path for this reproduction;
- that representative current-source OSM data equals the old paper input;
- raw unpatched-author byte equality for ambiguous duplicate-half-edge cases;
- that the public Python output writer is performance-optimal.
