# External Review Handoff: Goal3575 RayDB Stats Mode

Date: 2026-06-06

## Task

Please independently review Goal3575, which turns grouped-i64 `stats` from
structural support into a real RayDB-style CPU + OptiX partner-resident
benchmark mode.

Write your review to one of these paths:

- Claude: `docs/reviews/goal3576_claude_review_goal3575_raydb_stats_mode_2026-06-06.md`
- Gemini: `docs/reviews/goal3577_gemini_review_goal3575_raydb_stats_mode_2026-06-06.md`

Use one allowed verdict only: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

## Primary Files

- `docs/reports/goal3575_raydb_stats_mode_partner_resident_2026-06-06.md`
- `docs/reports/goal3575_raydb_stats_mode_partner_resident_a5000/stats.json`
- `src/rtdsl/columnar_aggregate_reference.py`
- `src/rtdsl/grouped_reduction.py`
- `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`
- `examples/v2_0/research_benchmarks/raydb_style/README.md`
- `tests/goal3575_raydb_stats_mode_partner_resident_test.py`
- `tests/goal3575_raydb_stats_mode_partner_resident_a5000_test.py`

## Context

Goal3572 added native structural support for the grouped-i64 `stats` operation
through `device_column_grouped_i64_small_group_reduction_kernel`, but the
RayDB-style benchmark app did not expose a `stats` mode. Goal3575 closes that
gap for the generic columnar aggregate surface:

- CPU oracle supports `stats`;
- grouped-reduction metadata maps `stats` to `group_stats_i64`;
- RayDB-style CPU and OptiX partner-resident modes include `stats`;
- older paper-shaped RT modes intentionally do not include `stats` yet;
- A5000 artifact validates partner-resident `stats` parity.

Pod artifact highlights:

- backend: `optix_partner_resident_experimental`
- mode: `stats`
- row count: `960000`
- matches CPU reference: `true`
- native launch count: `1`
- generic stats ABI used: `true`
- fused native reduction: `true`
- query median sec: `0.000477436930`
- public speedup claim: `false`
- true zero-copy claim: `false`

## Review Questions

1. Is `stats` added to the correct generic surfaces without leaking RayDB,
   SQL, DBMS, or app-specific logic into the runtime/engine?
2. Is it correct that CPU and OptiX partner-resident modes support `stats`,
   while paper-shaped RT modes remain unchanged pending separate evidence?
3. Does the A5000 artifact prove correctness/parity for `stats` and support
   only internal engineering evidence?
4. Does the report avoid overclaiming release/public speedup/whole-app/RT-core/
   true-zero-copy/paper-reproduction/package-install claims?
5. Are any fixes required before Goal3575 can be internally closed?

## Boundary

This review does not authorize a release or public claim. It is an internal
benchmark-app/primitive-surface review only.
