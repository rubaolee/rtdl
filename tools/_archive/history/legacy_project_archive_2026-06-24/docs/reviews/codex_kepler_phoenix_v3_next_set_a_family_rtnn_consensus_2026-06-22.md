# Phoenix V3 Next Set-A Family Consensus: RTNN Ranked Summary

Date: 2026-06-22

Status: `approved_for_implementation_not_release`

Verdict: choose `rtnn` as the next Set-A family, but only through a generic fixed-radius ranked-summary prepared-execution primitive. This does not authorize release, public speedup wording, all-app reruns, or broad V3-over-V2 claims.

## 2-AI Consensus

Codex decision: choose RTNN for Step 2 because the existing repeat50 evidence is the cleanest Set-A signal that matches Phoenix V3's runtime-trunk thesis: prepare once, keep RTDL-owned internal state resident, execute repeated ranked-summary work through a productized runner, and report hot/cold/runner-wall boundaries together.

Kepler review: choose RTNN, not Hausdorff or Triangle, for the next family. RTNN must be implemented as a generic `ranked_summary` prepared-session runtime-trunk node, not as an RTNN app patch. Required gates: explicit backend/partner metadata, repeat50 material-probe boundary, cache and residency flags, integer-signature parity, distance tolerance, no all-app/release/broad wording.

Consensus result: proceed with RTNN as Phoenix V3 Step-2 runtime-trunk generalization.

## Why RTNN

Existing reviewed row-scoped evidence:

- `docs/rebuild/v3/phoenix_v3_rtnn_prepared_repeat50_amortization_evidence_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_rtnn_prepared_repeat50_review_gate_2026-06-21.md`

The useful prior signal is repeat50 ranked-summary amortization on 1,048,576 3-D points, not symbol-cache hygiene. The symbol-cache thread produced only parity-level evidence and is not the V3 lever.

## Alternatives Rejected For This Step

Hausdorff is not rejected forever, but it is narrower for the immediate second trunk probe because the current strongest evidence is threshold-shaped and row-scoped.

Triangle is not rejected forever, but it carries synthetic-row and non-graph-stream boundary risk. It is a better later probe after the runner shape has already generalized once.

RTDBSCAN and RayJoin are not retried here because their current Phoenix paths already produced parity/no-go style signals. Repeating the same route would be cache hygiene, not trunk building.

## Implementation Bar

The implementation must add a generic primitive-family helper, not an app-specific native route:

- Route through `PreparedExecutionSessionTask` and `run_repeated_prepared_execution_session`.
- Use explicit backend and explicit partner.
- Record `productized_execution_path=prepared_execution_session_runner`.
- Record `runtime_trunk_executes_end_to_end` only when the prepared runner actually executes and output signatures match the requested query contract.
- Record internal RTDL device residency as V3, while keeping external device-buffer exposure and embedding unauthorized.
- Keep hot-query, cold-plus-query, and runner-wall evidence together.
- Treat repeat50 as the material-probe shape; smaller repeats are smoke only.

## Non-Authorization

This decision does not authorize:

- V3 release.
- all-app benchmark rerun.
- public speedup wording.
- broad V3-faster-than-V2 wording.
- broad RT-core speedup wording.
- true zero-copy wording.
- external device-buffer interop or embedding claims.

## Goal-Level Decision Audit

1. Was I foolish? Not in this decision.
2. If yes, what actions made it foolish? The prior foolish pattern was spending effort on isolated route/cache changes and then hoping they would add up to V3. This decision explicitly stops that pattern.
3. Was there another path? Yes: keep running all-app or retry RTDBSCAN/RayJoin. That would be lower-value because the runtime trunk still would not generalize.
4. Can I now try a different path that actually solves the problem? Yes. The path is to make the same productized prepared-execution runner execute a second residency-rich Set-A family before any all-app run.
