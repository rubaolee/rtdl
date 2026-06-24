# Robot Collision Flag Stream

Status: V3 rebuild tutorial with one exact row-scoped M7 qualification; not a release claim and not release authorization.

This lesson reads robot collision as a reusable RTDL capability:
`collision_flag_stream`. The app supplies robot-shaped grouped segment probes;
RTDL runs a prepared grouped segment any-hit flag stream. The qualified row is
only a discrete sampled probe contract. It is not full robot planning, exact
solid collision, continuous collision, or zero-copy.

Source files:

```text
examples\current\research_benchmarks\robot_collision\rtdl_robot_collision_benchmark_app.py
docs/rebuild/v3/phoenix_v3_robot_collision_flag_stream_no_probe_paired_rtx_evidence_2026-06-21.md
docs/rebuild/v3/evidence/phoenix_v3_robot_collision_flag_stream_no_probe_paired_20260621/summary.json
docs/reviews/claude_phoenix_v3_robot_collision_flag_stream_no_probe_paired_m7_review_2026-06-21.md
docs/reviews/codex_phoenix_v3_robot_collision_flag_stream_no_probe_paired_2ai_consensus_2026-06-21.md
```

Typical local command shape for a performance-only prepared run:

```powershell
py -3 examples\current\research_benchmarks\robot_collision\rtdl_robot_collision_benchmark_app.py --mode optix_prepared_device_buffers --dataset scaled --pose-count 8192 --obstacle-count 2048 --link-count 2 --repeats 101 --warmup 5 --no-probe-reference
```

The CPU probe-reference oracle is intentionally separate from the performance
run. Use validation runs to prove flags match; use `--no-probe-reference` runs
to time the prepared flag-stream route without the CPU oracle dominating wall
time.

## The Qualified Row

The exact row is:

```text
collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped
```

Shape:

| Field | Value |
| --- | ---: |
| poses | 8,192 |
| links | 2 |
| groups | 16,384 |
| segments | 147,456 |
| static obstacles | 2,048 |
| static obstacle triangles | 4,096 |

Result on the RTX 4000 Ada pod:

| Metric | OptiX speedup vs Embree |
| --- | ---: |
| Tail prepared query execution phase mean | 5.086x |
| Total-run window prepared query execution phase mean | 5.075x |
| No-probe wrapper mean | 1.171x |
| Weakest no-probe wrapper sample | 1.083x |

CPU probe-reference validation was run separately and matched both backends.
The wrapper speedup is the conservative process-level bound that includes all
costs except the CPU probe-reference oracle. The tail and window speedups are
prepared query execution phase metrics, not full prepare-and-query setup
claims.

## What To Learn

Use this as a V3 example of a generic flag-stream route:

1. Build grouped segment probes from app data.
2. Prepare a triangle scene.
3. Run the generic any-hit flag stream.
4. Validate flags against a CPU oracle separately.
5. Keep validation, prepared query timing, wrapper timing, and public wording
   separate.

## Allowed Wording

RTDL V3 includes a generic `collision_flag_stream` route where, on the
8,192-pose / 147,456-segment discrete sampled probe contract on a single RTX
4000 Ada pod, prepared OptiX grouped segment any-hit flags beat the
same-contract Embree route across five no-probe paired process samples: tail
prepared invocation speedup mean 5.086x, total-run window speedup mean 5.075x,
and no-probe wrapper speedup mean 1.171x with weakest no-probe wrapper speedup
1.083x. CPU probe-reference validation was run separately and matched both
backends. This is sampled flag-stream evidence, not full robot planning, exact
solid collision, or continuous collision. The tail and window speedups measure
the prepared query execution phase; the wrapper speedup is the conservative
process-level bound that includes all costs except the CPU probe-reference
oracle.

## What Not To Claim

- Do not claim Robot Collision V3 is 5x faster end to end.
- Do not claim RTDL accelerates full robot planning.
- Do not claim RTDL supports exact solid collision for this row.
- Do not claim RTDL supports continuous collision for this row.
- Do not claim this proves zero-copy.
- Do not claim this is a broad V3-over-V2 speedup.
- Do not claim any robot-collision row beyond
  `collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped`
  is M7-qualified.

This remains row-scoped V3 evidence, not a V3 release claim.
