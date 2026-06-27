# Phoenix V3 AABB Prepare-Reuse Scale Evidence

Status: `aabb_prepare_reuse_scale_evidence_not_m7_scale_does_not_clear_floor`.

The AABB prepare-reuse scale check does not reopen M7. At 32,768 AABBs, OptiX/Embree cold-plus-collect wall speedup was 1.140x, below the 1.20 floor. At 65,536 AABBs, it fell to 1.087x. Query-total speedup stayed positive but also declined, and OptiX collect became slower at 65,536. Scaling the same prepared-session shape therefore does not solve the V3 material wall requirement.

```text
release_authorized: false
public_speedup_claim_authorized: false
m7_promotion_authorized: false
M7 rows added by this packet: 0
```

## Scale Rows

| AABBs | Repeat | Prepare | Query total | Collect | Cold+collect wall | Runner wall |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 32768 | 50 | 0.624x | 1.178x | 1.005x | 1.140x | 1.137x |
| 65536 | 50 | 0.742x | 1.109x | 0.906x | 1.087x | 1.084x |

Material wall-speedup floor: `1.200x`.

## Next Engine Action

Stop scale-shopping this row. The next valid AABB work is generic engine overhead reduction: reduce OptiX prepare cost, reduce repeated query overhead, improve collect/compaction cost, or find a separately justified contract shape before any new M7 review.

## Forbidden Shortcuts

- Do not promote either 32,768 or 65,536 prepare-reuse row to M7.
- Do not claim V3 AABB prepare-reuse is faster from sub-floor 1.140x or 1.087x wall ratios.
- Do not use query-total speedup without reporting cold-plus-collect wall.
- Do not keep increasing scale until a ratio crosses the floor without a contract rationale.
- Do not claim full contact solver or broad V3-over-V2 speedup.

## Goal-Level Decision Audit

Decision: Record the 65,536-row AABB prepare-reuse rerun as scale evidence that does not clear the M7 material floor.

1. Was I foolish?
   No. The rerun tested whether a serious larger scale amortizes the prepared AABB path enough to meet the predeclared floor.
2. If yes, what actions made the decision foolish?
   The foolish action would be to keep shopping scales or quote query-only wins after the 65,536-row wall result got worse.
3. Was there another path that would have avoided getting stuck on that idea?
   Skip the scale rerun and assume 32,768 was representative. That would leave a plausible but untested scale question open.
4. Can I now try a different path that actually solves the problem?
   Use this no-go scale packet to drive actual generic overhead work instead of more app-specific or scale-only experiments.
