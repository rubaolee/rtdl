# External Technical Review: Phoenix V3 M60 Step-2 Set-A Selection

Date: 2026-06-23
Reviewer: Antigravity

## Verdict

`accept_m60_select_spatial_topology_stream_for_local_set_a_step2`

## Review Questions

**1. Is Spatial/RayJoin point-location topology stream a valid Set-A-shaped next target under Claude's Step-2 design?**
Yes. It provides multi-phase topology-stream work, which fits perfectly within Set-A's focus on residency-rich, continuation-heavy workloads. This contrasts with single-shot control rows like LibRTS.

**2. Does M60 correctly avoid RayJoin app-specific route tuning?**
Yes. M60 bounds the work strictly to generic topology-stream prepared-handle, internal residency, and full-M3 phase-accounting work. It explicitly forbids app-specific route tuning and prohibits promoting Spatial/RayJoin public wording.

**3. Is it correct to prioritize topology-stream prepared-handle/residency/full-M3 accounting over another LibRTS or Barnes-Hut cycle?**
Yes. LibRTS has been properly classified (via M59) as a Set-B yellow/open control limitation rather than a Step-2 optimization gap. Barnes-Hut is already focused-fix-covered pending validation (M45). Prioritizing Spatial/RayJoin addresses the clearest unresolved Set-A structural gap.

**4. Does the M3 device-resident internal delta support this as a V3 residency lever without becoming a V4/true-zero-copy claim?**
Yes. The reported internal route delta (2.282x speedup from default host-points wall to device-resident points wall) justifies this as a V3 residency lever. M60 clearly distinguishes between V3 (RTDL-owned internal device residency) and V4 (exposing external host-owned device buffers), properly restricting the work and explicitly forbidding true-zero-copy claims.

**5. Is M61 correctly limited to local no-POD gap-ledger/design/gate work?**
Yes. M60 explicitly limits M61 to reading existing productized surfaces, producing a machine-readable gap ledger, defining the reusable handle contract, tightening local gates to fail closed on route tuning, and explicitly defers any POD execution until a later reviewed packet.

**6. Does M60 preserve all non-authorization boundaries?**
Yes. M60 contains clear directives that ensure no unauthorized actions are taken, properly safeguarding against premature claims, releases, and execution.

**7. If rejecting, which Set-A family should be selected instead and why?**
N/A. The selection is accepted.

## Findings

- **P0**: None. The M60 selection correctly identifies a valid structural gap and establishes the correct technical boundaries for M61.
- **P1**: None. The decision accurately reflects the current status of LibRTS, Barnes-Hut, and Grouped Reduction.
- **P2**: None.

## Non-Authorization

This review strictly preserves all non-authorization constraints. It does NOT authorize:
- no V3 release
- no all-app benchmark
- no paid POD spend
- no focused POD spend
- no public speedup wording
- no broad V3-over-V2 claim
- no whole-app speedup claim
- no paper reproduction claim
- no V4
- no embedding
- no C ABI
- no true-zero-copy
- no watch-row closure
