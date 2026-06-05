# Goal3522 3-AI Consensus: v2.8 Internal Closeout

Date: 2026-06-05

Status: v2.8 internal closeout accepted with boundary; not public release authorization.

## Reviewed Packet

- `docs/reports/goal3522_v2_8_internal_closeout_packet_2026-06-05.md`
- `docs/reports/goal3521_v2_8_final_validation_packet_2026-06-05.md`
- `docs/reports/goal3520_v2_8_claim_boundary_and_stale_doc_audit_2026-06-05.md`
- `docs/reports/goal3519_v2_8_learner_docs_cleanup_audit_2026-06-05.md`
- `docs/reports/goal3518_v2_8_benchmark_matrix_refresh_2026-06-05.md`
- Representative artifacts under `docs/reports/goal3521_pod_artifacts/`

## Review Files

- Claude: `docs/reviews/goal3522_claude_review_v2_8_internal_closeout_2026-06-05.md`
- Gemini: `docs/reviews/goal3522_gemini_review_v2_8_internal_closeout_2026-06-05.md`

## Validation

Local closeout guard:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal3522_v2_8_internal_closeout_packet_test \
  tests.goal3521_v2_8_final_validation_packet_test \
  tests.goal3520_v2_8_claim_boundary_stale_audit_test \
  tests.goal3519_v2_8_learner_docs_cleanup_test \
  tests.goal3518_v2_8_benchmark_matrix_test

Ran 23 tests in 0.237s
OK
```

Positive-claim scan:

The forbidden-phrase scan covered the closeout packet, public front doors, learner docs,
tutorials, and research-benchmark examples. The scan returned no matches.

## Verdicts

| Reviewer | Verdict | Notes |
| --- | --- | --- |
| Codex | `accept-with-boundary` | v2.8 can close as an internal prepared-execution version after Goal3512-3521 evidence, docs, claim audit, validation, and review. |
| Claude | `accept-with-boundary` | Confirms tests pass, no authorization phrase leak, engine boundary intact, partner choice explicit, phase separation strong enough for internal closeout. Requests one nuance be carried forward: RT-DBSCAN raw RT-count is sub-1x at 32K; the 4x-4.9x speedup applies to the grouped-stream path. |
| Gemini | `accept-with-boundary` | Read-only review accepts internal closeout boundary, app-agnostic engine framing, explicit partner choice, and bounded benchmark claims. Notes future work remains but is not a blocker for internal closeout. |

## Consensus

Consensus verdict: `accept-with-boundary`.

RTDL v2.8 is closed as an internal version. The internal closeout means:

- the v2.8 prepared-execution story is documented;
- all 10 benchmark apps are represented in the matrix;
- active learner docs present a single v2.8-current source-tree surface;
- stale/overclaim wording is guarded by tests;
- targeted RTX A5000 validation exists for the closeout gaps;
- final Claude and Gemini reviews agree that no blocker remains for internal closeout.

## Public Boundary

This consensus does not authorize:

- a public v2.8 release;
- a package-install or PyPI promise;
- public speedup wording;
- broad RT-core speedup wording;
- true zero-copy wording;
- full RayJoin paper reproduction;
- RTDL-beats-RayJoin wording;
- full overlay geometry/output claims;
- hidden partner selection;
- app-specific native-engine behavior.

Any public release or public performance claim requires a separate user-requested release packet and review gate.

## Required Nuance For Future Readers

The RT-DBSCAN Goal3521 artifact contains two different timing stories:

- the raw RT-count row is `0.937x` versus prepared CuPy grid at 32K points, so it is not a universal speedup;
- the grouped-stream path is the promoted v2.8 row and reaches `4.080x`, `4.691x`, and `4.897x` versus prepared CuPy grid at 32K, 65K, and 131K points.

Future summaries must not collapse those into a broad DBSCAN or broad RT-core speedup claim.

## Deferred Work

The following are deferred and do not block the internal closeout:

- clean alias/migration plan for quarantined `v2_5` / `v2_6` Python helper and protocol names;
- further phase-split refreshes for selected matrix rows when another pod run is useful;
- deeper v3.0-style device residency and arbitrary partner composition;
- user-defined shader injection and extension surfaces;
- public release packaging, if the user later asks for it explicitly.

## Final Statement

v2.8 is internally closed. The next development lane can start from this point, but the repository must continue to preserve the same app-agnostic engine and claim-boundary discipline.
