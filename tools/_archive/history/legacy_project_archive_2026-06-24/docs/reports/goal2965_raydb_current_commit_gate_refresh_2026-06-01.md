# Goal2965: RayDB Current-Commit Gate Refresh

Date: 2026-06-01
Status: pod decision gate passed on current main

## Purpose

Goal2896 established the RayDB-style scalar grouped-reduction decision rule:
when a continuation exactly matches an existing fused app-agnostic RTDL
primitive, v2.5 should route primitive-first rather than force a typed
hit-stream plus Triton continuation.

Goal2965 refreshes that gate on the current pushed commit after the Goal2958 to
Goal2962 performance hardening chain. It also adds a 2,000,000-row stress row to
check that the decision remains directionally stable beyond the original 250K
and 1M acceptance rows.

## Pod Evidence

Pod target: `root@69.30.85.171 -p 22167`

Source commit: `28bcf380b078f6e3c0cbe55d9ed4ed78a9ac61e9`

Artifacts:

- `docs/reports/goal2965_raydb_current_gate_pod/goal2965_raydb_same_contract_raw_current.json`
- `docs/reports/goal2965_raydb_current_gate_pod/goal2965_raydb_same_contract_gate_current.json`

Run shape:

- rows: `250000`, `1000000`, `2000000`
- modes: `count`, `sum`
- group count: `256`
- backends:
  - `paper_rt_optix`
  - `paper_rt_optix_v2_5_primitive_first`
  - `paper_rt_optix_device_hit_stream_triton_prepared`
- repeats: `3`
- warmup: `1`

## Gate Result

The existing Goal2896 decision gate still passes:

| Field | Value |
| --- | --- |
| Status | `pass` |
| all_correct | `true` |
| errors | `[]` |

Same-contract acceptance rows:

| Rows | Mode | Primitive-first sec | Prepared hit-stream + Triton sec | Hit-stream slowdown | Required |
| ---: | --- | ---: | ---: | ---: | ---: |
| 250000 | count | `0.000430` | `0.012945` | `30.138x` | `>= 10x` |
| 250000 | sum | `0.001913` | `0.257141` | `134.389x` | `>= 50x` |
| 1000000 | count | `0.000459` | `0.014525` | `31.617x` | `>= 10x` |
| 1000000 | sum | `0.002162` | `0.308346` | `142.648x` | `>= 50x` |

2M stress rows from the raw artifact:

| Rows | Mode | Primitive-first sec | Prepared hit-stream + Triton sec | Hit-stream slowdown | Old full-call speedup |
| ---: | --- | ---: | ---: | ---: | ---: |
| 2000000 | count | `0.000456` | `0.015960` | `34.962x` | `10148.444x` |
| 2000000 | sum | `0.002334` | `0.252584` | `108.213x` | `2435.365x` |

## Interpretation

This refresh keeps the v2.5 planner rule unchanged:

1. Use the fused generic RTDL primitive when it exactly expresses the requested
   grouped reduction.
2. Keep typed hit-stream plus partner continuation available for continuations
   that the fused primitive set cannot express.
3. Do not promote Triton merely to say Triton was used.
4. Keep v3.0 user-defined shader injection out of the v2.5 release lane.

The 2M rows reinforce the direction but are not part of the formal Goal2896
threshold gate, whose required rows remain `250000` and `1000000`.

## Boundary

Goal2965 is internal planning and stress evidence. It does not authorize:

- v2.5 release or release tag action;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app speedup wording;
- true zero-copy wording;
- package-install wording;
- Triton preview auto-selection;
- paper reproduction claims;
- app-specific native engine customization.
