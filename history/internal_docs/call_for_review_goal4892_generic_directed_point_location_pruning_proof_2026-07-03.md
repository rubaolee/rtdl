# Call For Review: Goal4892 Generic Directed Point-Location Pruning Proof

Date: 2026-07-03

## Requested Verdict

Please review Goal4892 and return one of:

- `approve_goal4892_close_as_correct_but_not_enough_reassess_route_a_or_c`
- `approve_with_required_amendments`
- `fail_redo_goal4892`

## Files To Review

- `history/internal_docs/goal4892_generic_directed_point_location_pruning_implementation_proof_2026-07-03.md`
- `history/internal_docs/goal4892_generic_directed_point_location_pruning_proof_result_2026-07-03.md`
- `history/internal_docs/goal4892_rtdl_measurement_wrapper.py`

## Context

Goal4890 showed that RayJoin Section 5.7's hot-path gap is dominated by directed point-location/PIP candidate explosion, especially vertex PIP map0:

- RTDL: `511,943,147,571` segment-loop candidates
- AuthorPatch: `84,341,083`
- ratio: `6,069.9x`

Goal4891 authorized a bounded generic Route-B proof:

- no public API changes;
- no RayJoin-specific fast path;
- no Python/Numba/prepared-session work;
- preserve byte equality;
- require at least 10x candidate-work reduction before considering the path useful.

Goal4892 implemented one conservative generic proof:

- skip candidates only when their strict lower bound is above the current best hit;
- preserve equality/SoS cases;
- measure candidate work on the Australia representative pair.

## Result Summary

Correctness:

- byte equality against the Author+RTDLContractPatch representative comparator stayed true.

Candidate-work reduction:

| Stage | Baseline candidate work | After pruning | Reduction |
| --- | ---: | ---: | ---: |
| vertex PIP map0 | 511,943,147,571 | 474,354,384,456 | 1.079x |
| vertex PIP map1 | 36,359,368,176 | 23,338,764,038 | 1.558x |
| midpoint PIP map0 | 68,493,462 | 50,570,859 | 1.354x |
| midpoint PIP map1 | 105,145,275 | 67,699,430 | 1.553x |

The 10x hard gate failed.

The immediate-report variant preserved byte equality but did not further reduce candidate counts.

No product/native proof code is retained. Goal4892-specific symbols were removed from `src/native/optix` and `tests/`. Existing native diffs from earlier accepted RayJoin correctness/public primitive work are separate and should not be attributed to Goal4892.

## Review Questions

1. Did Goal4892 respect the generic/no-RayJoin/public-surface boundaries?
2. Is it correct to close the proof as failed despite byte equality, because the 10x candidate-work gate failed?
3. Is it correct to retain no native/product code from this proof?
4. Is the exit label `candidate_pruning_correct_but_not_enough_reassess_route_a_or_c` appropriate?
5. Does this result rule out only the cheap Route-B lower-bound proof, not the broader high-performance direction?
6. Should the next goal be Route A/C reassessment by design and measurement, rather than another small local pruning implementation?
7. Does the report avoid overclaiming performance or hiding the failed gate?

## Non-Authorization

This review must not authorize:

- a public performance claim;
- a RayJoin-specific hidden kernel;
- V3/V4 revival;
- raw OptiX callback API work;
- retaining the failed pruning proof in product code;
- starting implementation-first Route A/C work without a new design/measurement gate.
