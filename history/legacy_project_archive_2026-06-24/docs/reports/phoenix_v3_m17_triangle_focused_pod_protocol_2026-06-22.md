# Phoenix V3 M17 Triangle Focused POD Protocol

Date: 2026-06-22

Status: `m17_protocol_ready_for_review_no_pod_run`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_pod_spend_authorized_now: false
all_app_pod_spend_authorized: false
third_strict_set_a_material_probe_closed: false
```

2-AI verdict: `accept_m17_authorize_m18_runner_harness_no_pod`

Consensus record:
`docs/reviews/codex_bernoulli_phoenix_v3_m17_triangle_focused_pod_protocol_2ai_consensus_2026-06-22.md`

## Bottom Line

M17 defines the focused Triangle POD protocol, but it does not run POD.

The strict finding is that the old Triangle 80,000-clique row is strong but
still old evidence. The current Triangle app CLI has old app-front-door routes,
but no reviewed M16 productized-runner POD harness yet. Therefore a focused
POD run must not start until that harness exists, passes local dry-run/unit
tests, and M17/M18 review explicitly authorizes the spend.

## Exact Row

```text
row: Generated K4 clique ladder, 80,000 cliques
edge_count: 480000
oracle_triangle_count: 320000
serious_scale_floor: 80000 cliques
smoke_rows_count_for_release: false
```

This is a synthetic K4 clique-ladder row. It is not RT-Graph paper reproduction,
not graph database acceleration, and not broad V3-over-V2 evidence.

## Variants

M17 requires three variants on the same generated edge file:

```text
embree_same_contract_control
legacy_app_front_door_optix
productized_prepared_execution_runner
```

The old controls can use:

```text
$env:PYTHONPATH='src;.'; py -3 scripts/goal2631_generate_triangle_k4_binary.py --output build/phoenix_v3_m17_triangle/k4_cliques_80000.edge --cliques 80000

$env:PYTHONPATH='src;.'; py -3 examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py --mode rt_graph_2a1_generic_rt --edge-file build/phoenix_v3_m17_triangle/k4_cliques_80000.edge --edge-format binary --backend embree --detail summary --partner none --warmup 1 --repeat 5

$env:PYTHONPATH='src;.'; py -3 examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py --mode rt_graph_2a1_generic_rt --edge-file build/phoenix_v3_m17_triangle/k4_cliques_80000.edge --edge-format binary --backend optix --detail summary --partner cupy --warmup 1 --repeat 5
```

The runner route must use the M16 helper:

```text
run_ray_triangle_weighted_summary_device_output_stream_prepared_session
```

and must emit:

```text
runtime_executed: true
runtime_trunk_executes_end_to_end: true
productized_execution_path: prepared_execution_session_runner
primitive_family: ray_triangle_weighted_summary_device_output_stream
internal_device_residency_between_rtdl_phases: true
device_output_stream_validated: true
prepared_scene_reused: true
prepared_ray_batch_reused: true
ray_weights_device_resident: true
hot_path_host_materialization: false
weighted_hit_sum: 320000
```

## Success Bars

- Correctness: all variants must match `oracle_triangle_count=320000`.
- Productized runtime: runner metadata must prove the M16 path actually
  executed end to end.
- Material Set-A candidate: runner OptiX must beat Embree same-contract control
  by at least `1.20x` on both hot query median and runner-inclusive wall.
- Legacy no-regression: runner-inclusive wall must be at least `0.98x` of the
  legacy app-front-door OptiX route. If not, classify as productized coverage
  only unless a later 2-AI review accepts a specific exception.
- Claim boundary: release, public speedup, broad V3-over-V2, V4, and zero-copy
  flags stay false.

## Failure Actions

- No runner harness: stop and build/review the harness; do not spend POD.
- Hardware gate failure: stop and record environment failure.
- Oracle mismatch: stop; no performance interpretation.
- Missing M16 metadata: classify as productized-runner failure.
- Runner below `1.20x` over Embree: no third strict Set-A credit.
- Runner below `0.98x` versus legacy OptiX wall: productized coverage only.

## POD Budget If Later Authorized

```text
M18 runner harness local work: 1.5-3.0 h
focused POD wall time: 0.75-1.5 h
focused POD cost at $1 / 4 h: $0.19-$0.38
hard cap before new review: 2 h / $0.50
all-app POD: not authorized
```

The focused run must print heartbeat output at least every 30 seconds.

## Request

M17 asks external review to choose one:

```text
accept_m17_authorize_m18_runner_harness_no_pod
accept_m17_authorize_one_focused_triangle_pod_after_harness_gate
revise_m17_protocol
reject_m17_protocol
```

The reviewed verdict is `accept_m17_authorize_m18_runner_harness_no_pod`
because the current app route does not yet expose the M16 productized runner as
a serious POD harness. M18 is authorized for local harness implementation and
tests only; focused POD remains blocked.

## Goal-Level Decision Audit

Decision: write a protocol that exposes the missing runner harness as a pre-run
gate instead of running POD from old Triangle numbers.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   It would be foolish to reuse the old 347x/6.342x Triangle row as current
   Phoenix runner evidence or to run POD without a productized runner harness.
3. Was there another path?
   Yes: authorize a focused POD run immediately because the POD is online. That
   risks measuring the old app route again and learning nothing about V3.
4. Can I now try a different path?
   Yes. Freeze the exact row, controls, metrics, bars, harness gate, and
   resource cap; then seek 2-AI review before spending POD.
