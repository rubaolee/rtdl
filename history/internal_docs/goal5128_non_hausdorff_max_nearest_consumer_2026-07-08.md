# Goal5128 - Non-Hausdorff Consumer For Generic Max-Nearest Witness

## Verdict

`completed_non_hausdorff_consumer_for_generic_max_nearest_witness`

## Why This Goal Exists

Goal5127 extracted three generic helpers:

```text
pairwise_l2_distance_candidate_rows_numpy_columns
  -> nearest_witness_numpy_columns
  -> max_nearest_distance_witness_numpy_columns
```

External review approved the extraction, with one non-blocking note: the
`max_nearest_distance_witness_numpy_columns` helper was still only consumed by
the directed-Hausdorff compatibility wrapper and Goal5127 test. To strengthen
the "generic system API, app-owned Hausdorff" boundary, Goal5128 adds a
non-Hausdorff consumer.

## What Changed

Added `tests/goal5128_non_hausdorff_max_nearest_consumer_test.py`.

The test uses the same generic pipeline for a facility-service-radius scenario:

- demand points are assigned to their nearest facility;
- the generic max-nearest reducer finds the worst-served demand point;
- no directed-Hausdorff wrapper is called.

Fixture:

```text
demand ids:    100 @ 0, 101 @ 2, 102 @ 6
facility ids:  200 @ 0, 201 @ 4

nearest facilities:
  demand 100 -> facility 200, distance 0
  demand 101 -> facility 200, distance 2
  demand 102 -> facility 201, distance 2

worst-served deterministic witness:
  demand 101 -> facility 200, distance 2
```

## What This Proves

- The generic max-nearest witness helper has a non-Hausdorff consumer.
- The generic three-stage pipeline is usable as a general nearest-service
  coverage primitive.
- The Goal5127 non-blocking genericity note is addressed.

## What This Does Not Prove

- No new performance claim.
- No native/RT-core claim.
- No X-HD paper reproduction claim.
- No change to the X-HD bounded same-input status.

## Validation

Command:

```text
py -m unittest tests.goal5127_xhd_generic_nearest_pipeline_extraction_test tests.goal5128_non_hausdorff_max_nearest_consumer_test tests.goal5117_generic_3d_hausdorff_column_route_test tests.goal5115_xhd_rtdl_route_gate_test tests.goal5118_xhd_bounded3d_rtdl_route_gate_test
```

Result:

```text
Ran 13 tests in 1.008s
OK
```

## Claim Boundary

Allowed:

- "The generic max-nearest witness helper now has a non-Hausdorff consumer test."
- "The helper can model a facility-service-radius / worst-served-demand query."

Not allowed:

- "This is a performance improvement."
- "This implements X-HD in RTDL core."
- "This changes the X-HD bounded same-input reproduction status."
