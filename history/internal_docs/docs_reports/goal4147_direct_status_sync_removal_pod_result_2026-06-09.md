# Goal4147 - Direct-Status Sync Removal Pod Result

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

Goal4147 measures the Goal4146 redundant-sync removal at 1M points, factor
`0.25`, using the same Goal4117 runner protocol as Goal4138.

## Artifact

`docs/reports/goal4147_direct_status_sync_removal_1m_factor025_pod.json`

Setup:

- Source commit: `c79e7358`
- Point count: 1,048,576
- Repeat: 2
- Warmup: 1
- Factor: `0.25`

## Result Compared With Goal4138

Ratio below is `Goal4138 baseline / Goal4147 sync-removal candidate`; values
above `1.0x` mean the sync-removal candidate is faster.

| Profile | Goal4138 replay (s) | Goal4147 replay (s) | Replay ratio | Goal4138 total (s) | Goal4147 total (s) | Total ratio |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| clustered3d | 5.755256 | 5.744946 | 1.002x | 7.001828 | 7.077291 | 0.989x |
| road3d | 5.210240 | 5.191624 | 1.004x | 5.956892 | 6.035678 | 0.987x |
| ngsim_dense | 1.252143 | 1.251027 | 1.001x | 2.176086 | 2.232526 | 0.975x |

All rows preserved component-size signature parity.

## Interpretation

Removing the redundant stream synchronize is a valid replay-path cleanup: replay
timing improves slightly for all three 1M profiles. The improvement is small
(`1.001x` to `1.004x`) and should not be marketed as a benchmark win.

One-shot total timing is not improved in this run because prepare timing varied
upward. Goal4147 therefore does not update the Goal4139 route table, does not
promote a one-shot route claim, and does not authorize public speedup wording.

## Boundary

This result keeps Goal4146 as a generic direct-status convergence-loop cleanup
only. It does not authorize release, public speedup wording, broad RT-core
wording, whole-app benchmark claims, paper reproduction, automatic dispatch,
automatic partner selection, automatic factor selection, app-specific engine
logic, native ABI additions, AMD claims, or true-zero-copy claims.
