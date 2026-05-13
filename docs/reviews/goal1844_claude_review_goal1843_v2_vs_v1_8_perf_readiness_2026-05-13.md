# Goal1844: Claude External Review of Goal1843 v2.0-vs-v1.8 Performance Readiness

Date: 2026-05-13
Reviewer: Claude (independent external reviewer, distinct from Codex and Gemini)
Review type: read-only

## Scope

This review covers:

- `docs/reports/goal1843_v2_0_vs_v1_8_total_perf_readiness_2026-05-13.md`
- `docs/reports/goal1840_v2_0_progress_so_far_external_review_packet_2026-05-13.md`
- `docs/reviews/goal1841_gemini_review_v2_0_progress_so_far_2026-05-13.md`
- `docs/reports/goal1756_embree_same_surface_wall_clock_2026-05-12.md`
- `docs/reports/goal1750_same_contract_perf_summary_2026-05-12.md`
- `docs/reports/goal1838_optix_partner_owned_output_flags_zero_copy_2026-05-13.md`

No source files were edited.

---

## Question 1: Is Goal1843 accurate that the v1.8 baseline side is mostly ready, while the v2.0 app-level comparison side is not execution-ready yet?

**Verdict: `accept`**

The characterization is accurate and well-supported by the evidence inventory.

The v1.8 baseline side has concrete breadth:

- Goal1756 delivers a 16-row Embree same-surface app-wall-clock column across all
  active public apps, using the same CLI command for each row. The methodology
  notes are honest about workload limits (`polygon_set_jaccard` at `--copies 2000`,
  `robot_collision_screening` at `--pose-count 20000`), and the verdict correctly
  withholds public speedup wording.
- Goal1750 delivers 17 OptiX same-contract primary-ratio rows. The Embree
  same-contract side remains thin (one `database_analytics` row plus 14 recovered
  rows with documented classification problems), which Goal1843 correctly surfaces
  rather than papers over.

The v2.0 app-level comparison side is genuinely not execution-ready:

- No public app has been rewritten end-to-end as a v2.0 partner app.
- No v2.0 app-level timing harness exists.
- Goal1838 proves a single OptiX primitive slice (see Question 2 below); it is not
  an app-level row.

The phrase "plan-ready, not execution-ready" in Goal1843 correctly captures the
state. The seven required-work items are concrete and non-circular. Nothing in
the underlying reports contradicts this summary.

---

## Question 2: Is it correct to treat Goal1838 as a primitive-level OptiX partner zero-copy proof rather than an all-app v2.0 performance proof?

**Verdict: `accept`**

Goal1838 is precisely and only a primitive-level proof. The report, the pod
artifacts, and Gemini's Goal1841 review all agree on this boundary.

What Goal1838 proves:

- The OptiX prepared 2-D ray/triangle any-hit primitive reads partner-owned Torch
  and CuPy CUDA input columns and writes per-ray any-hit flags into a
  partner-owned CUDA output vector without RTDL-owned input or output staging
  buffers.
- Pod evidence on an NVIDIA RTX A4500 confirms `output_flags_true_zero_copy_observed:
  true` and `whole_primitive_true_zero_copy_authorized: true` for both partners,
  with `observed_flags: [1, 0]` matching expectations.

What Goal1838 does not prove:

- Both pod JSON artifacts carry `rt_core_speedup_claim_authorized: false` and
  `v2_0_release_authorized: false` explicitly.
- No app-level timing row exists. The validation path is a standalone script that
  allocates synthetic inputs, calls the primitive, and reads flags back only for
  assertion.
- No other OptiX primitive or Embree path has partner output zero-copy.
- OptiX GAS remains native acceleration state; the "no native state" claim would
  be false.

Treating Goal1838 as an all-app v2.0 performance proof would overstate the
evidence by several steps: app-level partner rewrites, a timing harness, and pod
wall-clock rows for public apps all remain unbuilt. Goal1843 correctly limits
Goal1838 to its actual scope.

---

## Question 3: Does the public app matrix classify all public apps without faking missing v2.0 partner rewrites?

**Verdict: `accept`**

The 18-row matrix in Goal1843 is honest. Verified against the evidence:

- Apps with no v2.0 partner work are uniformly described as "not rewritten for
  partner tensors", "not yet covered by Goal1838 any-hit slice", or "not yet
  covered beyond candidate discovery subphase". None of these cells claims a
  rewrite that does not exist.
- `apple_rt_demo` and `hiprt_ray_triangle_hitcount` are correctly marked as "not
  in active v2.0 scope" for both engines, which matches their appearance (or
  absence) in Goal1756 and Goal1750.
