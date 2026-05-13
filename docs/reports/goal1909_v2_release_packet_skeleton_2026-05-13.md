# Goal1909 - v2 Release Packet Skeleton

Status: skeleton-blocked-pod-and-consensus-pending

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
| Source-tree-only policy proposal | populated, needs final 3-AI consensus | Goal1902, Goal1907 |
| Pod batch packet | populated before hardware | Goal1903, Goal1904 |
| Post-pod artifact validator | populated before hardware | Goal1905 |
| Local non-pod preflight | populated and passing | Goal1908 |

## Hard Missing Slots

| Slot | Missing artifact or action |
| --- | --- |
| RTX pod batch execution | `docs/reports/goal1903_fixed_radius_batch_pod.json`, `goal1903_segment_polygon_batch_pod_512.json`, `goal1903_segment_polygon_batch_pod_2048.json`, `goal1889_road_hazard_prepared_reuse_pod_512.json`, `goal1889_road_hazard_prepared_reuse_pod_2048.json`, and `goal1903_v2_partner_pod_batch_summary.json` |
| Post-pod acceptance | strict `PYTHONPATH=src:. python3 scripts/goal1905_v2_partner_pod_batch_acceptance.py` pass |
| Fresh external artifact review | Claude or Pro-class review after actual pod artifacts land |
| Source-tree-only release exception consensus | final 3-AI consensus accepting source-tree-only v2.0, or validated packaging metadata instead |
| Final v2.0 release consensus | Codex plus two distinct external AI reviews after all evidence exists |
| Final release action | tag/package/public wording action explicitly requested by the user |

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

RTX pod batch:

```bash
OUT_DIR=docs/reports/goal1903_v2_partner_pod_batch \
OPTIX_PREFIX=/root/vendor/optix-sdk \
bash scripts/goal1903_v2_partner_pod_batch_runner.sh
```

Post-pod acceptance:

```bash
PYTHONPATH=src:. python3 scripts/goal1905_v2_partner_pod_batch_acceptance.py
```

## Boundary

This skeleton exists to prevent release drift. It does not authorize v2.0,
does not replace pod execution, and does not replace final 3-AI release
consensus.
