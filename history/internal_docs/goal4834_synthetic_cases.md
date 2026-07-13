# Goal4834 Synthetic Cases

Date: 2026-06-30

Synthetic tests were added in:

- `tests/goal4834_rayjoin_sos_synthetic_contract_test.py`

The tests are intentionally small and do not depend on large RayJoin datasets.
They check the contract before any public-sample or Section 5.7 execution.

## Covered Cases

1. **Map 0 slope direction**

   Equal primary `t`, slopes `-2.0` and `3.0`.

   Expected result: `query_map_id == 0` reports the larger slope with smaller
   `t_reported`.

2. **Map 1 slope direction**

   Equal primary `t`, slopes `-2.0` and `3.0`.

   Expected result: `query_map_id == 1` reports the smaller slope with smaller
   `t_reported`.

3. **Traversal/input order independence**

   Candidate order is reversed. The selected segment id remains the same for
   each query map.

4. **Map-directed endpoint exclusion**

   `query_map_id == 0` excludes the lower-x endpoint; `query_map_id == 1`
   excludes the higher-x endpoint.

5. **Midpoint face ownership**

   One intersection object receives different midpoint face classifications for
   map 0 and map 1. The two values must not overwrite each other.

6. **Source alignment guard**

   The test reads `src/native/optix/rtdl_optix_core.cpp` and verifies that the
   internal comparator and `t_reported` tie-breaker use the same direction.

## Result

Local focused command:

```text
py -3 -m unittest tests.goal4834_rayjoin_sos_synthetic_contract_test tests.goal4373_rayjoin_cdb_point_location_route_test tests.goal4374_rayjoin_exact_paper_suite_test.Goal4374RayjoinExactPaperSuiteTest.test_overlay_midpoint_faces_are_stored_per_map tests.goal4374_rayjoin_exact_paper_suite_test.Goal4374RayjoinExactPaperSuiteTest.test_overlay_output_chain_writer_is_not_legacy_seed
```

Result:

```text
Ran 12 tests in 1.001s
OK
```