- `dbscan_clustering` is recorded as a "shared primitive alias" with "CPU control
  scope decision needed" and "not independently comparable until alias policy is
  fixed". This is the honest position; it does not claim a comparable app row.
- `segment_polygon_anyhit_rows` is listed as "closest current app to Goal1838;
  still needs app-level partner rewrite", which is accurate: Goal1838 proved the
  underlying primitive path, but the app adapter has not been written.
- `robot_collision_screening` is listed as a candidate "after partner output flags
  are lifted to app-level pose flags", correctly acknowledging that the current
  output-flags evidence is at the primitive flag level, not the app pose-flag
  level.

No app row in the matrix falsely claims an implemented v2.0 partner path.

---

## Question 4: Is `segment_polygon_anyhit_rows` a reasonable first app-level v2.0 partner adapter target?

**Verdict: `accept`**

The choice is reasonable and directly supported by the evidence chain.

Supporting factors:

- Goal1750 shows `segment_polygon_anyhit_rows` has a stable OptiX
  same-contract primary ratio (query_median 1.051x), confirming existing
  v1.8 baseline evidence is usable as a comparison anchor.
- Goal1756 provides the Embree same-surface app-wall row (0.943x), giving a
  CPU control column for the same app.
- The app's core operation is ray/segment-polygon any-hit: this is exactly the
  primitive that Goal1838 validated at the CUDA device-pointer level for both
  Torch and CuPy input columns and output flags.
- The any-hit output semantic (per-ray hit flag) is narrow enough that the path
  from primitive output flags to app-level selected-row output is a well-defined
  engineering step, not an open-ended design question.

Boundary to note: "reasonable first target" does not mean it is trivially close.
The app adapter still needs to be written, the v2.0 app timing harness needs to
exist, and a pod row with explicit cold/warm timing phases and parity verification
must be produced before this app generates release-eligible evidence. Goal1843
names all of these requirements.

No evidence in the reviewed documents suggests a better alternative first app;
the other any-hit/count candidates (`service_coverage_gaps`,
`event_hotspot_screening`, `road_hazard_screening`, `segment_polygon_hitcount`)
are equally or more distant from the current Goal1838 primitive proof.

---

## Question 5: Should v2.0-vs-v1.8 total performance conclusions remain blocked until pod evidence plus 3-AI consensus exists?

**Verdict: `accept`**

Blocking total performance conclusions is the correct and necessary position
given the current state of evidence.

Reasons:

1. **No app-level v2.0 timing rows exist.** A total v2.0-vs-v1.8 table cannot be
   assembled from one primitive-level zero-copy proof. Goal1843 correctly
   identifies that no all-app v2.0 partner timing harness exists and no public
   app has been rewritten.

2. **The local machine is not an accepted performance machine for OptiX claims.**
   Goal1843 notes that the local Linux GTX 1070 can smoke-test builds but is not
   the accepted platform for broad RT-core claims. NVIDIA pod evidence is required
   for OptiX performance rows that will support public wording.

3. **Remaining Goal1814/Goal1818 blockers are real.** Goal1841 (Gemini) lists
   six blockers from the strict birth gate; Goals 1836 and 1838 address only part
   of the "true zero-copy" blocker for one primitive. Broad RT-core speedup
   evidence, whole-application acceleration evidence, arbitrary partner
   acceleration scope, and the package-install release surface all remain
   unaddressed.

4. **External review gaps remain open.** Goal1836 still needs a valid external
   review (the Gemini stub was removed). Goal1838 is the subject of this review
   packet but has not yet had its dedicated external review accepted into
   consensus. Counting incomplete or blank stubs as consensus would undermine the
   3-AI gate.

5. **Codex and Gemini verdicts agree.** Goal1840 (Codex) and Goal1841 (Gemini)
   both give v2.0 release readiness `needs-more-evidence`. This review does not
   find grounds to diverge from that position.

Releasing or publishing total v2.0-vs-v1.8 performance conclusions before pod
evidence and 3-AI consensus would overstate what has been proved and would
contradict the explicit `v2_0_release_authorized: false` flags present in every
pod artifact reviewed.

---

## Overall Summary

| Question | Verdict |
| --- | --- |
| 1. v1.8 mostly ready; v2.0 app comparison not execution-ready | `accept` |
| 2. Goal1838 is primitive-level proof, not all-app proof | `accept` |
| 3. Public app matrix does not fake missing v2.0 rewrites | `accept` |
| 4. `segment_polygon_anyhit_rows` is a reasonable first adapter target | `accept` |
| 5. Total perf conclusions must remain blocked pending pod evidence + 3-AI consensus | `accept` |

No finding in this review authorizes v2.0 release, public speedup wording,
RT-core speedup claims, or relaxation of the Goal1814/Goal1818 strict birth gate.
