# Phoenix V3 M72 Barnes-Hut Blocker-Bound Runtime Trunk Local Evidence

Date: 2026-06-24

Status: `m72_local_wiring_ready_for_external_review_no_release_no_all_app`

## Purpose

M72 follows the revised Phoenix V3 direction: stop proving clean runner execution on
non-blocking families and aim the runtime trunk at a scorecard-controlling Set-A
blocker.

The bound blocker is:

| Field | Value |
| --- | --- |
| Scorecard row id | `set_a_barnes_hut_app_geomean_0_844x` |
| Set | `A` |
| App | `barnes_hut` |
| Metric | `set_a_app_geomean_v3_vs_v2_14` |
| Current value | `0.844x` |
| Source | `docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.md` |
| Target | `move_toward_or_above_parity` |
| Route kind | `trunk_fix_candidate` |

This report is not a speedup claim. It records the local code and contract work
needed before a focused POD benchmark can be responsibly requested.

## What Changed

### Generic Runtime Helper

File: `src/rtdsl/prepared_execution.py`

The app-agnostic helper
`run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session` now accepts:

- `scorecard_binding`: optional metadata that binds a runtime-trunk use to a
  named scorecard row.
- `win_source`: required classification of the expected win source.

Accepted `win_source` values are:

- `residency_wall`
- `partner_continuation`
- `kernel`

The helper validates that a release-path binding includes the required fields:

- `id`
- `set`
- `app`
- `metric`
- `current_value`
- `source`
- `route_kind`

The helper also rejects unknown route kinds. Valid route kinds are:

- `trunk_fix_candidate`
- `severe_regression_repair`

If no scorecard binding is supplied, the helper can still run as a generic
runtime primitive, but it explicitly records:

- `scorecard_blocker_bound: false`
- `release_path_candidate: false`

This prevents unbound clean execution from being misread as Phoenix V3 release
progress.

### Barnes-Hut Front Door Adapter

File:
`examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py`

The Barnes-Hut prepared execution route now calls the generic helper with the
exact Set-A blocker binding above. The app-level payload records:

- `phoenix_v3_m72`
- `scorecard_blocker_bound`
- `scorecard_blocker_app`
- `scorecard_blocker_current_value`
- `scorecard_blocker_route_kind`
- `scorecard_blocker_target`
- `win_source`
- `m43_reuse_scope`
- `pod_authorized: false`
- `release_authorized: false`
- `all_app_authorized: false`

The generic helper is not Barnes-Hut-specific. The app front door supplies the
scorecard binding; the runtime helper remains an aggregate-tree weighted vector
sum node.

### M43 Reuse Boundary

M72 reuses the M43 discipline, not the M43 CuPy kernel:

- explicit partner selection;
- prepared-session runner metadata;
- runtime-executed path evidence;
- blocker-aware claim boundaries;
- no automatic public speedup claim.

The aggregate-tree path currently uses the existing Numba CUDA continuation.
The metadata records this explicitly so reviewers do not confuse the M43 CuPy
grouped-reduction kernel with the M72 Barnes-Hut aggregate-tree path.

## Local Verification

