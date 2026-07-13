# Goal4892 Result: Generic Directed Point-Location Pruning Proof

Date: 2026-07-03

## Exit Label

`candidate_pruning_correct_but_not_enough_reassess_route_a_or_c`

## One-Line Result

The bounded generic in-loop pruning proof preserved RayJoin representative correctness, but reduced directed point-location candidate work by only 1.08x to 1.56x, far below the required 10x hard gate; no product/native code from this proof should be retained.

## Why This Goal Existed

Goal4890 showed that the RayJoin Section 5.7 hot-path gap is dominated by directed point-location/PIP candidate explosion:

| Stage | RTDL candidate work | AuthorPatch candidate work | RTDL / AuthorPatch |
| --- | ---: | ---: | ---: |
| vertex PIP map0 | 511,943,147,571 | 84,341,083 | 6,069.9x |
| vertex PIP map1 | 36,359,368,176 | 18,561,490 | 1,958.9x |
| midpoint PIP map0 | 68,493,462 | 74,815 | 915.5x |
| midpoint PIP map1 | 105,145,275 | 108,540 | 968.7x |

Goal4891 authorized one cheap, bounded Route-B proof before any larger compiler or indexing work:

- keep the public API unchanged;
- avoid RayJoin-specific branches;
- preserve byte-for-byte correctness;
- measure candidate-work reduction directly;
- require at least 10x candidate reduction on the representative workload before considering the path useful.

## Implemented Proof

The proof temporarily added a conservative lower-bound skip inside directed point-location traversal:

```text
After a best hit exists, if a candidate segment's minimum possible directed
hit height is strictly greater than the current best hit height, that segment
cannot become the winner and may be skipped.
```

Important correctness constraint:

- equality cases were not pruned;
- the existing Simulation-of-Simplicity tie-break stayed in the normal comparator path;
- the rule did not reference RayJoin overlay topology, output chains, or paper-specific data.

An internal diagnostic wrapper measured candidate work on the Australia current-source representative pair:

- left: `/workspace/goal4848_rep/current_osm_au/lakes_Australia_current_osm_Point.cdb`
- right: `/workspace/goal4848_rep/current_osm_au/parks_Australia_current_osm_Point.cdb`
- comparator output: `/workspace/goal4875_section57_au_representative/author_contract_full/author_contract_au_overlay.txt`

The POD build was performed on:

- host: `root@157.157.221.29 -p 23132`
- GPU: NVIDIA RTX 4000 Ada Generation
- scratch tree: `/workspace/goal4892_rtdl_prune`
- build: `make build-optix OPTIX_PREFIX=/tmp/optix-sdk-probe`

## Verification Results

### Correctness

Both proof variants preserved byte equality against the Author+RTDLContractPatch comparator on the representative workload.

| Variant | Byte Equal |
| --- | --- |
| conservative lower-bound skip | true |
| lower-bound skip plus immediate report of improved hits | true |

### Candidate Work

The hard gate was 10x fewer tested candidates on vertex PIP map0. The proof did not come close.

| Stage | Baseline candidate work | After pruning | Reduction |
| --- | ---: | ---: | ---: |
| vertex PIP map0 | 511,943,147,571 | 474,354,384,456 | 1.079x |
| vertex PIP map1 | 36,359,368,176 | 23,338,764,038 | 1.558x |
| midpoint PIP map0 | 68,493,462 | 50,570,859 | 1.354x |
| midpoint PIP map1 | 105,145,275 | 67,699,430 | 1.553x |

The immediate-report variant produced the same candidate counts. It did not materially change traversal pruning.

### Wall Time

Wall time was not a success metric for this proof, but the diagnostic run made traversal slower because it added checks and counters:

- vertex PIP map0 traversal was about 41.6 s in the proof run;
- vertex PIP map1 traversal was about 4.9 s in the proof run.

No performance claim is authorized from Goal4892.

## Local Validation

The temporary synthetic contract guard and existing correctness tests passed before the POD proof:

