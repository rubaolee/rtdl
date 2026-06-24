# 2AI Consensus: Phoenix V3 M72 Focused Barnes-Hut POD Authorization

Date: 2026-06-24

Status: `authorize_one_focused_barnes_hut_pod_no_release_no_all_app`

## Scope

This consensus applies only to the Phoenix V3 M72 Barnes-Hut / aggregate-tree
Set-A blocker focused POD packet.

It does not authorize V3 release, all-app benchmarking, public speedup wording,
broad V3-over-V2 claims, V4 work, embedding, or external zero-copy claims.

## Inputs

- Local evidence:
  `docs/reports/phoenix_v3_m72_barnes_hut_blocker_bound_runtime_trunk_2026-06-24.md`
- Review request:
  `docs/reviews/call_for_review_phoenix_v3_m72_barnes_hut_blocker_bound_runtime_trunk_2026-06-24.md`
- Claude review:
  `docs/reviews/claude_phoenix_v3_m72_barnes_hut_blocker_bound_runtime_trunk_review_2026-06-24.md`
- Focused packet:
  `scripts/v3_phoenix_barnes_hut_runner_parity_pod_ab.py`
- Tests:
  `tests.v3_phoenix_barnes_hut_runner_parity_pod_ab_test`
  `tests.v3_phoenix_barnes_hut_prepared_execution_runner_wiring_test`
  `tests.v3_phoenix_prepared_execution_session_runner_test`

## Review Chain

| Seat | Verdict |
| --- | --- |
| Claude | `accept_with_required_amendments_before_focused_pod` |
| Codex | `amendments_closed_authorize_one_focused_barnes_hut_pod_no_release` |

## Amendment Closure

Claude required two amendments before a focused POD run.

| Amendment | Closure evidence |
| --- | --- |
| A1: behavioral dispatch test | `test_prepared_execution_mode_dispatches_to_runtime_runner_payload` verifies the mode dispatch calls the M72 payload without GPU. |
| A2: incumbent route declaration | `summary.incumbent_route_declaration` names the baseline mode `fused_frontier_force_sum_bucketized_numba_cuda`, candidate mode `prepared_execution_fused_vector_sum_numba_cuda`, body counts, theta, bucket size, max depth, repeat, warmup, samples, scorecard row, and source. |

Targeted verification:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.v3_phoenix_barnes_hut_runner_parity_pod_ab_test tests.v3_phoenix_barnes_hut_prepared_execution_runner_wiring_test tests.v3_phoenix_prepared_execution_session_runner_test
```

Result:

```text
Ran 52 tests in 1.159s
OK
```

## Authorized Run

Exactly one focused POD run is authorized:

```bash
PYTHONPATH=src:. python3 scripts/v3_phoenix_barnes_hut_runner_parity_pod_ab.py \
  --output-dir docs/rebuild/v3/evidence/phoenix_v3_m72_barnes_hut_blocker_bound_pod_20260624 \
  --body-counts 32768 65536 131072 \
  --query-repeat 11 \
  --warmup 3 \
  --samples 5
```

The run must collect:

- existing fused-control route;
- M72 prepared-execution runner route;
- historical OptiX no-go reference route.

The packet must report:

- current-control parity;
- historical no-go displacement;
- runtime execution;
- scorecard binding;
- `win_source`;
- phase/residency accounting;
- claim flags all closed.

## Non-Authorization

This consensus does not authorize:

- V3 release;
- all-app benchmarking;
- public speedup wording;
- broad V3-over-V2 claims;
- V4 work;
- embedding;
- external zero-copy claims;
- treating the focused POD result as a general V3 speed claim.
