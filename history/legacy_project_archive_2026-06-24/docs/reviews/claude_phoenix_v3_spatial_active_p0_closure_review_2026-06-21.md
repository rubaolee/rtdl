# Claude External Review: Phoenix V3 Spatial Active-P0 Closure Decision

Reviewer: Claude (claude-sonnet-4-6), acting as independent external reviewer.
Date: 2026-06-21
This review does not authorize release, M7 promotion, broad V3-over-V2 speedup,
RTDL-beats-RayJoin, true-zero-copy, RayJoin-paper, or whole Spatial RayJoin wording.

---

## verdict

`close-active-p0`

---

## rationale

The evidence record is honest and complete: the exact-f64 device scalar-count repair is
real internal generic-engine progress (3.680x improvement in RTDL prepared-query median
vs the prior RTDL exact executor, exact parity at 47,262 rows, adverse-subset parity
closed, host topology-continuation eliminated). However, RayJoin author Query remains
3.382x faster than the current RTDL exact-f64 prepared-query median on the same dataset
(1.866 ms vs 6.309 ms), author result count is not printed so count parity is unverified
on that run, external AI review has been blocked twice with no real verdict produced, and
no Codex consensus after external review exists. The remaining prepared-query cost is
dominated by the device-side exact closed-shape predicate evaluating 155,555 AABB
candidates (99.663% of prepared-query median); reducing that by 3.4x is a real
engineering task with no guaranteed timeline and no guarantee it reaches the author
timer. Keeping this item P0-active indefinitely serves no user-facing purpose: it adds
zero M7 rows, it cannot close the release-readiness blocker without either beating the
author timer or an explicit reviewer acceptance of a weaker scope, and the external
review gate is deadlocked. Closure to future-research status, with strict machine-readable
reopen conditions, is the honest position. It matches the current M7 classification
packet, which already classifies all three Spatial rows as `not_m7_qualified` with
leading blocker `rayjoin_author_rt_faster_than_rtdl_optix`.

---

## must_record_if_closed

- Exact internal delta: RTDL exact-f64 prepared-query median `6.309319 ms`, 3.680x
  faster than prior RTDL exact executor (`23.217812 ms`); this is RTDL-vs-RTDL only,
  not RTDL-vs-RayJoin-author.
- Author timing gap: RayJoin author Query `1.865660 ms` is `3.382x` faster than RTDL
  exact-f64 prepared-query median on the same br_county.cdb dataset; RTDL does NOT beat
  RayJoin author.
- Author result count not printed: count parity on the same-dataset author run is
  unverified; `RTDL-beats-RayJoin` and `author-count-parity` claims remain false.
- Exact public-county row count: `47,262` (exact-f64 route, repeat50/sample5 RTX 4000
  Ada, stable).
- Adverse-subset parity: br_county_subset row_count `6`, exact-f64 route, closes only
  the adverse-subset parity blocker.
- No-go record retained: relation-status corrected executor failed at `47,259 != 47,262`
  (-3); that route remains a correctness blocker and must not be promoted.
- Bottleneck recorded: topology/exact refinement (device-side closed-shape predicate over
  AABB candidates) is `52.893x` RT traversal/candidate-emission median and accounts for
  `99.663%` of exact-f64 prepared-query median; RT traversal itself is fast.
- AABB candidate funnel: `155,555` raw candidates → `47,550` boundary-status candidates
  → `47,262` emitted exact; the device predicate evaluates all 155,555 candidates.
- External review attempts: Claude and Gemini both produced no real AI verdict on the
  exact-f64 intake; blocked records exist and must not be mistaken for approval.
- All claim flags remain false at closure: `release_authorized`, `public_speedup_claim_authorized`,
  `broad_v3_over_v2_claim_authorized`, `rtdl_beats_rayjoin_claim_authorized`,
  `true_zero_copy_claim_authorized`, `m7_promotion_authorized` all `false`.
- Reopen condition (exact): closure is reopened only after (a) a fresh POD run on the
  same br_county.cdb public-county dataset produces RTDL prepared-query median at or
  below the same-dataset RayJoin author Query timer (`1.865660 ms`), with verified count
  parity and a full M3 phase table, OR (b) a real external AI reviewer explicitly accepts
  a weaker scope (e.g., "RTDL topology-stream within Nx of RayJoin author") with stated
  rationale and Codex consensus response.
