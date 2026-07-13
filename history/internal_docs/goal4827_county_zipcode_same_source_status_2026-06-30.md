# Goal4827 County x Zipcode Same-Source Status

Date: 2026-06-30

## Scope

This goal is working on the RayJoin Section 5.7 second-priority line using the
same-source regenerated County x Zipcode CDB pair:

- left: `/workspace/rayjoin_section57_same_source_cdb/point_cdb/dtl_cnty/dtl_cnty_Point.cdb`
- right: `/workspace/rayjoin_section57_same_source_cdb/point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb`
- historical author-output clue:
  `/workspace/rtdl_goal4806_fast_min/artifacts/section57_author_output_debug/author_overlay_debug.overlay.txt`

This is not an exact paper-input/answer run. It is a same-source regenerated CDB
revalidation target.

## Product Fixes Applied

1. Directed point-location SoS reported-distance contract was corrected to match
   the author determinism note:
   - `query_map_id == 0`: larger slope preferred.
   - `query_map_id == 1`: smaller slope preferred.
   - the preferred edge receives the smaller `t_reported`, so OptiX strict
     depth pruning cannot bypass the tie-break.

2. Overlay output-chain intersection sorting now matches the author comparator
   more closely:
   - sort by squared distance from the query edge start;
   - do not add a hidden `(eid0, eid1)` tie-break not present in the author code.

3. LSI materialization now preserves scaled rational intersection coordinates
   for midpoint generation:
   - output coordinates still use the author's truncation-to-internal behavior;
   - midpoint PIP queries use the rational midpoint before truncation, rather
     than averaging already-truncated internal coordinates.

These are general directed-segment point-location / directed-overlay repairs,
not RayJoin-only hidden kernels.

## Verification Already Run

Local regression:

```text
py -m unittest tests.goal4374_rayjoin_exact_paper_suite_test tests.goal4373_rayjoin_cdb_point_location_route_test
Ran 32 tests in 3.401s
OK
```

POD regression after rebuilding OptiX:

```text
RTDL_OPTIX_LIB=/workspace/rtdl_goal4820_sos_fix/build/librtdl_optix.so \
PYTHONPATH=src python3 -m unittest \
  tests.goal4374_rayjoin_exact_paper_suite_test \
  tests.goal4373_rayjoin_cdb_point_location_route_test
Ran 32 tests in 7.151s
OK
```

Author public County x Soil sample rerun after the SoS correction:

```json
{
  "answer_bytes": 16631243,
  "answer_sha256": "464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e",
  "byte_equal": true,
  "elapsed_sec": 7.173158057034016,
  "output_bytes": 16631243,
  "output_sha256": "464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e"
}
```

## County x Zipcode Probe Findings

The current first exposed window around the old mismatch is:

- author historical output:
  - chain30135: `106 107`
  - chain30138: `63 110`
- RTDL with author-reply deterministic SoS:
  - chain30135: moved to the other equal-height side;
  - chain30139: the formerly mismatching single-point span now uses the
    author-reply preferred side.

This is not a simple "RTDL still wrong at one chain" result. It shows that the
historical County x Zipcode author output is not a stable deterministic truth
under a single global SoS preference. That matches the user's author-reply note:
equal-height PIP candidates can be pruned by OptiX traversal order before the
shader-internal slope tie-break sees all candidates.

## Current Problem

The remaining problem is not performance. Performance remains blocked.

The current correctness problem is: for the same-source County x Zipcode data,
we do not yet have a deterministic author baseline generated with the
author-reply `t_reported` SoS fix. The old author-output artifact is a useful
debug clue, but it should not be treated as byte-equality ground truth.

## Next Correct Step

Do not chase the old single-run author output with more RTDL heuristics.

The next goal should generate a deterministic author-reference baseline from the
author source plus the author-reply `t_reported` patch, then compare RTDL against
that deterministic baseline on the same-source County x Zipcode pair.

If RTDL matches that deterministic author baseline, the same-source reproduction
line can proceed to bounded performance. If it does not, the next mismatch is a
real RTDL correctness gap under the declared deterministic contract.

## Forbidden

- Do not run performance while the deterministic correctness baseline is
  unresolved.
- Do not claim exact Section 5.7 paper reproduction from same-source regenerated
  CDBs.
- Do not tune RTDL to mimic one old nondeterministic author-output file.
- Do not introduce a RayJoin-only hidden overlay kernel.
