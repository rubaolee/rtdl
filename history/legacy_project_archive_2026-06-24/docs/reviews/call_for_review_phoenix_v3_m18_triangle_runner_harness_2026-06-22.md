# Call For Review: Phoenix V3 M18 Triangle Runner Harness

Date: 2026-06-22

Status: `request_m18_harness_review_not_pod_run`

This asks for strict review of the local M18 harness. It does not authorize
release or POD spend by itself.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_pod_spend_authorized_now: false
all_app_pod_spend_authorized: false
third_strict_set_a_material_probe_closed: false
```

## Packet

- M18 JSON:
  `docs/rebuild/v3/phoenix_v3_m18_triangle_runner_harness_2026-06-22.json`
- M18 report:
  `docs/reports/phoenix_v3_m18_triangle_runner_harness_2026-06-22.md`
- Harness:
  `scripts/v3_phoenix_triangle_runner_m18_pod_ab.py`
- Test:
  `tests/v3_phoenix_triangle_runner_m18_pod_ab_test.py`
- M17 consensus:
  `docs/reviews/codex_bernoulli_phoenix_v3_m17_triangle_focused_pod_protocol_2ai_consensus_2026-06-22.md`
- Initial M18 review:
  `docs/reviews/codex_bernoulli_phoenix_v3_m18_triangle_runner_harness_initial_review_2026-06-22.md`
- Second M18 review:
  `docs/reviews/codex_bernoulli_phoenix_v3_m18_triangle_runner_harness_second_review_2026-06-22.md`

## Revision Since Initial Review

The initial M18 verdict was `revise_m18_harness` because the first draft read
`weighted_hit_sum_out.get()` inside the measured runner body while claiming
`hot_path_host_materialization=false`.

The revised harness moves scalar read/finalization out of the measured launch
body:

```text
launch_weighted_summary_device_output_stream:
  enqueue/synchronize device-output executor only

finalize_weighted_summary_device_output_stream:
  read weighted_hit_sum_out once after measured repeats
```

Regression coverage now checks that `weighted_hit_sum_out.get` appears only in
the finalize body, not the measured launch body.

Local verification after the revision includes the combined M16/M17/M18 suite
(`58 tests OK`), dry-run success with `failed_check_count=0`, wording gate pass,
and `py_compile` for the runner plus prepared execution helper.

## Revision Since Second Review

The second M18 verdict was again `revise_m18_harness`. The revised harness now:

- records expected/actual K4 binary edge-file sha256, byte count, and edge
  count;
- stops before real variants if the edge-file identity preflight fails;
- requires Embree, legacy OptiX, and productized runner payloads to expose and
  match `oracle_triangle_count`;
- includes regression tests for control oracle mismatch and edge checksum
  mismatch.

## Review Questions

1. Does the M18 script satisfy the M17 runner-harness blocker?
2. Is the productized runner variant correctly wired through the M16 helper and
   device-output executor rather than the old host-scalar route?
3. Does the revision close the initial hot-path scalar materialization blocker?
4. Does the revision close the second-review control oracle and edge checksum
   blockers?
5. Are dry-run and fail-closed gates sufficient before one focused POD run?
6. Is one focused Triangle POD run now authorized?
7. If authorized, is the provided command and 2 h / $0.50 cap acceptable?
8. Is any all-app POD authorized? My position: no.
9. Is any release/public/broad V3-over-V2 wording authorized? My position: no.

## Requested Verdict Labels

Choose exactly one:

- `accept_m18_authorize_one_focused_triangle_pod`: harness is sufficient and
  one focused Triangle POD run is authorized under the M17/M18 command, success
  bars, heartbeat, and 2 h / $0.50 cap.
- `accept_m18_harness_only_no_pod`: harness is directionally sufficient, but
  still requires local/code fixes before POD.
- `revise_m18_harness`: require specific code, test, metadata, or protocol
  fixes before any POD decision.
- `reject_m18_harness`: the harness does not satisfy M17.

Regardless of verdict, explicitly state:

- release authorization: yes/no
- public speedup authorization: yes/no
- broad V3-over-V2 authorization: yes/no
- focused POD authorization now: yes/no
- all-app POD authorization now: yes/no
- whether M18 satisfies the runner harness blocker
- whether Triangle counts as the third strict Set-A material probe now

Please be strict. A focused POD run is useful only if it measures the current
Phoenix V3 productized runner path and keeps hot-query, runner-wall, and legacy
controls separate.

## Goal-Level Decision Audit

Decision: seek 2-AI review after local M18 harness dry-run before any POD run.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   The foolish action would be treating dry-run as performance evidence.
3. Was there another path?
   Yes: run the POD immediately because the harness exists. That would skip the
   required review.
4. Can I now try a different path?
   Yes. Get review, then run at most one focused POD only if authorized.
