# V4 Goal4714 Custom Predicate Early-Exit Smoke POD Result

Date: 2026-06-26

Status: `complete_pending_3ai_review_debt`

Decision: `pass_smoke_gate_not_timing_not_release`

## Goal

Implement and run a bounded POD smoke for the Goal4713 target:

`ray_triangle_custom_predicate_early_exit_multi_hit`

This smoke checks only:

- Numba predicate PTX generation;
- OptiX wrapper compile/link/launch;
- correctness;
- whether V4 actually performs early termination in primary regimes.

It is not a performance timing gate.

## Evidence

- JSON:
  `future/v4/evidence/v4_goal4714_custom_predicate_early_exit_smoke_pod_2026-06-26.json`
- Markdown:
  `future/v4/evidence/v4_goal4714_custom_predicate_early_exit_smoke_pod_2026-06-26.md`
- POD stdout log:
  `future/v4/evidence/v4_goal4714_custom_predicate_early_exit_smoke_pod_2026-06-26.stdout.log`
- Source:
  `src/rtdsl/v4_goal4714_custom_predicate_early_exit_smoke_result.py`
- Script:
  `scripts/v4_goal4714_custom_predicate_early_exit_smoke_pod.py`
- Tests:
  `tests/v4_goal4714_custom_predicate_early_exit_smoke_result_test.py`

POD:

- Host: `root@194.68.245.170 -p 22089`
- Workspace: `/root/rtdl_v4_candidate_pod`
- Python: `/usr/bin/python3`

## Result

Classification:

`pass_smoke_gate_not_timing_not_release`

Rows:

| regime | role | correctness | V4 any-hit invocations | fallback all-hit invocations | early termination |
|---|---|---|---:|---:|---|
| `dense_early_accept_k8` | primary | true | 4096 | 32768 | true |
| `dense_early_accept_k32` | primary | true | 4096 | 131072 | true |
| `dense_reject_all_k32` | control | true | 131072 | 131072 | false |
| `no_hit_empty` | control | true | 0 | 0 | false |

Interpretation:

The new target passes the smoke gate. Unlike Goal4711, this route changes the
cost model: in primary early-accept regimes, V4 reduces any-hit work from
`ray_count * candidates_per_ray` to roughly `ray_count`. The controls behave as
expected.

This is not yet a speed claim. It only authorizes Goal4715 to freeze and run a
focused timing gate under the already defined Goal4713 protocol.

## Validation

Local:

```text
py -m py_compile src/rtdsl/v4_goal4714_custom_predicate_early_exit_smoke_result.py scripts/v4_goal4714_custom_predicate_early_exit_smoke_pod.py src/rtdsl/v4.py
py scripts/v4_goal4714_custom_predicate_early_exit_smoke_pod.py --dry-run --json-out future/v4/evidence/v4_goal4714_custom_predicate_early_exit_smoke_dry_run_2026-06-26.json --md-out future/v4/evidence/v4_goal4714_custom_predicate_early_exit_smoke_dry_run_2026-06-26.md
py -m unittest tests.v4_goal4714_custom_predicate_early_exit_smoke_result_test tests.v4_goal4713_custom_predicate_early_exit_protocol_test
```

Remote:

```text
/usr/bin/python3 -m py_compile src/rtdsl/v4_goal4713_custom_predicate_early_exit_protocol.py src/rtdsl/v4_goal4714_custom_predicate_early_exit_smoke_result.py scripts/v4_goal4714_custom_predicate_early_exit_smoke_pod.py
/usr/bin/python3 scripts/v4_goal4714_custom_predicate_early_exit_smoke_pod.py --dry-run
/usr/bin/python3 -m unittest tests.v4_goal4714_custom_predicate_early_exit_smoke_result_test
/usr/bin/python3 scripts/v4_goal4714_custom_predicate_early_exit_smoke_pod.py --ray-count 4096 --json-out /root/v4_goal4714_smoke_20260626.json --md-out /root/v4_goal4714_smoke_20260626.md
```

Observed:

- local tests: `4 tests OK` for Goal4714/4713 pair.
- remote dry-run/unit tests: passed.
- remote smoke: passed.

## Non-Authorization

Goal4714 does not authorize:

- performance claims;
- formal high-performance V4 wording;
- V4 release;
- public Tier-3 support;
- arbitrary callback support;
- raw OptiX callback support;
- all-app benchmarking.

## Goal-Level Decision Audit

1. Was I being stupid?

No. This goal did not jump to timing; it first proved the new route actually
changes early-exit behavior.

2. If yes, what actions made the decision stupid?

Not applicable.

3. Is there another path that avoids getting stuck on a bad premise?

Yes. If early termination had not appeared, the correct path would be to repair
the runner before timing. It did appear, so proceeding to a timing gate is
justified.

4. Can I now try the different path that actually solves the problem?

Yes. Goal4715 should run the focused timing gate under the Goal4713 protocol.
