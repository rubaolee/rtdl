# Goal1116 Current-Source RTX Rerun Packet Report

Date: 2026-04-29

## Verdict

ACCEPT for pre-cloud preparation. Goal1116 creates a current-source RTX rerun
packet for the three engineering-ready primary apps: Facility, Robot, and
Barnes-Hut.

## Why This Was Needed

The older Goal1068 packet is now stale for current claim-review work: Facility
needs the recentered contract, and Barnes-Hut needs the corrected depth-8 /
radius-0.1 contract. Goal1116 avoids spending pod time on obsolete commands.

## Packet Rows

| App | Row | Contract |
|---|---|---|
| Facility | same-scale validation and timing | `facility_service_coverage_recentered`, 2.5M copies, radius 1.0 |
| Robot | correctness validation | prepared pose flags, 4,096 poses, 256 obstacles |
| Robot | large timing repeat | prepared pose-count summary, 8M poses, 4,096 obstacles, packed arrays |
| Barnes-Hut | correctness validation | node coverage, 4,096 bodies, depth 8, radius 0.1, threshold 4 |
| Barnes-Hut | large timing repeat | node coverage, 20M bodies, depth 8, radius 0.1, threshold 4 |

## Generated Artifacts

- `scripts/goal1116_current_source_rtx_rerun_packet.py`
- `scripts/goal1116_current_source_rtx_rerun_runner.sh`
- `tests/goal1116_current_source_rtx_rerun_packet_test.py`
- `docs/reports/goal1116_current_source_rtx_rerun_packet_2026-04-29.json`
- `docs/reports/goal1116_current_source_rtx_rerun_packet_2026-04-29.md`

## Boundary

This packet does not create cloud resources, does not run cloud locally, does
not authorize release, does not change public wording, and does not authorize
public RTX speedup claims. Outputs from this packet still require intake,
comparison, 2+ AI review, and public wording review.

## Verification

Command:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1116_current_source_rtx_rerun_packet_test -v
```

Result: 4 tests OK.

Command:

```text
PYTHONPATH=src:. python3 scripts/goal1116_current_source_rtx_rerun_packet.py
```

Result: `valid: true`.
