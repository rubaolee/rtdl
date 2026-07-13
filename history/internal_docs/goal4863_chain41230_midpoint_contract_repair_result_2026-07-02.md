# Goal4863 Result: Chain 41230 Midpoint Contract Repair

Date: 2026-07-02

## Verdict

Goal4863 repaired the chain `41230` midpoint face-selection mismatch exposed by
Goal4862.

The current Section 5.7 first-difference chain now matches the AuthorPatch
header:

```text
41230 2 42104 42105 280 290
```

This does **not** authorize full Section 5.7 correctness.  It only closes the
localized chain-41230 midpoint contract defect.

## What Was Wrong

Goal4862 proved the first mismatch was not a final face-id renumbering artifact:

- Author-implied raw face key: `(5, 10950)` and `(22, 10950)`.
- RTDL before repair: `(5, 10938)` and `(22, 10938)`.

Goal4863 localized the defect to midpoint query-point construction between two
adjacent intersections on map0 edge `43212`.

The targeted midpoint probe showed:

| variant | scaled point | face |
| --- | --- | ---: |
| rational midpoint current | `(-33924059549368, 9057003035588)` | 10938 |
| trunc scaled endpoint midpoint | `(-33924059549367, 9057003035588)` | 10950 |

The author-implied expected opposite-map face for this chain is `10950`.

## Repair

File changed:

- `src/rtdsl/rayjoin_overlay.py`

Function changed:

- `_midpoints_for_sorted_xsects(...)`

Contract after repair:

1. If materialized scaled intersection endpoints are available, midpoint
   query points are constructed from those materialized scaled endpoints:

   ```text
   trunc_div2(left.scaled + right.scaled)
   ```

2. The rational midpoint fallback remains available only when materialized
   scaled endpoints are absent.

Reason:

The Section 5.7 output-chain path queries midpoint faces using the materialized
intersection rows.  On boundary cases, recomputing from rational coordinates can
land on the wrong side of the directed point-location contract by one internal
coordinate.  The author-compatible behavior for the exposed chain is the
materialized-scaled-endpoint midpoint.

## Regression Tests

Files changed:

- `tests/goal4374_rayjoin_exact_paper_suite_test.py`

Relevant tests:

- `test_output_chain_midpoint_prefers_materialized_scaled_endpoints`
- `test_output_chain_midpoint_uses_rational_when_scaled_endpoints_absent`
- `test_negative_half_unit_midpoint_matches_author_internal_cast`

Local command:

```text
PYTHONPATH=src py -m unittest \
  tests.goal4374_rayjoin_exact_paper_suite_test \
  tests.goal4834_rayjoin_sos_synthetic_contract_test \
  tests.goal4857_planar_map_point_location_public_front_door_test
```

Local result:

```text
Ran 43 tests in 2.363s
OK
```

POD command:

```text
cd /workspace/rtdl_goal4859_exec &&
timeout 120s env PYTHONPATH=src RTDL_OPTIX_LIB=/workspace/rtdl_goal4859_exec/build/librtdl_optix.so \
  python3 -m unittest \
    tests.goal4834_rayjoin_sos_synthetic_contract_test.Goal4834RayjoinSosSyntheticContractTest.test_negative_half_unit_midpoint_matches_author_internal_cast \
    tests.goal4374_rayjoin_exact_paper_suite_test.Goal4374RayjoinExactPaperSuiteTest.test_output_chain_midpoint_prefers_materialized_scaled_endpoints \
    tests.goal4374_rayjoin_exact_paper_suite_test.Goal4374RayjoinExactPaperSuiteTest.test_output_chain_midpoint_uses_rational_when_scaled_endpoints_absent
```

POD result:

```text
Ran 3 tests in 1.376s
OK
```

## Targeted POD Evidence

Before repair evidence:

- `history/internal_docs/goal4863_chain41230_midpoint_point_location_probe_summary.json`
- `rational_midpoint_current` returned face `10938`.
- `trunc_scaled_endpoint_midpoint` returned face `10950`.

After repair evidence:

- `history/internal_docs/goal4863_chain41230_face_assignment_after_fix_probe_summary.json`

Target chain after repair:

```json
{
  "author_header": "41230 2 42104 42105 280 290",
  "generated_header": "41230 2 42104 42105 280 290",
  "header_match": true,
  "other_map_polygon_id": 10950,
  "left_key": [5, 10950],
  "right_key": [22, 10950]
}
```

## Efficiency Retrospective

The debugging direction was correct, but the first probes were inefficient.

Problem:

- The target was chain `41230`, but the probe still entered through
  `run_rayjoin_overlay_rtdl_from_cdb_paths(...)`.
- That forced repeated full CDB packing / LSI / PIP precomputation.
- Each focused chain probe therefore cost roughly `440-480` seconds.

Correct future discipline:

1. First derive a small synthetic or extracted local contract test.
2. Run the local contract test in milliseconds/seconds.
3. Only then run one large POD confirmation.

Goal4863 now has such a local regression gate.  Future midpoint/face defects
should not be debugged by repeatedly running full Section 5.7.

## Claim Boundary

Authorized:

- chain `41230` midpoint face-selection defect is repaired;
- the exposed midpoint construction contract is now regression-tested;
- the next Section 5.7 step may resume from this fixed first-difference chain.

Not authorized:

- full Section 5.7 byte-equal correctness;
- full Section 5.7 performance;
- broad RayJoin paper reproduction;
- broad RTDL correctness or performance claims.

## Recommended Next Step

Run the Section 5.7 streaming compare once to see whether:

- the full County x Zipcode output now matches; or
- a later first difference appears.

If a later first difference appears, repeat the **small synthetic first**
discipline rather than starting with another full debug loop.
