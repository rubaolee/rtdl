# Claude Review: Goal3846 Stress Probe Candidates

Date: 2026-06-08

Reviewer: Claude (independent read-only review)

Scope reviewed:

- `docs/reports/goal3846_stress_probe_candidates_2026-06-08.md`
- `docs/reports/goal3846_stress_probe_candidates_a5000/*.json` and `*.stderr.txt`
- `docs/reports/goal3846_stress_probe_candidates_a5000/pod_goal3846_stress_probe.stdout.log`
- `tests/goal3846_stress_probe_candidates_test.py`
- Optional context: `docs/reports/goal3844_current_scale_profile_refresh_2026-06-08.md`,
  `docs/reports/goal3844_current_scale_profiles_refresh_a5000/outputs/librts_spatial_index_optix_scale_default_32768.stdout.json`

## Verdict

`accept-with-boundary`

This is internal A5000 stress-triage evidence for next-target selection, **not**
release authorization, **not** public speedup wording, and **not** paper
reproduction.

## Findings (ordered by severity)

### 1. (Medium) "Process observation" column mixes three different kinds of measurements

The results table's "Process observation" column is presented as a single,
comparable axis (paired against "App-reported hot metric"), but it actually
holds three different kinds of numbers across the four rows:

- `raydb_count_4m_repeat50` / `raydb_sum_4m_repeat50`: genuine whole-process
  wall time ("completed in ~11s / ~25s wall including setup/output"). I
  cross-checked these against `pod_goal3846_stress_probe.stdout.log`
  start/done timestamps (`01:18:10`→`01:18:21` = 11s; `01:18:21`→`01:18:46`
  = 25s) — the figures are correct and this is exactly the
  hot-metric-vs-wall-time distinction Review Question 1 asks about, done well.
- `librts_131k_repeat10`: an *intra-run summed metric* taken from the JSON's
  `repeat_protocol.query_sec_total` (6.463s), **not** the whole-process wall
  time. The pod log shows this probe's actual start-to-done wall was also
  ~11s (`01:18:46`→`01:18:57`), close to the `raydb_count` row's wall time —
  but the report cites the smaller in-app summed-query figure instead, so the
  comparison a reader would naturally draw between rows ("11s, 25s, 6.5s,
  ...") is not apples-to-apples.
- `triangle_native_8192_repeat5`: not a timing figure at all — it's a
  claim-boundary remark ("remains not an RT-core graph claim"). The actual
  measured wall here was ~2s per the pod log (`01:18:57`→`01:18:59`), and the
  app-reported hot metric (`query_raw_view_sec` = 0.826945s) is also available
  but the "process observation" cell reports neither.

None of the individual numbers are wrong — they are all traceable to the
underlying JSON/log evidence — but the column conflates "whole process wall,"
"in-app summed repeat total," and "qualitative boundary remark" under one
header. That weakens a clean answer to Review Question 1: the
hot-vs-wall-time distinction is made cleanly for the two RayDB rows, but is
blurred for the LibRTS and triangle rows.

**Suggested fix for a future revision:** either add a fourth column for
whole-process wall time (so all four rows report it uniformly, derived from
the pod log timestamps as already done for RayDB), or relabel the column to
make explicit which kind of number each cell holds.

### 2. (Low) Imprecise phrase: "0.646s median across the three operations"

The interpretation section says LibRTS "produces seconds-level hot work
(`0.646s` median across the three operations)". Looking at
`librts_131k_repeat10.json`, `0.6460927510634065` is
`repeat_protocol.query_sec_median` — the median, across the 10 measured
repeats, of the *summed* per-repeat time across all three query operations
(`run_phases.query_sec.point_contains` + `range_contains` +
`range_intersects` ≈ 0.1558 + 0.1650 + 0.3253 ≈ 0.646). It is not "the median
[value] across the three operations" — the median of those three
operation-level numbers would be ≈ 0.165s, a very different figure. The
phrase as written could lead a reader to think 0.646s represents a
single-operation cost rather than a per-repeat sum across all three
operations. This is a wording nit in the prose, not a data error — the JSON
and the table row above it ("`0.646093s median query`") are both correct.

### 3. (Informational) The LibRTS "plausible future target" claim is supported, and slightly understated

Comparing this probe's row (131,072 boxes/queries, `query_sec_median` ≈
0.646s) against the Goal3844 default-scale row at 32,768 boxes/queries
(`docs/reports/goal3844_current_scale_profiles_refresh_a5000/outputs/librts_spatial_index_optix_scale_default_32768.stdout.json`,
`query_sec_median` ≈ 0.0366s) shows roughly a 4× increase in problem size
producing roughly a 17.6× increase in median query time — clearly
super-linear growth in the generic AABB-index query path. That comparison is
stronger evidence for "LibRTS scale behavior is a plausible future
performance target" than the single absolute number the report leans on, and
the report could have cited it explicitly. This doesn't change the
conclusion — it would only have strengthened it.

