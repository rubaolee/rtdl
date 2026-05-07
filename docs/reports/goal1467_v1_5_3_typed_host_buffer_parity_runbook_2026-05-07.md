# Goal1467 v1.5.3 Typed Host Buffer Backend Parity Runbook

## Verdict

Prepared the required Embree+OptiX parity runner and pod executor for the
v1.5.3 typed host input plus prepared host output path. This is a runbook and
tooling package only; backend parity is not yet accepted until the runner passes
on a real Embree+OptiX environment.

## Runner

- `scripts/goal1467_v1_5_3_typed_host_buffer_parity.py`
- `scripts/goal1467_v1_5_3_typed_host_buffer_pod_executor.sh`

## Required Pod Command

```bash
PYTHONPATH=src:. bash scripts/goal1467_v1_5_3_typed_host_buffer_pod_executor.sh
```

The pod executor builds OptiX, sets `RTDL_OPTIX_LIB`, and runs:

```bash
python3 scripts/goal1467_v1_5_3_typed_host_buffer_parity.py \
  --backends embree optix \
  --required-backends embree optix
```

## Acceptance Criteria

- Embree: pass=4, fail=0, skipped=0.
- OptiX: pass=4, fail=0, skipped=0.
- `accepted=true`.
- `skipped_required=[]`.

## Boundary

This runbook does not authorize true zero-copy wording, public speedup wording,
whole-app claims, stable primitive promotion, partner tensor handoff, or release
action.