- Closure does not foreclose: future Spatial work is still possible; it becomes
  future-research, the same status as Barnes-Hut vector accumulation.

---

## must_do_if_kept_active

(Not applicable given verdict `close-active-p0`. Provided for completeness in case
Codex disagrees and keeps active.)

- Do not count "kept active" as forward progress; the queue being open is a release
  blocker, not an evidence milestone.
- The single next generic-engine optimization must target the device-side AABB candidate
  predicate cost: reduce the 155,555-candidate exact evaluation to fewer candidates
  before the closed-shape predicate fires. Concretely: tighten the RT-side candidate
  emission so that fewer non-interior candidates reach the exact device predicate (target:
  raw AABB candidate count approaching the boundary-status count of `47,550`, or a
  cheaper per-candidate predicate that maintains exactness).
- Evidence bar to reopen M7: fresh POD run (repeat50/sample5, same RTX 4000 Ada,
  br_county.cdb public county) with RTDL prepared-query median at or below `1.865660 ms`,
  count stable at `47,262`, full M3 phase table, and same-dataset author timing re-run
  in the same packet.
- Do not claim the optimization is complete until a real external AI review produces an
  explicit approve/block verdict; the existing Gemini CLI stderr is not a verdict.
- Route-name must be updated from `relation_status_corrected` to reflect exact-f64 device
  predicate semantics before any M7 discussion.

---

## claim_boundary_risks

- **3.680x misread as beating RayJoin**: The exact-f64 internal delta (3.680x) is
  RTDL-vs-prior-RTDL only. It is not a RayJoin author comparison. Any wording that
  omits "vs prior RTDL exact executor" would be a false claim.
- **Runner-wall ratio (3.426x RTDL faster) misread as public evidence**: RTDL runner
  wall (`1.975 s`) vs RayJoin wrapper elapsed (`6.765 s`) is not a same-contract
  public comparison; wrapper overhead is apples-to-oranges. This ratio must not appear
  in any public wording.
- **Adverse-subset parity misread as release evidence**: The br_county_subset 6-row pass
  closes a correctness blocker only. It does not demonstrate scale, performance, or
  author-parity; using it as evidence for M7 or release would be an overclaim.
- **"Strong internal candidate" language misread as near-M7**: The work queue and M7
  classification already use "strong internal evidence" language. At closure, this must
  be paired with explicit disclosure that RayJoin author is 3.382x faster and no M7 row
  exists; omitting the gap creates a misleading internal story.
- **Device-resident internal delta misread as true zero-copy**: The M3 gap analysis and
  work queue both prohibit calling the device-resident query-stream path "true zero-copy."
  Closure records must repeat this prohibition explicitly.
- **Topology-continuation bottleneck misread as "almost solved"**: The host topology
  continuation is now zero (device path), but the device-side exact predicate is 99.663%
  of prepared-query time. This is the new bottleneck, not a solved one.
- **No-go record (47,259) omission risk**: If the closure summary omits the failed
  relation-status corrected executor, a future reader might attempt to use the faster
  non-exact route without knowing it failed exactness. The -3 mismatch record must
  survive the closure.
- **V3 release readiness misread from queue closure**: Closing Spatial from active P0
  to future-research removes one release blocker (open generic-engine queue), but does
  NOT authorize release. All other V3 P0 blockers remain.

---

## recommended_next_action

Close `spatial_rayjoin_topology_stream_author_gap` to future-research in the next
`phoenix_v3_next_generic_engine_work_queue` update. The machine-readable closure record
must include every item in `must_record_if_closed` above, with the reopen condition
stated as a numeric threshold (`RTDL prepared-query median <= 1.865660 ms, same dataset,
count 47,262 stable`) rather than qualitative language. After closure, Codex should
record a consensus response that confirms the active queue is now empty, updates the
V3 release readiness blockers document to reflect the generic-engine queue as closed,
and explicitly confirms that closure does not authorize release, M7 promotion, or any
RTDL-beats-RayJoin wording. The remaining V3 release path is then a narrow eleven-row
bounded performance surface: work should shift to packaging, docs review, second-machine
RT confirmation, and the outstanding P0 release-authorization blockers, rather than
continued Spatial topology-stream optimization in the current release cycle.