## Answers to the review questions

1. **Does Goal3846 correctly distinguish hot app-reported metrics from whole
   process wall time?** Partially. The two RayDB rows do this cleanly and
   correctly (verified against the pod stdout log timestamps and the
   `timings.*` breakdown inside each JSON: `native_call_wall` ≈ 2.0ms / 25.6ms
   versus `workload_build` ≈ 1.67s / 10.46s versus measured wall ≈ 11s / 25s).
   The LibRTS and triangle rows blur the distinction — see Finding 1.

2. **Does the RayDB evidence support the conclusion that fused count/sum is
   not the next best primitive-runtime bottleneck?** Yes. At 4,194,304 rows
   with `matches_cpu_reference: true`, the app-reported hot metric is ~4.7ms
   (count) / ~28ms (sum), the `native_call_wall` phase is ~2.0ms / ~25.6ms,
   and the dominant costs are `workload_build` (~1.67s / ~10.46s) and
   `cold_prepare_total` (~2.38s / ~14.5s) — i.e., fixture/harness/setup, not
   the fused `RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D` primitive
   itself. The conclusion that the next engineering win here is harness
   accounting or full-pipeline work, not a missing primitive, is directly
   supported by these numbers.

3. **Does the LibRTS evidence support treating larger AABB-index scale
   behavior as a plausible future performance target?** Yes, and the case is
   actually a bit stronger than presented (see Finding 3): seconds-level
   `rt_core_accelerated: true` query cost at 131,072 boxes/queries, combined
   with clearly super-linear scaling versus the 32,768-scale default-profile
   row, is solid grounds to flag this as a next major-perf-target candidate.

4. **Does the triangle-counting stress row preserve the boundary that it is
   not an authorized RT-core graph-acceleration claim?** Yes, unambiguously.
   `section.rt_core_accelerated: false`,
   `section.optix_performance.class: "host_indexed_fallback"`,
   `section.ray_tracing_accelerated: false`, and
   `claim_boundary.triangle_count_rt_core_claim_authorized: false` are all
   present and consistent with the report's text ("remains a boundary row...
   reports `rt_core_accelerated=false`... a host-indexed/native summary
   correctness path").

5. **Are all release/public-speedup/paper-reproduction/auto-selection
   boundaries kept blocked?** Yes. Across all four artifacts:
   `rt_core_claim_authorized: false`, `public_speedup_claim_authorized: false`,
   `true_zero_copy_authorized: false`,
   `partner_continuation_required: false` /
   `promoted_performance_path: false` /
   `rt_core_speedup_claim_authorized: false` for the v2.5 partner-continuation
   previews, `paper_reproduction: false` for LibRTS and triangle counting (the
   RayDB rows use the descriptive, non-claiming label
   `paper_shaped_rt_prepared_grouped_reduction_optix` together with an
   explicit `claim_boundary` stating it is "not a public speedup claim"), and
   `automatic_partner_selection`/`app_specific_native_engine_logic` are not
   exercised anywhere in this packet. The report's top-level "Boundary"
   section restates all of this plainly. All stderr files for the four probes
   are empty (verified independently), and `rc=0` for all four per the pod
   log, so there is no hidden failure being glossed over.

## Boundary statement (if accepted)

This review treats Goal3846 as internal A5000 stress-triage evidence used to
decide where to point the next round of major performance engineering. It is
**not** release authorization, **not** public speedup wording, **not** paper
reproduction, and **not** an automatic partner/backend-selection claim. The
two issues noted above (Findings 1 and 2) are presentation/labeling nits in
the human-readable report; they do not change the underlying JSON evidence or
the engineering-direction conclusions, and do not require re-running the pod
probes.
