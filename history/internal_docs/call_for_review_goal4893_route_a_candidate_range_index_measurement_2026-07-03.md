# Call For Review: Goal4893 Route-A Candidate-Range / Index Measurement

Date: 2026-07-03

## Requested Verdict

Please review Goal4893 and return one of:

- `approve_goal4893_route_a_passed_authorize_productization_goal4894`
- `approve_with_required_amendments`
- `fail_redo_goal4893`

## Files To Review

- `history/internal_docs/goal4893_route_a_candidate_range_index_redesign_measurement_gate_2026-07-03.md`
- `history/internal_docs/goal4893_route_a_candidate_range_index_measurement_result_2026-07-03.md`
- `history/internal_docs/goal4893_pip_group_mode_matrix_runner.py`
- `history/internal_docs/goal4893_pip_group_full_matrix_2026-07-03.json`
- `history/internal_docs/goal4893_block_merge64_i0_e1p5_full_overlay_summary_2026-07-03.json`

## Core Result

Route A passed.

Best measured mode:

```text
RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MODE=block_merge64
RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MAX_ITER=0
RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_AREA_ENLARGE=1.5
```

Candidate reduction:

| Stage | fixed8 candidates | Route-A candidates | Reduction |
| --- | ---: | ---: | ---: |
| vertex PIP map0 | 511,943,147,571 | 9,586,860 | 53,400.5x |
| vertex PIP map1 | 36,359,368,176 | 1,960,935 | 18,541.9x |
| midpoint PIP map0 | 68,493,462 | 7,581 | 9,034.9x |
| midpoint PIP map1 | 105,145,275 | 13,131 | 8,006.0x |

Full overlay:

```text
byte_equal_to_author: true
sha256: a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e
```

Wall-time interpretation:

| Metric | fixed8 | Route-A mode | Speedup |
| --- | ---: | ---: | ---: |
| full elapsed | 129.448 s | 93.345 s | 1.39x |
| elapsed excluding load/pack | 52.888 s | 16.292 s | 3.25x |

## Review Questions

1. Does Goal4893 correctly choose Route A after Goal4892, rather than deferring the choice back to the user?
2. Is the candidate-work reduction real enough to say the Route-A measurement gate passed?
3. Does the full-overlay byte-equality result sufficiently guard against a stage-only false positive?
4. Is the result generic directed point-location range construction, not a RayJoin-specific hidden kernel?
5. Does the report correctly avoid overclaiming full app victory, given load/pack and LSI still dominate end-to-end wall time?
6. Should the next goal be productization of a clean generic fine-grained range-construction default, rather than Route C compiler/fusion work?
7. What amendments are required before Goal4894 starts?

## Non-Authorization

This review must not authorize:

- public performance claims;
- changing public docs/tutorials;
- calling this a full RayJoin-vs-AuthorPatch win;
- V3/V4 revival;
- raw OptiX callbacks;
- RayJoin-specific product code.

The only requested authorization is to start a bounded productization goal for
generic directed point-location range construction.
