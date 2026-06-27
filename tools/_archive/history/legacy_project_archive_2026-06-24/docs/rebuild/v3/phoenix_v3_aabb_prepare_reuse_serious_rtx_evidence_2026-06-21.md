# Phoenix V3 AABB Prepare-Reuse Serious RTX Evidence

Status: `aabb_prepare_reuse_serious_rtx_evidence_not_m7_low_margin`.

This packet records a serious RTX run for the generic
`aabb_candidate_stream` prepare-reuse queue item. It does not promote a
new M7 row.

```text
release_authorized: false
public_speedup_claim_authorized: false
m7_promotion_authorized: false
M7 rows added by this packet: 0
```

## Hardware And Scale

- Host: `root@213.173.108.14 -p 11592`
- GPU: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.05`
- Compute capability: `8.9`
- RT hardware gate: `pass`
- Dataset: `jittered_grid`
- Indexed AABBs: `32768`
- Query AABBs: `32768`
- Warmup/repeat: `3` / `50`

## Phase Table

| Backend | Prepare s | Query total s | Collect s | Broadphase wall s | Cold+collect wall s |
| --- | ---: | ---: | ---: | ---: | ---: |
| `embree` | 0.332196 | 17.488089 | 0.083608 | 18.950513 | 19.034121 |
| `optix` | 0.532792 | 14.847732 | 0.083176 | 16.613295 | 16.696470 |

## Ratios

- OptiX / Embree prepare speedup: `0.624x`
- OptiX / Embree query-total speedup: `1.178x`
- OptiX / Embree broadphase-wall speedup: `1.141x`
- OptiX / Embree cold-plus-collect wall speedup: `1.140x`
- Material wall-speedup floor: `1.200x`

This serious RTX run is useful V3 engine evidence but not an M7 reopen candidate. Reusing the prepared AABB path moves the wall comparison from the earlier contact regression into a positive 1.140x cold-plus-collect wall result, but it is below the runner's 1.20 material-speedup floor. OptiX query work improves, while OptiX prepare is still slower than Embree.

## Next Engine Action

Keep AABB prepare-reuse in the Phoenix queue. The next valid work is generic engine tuning that either reduces OptiX prepare/query overhead or finds a reviewer-approved workload shape where repeated prepared reuse clears the material wall-speedup floor without app-specific native logic.

## Forbidden Shortcuts

- Do not promote this row to M7.
- Do not claim V3 AABB is faster from a 1.140x low-margin wall result.
- Do not quote the 1.178x query-total speedup as a release claim.
- Do not claim full contact solver speedup or broad V3-over-V2 speedup.
- Do not treat this as 2-AI reviewed evidence.

## Goal-Level Decision Audit

Decision: Record the serious AABB prepare-reuse RTX run as useful not-M7 evidence.

1. Was I foolish?
   No. The run used serious scale, RTX hardware, both backends, parity, phase accounting, and the predeclared material-speedup floor.
2. If yes, what actions made the decision foolish?
   The foolish action would be to round 1.140x up into a V3 win, quote query-only numbers, or ignore that OptiX prepare remains slower.
3. Was there another path that would have avoided getting stuck on that idea?
   Skip the run and keep the runner as a plan. That would preserve a clean story but would not answer whether prepare reuse materially fixes AABB.
4. Can I now try a different path that actually solves the problem?
   Use this low-margin evidence to drive engine-level overhead work or another reviewer-approved prepared-reuse shape before any M7 review.
