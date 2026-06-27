# Kepler Review: Phoenix V3 Hausdorff M5 Pre-Pod

Date: 2026-06-22
Verdict: `accept_for_focused_pod`

## Reviewed Scope

Kepler reviewed the third Set-A Hausdorff runtime-trunk local contract:

- `docs/reviews/codex_kepler_phoenix_v3_third_set_a_family_hausdorff_consensus_2026-06-22.md`
- `docs/reports/phoenix_v3_hausdorff_threshold_runner_route_m5_2026-06-22.md`
- `src/rtdsl/generic_primitives.py`
- `src/rtdsl/prepared_execution.py`
- `src/rtdsl/__init__.py`
- `examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py`
- `tests/v3_phoenix_prepared_execution_session_runner_test.py`
- `tests/v3_phoenix_hausdorff_prepared_execution_runner_wiring_test.py`

## Verdict

Kepler found no blocking issues and accepted the route for a focused pod probe.

Accepted facts:

- the new helper is generic and app-name-free;
- Hausdorff's new `directed_threshold_prepared_runner` mode calls the
  productized runner;
- the legacy `directed_threshold_prepared` mode remains available as the A/B
  incumbent;
- residency/materialization metadata is honest enough for a focused pod probe.

## Required Pod Gates

The focused pod run must show:

- both directed legs through `prepared_execution_session_runner`;
- repeat 5 / warmup 1;
- oracle parity;
- native scalar count;
- no threshold rows materialized on host;
- no hot-path host materialization;
- exact residency scope carried through;
- hot, cold, and runner-wall timings together;
- same-contract Embree baseline;
- no regression versus legacy app-front-door.

## Wording Risk

Kepler's main caution:

Do not treat `internal_device_residency_between_rtdl_phases=true` here as full
query-buffer/no-hidden-copy evidence. It is prepared search-structure residency
only. Query-point device residency remains false, true-zero-copy remains false,
and V4/external-buffer claims remain false.

## Non-Authorization

This review does not authorize:

```text
release_authorized: false
all_app_rerun_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
whole_hausdorff_speedup_claim_authorized: false
true_zero_copy_claim_authorized: false
v4_external_buffer_claim_authorized: false
```

## Local Gates Rechecked By Kepler

Kepler reran/accepted:

```text
py_compile OK
39-test focused suite OK
37-test wording/scorecard suite OK
```

The known Windows Python launcher `<prefix>` warning appeared, but commands
exited successfully.

## Goal-Level Decision Audit

Decision: accept the local Hausdorff M5 route for a focused pod probe.

1. Was I foolish?

   No. The decision follows a second-AI pre-pod review and keeps the run
   focused and non-release.

2. If yes, what actions made the decision foolish?

   Not applicable. The foolish action would be skipping review or treating
   prepared search-structure residency as full zero-copy/no-hidden-copy proof.

3. Was there another path?

   Yes. I could block the pod until query-point device residency is implemented,
   but that would collapse Step 2 generalization into Step 3 residency-default
   work and hide whether the runner route itself is stable.

4. Can I now try a different path that actually solves the problem?

   Yes. Run exactly the focused pod probe, record the result honestly, then
   move to Step 3 only if the route passes its limited gates.
