# Call For Review: Phoenix V3 AABB Query-Cache Evidence

Please critically review this Phoenix V3 AABB query-cache evidence and the
decision to keep it out of M7.

Project context:

- Phoenix V3 is rebuilding RTDL as a user-responsible Python-hosted RTDL
  language surface, not as app-specific benchmark tuning.
- V4, C ABI, embedding, SDK, and external zero-copy interop are out of this
  V3 goal.
- A new Phoenix V3 performance row must be reusable, row-scoped, correct,
  phase/wall measured, provenance-backed, and materially faster. A 1.01x-style
  or sub-floor result cannot qualify.

Files to review:

- `src/rtdsl/aabb_index.py`
- `examples/current/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py`
- `scripts/v3_phoenix_aabb_prepare_reuse_pod_runner.py`
- `scripts/v3_phoenix_aabb_query_cache_evidence.py`
- `scripts/v3_phoenix_next_engine_work_queue.py`
- `scripts/v3_release_wording_gate.py`
- `docs/rebuild/v3/phoenix_v3_aabb_prepare_reuse_query_cache_evidence_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_aabb_prepare_reuse_query_cache_evidence_2026-06-21.json`
- `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.md`
- `docs/rebuild/v3/README.md`
- `docs/reports/phoenix_v3_status_and_next_steps_2026-06-21.md`

Implementation summary:

- Added prepared query-record caches to `OptixAabbIndex2D` and
  `EmbreeAabbIndex2D`.
- This is not native result caching. Each query still calls the native
  collector.
- The cache avoids rebuilding the same normalized query records across repeated
  prepared-session windows.
- Contact Manifold evidence now surfaces `prepared_query_cache_stats` in the
  final payload, so the POD summaries can prove the cache actually hit.
- The query-cache evidence packet and work queue classify the result as useful
  generic cleanup, not as M7 or release evidence.

POD evidence:

- `docs/rebuild/v3/evidence/phoenix_v3_aabb_prepare_reuse_query_cache_stats_32768_r50_20260621/`
- `docs/rebuild/v3/evidence/phoenix_v3_aabb_prepare_reuse_query_cache_stats_65536_r50_20260621/`

Observed result:

- Both serious rows show one range-intersection cache entry, one miss, and 52
  hits per backend.
- 32,768 indexed/query AABBs: `1.188x` OptiX/Embree cold-plus-collect wall.
- 65,536 indexed/query AABBs: `1.135x` OptiX/Embree cold-plus-collect wall.
- Material wall-speedup floor: `1.200x`.
- Query-total speedup is positive but explicitly forbidden as public V3 success
  while cold-plus-collect wall is below the floor.
- M7 rows added: 0.

Verification:

- `C:\Python311\python.exe -m unittest tests.v3_phoenix_aabb_query_cache_evidence_test tests.v3_phoenix_aabb_prepared_query_cache_test tests.v3_phoenix_aabb_prepare_reuse_pod_runner_test`:
  12 tests passed.
- `C:\Python311\python.exe -m unittest tests.v3_phoenix_next_engine_work_queue_test tests.v3_phoenix_aabb_query_cache_evidence_test`:
  10 tests passed.
- `C:\Python311\python.exe -m unittest tests.v3_release_wording_gate_test tests.v3_phoenix_next_engine_work_queue_test tests.v3_phoenix_aabb_query_cache_evidence_test tests.v3_phoenix_aabb_prepared_query_cache_test tests.v3_phoenix_aabb_prepare_reuse_pod_runner_test tests.v3_phoenix_release_readiness_gate_test`:
  23 tests passed.
- `C:\Python311\python.exe scripts\v3_release_wording_gate.py --pretty`:
  pass, no violations, no missing required strings.
- `C:\Python311\python.exe scripts\v3_phoenix_release_readiness_gate.py --pretty`:
  `blocked_not_release`, `failed_checks: []`.
- `C:\Python311\python.exe scripts\run_test_matrix.py --group v3_rebuild`:
  73 modules / 350 tests passed.

Questions:

1. Is the no-go interpretation correct, or does any evidence justify reopening
   M7 now?
2. Is this still a V3 generic-engine optimization rather than app-specific
   Contact Manifold tuning?
3. Are the release wording gate and work queue strong enough to prevent users
   from reading `1.188x`, `1.135x`, or query-total speedup as a public V3 win?
4. Is the proposed next path correct: native packed-query buffer reuse, OptiX
   prepare-cost reduction, and collect/compaction overhead reduction?
5. What concrete P0/P1 fixes would you require before this AABB route can be
   reconsidered?

Please answer with:

- Verdict: approve no-go / approve with required fixes / reject no-go.
- P0 issues.
- P1 issues.
- Concrete next engineering actions.
- Any wording that must be changed before users see this result.
