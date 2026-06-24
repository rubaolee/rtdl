# Phoenix V3 M72 Barnes-Hut Blocker-Bound POD Intake

Date: 2026-06-24

Status: `m72_focused_pod_valid_not_release_not_all_app`

## Artifact

Evidence directory:

`docs/rebuild/v3/evidence/phoenix_v3_m72_barnes_hut_blocker_bound_pod_20260624_091320/`

Summary:

`docs/rebuild/v3/evidence/phoenix_v3_m72_barnes_hut_blocker_bound_pod_20260624_091320/summary.json`

Run shape:

- body counts: `32768`, `65536`, `131072`;
- query repeat: `11`;
- warmup: `3`;
- samples: `5`;
- theta: `0.5`;
- bucket size: `32`;
- max depth: `32`;
- same POD session.

Environment:

- GPU: NVIDIA RTX 4000 Ada Generation;
- driver: `550.127.05`;
- Python used for successful run:
  `/root/rtdl_v3_rebuild_20260620/.venv/bin/python`;
- CUDA compiler environment followed the existing runbook:
  `NUMBA_CUDA_PREFIX=/root/rtdl_v3_rebuild_20260620/.venv/lib/python3.12/site-packages/nvidia/cuda_nvcc`.

Two failed launches preceded the successful run:

1. system `python3` had no `numba`;
2. `venv_partner_py312` emitted PTX too new for the driver-side linker.

Those failed launches produced no performance artifact and are not counted.

## Gate Result

The successful packet completed with:

```text
failed_checks: []
```

Key checks:

- `runner_used_all_samples: true`;
- `runner_runtime_trunk_executes_all_samples: true`;
- `runner_internal_device_residency_all_samples: true`;
- `runner_scorecard_blocker_bound_all_samples: true`;
- `runner_scorecard_blocker_id_all_samples: true`;
- `runner_win_source_partner_continuation_all_samples: true`;
- `control_not_scorecard_bound: true`;
- `all_claim_flags_false: true`.

The M72 scorecard binding is present:

```text
set_a_barnes_hut_app_geomean_0_844x
```

The incumbent route declaration is present:

```text
baseline: fused_frontier_force_sum_bucketized_numba_cuda
candidate: prepared_execution_fused_vector_sum_numba_cuda
historical no-go reference: prepared_aggregate_frontier_weighted_vector_optix
```

## Performance Read

Primary current-control comparison:

| Body count | Control sec | Runner sec | Runner/control speedup |
| --- | ---: | ---: | ---: |
| `32768` | `0.010795198380947113` | `0.01080198585987091` | `0.9993716452685786x` |
| `65536` | `0.015763655304908752` | `0.01577114313840866` | `0.9995252193557439x` |
| `131072` | `0.04136938601732254` | `0.0413535013794899` | `1.000384118328624x` |

Geomean runner vs existing fused-control:

```text
0.9997602284020717x
```

Interpretation: the productized prepared runner preserves the existing fused
Numba CUDA route's speed within noise. It is not a new current-control speedup.

Historical no-go reference comparison:

| Body count | Historical OptiX sec | Runner sec | Historical/runner speedup |
| --- | ---: | ---: | ---: |
| `32768` | `0.09551071375608444` | `0.01080198585987091` | `8.841958783792172x` |
| `65536` | `0.21427969634532928` | `0.01577114313840866` | `13.586820845185134x` |
| `131072` | `0.7144575119018555` | `0.0413535013794899` | `17.27683238585947x` |

Geomean historical OptiX over runner:

```text
12.75587197083642x
```

Interpretation: the runner displaces a known slow historical OptiX frontier
route. This is useful as a no-go-route replacement, but it is not the primary
claim and does not authorize public speedup wording.

## M72 Conclusion

M72 successfully proves a scorecard-bound, productized runtime-trunk route for
the Barnes-Hut aggregate-tree family:

- the front door routes into the prepared-session runner;
- the runner executes;
- RTDL-owned residency between phases is recorded;
- the M72 scorecard blocker metadata is carried by runner samples;
- the existing fused partner's hot-path speed is preserved.

But M72 does not prove a material speedup over the current fused-control route.
It should be classified as:

`runtime_trunk_productization_parity_for_barnes_hut_not_current_control_speedup`

This is good engineering progress, but not enough by itself to make V3 a
performance release. The next Phoenix V3 work should target a second blocker
where the runtime trunk can plausibly create a real current-control win, not
another parity-only wrapper.

## Decision Audit

### Goal-level decision: accept the valid M72 focused POD result as trunk progress but not as a speedup win

1. Was I stupid?

No. The stupid action would be to claim the `12.7559x` historical OptiX number
as the Barnes-Hut current-control result.

2. If yes, what actions made it stupid?

The earlier failure pattern was mixing a historical no-go route with the real
current control. This intake explicitly separates them.

3. Was there another possibility that avoids being stuck on one foolish path?

Yes. If the target is major V3 performance, continue to M74 only with blockers
where the trunk can beat or materially improve the current control. Do not keep
polishing Barnes-Hut if it remains parity-only.

4. Can I start a different path that truly solves the problem?

Yes. Use this M72 result as proof that the trunk can carry a real app-family
route, then move to the next Set-A blocker and require a current-control gain
before considering all-app rerun.

## Non-Authorization

This intake does not authorize:

- V3 release;
- all-app benchmarking;
- public speedup wording;
- broad V3-over-V2 claims;
- V4 work;
- embedding;
- external zero-copy claims.
