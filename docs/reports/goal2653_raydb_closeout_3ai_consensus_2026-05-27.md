# Goal2653 RayDB Closeout 3-AI Consensus

Status: accepted for internal benchmark closeout. Public speedup wording remains
unauthorized.

## Reviewed Files

- `docs/reports/goal2653_raydb_benchmark_closeout_2026-05-27.md`
- `docs/reports/goal2652_raydb_10s_prepared_query_configs_2026-05-27.md`
- `docs/reports/goal2651_raydb_reusable_table_descriptor_2026-05-27.md`
- `docs/reports/goal2650_raydb_prepared_backend_split_2026-05-27.md`
- `examples/v2_0/research_benchmarks/raydb_style/README.md`
- `docs/application_catalog.md`
- `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`
- `scripts/goal2646_raydb_prepared_payload_perf_pod.py`
- `src/rtdsl/generic_primitives.py`
- `src/rtdsl/embree_runtime.py`
- `src/rtdsl/optix_runtime.py`

## External Review Files

- Claude:
  `docs/reports/goal2653_raydb_closeout_claude_review_2026-05-27.md`
- Gemini:
  `docs/reports/goal2653_raydb_closeout_gemini_review_2026-05-27.md`

Note: `docs/gemini_cli_notes.md` was not present in this checkout, so Gemini
was run from the repo root with a bounded review prompt and the saved output is
the evidence used here.

## Review Results

Codex verdict:

- Accept the RayDB closeout as an internal benchmark app result.
- The native engine remains app-agnostic for this path.
- The old Goal2520 partner-resident grouped-reduction path must remain
  historical supporting evidence, not the current RayDB RT-core claim.

Claude verdict:

- Accept with fixes.
- No blocking issues.
- Required README/documentation clarifications were to distinguish whole-run
  setup-included rows from prepared-query-only rows, label old Goal2527/2528
  fused-stats numbers as the old partner-resident backend, and acknowledge that
  Goal2652 supersedes Goal2651 for closeout wording.

Gemini verdict:

- Accept.
- No blocking or non-blocking issues reported.
- Gemini used the phrase "generated or repeated" in one summary bullet; this
  consensus narrows the accepted claim to the generated 2M fixture only, which
  matches the closeout report and Goal2652 artifacts.

## Fixes Applied After Review

- `examples/v2_0/research_benchmarks/raydb_style/README.md` now labels the
  1.427x/1.386x rows as setup-included whole-run timings and says not to compare
  them directly with Goal2652 prepared-query-only rows.
- `examples/v2_0/research_benchmarks/raydb_style/README.md` now labels the
  Goal2527/2528 fused-stats numbers as the old
  `optix_partner_resident_experimental` columnar payload backend, not the
  current paper-shaped `paper_rt_optix` path.
- `docs/reports/goal2653_raydb_benchmark_closeout_2026-05-27.md` now states
  that Goal2652 supersedes Goal2651 single-run prepared-query speedups for
  closeout wording.
- `docs/application_catalog.md` now uses `104.0x` precision consistently for
  the RayDB generated 2M grouped sum prepared-query row.
- `examples/v2_0/research_benchmarks/raydb_style/README.md` now says this is
  not a public or whole-app performance claim, leaving room for the accepted
  internal prepared-query claim.

## Accepted Internal Claim

The exact accepted internal claim is:

> For the generated 2M-row RayDB-style fixture, using the same app-owned
> paper-shaped lowering and the same generic RTDL grouped ray/triangle reduction
> contract, steady-state prepared OptiX RT queries on the RTX A5000 pod are
> 27.7x faster than prepared Embree queries for grouped count and 104.0x faster
> for grouped sum. This measures the prepared-query phase only; table descriptor
> construction, workload buffer build, scene/GAS build, payload preparation, and
> ray-batch preparation are excluded.

## Still Forbidden

- Public speedup wording.
- Whole-app RayDB speedup wording.
- Authors-code or RayDB paper result comparison.
- Crystal, PostgreSQL, DuckDB, cuDF, GPU database, or DBMS performance
  comparison.
- Full SSB reproduction claim.
- Package-install support claim.
- True zero-copy claim.
- Treating Torch/CuPy as the fair Embree-vs-OptiX comparison row.

## Consensus Decision

3-AI consensus accepts RayDB as closed for internal benchmark purposes with the
strict prepared-query boundary above. Any public release wording or broader
performance claim needs a separate review packet with exact claim text.
