# Goal2064 All-App v2 Current Pod Evidence Audit

Date: 2026-05-15

Status: `accept-with-boundary`

## Purpose

Goal2064 refreshes the all-app v2 matrix after the current NVIDIA L4 pod evidence from Goals 2052 through 2062 and closes the last stale current-pod timing row.

This is an evidence/readiness audit. It is not v2.0 release authorization.

## New Current Pod Rerun

Artifact:

- `docs/reports/goal2064_segment_polygon_v2_partner_anyhit_cupy_l4_2048.json`

Command shape:

```bash
timeout 900 /root/rtdl_goal2046_venv/bin/python \
  scripts/goal1856_segment_polygon_v2_partner_perf.py \
  --count 2048 \
  --iterations 5 \
  --partners cupy \
  --output-capacity 4194304 \
  --source-commit-label 39efaf3d-pod-anyhit-2048
```

Result:

- status: `pass`
- strict row parity: `true`
- output capacity overflow check: `pass`
- v1.8 native OptiX median: `0.033606` seconds
- v2 partner-column any-hit median: `0.043524` seconds
- v2/v1.8 ratio: `1.295x`

Interpretation:

- The current pod row is now measured and correct.
- It is not a speedup. This row materializes witness rows, which is the weaker v2 shape compared with compact count/flag/threshold outputs.

## Refreshed All-App Matrix

Artifacts:

- `docs/reports/goal2064_all_app_v2_matrix_after_goal2062.json`
- `docs/reports/goal2064_all_app_v2_matrix_after_goal2062.md`

Current matrix summary:

- row count: `16`
- blockers: `[]`
- final pod batch needed: `false`
- pod-evidence-collected: `10`
- pod-evidence-collected-bounded: `4`
- pod-evidence-collected-mixed: `2`

The two mixed rows are:

- `segment_polygon_anyhit_rows`: current pod timing exists and parity passes, but v2 row materialization is slower than v1.8 native rows.
- `robot_collision_screening`: current pod timing exists and parity passes with zero-copy metadata, but v2 is slower than v1.8 prepared at the tested size.

## Public Claim Scan

Artifact:

- `docs/reports/goal2064_public_v2_claim_boundary_scan_after_current_pod.json`

Result:

- status: `pass`
- findings: `[]`
- v2.0 release authorized: `false`
- broad RT-core speedup authorized: `false`
- whole-app speedup authorized: `false`
- arbitrary partner-program acceleration authorized: `false`
- package-install claim authorized: `false`

## Readiness Aggregator

Artifact:

- `docs/reports/goal2064_v2_readiness_aggregator_after_current_pod.json`

Result:

- status: `blocked`
- pod evidence collected: `true`
- missing pod artifacts: `[]`
- missing supporting files: `[]`

Remaining blockers are process/release blockers:

- final Claude v2.0 release review missing;
- final v2.0 release consensus missing;
- explicit user-requested release action missing.

## Interpretation

This is a meaningful improvement over the prior state:

1. Every app row now has a current pod evidence classification.
2. No row remains in `needs-pod-timing` or `needs-current-pod-rerun`.
3. The audit honestly keeps mixed rows as mixed rather than converting them into speedup claims.
4. The public docs scan still blocks premature v2.0 wording.

## Boundary

Allowed claim:

- The current all-app v2 matrix has no missing pod-timing rows.
- v2.0 has strong positive evidence for compact fixed-radius and prepared count/flag rows.
- v2.0 has bounded evidence for authored RawKernel/control rows.
- v2.0 has mixed evidence for row-materializing any-hit and robot collision rows that still need optimization.

Not allowed:

- v2.0 release readiness;
- all apps have measured v2 speedup;
- whole-app speedup;
- broad RT-core speedup;
- arbitrary partner-program acceleration;
- package-install readiness.

## Verdict

`accept-with-boundary`
