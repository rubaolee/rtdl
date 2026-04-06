# RTDL v0.2 External Review Packet

Date: 2026-04-06
Status: Gemini pending, Claude complete

## Purpose

This packet is the shortest clean handoff for obtaining the remaining literal
Gemini review artifact for the current RTDL v0.2 line.

It is intentionally limited to:

- Goals `107` through `123`
- the current v0.2 planning, workload, generate-only, and
  `segment_polygon_hitcount` performance line

## Current v0.2 context summary

Use this summary when briefing either model:

- v0.2 began after the archived `v0.1.0` baseline
- Goals `107` and `108` define the roadmap and workload scope
- Goal `109` archives v0.1
- Goal `110` closes the first new workload family:
  - `segment_polygon_hitcount`
- Goals `111` and `113` create and mature a narrow generate-only feature
- Goals `112`, `114`, `115`, `116`, `117`, `118`, `121`, `122`, and `123`
  build the correctness, productization, and performance story around
  `segment_polygon_hitcount`
- Goal `119` is the redesign-analysis step
- Goal `120` is an OptiX native-promotion attempt that improved architecture but
  not speed
- Goal `122` is the main CPU/Embree/Vulkan candidate-index performance win
- Goal `123` aligns OptiX with the same candidate-index strategy and restores
  competitive large-row Linux performance

Important honesty boundary:

- this line is strong on correctness and audited deterministic performance
- it does **not** claim full mature RT-core-native traversal for every backend

## Files to review

### Planning and archive layer

- [docs/goal_107_v0_2_roadmap_planning.md](../goal_107_v0_2_roadmap_planning.md)
- [docs/goal_108_v0_2_workload_scope_charter.md](../goal_108_v0_2_workload_scope_charter.md)
- [docs/goal_109_archive_v0_1_baseline.md](../goal_109_archive_v0_1_baseline.md)
- [docs/v0_2_roadmap.md](../v0_2_roadmap.md)
- [docs/v0_2_workload_scope_charter.md](../v0_2_workload_scope_charter.md)
- [docs/archive/v0_1/README.md](../archive/v0_1/README.md)

### Workload-family and generate-only layer

- [docs/goal_110_v0_2_segment_polygon_hitcount_closure.md](../goal_110_v0_2_segment_polygon_hitcount_closure.md)
- [docs/goal_111_v0_2_generate_only_mvp.md](../goal_111_v0_2_generate_only_mvp.md)
- [docs/goal_112_segment_polygon_performance_maturation.md](../goal_112_segment_polygon_performance_maturation.md)
- [docs/goal_113_generate_only_maturation.md](../goal_113_generate_only_maturation.md)
- [docs/goal_114_segment_polygon_postgis_large_scale_validation.md](../goal_114_segment_polygon_postgis_large_scale_validation.md)
- [docs/goal_115_segment_polygon_feature_productization.md](../goal_115_segment_polygon_feature_productization.md)

### Backend/performance redesign layer

- [docs/goal_116_segment_polygon_full_backend_audit.md](../goal_116_segment_polygon_full_backend_audit.md)
- [docs/goal_117_v0_2_feature_usage_surface.md](../goal_117_v0_2_feature_usage_surface.md)
- [docs/goal_118_segment_polygon_linux_large_perf.md](../goal_118_segment_polygon_linux_large_perf.md)
- [docs/goal_119_segment_polygon_native_maturity_redesign.md](../goal_119_segment_polygon_native_maturity_redesign.md)
- [docs/goal_120_optix_segment_polygon_native_promotion.md](../goal_120_optix_segment_polygon_native_promotion.md)
- [docs/goal_121_segment_polygon_bbox_prefilter.md](../goal_121_segment_polygon_bbox_prefilter.md)
- [docs/goal_122_segment_polygon_candidate_index_redesign.md](../goal_122_segment_polygon_candidate_index_redesign.md)
- [docs/goal_123_optix_candidate_index_alignment.md](../goal_123_optix_candidate_index_alignment.md)

### Current v0.2 reports

- [docs/reports/v0_2_current_status_2026-04-05.md](v0_2_current_status_2026-04-05.md)
- [docs/reports/v0_2_feature_status_2026-04-06.md](v0_2_feature_status_2026-04-06.md)
- [docs/reports/v0_2_so_far_report_2026-04-06.md](v0_2_so_far_report_2026-04-06.md)

## External review state

- Claude: complete
  - [goal107_123_package_review_claude_2026-04-06.md](goal107_123_package_review_claude_2026-04-06.md)
- Gemini: pending

## Gemini prompt

Use this exact prompt for Gemini:

```text
Review RTDL v0.2 Goals 107 through 123 as a package.

Your job is to audit:
1. technical honesty
2. process honesty
3. whether the claimed v0.2 progress is actually supported by the goal docs and reports
4. whether any goal overclaims native RT maturity, performance competitiveness, or review completeness

Please focus on the goal docs and reports listed in the supplied packet.

Output requirements:
- Start with a one-line verdict: APPROVE / APPROVE-WITH-NOTES / BLOCK
- Then list findings ordered by severity
- Each finding should name the goal number(s) involved
- If no blocking issue exists, say that explicitly
- End with one concise summary of what v0.2 has really achieved so far
```

## Claude prompt

Claude review is already complete, but the prompt is kept here for traceability
and possible reruns.

Use this exact prompt for Claude:

```text
Audit RTDL v0.2 Goals 107 through 123 as a single package.

Please review the supplied goal docs and reports for:
1. overclaiming
2. missing caveats
3. inconsistencies between planning docs and later technical reports
4. whether the segment_polygon_hitcount line is honestly described in terms of correctness, performance, and native RT maturity
5. whether the generate-only line is framed at the right narrow scope

Output requirements:
- Give a one-line verdict: ACCEPT / ACCEPT WITH NOTES / REJECT
- Provide findings first, ordered by severity
- Refer to goal numbers directly
- If the package is technically strong but still missing external-review closure, say that explicitly
- End with a short paragraph describing the real current state of v0.2
```

## Expected artifact naming

Suggested saved filenames:

- `history/ad_hoc_reviews/YYYY-MM-DD-gemini-review-v0_2-goals107-123.md`
- `history/ad_hoc_reviews/YYYY-MM-DD-claude-review-v0_2-goals107-123.md`

## Expected output schema

Ask both reviewers to return:

1. verdict line
2. findings
3. package-level summary

That makes later comparison and consensus easier.
