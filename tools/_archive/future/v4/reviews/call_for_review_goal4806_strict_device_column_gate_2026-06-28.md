# Call For Review: Goal4806 Strict Device-Column And Preflight Gate

Date: 2026-06-28

## Review Target

Review the latest Goal4806 changes on branch:

```text
codex/v4-tier2-section8
```

Relevant commits:

```text
79a178437 Integrate Goal4806 V4 Numba into RayJoin matrix
2ac5bb4a9 Tighten Goal4806 device-column measurement gate
<pending> Add Section 5.7 preflight and static device-column component audit
```

## Context

Goal4806 is the V4+Numba RayJoin Section 5.7 Polygon Overlay auto-primitive
planner. The final goal is not merely to plan a route. It must eventually
produce a fair paper-reproduction comparison across:

1. RayJoin author code (`query_exec` / `polyover_exec`)
2. V2.14 exact-suite route
3. V4+Numba selected plan

with correctness and performance on the same Section 5.7 inputs.

## What Changed

The Section 5.7 matrix runner now recognizes `v4_numba` alongside:

```text
author_rt
rtdl_optix
rtdl_embree
```

The V4+Numba planner now has a strict measurement gate. A candidate is
measurable only if all of these are true:

- exact Section 5.7 inputs exist;
- Numba CUDA is available;
- RTDL exposes the Section 5.7 candidate/refinement stream as device-resident
  columns.

If inputs and Numba are available but device columns are not available, the
candidate status is:

```text
blocked_missing_section57_device_columns
```

This prevents a host-materialized overlay summary path from being mislabeled as
a V4+Numba measured performance route.

The public RayJoin wrapper now also exposes:

```bash
python3 examples/paper_reproduction/rayjoin.py --section57-preflight --dataset-root data/rayjoin_section57_cdb --query-exec /path/to/query_exec --polyover-exec /path/to/polyover_exec --json
```

The preflight separates:

- exact Section 5.7 CDB inputs;
- RayJoin author binaries;
- RT-core GPU presence;
- Numba CUDA availability;
- static Section 5.7 device-column component declarations.

Current static device-column audit result:

```text
static_components_declared: true
end_to_end_composition_status: components_present_pod_validation_required
performance_evidence_status: not_measured
```

That means the route pieces are present in source, but a real RT-core POD run is
still required before correctness/performance evidence exists.

## Files To Inspect

```text
src/rtdsl/rayjoin_numba_auto_planner.py
scripts/rayjoin_section57_overlay_matrix.py
examples/paper_reproduction/rayjoin.py
tests/v4_goal4806_rayjoin_numba_auto_planner_test.py
tests/v4_rayjoin_section57_public_entry_test.py
tests/goal4374_rayjoin_exact_paper_suite_test.py
docs/research/rayjoin/rayjoin_section57_polygon_overlay_v4_workload_status.md
tools/_archive/future/v4/reports/goal4806_author_source_and_matrix_integration_status_2026-06-28.md
```

Evidence directory:

```text
tools/_archive/future/v4/evidence/goal4806_section57_matrix_with_v4_numba_2026-06-28
tools/_archive/future/v4/evidence/goal4806_section57_preflight_2026-06-28.json
```

## Verification Already Run

Windows:

```bash
py -3 -m unittest \
  tests.v4_goal4806_rayjoin_numba_auto_planner_test \
  tests.v4_rayjoin_section57_public_entry_test \
  tests.goal4374_rayjoin_exact_paper_suite_test \
  tests.v4_goal4640_public_docs_cleanup_test
```

Result:

```text
Ran 48 tests in 98.513s
OK
```

Focused Windows retest after the preflight/static-component update:

```bash
py -3 -m unittest \
  tests.v4_rayjoin_section57_public_entry_test \
  tests.v4_goal4806_rayjoin_numba_auto_planner_test \
  tests.goal4374_rayjoin_exact_paper_suite_test
```

Result:

```text
Ran 34 tests in 14.234s
OK
```

Linux clean clone on `192.168.1.20`:

```bash
python3 -m unittest \
  tests.v4_goal4806_rayjoin_numba_auto_planner_test \
  tests.v4_rayjoin_section57_public_entry_test
```

Result:

```text
Ran 10 tests in 4.827s
OK
```

## Questions For Reviewer

1. Does the four-column matrix integration correctly prevent V4+Numba from
   drifting outside the author/V2/V4 comparison surface?
2. Is `blocked_missing_section57_device_columns` the correct status when exact
   inputs and Numba exist but RTDL only exposes host overlay summaries?
3. Does this gate avoid false performance claims?
4. Does it accidentally block a legitimate existing Section 5.7 device-column
   route that already exists elsewhere in the codebase?
5. Does the static component audit correctly distinguish source-level route
   pieces from measured Section 5.7 evidence?
6. Is the preflight surface the right next handoff point for POD execution?
7. Are the docs and evidence honest that Goal4806 is still not complete?
8. What is the next required engineering step to make Goal4806 measurable?

## Non-Authorization

This packet does not authorize:

- a full RayJoin Section 5.7 paper-reproduction claim;
- public performance wording;
- a V4.0/V4.1 release claim;
- arbitrary OptiX callback scope;
- treating host-materialized overlay rows as device-resident V4+Numba evidence.