Command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.v3_phoenix_prepared_execution_session_runner_test tests.v3_phoenix_barnes_hut_prepared_execution_runner_wiring_test
```

Result:

```text
Ran 52 tests in 1.159s
OK
```

The local test gate verifies:

- the aggregate-tree helper exposes and validates `scorecard_binding`;
- invalid `win_source` values fail;
- incomplete scorecard bindings fail;
- invalid route kinds fail;
- unbound helper calls are not release-path candidates;
- Barnes-Hut binds the exact blocker row in the front-door adapter;
- benchmark mode `prepared_execution_fused_vector_sum_numba_cuda` dispatches
  to the M72 payload behaviorally, not just by static source text;
- the focused POD packet requires runner samples to carry the M72 scorecard
  binding and `win_source`;
- the helper body does not hard-code Barnes-Hut app semantics.

## External Review And Amendments

Claude review:

`docs/reviews/claude_phoenix_v3_m72_barnes_hut_blocker_bound_runtime_trunk_review_2026-06-24.md`

Verdict:

`accept_with_required_amendments_before_focused_pod`

Required amendment status:

| Amendment | Status |
| --- | --- |
| A1 CPU-side behavioral dispatch test | Closed by `test_prepared_execution_mode_dispatches_to_runtime_runner_payload`. |
| A2 incumbent route declaration | Closed in `scripts/v3_phoenix_barnes_hut_runner_parity_pod_ab.py` summary field `incumbent_route_declaration`. |

The updated focused POD packet now fails if runner samples do not carry:

- `scorecard_blocker_bound`;
- `scorecard_blocker_id == set_a_barnes_hut_app_geomean_0_844x`;
- `scorecard_blocker_app == barnes_hut`;
- `win_source == partner_continuation`;
- the M43 reuse boundary text.

The packet also fails if the fused-control baseline is accidentally marked as
scorecard-bound.

## Existing Prior POD Evidence

Prior evidence exists at:

`docs/rebuild/v3/evidence/phoenix_v3_barnes_hut_runner_parity_pod_ab_fixed_20260622_182718/summary.json`

Important prior result:

- runner vs existing fused-control geomean: `0.999328063165968x`;
- historical OptiX over runner geomean: `12.730691398985789x`;
- runner/control parity with existing fused partner: `true`;
- release authorized: `false`;
- all-app authorized: `false`.

Interpretation: the runner preserved the existing fused partner's hot-path speed
but did not prove a wrapper-faster-than-current-control win. The large number
versus historical OptiX is only a no-go reference displacement, not the primary
claim.

## POD Readiness Smoke

The current RTX POD endpoint is reachable with the historical current-pod key:

```text
ssh -p 11592 -i ~/.ssh/id_ed25519_rtdl_codex_current_pod root@213.173.108.14
```

Read-only smoke result:

```text
hostname: 2bcb58b259e4
GPU: NVIDIA RTX 4000 Ada Generation
driver: 550.127.05
memory: 20475 MiB
```

No focused M72 benchmark has been run yet from this report. The next benchmark
must be a bounded Barnes-Hut blocker run, not an all-app run.

## Current Step Mapping

| Claude step | M72 status |
| --- | --- |
| Step 0 stop and freeze | Preserved: no all-app run and no symbol-cache route expansion. |
| Step 1 build trunk | Already partially established by earlier runner work; M72 retargets the trunk at a real blocker. |
| Step 2 generalize | In progress: Barnes-Hut is the next Set-A family bound to the same prepared-session discipline. |
| Step 3 residency default | Not complete; phase/residency metadata exists, but it is not yet mandatory for every hot path. |
| Step 4 continuation in core | Partial: grouped reduction exists; aggregate-tree weighted vector sum is now routed through the prepared runner boundary. |
| Step 5 all-app | Not authorized. |
| Step 6 external review and release decision | External review required before any focused POD authorization. |

## Decision Audit

### Goal-level decision: target Barnes-Hut blocker through the generic aggregate-tree helper

1. Was I stupid?

No, this decision corrects the earlier error of proving clean runner execution
without moving a scorecard blocker.

2. If yes, what actions made it stupid?

The earlier stupid pattern was chasing route hygiene and non-blocker wins. This
M72 decision avoids that by binding a named blocker before implementation.

3. Was there another possibility that avoids being stuck on one foolish path?

Yes. If the aggregate-tree runner cannot move Barnes-Hut on focused POD
evidence, the next move is not to keep polishing this route; it is to classify
the route as capability evidence or severe regression repair and retarget M74 to
another blocker.

4. Can I start a different path that truly solves the problem?

Yes. The controlling path is blocker-first runtime work: bind a Set-A row,
route it through the trunk, run a focused same-contract benchmark, and keep or
drop it based on whether it moves the scorecard.

## Non-Authorization

This report does not authorize:

- V3 release;
- all-app benchmarking;
- public speedup wording;
- broad V3-over-V2 claims;
- V4 work;
- embedding;
- external zero-copy claims;
- treating local unit tests as performance evidence.

The only requested next action is external review of whether this M72 local
wiring is sufficient to justify one focused Barnes-Hut POD run.
