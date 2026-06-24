# Call For Review: Phoenix V3 AABB Prepare-Reuse POD Runner

Please critically review the new Phoenix V3 AABB prepare-reuse POD runner and
its claim boundary.

Files to inspect:

- `scripts/v3_phoenix_aabb_prepare_reuse_pod_runner.py`
- `tests/v3_phoenix_aabb_prepare_reuse_pod_runner_test.py`
- `scripts/v3_phoenix_aabb_prepare_reuse_contract.py`
- `docs/rebuild/v3/phoenix_v3_aabb_prepare_reuse_contract_2026-06-21.md`
- `scripts/v3_phoenix_next_engine_work_queue.py`
- `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.md`
- `scripts/v3_release_wording_gate.py`

Context:

- Phoenix V3 is not release-ready.
- Current M7 row count remains 8.
- Broad V3-over-V2 speedup wording remains unauthorized.
- The AABB prepare-reuse queue item is still open.
- `192.168.1.20` is GTX 1070 and cannot be used as RT-core performance
  evidence.
- The old public pods are currently unavailable from this shell, so this patch
  stages the serious RTX runner rather than claiming fresh POD evidence.

What changed:

- Added `scripts/v3_phoenix_aabb_prepare_reuse_pod_runner.py`.
- The runner defaults to a serious fixture: 32,768 indexed AABBs and 32,768
  query AABBs, `jittered_grid`, warmup 3, repeat 50, Embree+OptiX, and
  `--require-rt-hardware`.
- It writes per-backend payloads, `environment.json`, `summary.json`, and
  `README.md`.
- It records prepare, query median/total, collect-k, broadphase wall,
  cold-plus-collect wall, and runner wall.
- It keeps `release_authorized`, `public_speedup_claim_authorized`, and
  `m7_promotion_authorized` false.
- It only becomes `aabb_prepare_reuse_pod_evidence_pending_2ai_not_m7` if the
  serious checks pass and OptiX has at least a 1.20x cold-plus-collect wall
  speedup over Embree.
- The wording gate now requires the runner path and
  `runner_available_not_yet_rt_pod_evidence`.

Verification already run locally:

- `py -3 -m unittest tests.v3_phoenix_aabb_prepare_reuse_contract_test tests.v3_phoenix_aabb_prepare_reuse_pod_runner_test tests.v3_phoenix_next_engine_work_queue_test tests.v3_phoenix_contact_manifold_broadphase_boundary_test tests.v3_release_wording_gate_test`
  passed 22 tests.
- `py -3 scripts\v3_release_wording_gate.py --pretty` passed.
- `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty` returned
  `blocked_not_release` with no failed checks.
- `py -3 scripts\run_test_matrix.py --group v3_rebuild` passed
  57 modules / 267 tests.

Review request:

1. Are there any P0 blockers where this runner could still mislead users into
   thinking AABB prepare-reuse is already M7-qualified or release-ready?
2. Is the 32,768/32,768 scale floor and 1.20x cold-plus-collect wall threshold
   adequate as a minimum gate before review, or should the runner require
   stronger defaults?
3. Does the runner prove generic engine work rather than Contact-specific app
   tuning?
4. What exact amendments should be required before this runner is used on a
   paid RTX pod or before any resulting evidence is considered for M7?

Please return a verdict: `approve`, `approve_with_amendments`, or `reject`,
with P0/P1/P2 findings.
