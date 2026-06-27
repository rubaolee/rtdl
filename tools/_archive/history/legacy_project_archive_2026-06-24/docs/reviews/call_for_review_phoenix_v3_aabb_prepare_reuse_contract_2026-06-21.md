# Call For Review: Phoenix V3 AABB Prepare-Reuse Contract

Please critically review the Phoenix V3 AABB prepare-reuse contract packet.

Primary files:

- `docs/rebuild/v3/phoenix_v3_aabb_prepare_reuse_contract_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_aabb_prepare_reuse_contract_2026-06-21.json`
- `examples/current/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py`
- `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.md`

Context:

- Phoenix V3 is not released.
- Current M7 count remains 8.
- This packet must add zero M7 rows.
- Existing AABB M7 remains only
  `aabb_candidate_stream_all_count_only_float32_32768`.
- Contact broadphase remains wall-slower on OptiX:
  `wall_optix_over_embree: 0.8029757821318222`.
- The intended improvement is contract visibility: the contact harness now
  emits generic `aabb_index_query_2d` prepared-session residency metadata with
  explicit cold/hot phases. It is not performance promotion.

Review questions:

1. Does the packet clearly avoid promoting contact manifold or AABB prepare
   reuse to M7?
2. Is the new prepared-session metadata generic enough, or does it leak
   contact-specific native-engine behavior?
3. Does the packet avoid broad V3-over-V2, full contact solver, paper,
   authors-code, automatic partner, and device interop claims?
4. Is the next POD evidence requirement specific enough to be actionable?
5. List any P0 blockers that must be fixed before this packet can be treated as
   a valid Phoenix queue advancement. Then list P1/P2 improvements.

Please give a verdict:

- `approve_queue_advancement`
- `approve_with_amendments`
- `reject_until_fixed`

Do not judge this as V3 release readiness. Judge only whether it is a valid
non-M7 Phoenix queue advancement.
