I have all the inputs I need. Here is the verdict.

---

## External Technical Review: Phoenix V3 M60 Step-2 Set-A Selection

**Date:** 2026-06-23
**Reviewer role:** External (non-project)
**Verdict:**

```
accept_m60_select_spatial_topology_stream_for_local_set_a_step2
```

---

### Findings Summary

**P0 (blocking):** None.

**P1 (must track before M61 produces output rows):**

> **P1-A: The 2.282x device-resident delta must not appear as a public speedup row in any M61 output.**
> The M3 gap analysis is explicit that `RTDL OptiX < RayJoin author` on the same-stream contract. The internal delta is the difference between two RTDL-internal routing paths, not a V3-over-incumbent claim. Any gap-ledger document produced by M61 must label this delta `internal_routing_delta_not_public_row` and must not present it alongside the RayJoin author comparison in a way that implies RTDL beats RayJoin. M60's forbidden-shortcuts section addresses this, but the risk is material enough that M61 must re-assert the boundary at the start of its output.

> **P1-B: Claude M43 review debt is still open.**
> M44 records Claude review debt for grouped-reduction closure. M60 does not depend on this, but M61 should not be treated as a Step-2 second-family confirmation until that debt is cleared. Do not cite M43/M44 as fully triply-reviewed evidence in M61 materials.

**P2 (carry-forward, must not be lost):**

> **P2-A: OptiX cold single-shot Set-B row is yellow/open (P1 by Antigravity's read).**
> M59 3-AI consensus elevated this to the strictest carry-forward rule: the row needs an accepted user-language explanation or a separately reviewed runtime-overhead fix before any V3 release decision. M60 correctly defers this; it must appear explicitly in any future release scorecard.

> **P2-B: The `PreparedExecutionReport` required-phases vocabulary does not map to the M3 topology-stream phase table.**
> The runner requires: `prepare`, `cache_load`, `warmup`, `steady_state_stream`, `planner`, `executor`, `validation`. The M3 gap analysis requires: `static_scene_prepare_sec`, `query_stream_prepare_sec`, `device_transfer_or_residency_sec`, `rt_traversal_sec`, `topology_continuation_sec`, `host_return_or_scalar_materialization_sec`. These are not the same decomposition. M61's gap-ledger work must explicitly address how the full M3 phase table will be emitted — whether as additional notes fields on existing phases, or as a separate topology-stream-specific report wrapper — before any M3 evidence row can be treated as public-row-ready.

---

### Question Answers

**Q1. Is Spatial/RayJoin point-location topology stream a valid Set-A-shaped next target?**

Yes. The qualifying condition from M35 was "Revisit only if RayJoin becomes a multi-phase topology pipeline where the runner removes materialization or repeated planning." M60 does not assert that condition is already met — it asserts that M61's purpose is to determine whether and how the condition can be met via a reusable prepared handle and full phase table. That is the correct order of operations. The workload has the structural prerequisites (multi-phase, device-residency lever, continuation path) to qualify as Set-A-shaped once the missing M3 accounting exists.

**Q2. Does M60 correctly avoid RayJoin app-specific route tuning?**

Yes. The selection is framed as generic topology-stream prepared-handle work, not as "go improve Spatial/RayJoin performance." The M50 fail-closed gate enforces this at the code level: the POD runner requires the explicit reviewed token `M50_SPATIAL_TOPOLOGY_STREAM_M3_POD_AUTHORIZED`. The M60 forbidden-shortcuts list is comprehensive and correct.

**Q3. Is it correct to prioritize topology-stream prepared-handle/residency/full-M3 accounting over another LibRTS or Barnes-Hut cycle?**

Yes. LibRTS is a Set-B control row; M59 3-AI consensus correctly rules it out as the Step-2 trunk target. Barnes-Hut has a diagnosed root cause and a generic fix already reviewed with boundary under M24/M7; M45 correctly classifies it as focused-fix-covered pending full-suite validation, not active coding. Another coding cycle on either would not advance the Step-2 question: can the productized runner generalize across Set-A families? The topology-stream work directly tests that question with an identified residency lever.

**Q4. Does the M3 device-resident internal delta support this as a V3 residency lever without becoming a V4/true-zero-copy claim?**

Yes. The V3/V4 boundary is drawn correctly: RTDL-owned internal device residency between RTDL phases is V3; exposing external host-owned device buffers is V4. The 2.282x delta (0.274s → 0.120s on the large PIP route) is internal evidence of what the prepared handle could achieve if the missing M3 phase table is built. The `PreparedExecutionReport` dataclass enforces `true_zero_copy_claim_authorized: bool = False` as a hard constraint at construction time, so the code cannot accidentally generate an authorized claim.

**Q5. Is M61 correctly limited to local no-POD gap-ledger/design/gate work?**

Yes. The five allowed M61 actions in M60 are all read-local or design artifacts: read the existing surface, produce a machine-readable gap ledger, define the prepared-handle contract, tighten local gates, and defer any POD until a separate reviewed packet with exact command/token/stop rules. That is the right scope for the next milestone.

**Q6. Does M60 preserve all non-authorization boundaries?**

Yes. All thirteen listed non-authorization boundaries appear explicitly in M60's non-authorization section. The M50 fail-closed runner provides code-level enforcement for the POD-spend boundary. No language in M60 or the supporting packet set implies proximity to release, benchmark, or external claim authorization.

**Q7. If rejecting, which Set-A family instead?**

Not applicable; the selection is accepted.

---

### Rationale for Accept

The selection is technically disciplined. It converts a stale row-loss entry (M8's RayJoin regression) into a generic V3 engine task (reusable topology-stream prepared handle, full M3 phase accounting) without authorizing the shortcuts that have caused V3 progress to stall historically. The 2.282x device-resident internal delta provides a concrete motivation. The productized `run_point_location_topology_stream_prepared_session` runner already exists in `prepared_execution.py` at line 2048, so M61 starts from a real surface rather than a speculative one. All non-authorization boundaries are preserved. No blocking findings were identified.
