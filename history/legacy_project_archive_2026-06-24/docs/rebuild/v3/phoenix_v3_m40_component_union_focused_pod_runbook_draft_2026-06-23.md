# Phoenix V3 M40 Component-Union Focused POD Runbook Draft

Date: 2026-06-23

Status: `ready_after_m39_consensus_not_executed`

This runbook is ready after M39 Codex+Claude consensus. It authorizes exactly
one focused component-union POD run and does not authorize all-app POD, V3
release, or public speedup wording.

## Preconditions

All must be true before this runbook is used:

- M38 consensus remains in force:
  `docs/reviews/codex_claude_phoenix_v3_m38_component_union_focused_pod_protocol_2ai_consensus_2026-06-23.md`
- M39 harness review returns exactly
  `accept_m39_authorize_one_focused_component_union_pod`.
- M39 consensus is recorded at
  `docs/reviews/codex_claude_phoenix_v3_m39_component_union_harness_2ai_consensus_2026-06-23.md`.
- Local M39 gates are still green.
- Target machine passes `scripts/v3_optix_hardware_gate.py --require-rt-hardware`.
- The operator accepts the `2h / $0.50` hard cap.

## Command

```bash
PYTHONPATH=src:. python scripts/v3_phoenix_component_union_m38_pod_ab.py \
  --output-dir docs/rebuild/v3/evidence/phoenix_v3_component_union_m39_focused_pod_ab_$(date +%Y%m%d_%H%M%S) \
  --variant all \
  --dataset clustered3d \
  --point-count 262144 \
  --radius 3.0 \
  --min-neighbors 4 \
  --seed 20260623 \
  --warmup 1 \
  --repeat 5 \
  --heartbeat-sec 30 \
  --hard-cap-sec 7200 \
  --require-rt-hardware
```

## Interpretation

The run can count only as a focused component-union Set-A candidate if:

- all three variants complete;
- canonical component signatures match;
- the productized runner reports component-label outputs;
- `runtime_trunk_executes_end_to_end=true`;
- `component_union_phase_accounting_visible=true`;
- `component_signature_pass_executed=false`;
- runner vs Embree clears `1.20x` on both hot and wall metrics;
- runner vs legacy OptiX wall is at least `0.98x`.

If the hard cap trips, the result is blocked or negative evidence, not a speed
claim.

## Non-Authorization

This draft authorizes no V3 release, no all-app POD, no public speedup wording,
no broad V3-over-V2 wording, no true-zero-copy wording, no V4 work, no C ABI
work, and no embedding work.
