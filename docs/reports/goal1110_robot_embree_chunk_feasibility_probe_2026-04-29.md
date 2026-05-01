# Goal1110 Robot Embree Chunk Feasibility Probe

Date: 2026-04-29

## Result

Status: BLOCKED FOR CURRENT 180-CHUNK RUNBOOK

The Goal1090 smoke test passed on Linux, but one real Goal1085 chunk did not finish within 12 minutes and was terminated. Running all 180 chunks under the current validated-per-chunk contract is not practical on the current Linux host.

## Host

- Host: `lx1`
- Checkout path: `/tmp/rtdl_goal1110_robot`
- Source commit: `b2c110a`
- Backend: Embree

## Smoke

Command:

```text
PYTHONPATH=src:. python3 scripts/goal839_robot_pose_count_baseline.py --backend embree --pose-count 1000 --obstacle-count 128 --iterations 1 --worker-count 1 --pose-id-start 1 --output-json build/goal1110_robot_embree_smoke.json
```

Result:

- status: `ok`
- correctness parity: `true`
- native any-hit query: `0.004184 s`
- backend scene prepare: `7.644148 s`
- oracle validation separate: `1.959556 s`

## Real Chunk Attempt

Command:

```text
RTDL_GOAL1085_START_CHUNK=0 RTDL_GOAL1085_END_CHUNK=0 RTDL_GOAL1085_SKIP_EXISTING=1 bash scripts/goal1085_robot_chunked_embree_baseline_runner.sh
```

Observation:

- The chunk launched 8 worker processes for CPU-oracle validation.
- The process was still running after `12:17.12`.
- Max RSS was about `567,848 KB`.
- The run was terminated with exit status `143`.
- No chunk artifact was written.

## Interpretation

The current Goal1085 runner validates every 200k-pose chunk by computing a full CPU oracle before running the Embree prepared kernel. That makes the baseline dominated by validation cost, not by the Embree RT query itself. Extrapolating from the terminated first chunk, the 180-chunk run would be impractical on this host.

## Next Move

Do not run all 180 chunks under the current contract.

Recommended remediation:

1. Add a timing-only robot Embree chunk mode that skips per-chunk CPU oracle after separate correctness validation has been established.
2. Keep a small or medium validation artifact with `matches_reference: true`.
3. Change the intake model to distinguish `validation_chunks` from `timing_chunks`.
4. Preserve the public-claim boundary: this would still be engineering baseline evidence only until 2+ AI review accepts the comparison boundary.

## Boundary

This probe does not authorize public RTX speedup claims. It records that the current robot non-cloud baseline runbook is too validation-heavy to complete efficiently.
