# Goal3522: v2.8 Internal Closeout Packet

Date: 2026-06-05

Status: closeout packet for external review; not public release authorization.

## Verdict Requested

`accept-with-boundary`

This packet asks reviewers to decide whether RTDL v2.8 can be closed as an
internal version. It does not ask for a public release, package-install promise,
broad speedup claim, broad RT-core claim, true zero-copy claim, full paper
reproduction claim, hidden partner selection, or app-specific native-engine
authorization.

## Closeout Evidence Chain

| Goal | Artifact | Result |
| --- | --- | --- |
| Goal3512/3515 | `docs/reports/goal3512_v2_8_closeout_goal_sequence_and_consensus_plan_2026-06-05.md`, `docs/reports/goal3515_v2_8_closeout_goal_sequence_3ai_consensus_2026-06-05.md` | 3-AI accepted the closeout order: evidence bookkeeping, prepared execution, matrix, docs, claim audit, validation, closeout. |
| Goal3516 | `docs/reports/goal3516_v2_8_evidence_bookkeeping_closure_2026-06-05.md` | Closed Goal3507/3509/3511 evidence bookkeeping and review intake. |
| Goal3517 | `docs/reports/goal3517_prepared_execution_user_pattern_2026-06-05.md` | Defined the v2.8 prepared-execution pattern: prepare, pack/cache, warm, steady-state run, explain timings. |
| Goal3518 | `docs/reports/goal3518_v2_8_benchmark_matrix_refresh_2026-06-05.md` | Refreshed all 10 benchmark apps into a 12-row matrix with no bare `n/a` cells. |
| Goal3519 | `docs/reports/goal3519_v2_8_learner_docs_cleanup_audit_2026-06-05.md` | Cleaned active learner docs and research benchmark docs to tell a single v2.8-current story. |
| Goal3520 | `docs/reports/goal3520_v2_8_claim_boundary_and_stale_doc_audit_2026-06-05.md` | Audited stale docs/claims, patched user-facing stale version strings, and added fail-closed claim-boundary tests. |
| Goal3521 | `docs/reports/goal3521_v2_8_final_validation_packet_2026-06-05.md` | Ran focused local gate and targeted RTX A5000 pod validation at commit `9ad59f1e7abbe0b2a97e785b28f7358aaa14d6c8`. |

## Current Position

v2.8 is an internal prepared-execution closeout. The design story is now:

1. The engine stays app-agnostic and primitive-first.
2. Users choose partners explicitly; no automatic Triton/CuPy/Numba/Torch
   selection is hidden in the runtime.
3. Performance-sensitive apps should expose setup, cache load, warmup,
   steady-state primitive time, partner continuation time, and validation time
   separately.
4. Benchmark apps are reference implementations and evidence sources, not
   release-speedup marketing claims.
5. Historical version details are in history/reports; active learner docs teach
   the current v2.8 source-tree surface.

## Benchmark Matrix Summary

Goal3518 is the matrix source of truth. It covers all 10 promoted benchmark apps
with 12 rows:

- Primitive-only: Hausdorff promoted RT-core path, contact manifold, RayDB count
  and sum primitive-first rows, triangle counting.
- Partner-needed: RT-DBSCAN grouped-stream components, Barnes-Hut vector sum.
- Prepared-execution-needed: Spatial RayJoin count/parity and exact overlay
  area, robot collision, librts spatial index, RTNN ranked summary.

Key final validation refreshes from Goal3521:

| App row | Evidence |
| --- | --- |
| Robot collision | RTX A5000 OptiX prepared tail median `0.0353194466s`; CPU reference tail median `3.4537386205s`; prepared scene reused; public speedup claims remain blocked. |
| Contact manifold | OptiX AABB discovery over `grid_4096` matches CPU reference; phase split: scene build `0.573764368s`, RT traversal median `0.027931150s`, exact app refinement `0.009864520s`, materialization `0.010725705s`. |
| RT-DBSCAN | Grouped stream passes at 32K/65K/131K; speedup versus prepared CuPy grid is `4.080x`, `4.691x`, `4.897x`; signatures match; paper and broad-speedup claims remain blocked. |
| Spatial RayJoin overlay | Public-CDB read-mode steady state: active relation device columns `0.003779787s`, cache load `0.175631035s`, planner `0.236281021s`, tile executor `0.057250103s`, exact area error `9.23e-09`; RayJoin reproduction and rtdl-beats-RayJoin claims remain blocked. |

## Local Gate

Goal3521 focused local validation:

```text
Ran 112 tests in 0.314s
OK (skipped=5)
```

Goal3521 packet guard plus docs/claim/matrix tests:

```text
Ran 16 tests in 0.135s
OK
```

## Public Claim Boundary

The following remain blocked:

- public v2.8 release authorization;
- package-install / PyPI-style promise;
- public speedup wording;
- broad RT-core speedup wording;
- true zero-copy wording;
- full RayJoin paper reproduction;
- RTDL beats RayJoin wording;
- full overlay geometry/output claim;
- hidden partner selection;
- app-specific native-engine behavior.

This is important: v2.8 has strong internal benchmark evidence, but it remains
an internal closeout unless the user explicitly asks for a separate public
release packet.

## Known Boundaries

- Robot collision and contact manifold now have fresh RTX validation rows, but
  they remain benchmark evidence, not public speedup claims.
- The Goal3521 robot pod row used OptiX in a clean checkout and recorded an
  Embree row error because no Embree library was configured on that pod. This
  does not invalidate the targeted RTX evidence; Embree evidence remains from
  earlier accepted local/legacy rows.
- Spatial RayJoin overlay still proves exact area for the scoped public-CDB
  route, not full RayJoin paper reproduction or full general polygon overlay.
- Legacy `v2_5` / `v2_6` helper/protocol names remain quarantined Python
  compatibility debt and are recorded in
  `docs/research/future_version_to_do_list.md`.
- v3.0-style device-residency across arbitrary partner composition and
  user-defined shader injection remains future work.

## Requested External Review

Reviewers should inspect:

- this packet;
- Goal3518 benchmark matrix;
- Goal3519 learner docs cleanup;
- Goal3520 claim-boundary audit and 3-AI consensus;
- Goal3521 final validation packet and test;
- representative artifacts under `docs/reports/goal3521_pod_artifacts/`.

Review questions:

1. Is v2.8 ready to close as an internal version?
2. Does the packet preserve the app-agnostic engine boundary?
3. Does it keep partner choice explicit and avoid hidden dispatch?
4. Are setup/cache/warmup/steady-state/continuation/validation phases separated
   clearly enough?
5. Are the benchmark claims correctly bounded?
6. Is any public release or speedup wording accidentally authorized?
7. Are any blockers left before writing the final 3-AI closeout consensus?

## Codex Position

Codex recommends `accept-with-boundary`.

v2.8 can be closed internally after fresh Claude and Gemini review, provided the
final consensus repeats the same public-claim boundary. No additional pod run is
needed unless reviewers find a specific evidence defect.
