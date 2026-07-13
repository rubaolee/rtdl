# Call For Review: Interim Check After Goal4999 And Goals5000-5006 Plan

Please review:

```text
history/internal_docs/interim_check_goal4999_and_goals5000_5006_device_resident_pipeline_2026-07-04.md
history/internal_docs/goal4999_device_midpoint_query_points_handoff_result_2026-07-04.md
history/internal_docs/goal4999_device_midpoint_query_points_artifacts_2026-07-04/device_query_midpoint_top4_repeat5.json
```

## Context

The owner forced a correction after rejecting the phrase "not strictly full
zero-copy" as an unacceptable caveat. The project had to stop describing the
remaining host boundary and instead remove it.

Goal4999 then added a generic directed point-location device-query input and
changed the RayJoin Section 5.7 writer-free route so midpoint query points are
generated on device and handed directly to native point-location.

This review is not only for Goal4999. It also reviews whether Goals5000-5006 are
the correct continuation toward the v2.14.3 device-resident binary operator.

## Requested Verdict Label

```text
approve_interim_check_goal4999_and_goals5000_5006_plan
```

or, if issues remain:

```text
revise_goal5000_5006_plan_before_implementation
```

## Review Questions

1. Does the interim report correctly explain why the owner forced the correction:
   Goal4998 still had a midpoint host packed scaled-point boundary, and a caveat
   was not an acceptable substitute for engineering work?

2. Did Goal4999 genuinely remove that midpoint host pack boundary in the
   `--device-resident-carrier` route?

3. Is the new native/API work correctly classified as generic directed
   point-location device-query input, rather than a RayJoin-specific overlay
   kernel hidden in RTDL core?

4. Does the POD evidence support the narrow claim?
   Required facts:
   - compatible OptiX 8.1 rebuild succeeded;
   - exported symbol exists;
   - 9 related tests passed on POD;
   - top4 route completed;
   - `lsi_row_count=428322`;
   - `descriptor_pair_count=15014`;
   - median writer-free hot route improved from `0.3381s` to `0.3295s`.

5. Does the report interpret the performance honestly as a modest improvement
   and an architectural boundary removal, rather than author parity or a broad
   performance win?

6. Are the remaining floors identified correctly:
   - sort/order;
   - device carrier construction;
   - descriptor consumer;
   - not midpoint query-point host packing?

7. Is Goal5001 the right next implementation target: device-side run-bound
   generation for generic sorted-key runs?

8. Is Goal5002 framed correctly: either find a better existing generic GPU
   ordering primitive or record the current device sort as the v2.14.3 ordering
   floor, without inventing a RayJoin-specific sorter?

9. Is Goal5003 framed as a generic binary carrier output contract rather than
   RayJoin paper text output in RTDL core?

10. Is Goal5004 necessary to prove the binary route as a real pipeline operator
    by attaching a writer-free downstream operator?

11. Does Goal5005 correctly require fresh/warm/prepared/text-writer/binary routes
    to stay separated in the performance matrix?

12. Does Goal5006 correctly preserve release boundaries and public-surface
    cleanliness?

13. Are any goals missing before v2.14.3 release/staging?

14. Should implementation proceed in the proposed order:

```text
Goal5000 -> Goal5001 -> Goal5002 -> Goal5003 -> Goal5004 -> Goal5005 -> Goal5006
```

## Non-Authorization Boundary

This review should not approve:

- author-performance parity;
- fresh one-shot performance headline from prepared/hot numbers;
- hidden RayJoin-specific native/core primitives;
- claims that all remaining host/device boundaries are solved;
- publication of v2.14.3 without Goal5005/5006 final matrix and release-boundary
  checks.
