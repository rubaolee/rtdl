# Review - Goals5127-5128 X-HD System Extraction

## Verdicts

```text
approve_goal5127_generic_nearest_pipeline_extraction
approve_goal5128_non_hausdorff_max_nearest_consumer
```

Blocking findings: none.

Required amendments: none.

## Goal5127

- The three helpers
  `pairwise_l2_distance_candidate_rows_numpy_columns`,
  `nearest_witness_numpy_columns`, and
  `max_nearest_distance_witness_numpy_columns` are app-neutral by name and
  metadata (`contract=generic_*`, `app_semantics="none"`).
- `directed_hausdorff_2d_numpy_columns` and
  `directed_hausdorff_3d_numpy_columns` are compatibility wrappers over the
  generic pipeline and expose `generic_pipeline_contract`.
- Goal5127 tests prove the wrapper result equals the generic pipeline result
  for source id, target id, and distance.
- The generic implementation window is free of X-HD / paper / author /
  `hd_exec` identity.
- Claim boundaries remain conservative: no RT-core X-HD, no performance, no
  paper-reproduction claim.

## Goal5128

- The facility-service-radius / worst-served-demand fixture is a real
  non-Hausdorff consumer of the same generic pipeline.
- It calls the three generic helpers directly and does not call
  `directed_hausdorff_*` wrappers.
- Hand-checked fixture:
  - demand points 100/101/102 at 0/2/6;
  - facilities 200/201 at 0/4;
  - nearest facilities `[200, 200, 201]` with distances `[0, 2, 2]`;
  - deterministic worst-served witness = demand 101, facility 200, distance 2.
- This closes the Goal5127 non-blocking genericity note: the max-nearest helper
  now has an independent non-Hausdorff consumer.

## Register Disposition

The X-HD register may mark Goals5127 and 5128 as externally reviewed and
approved. This does not alter the bounded same-input paper-app status and does
not authorize performance or RT-core X-HD claims.