```text
PYTHONPATH=src py -m unittest \
  tests.goal4892_directed_point_location_pruning_contract_test \
  tests.goal4834_rayjoin_sos_synthetic_contract_test \
  tests.goal4857_planar_map_point_location_public_front_door_test

Ran 25 tests ... OK
```

After the POD proof failed the 10x gate, the temporary Goal4892 source/test surface was removed. The retained local validation is:

```text
PYTHONPATH=src py -m unittest \
  tests.goal4834_rayjoin_sos_synthetic_contract_test \
  tests.goal4857_planar_map_point_location_public_front_door_test

Ran 22 tests ... OK
```

Static residue scan:

```text
rg "candidate_segment_count|pruned_segment_count|directed_segment_scaled_min_y_strictly_above_best|directed_segment_world_min_t_strictly_above_best|RTDL_OPTIX_POINT_LOCATION_DIAGNOSTICS|rtdl_optix_.*get_last_work_counts" src/native/optix tests
```

returned no matches.

## Product-Code Decision

Do not retain the Goal4892 native proof.

Reason:

- correctness was preserved, but the measured candidate reduction was too small;
- retaining extra branch logic and diagnostics would add complexity without moving the measured bottleneck;
- the immediate-report variant also failed to reduce candidate counts;
- this is precisely the kind of "looks like progress but does not move the blocker" work the project must reject.

The current working tree may still contain tracked native changes from earlier accepted RayJoin correctness and public primitive goals. Those are separate. Goal4892-specific proof symbols were removed from the product/test surface.

Retained artifacts:

- this result report;
- `history/internal_docs/goal4892_generic_directed_point_location_pruning_implementation_proof_2026-07-03.md`;
- `history/internal_docs/goal4892_rtdl_measurement_wrapper.py`, as historical measurement tooling only.

## Interpretation

The cheap Route-B lower-bound pruning proof is falsified.

The result means:

- candidate explosion is not solved by a local "skip obvious losers after best hit exists" rule;
- most of the pathological work survives because broad candidate ranges still get visited and tested before this local rule can remove them;
- the next useful work must move to a larger mechanism:
  - Route A: rebuild candidate grouping/range construction/indexing so traversal visits far fewer candidates;
  - Route C: data-flow pushdown / in-traversal fused operator work that changes what the traversal does, not just a small post-best-hit skip.

It does not mean:

- RTDL cannot become high performance;
- RayJoin reproduction is invalid;
- Numba/partner work is useless;
- public v2.14 correctness fixes are suspect.

It only means this specific cheap pruning proof does not provide the needed performance source.

## Next Recommended Goal

Do not start another small in-loop pruning tweak.

Start a design/measurement goal that chooses between:

1. **Route A candidate-range redesign**:
   - inspect how current segment grouping creates huge ranges;
   - compare against author range/candidate construction;
   - prove whether a generic planar-map spatial index can cut candidate visits by at least 10x before exact testing.

2. **Route C data-flow pushdown proof**:
   - define a generic directed point-location operator that can push the relevant predicate/reduction into traversal;
   - keep the user model data-flow, not raw OptiX callbacks;
   - require a non-RayJoin second workload before calling it generic.

The next goal should be a design-plus-measurement gate, not implementation-first coding.

## Goal-Level Decision Audit

1. **Am I being stupid?**

   Continuing to polish this proof after a 1.079x map0 reduction would be stupid. The measured gate failed.

2. **What actions would make the decision stupid?**

   Keeping native proof code because it is "correct," claiming wall-time progress, or opening another local pruning tweak without proving it can hit candidate work.

3. **Is there another possible path?**

   Yes. Route A and Route C are the real remaining paths. This goal's useful contribution is to rule out the cheap Route-B variant.

4. **Can we start a different path that truly solves the problem?**

   Yes. The next goal should inspect candidate-range/index construction or define a data-flow pushdown proof. Both attack the measured source of the 6,000x work gap; this proof does not.
