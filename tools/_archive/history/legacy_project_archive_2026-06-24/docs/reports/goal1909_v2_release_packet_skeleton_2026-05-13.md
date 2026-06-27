# Goal1909 - v2 Release Packet Skeleton

Status: skeleton-blocked-consensus-and-policy-pending

Date: 2026-05-13

## Scope

Goal1909 is not a release packet. It is the current skeleton for the eventual
v2.0 release packet, showing which evidence slots are already populated and
which slots are still blocked.

## Current Populated Slots

| Slot | Status | Evidence |
| --- | --- | --- |
| Partner acceleration boundary wording | populated, needs final release consensus | Goal1900, Goal1907 |
| Public wording scan | populated, local gate passes | Goal1906 |
| Source-tree-only policy consensus | populated and accepted with boundary | Goals1902, 1907, 1943, 1944, 1945, 1947 |
| Pod evidence | populated with initial batch, repeat-3 fixed-radius, and robot/segment scale-up evidence | Goals1903, 1905, 1916, 1919, 1937, 1940 |
| Post-pod artifact review | populated with Claude/Gemini reviews, plus Goal1941/1942 Gemini follow-up reviews | Goals1912, 1923, 1935, 1936, 1938, 1941, 1942 |
| Local non-pod preflight | populated and passing | Goal1908 |
| All-app rollup | populated, needs final release consensus | Goal1931, Goal1942, Goal1946 |
| User-owned native continuation example | populated, not release speedup evidence | Goal1948 |
| Final v2.0 release review | partially populated, Claude still required for 3-AI consensus | Goal1950 Gemini review |

## Hard Missing Slots

| Slot | Missing artifact or action |
| --- | --- |
| Final v2.0 release consensus | Codex plus two distinct external AI reviews after all evidence exists |
| Final release action | tag/package/public wording action explicitly requested by the user |

## Evidence Boundaries Still Required In The Final Packet

| Topic | Required wording |
| --- | --- |
| Positive rows | Name the row families explicitly; do not claim every app has the same speedup shape. |
| Robot collision | Positive and exact-parity through 8,388,608 poses, but v1.8 remains subsecond, so not a seconds-scale whole-app claim. |
| Control rows | `database_analytics`, `graph_analytics`, `polygon_pair_overlap_area_rows`, and `polygon_set_jaccard` are evidence-only controls, not v2 partner speedup rows. |
| True zero-copy/direct pointer handoff | Bounded to selected OptiX partner input/output device-column contracts. |
| Package install | Blocked unless source-tree-only v2.0 receives final 3-AI consensus or packaging metadata is added and validated. |

## Non-Authorized Claims

Until the missing slots close, the following remain unauthorized:

- v2.0 release readiness;
- broad RT-core speedup;
- whole-application speedup;
- arbitrary PyTorch/CuPy acceleration;
- package-install support;
- unconstrained true zero-copy or direct-device-pointer claims.

## Current Commands

Local preflight:

```bash
PYTHONPATH=src:. python3 scripts/goal1908_v2_local_preflight.py
```

Optional additional RTX stress, if the team wants more robot scale evidence:

```bash
PYTHONPATH=src:. python3 scripts/goal1928_robot_collision_v2_partner_perf.py \
  --pose-count 16777216 --obstacle-count 16384 --partners cupy,torch --repeat 3 \
  --output docs/reports/goal1940_robot_segment_scaleup_pod/robot_16777216x16384.json
```

Post-pod acceptance:

```bash
PYTHONPATH=src:. python3 scripts/goal1905_v2_partner_pod_batch_acceptance.py
```

## Boundary

This skeleton exists to prevent release drift. It does not authorize v2.0 and
does not replace final 3-AI release consensus or the explicit user release
action.
