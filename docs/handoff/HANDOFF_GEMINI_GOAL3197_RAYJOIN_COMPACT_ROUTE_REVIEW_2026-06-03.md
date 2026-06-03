# Handoff: Gemini Review for Goal3197 RayJoin Compact Grouped-Count Route

Please perform an independent read-only Gemini review of Goal3197 at current
`main`.

Write the review to:

`docs/reviews/goal3198_gemini_review_goal3197_rayjoin_compact_grouped_count_route_2026-06-03.md`

Do not leave placeholder answer sections. Answer each question explicitly after
checking the files.

## Context

Goal3197 exposes the Goal3193 generic compact grouped-count device columns as an
app-facing reference route in the Spatial RayJoin benchmark app:

`prepared_optix_compact_grouped_count`

The route is LSI-only. It remaps left segment IDs densely in Python because the
generic grouped-count primitive uses direct-address key capacity. Native code
remains generic: segment-pair candidate columns plus compact grouped-count
columns.

Pod evidence:

`docs/reports/goal3197_rayjoin_compact_grouped_count_route_pod_2026-06-03.json`

It proves the fixture route executes and returns compact resident metadata. It
does not prove performance because the fixture has only one result row.

## Files To Review

- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `tests/goal3197_rayjoin_compact_grouped_count_route_test.py`
- `docs/reports/goal3197_rayjoin_compact_grouped_count_route_2026-06-03.md`
- `docs/reports/goal3197_rayjoin_compact_grouped_count_route_pod_2026-06-03.json`
- `docs/reports/goal3195_compact_grouped_count_timing_probe_2026-06-03.md`
- `docs/reports/goal3195_compact_grouped_count_timing_probe_2026-06-03.json`

## Suggested Validation

Run:

```powershell
$env:PYTHONPATH="src;."; py -3 -m unittest tests.goal3197_rayjoin_compact_grouped_count_route_test tests.goal3195_compact_grouped_count_timing_probe_test tests.goal3193_compact_grouped_count_device_columns_test
```

## Questions To Answer

1. Does Goal3197 keep native engine app-agnostic, with RayJoin interpretation and
   left-ID remapping staying in Python?
2. Is the route correctly scoped as LSI-only and app-facing, not a native
   RayJoin extension?
3. Does the route use the Goal3193 compact resident grouped-count columns
   correctly and preserve false claim flags?
4. Does the pod artifact prove only route correctness/metadata shape, not
   performance?
5. Is the relationship with Goal3195 timing evidence clear: Goal3195 is the
   internal timing probe; Goal3197 is the fixture route correctness proof?
6. What should be the next engineering step for this RayJoin/segment-pair lane?

## Required Verdict

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Expected likely verdict: `accept-with-boundary`.
