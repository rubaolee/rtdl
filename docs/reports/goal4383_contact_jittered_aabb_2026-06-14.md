# Goal4383 Contact Manifold Jittered AABB Refresh

Date: 2026-06-14

Status: v2.14 cleanup evidence for the generic AABB broadphase plus bounded witness-row primitive. This replaces the earlier small-grid-only contact row with a large deterministic jittered fixture, but it remains a broadphase/contact-witness primitive claim rather than a full contact-manifold physics claim.

## Contract

Both backends run the same candidate-discovery contract:

`AABB_INDEX_QUERY_2D / generic_aabb_intersection_pair_rows_2d`

The app then passes the discovered candidate id rows through the app-agnostic bounded row primitive:

`COLLECT_K_BOUNDED / bounded_witness_collection`

The native engine sees only AABB boxes, query boxes, bounded `int64` rows, and `valid_count`. Triangle-intersection refinement and contact interpretation remain app-owned Python/partner continuation logic.

## Dataset

The new fixture is `jittered_grid_65536`.

It constructs 65,536 deterministic two-dimensional cells. Each cell has one scene AABB and one query AABB with a guaranteed witness overlap, plus deterministic jitter so the data is not a perfectly aligned repeated toy. The full all-pairs search space is:

`65,536 x 65,536 = 4,294,967,296` possible pairs

The broadphase output contains 65,536 candidate/witness rows. Both backends match the CPU reference and report complete candidate coverage.

## Results

| Backend | Dataset | All pairs | Candidate rows | Valid rows | Prepared scene sec | AABB query median sec | AABB query total sec, 5 repeats | Bounded-row collect sec | Python exact refinement sec |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Embree CPU | jittered_grid_65536 | 4,294,967,296 | 65,536 | 65,536 | 0.622634 | 0.680673 | 3.396490 | 0.171466 | 0.099255 |
| OptiX RT cores | jittered_grid_65536 | 4,294,967,296 | 65,536 | 65,536 | 0.865219 | 0.552924 | 2.740281 | 0.169510 | 0.098755 |

## Same-Contract Speedup

| Phase | Embree sec | OptiX sec | Embree / OptiX | Interpretation |
| --- | ---: | ---: | ---: | --- |
| Prepared AABB query median | 0.680673 | 0.552924 | 1.23x | RT cores are faster on the broadphase traversal, but the workload is sparse and output-bound enough that the speedup is modest. |
| Query plus bounded collect plus exact refinement | 0.951393 | 0.821189 | 1.16x | Shared bounded-row handling and Python refinement compress the end-to-end hot-path speedup. |
| Prepared scene build | 0.622634 | 0.865219 | 0.72x | Embree builds this CPU AABB index faster in this run; this should be reported separately from hot traversal. |

## Validation

Both JSON artifacts have:

- `matches_cpu_reference=true`
- `complete_candidate_coverage=true`
- `overflowed=false`
- `valid_count=65536`
- `aabb_candidate_pair_count=65536`
- `all_pairs_count=4294967296`

An intentionally under-provisioned smoke run without `--witness-capacity 65536` failed closed because the default capacity could not hold all rows. That behavior is correct for `COLLECT_K_BOUNDED`: overflow is not silently truncated.

## Conclusion

The contact row is now good v2.14 evidence for a large app-agnostic AABB broadphase/contact-witness primitive. The result is reasonable: OptiX is 1.23x faster than Embree for the prepared broadphase query, while shared row collection and Python exact refinement reduce the hot end-to-end advantage to 1.16x.

Public wording must stay narrow. This is not a full contact manifold solver, not continuous collision detection, not physics contact generation, and not an original-paper dataset claim. It is a large deterministic contact-witness broadphase row with explicit validation.
