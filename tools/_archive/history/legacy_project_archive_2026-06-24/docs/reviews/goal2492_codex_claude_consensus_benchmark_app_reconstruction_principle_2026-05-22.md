# Goal2492 Codex + Claude Consensus

Date: 2026-05-22

## Verdict

APPROVE. Goal2492 can be used as the project-facing scope for the next
benchmark-app campaign.

## Basis

Codex wrote the Goal2492 scope report and guard test. Claude independently
reviewed the report and README update in
`docs/reviews/goal2492_claude_review_benchmark_app_reconstruction_principle_2026-05-22.md`
and returned `APPROVE_WITH_NON_BLOCKING_NOTES`.

## Consensus

Codex and Claude agree on these points:

- Benchmark apps are reconstruction instruments for RTDL language/runtime
  design, not mandatory full paper-system reproductions.
- Partial app slices are acceptable when they expose a missing RTDL primitive,
  result contract, memory/lifetime contract, partner boundary, prepared
  execution model, or evidence protocol.
- RayDB should only proceed if it exposes database-shaped ray-query contracts
  not already covered by the spatial RayJoin-style app.
- Python owns schema, query names, database-like syntax, paper interpretation,
  and row labels.
- Native Embree/OptiX must remain app-name-free and must not gain RayDB, SQL,
  table, or database-specific ABI.
- No authors-code comparison, paper reproduction, SQL/DBMS claim, public
  speedup claim, or broad database-engine claim is authorized by Goal2492.

## Non-Blocking Notes Resolved

Claude noted that consensus process and pod-unavailable closure conditions could
be clearer. The report now points to `/Users/rl2025/refresh.md` for the 2-AI
definition and states that the RayDB campaign may close as a CPU/Embree
reconstruction slice if OptiX pod access is unavailable, with NVIDIA/OptiX
claims deferred.

Claude also questioned the date stamp. The current session date is 2026-05-22,
so the date remains unchanged.

## Next Step

Proceed to Goal2493: RayDB local/external code intake. The first task is to
verify available RayDB code/datasets and decide whether to use verified external
code or a synthetic database-shaped RTDL fixture. No performance or authors-code
comparison should be attempted until that intake is complete.
