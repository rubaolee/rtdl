# Phoenix V3 Hausdorff Threshold Runner Route M5

Date: 2026-06-22
Status: `local_contract_passed_pre_pod_review_required`

## What Changed

This step routes the Hausdorff threshold-summary probe through the productized
Phoenix V3 prepared-execution/session runner without making it an app-specific
optimization.

New reusable runtime surface:

```text
run_fixed_radius_threshold_reached_count_2d_prepared_session
primitive_family: fixed_radius_threshold_reached_count_2d
productized_execution_path: prepared_execution_session_runner
```

Hausdorff now has two distinct modes:

```text
directed_threshold_prepared         legacy app-front-door prepared loop
directed_threshold_prepared_runner  productized prepared-execution runner route
```

The legacy mode remains available as the focused pod A/B incumbent. The runner
mode is the Phoenix V3 trunk probe.

Focused pod runner:

```text
scripts/v3_phoenix_hausdorff_threshold_runner_pod_ab.py
```

It runs only the three focused routes: same-contract Embree, legacy
app-front-door prepared OptiX, and productized prepared-execution runner OptiX.
It does not run V2.x and does not run all apps.

## Boundary

This is not release evidence yet.

The route records all claim flags false:

```text
release_authorized: false
all_app_rerun_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
whole_hausdorff_speedup_claim_authorized: false
true_zero_copy_claim_authorized: false
v4_external_buffer_claim_authorized: false
automatic_partner_selection_authorized: false
app_specific_native_engine_logic_allowed: false
```

Runtime-returned materialization/residency evidence is explicit:

- native scalar count used;
- threshold candidate rows not materialized on host;
- prepared search structure resident between RTDL phases when the backend
  reports it;
- query points are not claimed device-resident between phases;
- residency scope is
  `prepared_search_structure_only_query_points_not_device_resident`.

## Why This Addresses The Current Error

The previous failure was order-of-work: optimizing isolated route leaves before
the execution graph/runtime trunk actually executed. This patch moves the
Hausdorff probe from app-local prepared looping into the shared
`prepared_execution_session_runner` path.

This does not yet solve every residency problem. It is a controlled Step-2
generalization probe. The next Step-3 work is to make measured no-hidden-copy /
device-resident phase accounting a runner default across the Set-A probes.

## Validation

Local focused gates:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_phoenix_hausdorff_prepared_execution_runner_wiring_test \
  tests.goal879_hausdorff_threshold_rt_core_subpath_test \
  tests.goal1132_hausdorff_phase_contract_test

39 tests OK
```

Additional gates:

```text
PYTHONPATH=src;. py -3 -m py_compile \
  src/rtdsl/prepared_execution.py \
  src/rtdsl/generic_primitives.py \
  src/rtdsl/__init__.py \
  examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py \
  scripts/v3_phoenix_rtnn_prepared_execution_runner_repeat50_pod_ab.py

OK
```

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_phoenix_hausdorff_prepared_execution_runner_wiring_test \
  tests.v3_phoenix_set_ab_scorecard_gate_test \
  tests.v3_release_wording_gate_test

37 tests OK
```

POD runner dry-run and combined focused gate:

```text
PYTHONPATH=src;. py -3 -m py_compile \
  scripts/v3_phoenix_hausdorff_threshold_runner_pod_ab.py

OK
```

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_hausdorff_threshold_runner_pod_ab_test \
  tests.v3_phoenix_hausdorff_prepared_execution_runner_wiring_test \
  tests.v3_phoenix_prepared_execution_session_runner_test

35 tests OK
```

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_phoenix_hausdorff_prepared_execution_runner_wiring_test \
  tests.v3_phoenix_hausdorff_threshold_runner_pod_ab_test \
  tests.goal879_hausdorff_threshold_rt_core_subpath_test \
  tests.goal1132_hausdorff_phase_contract_test \
  tests.v3_phoenix_set_ab_scorecard_gate_test \
  tests.v3_release_wording_gate_test

47 tests OK
```

The Windows Python launcher still prints
`Could not find platform independent libraries <prefix>` before tests; this is
environment noise already seen in earlier passing gates.

## Pod Plan

Do not run all-app. Do not rerun V2.x. The next pod use is focused only.

Precondition:

- Kepler/second-AI pre-pod review accepts this local contract;
- the review agrees the focused run is allowed as non-release evidence;
- no reviewer upgrades this to all-app or release work.

Focused pod configuration:

```text
points per side: 1,048,576
threshold: 0.4
repeat: 5
warmup: 1
routes:
  - productized runner: directed_threshold_prepared_runner
  - legacy incumbent: directed_threshold_prepared
  - same-contract Embree baseline
required result fields:
  - oracle parity
  - runner metadata for both directed legs
  - hot query, cold-plus-query, runner-wall timings
  - no regression versus legacy app-front-door route
```

Expected pod use:

```text
best case: 0.5-1.0 pod hours
expected: 1-2 pod hours
buffer if native rebuild/sync is needed: 2-4 pod hours
cost at $1/4h:
  best case: about $0.13-$0.25
  expected: about $0.25-$0.50
  buffer cap before asking: about $1.00
```

## What Comes After

If focused pod evidence passes:

1. record pod evidence;
2. request second-AI result review;
3. count Hausdorff as the third runner-backed Set-A probe only if the review
   accepts the route and boundaries;
4. move to Step 3: make measured residency/no-hidden-copy accounting a runner
   default.

If focused pod evidence fails:

1. do not all-app rerun;
2. do not promote Hausdorff as third Set-A material evidence;
3. inspect whether the failure is generic runner overhead or lack of runtime
   residency evidence;
4. stop or choose another Set-A route only after a new 2-AI decision.

## Goal-Level Decision Audit

Decision: implement Hausdorff as the third Set-A local runner route and require
pre-pod review before spending pod time.

1. Was I foolish?

   No for this decision. It moves a real Set-A probe into the shared runtime
   path and blocks paid pod time until local gates pass.

2. If yes, what actions made the decision foolish?

   Not applicable. The foolish action would be running the pod from the old
   app-local loop and calling the old speedup Phoenix trunk evidence.

3. Was there another path?

   Yes. I could choose Triangle for a larger isolated number, or continue
   RTDBSCAN. Both paths are weaker for this immediate trunk-generalization
   step.

4. Can I now try a different path that actually solves the problem?

   Yes. Use this route as a controlled third-family trunk probe, then shift to
   the real Step-3 residency/no-hidden-copy runner default instead of continuing
   leaf optimization.
