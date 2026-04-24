# Goal877 Two-AI Consensus

- date: `2026-04-24`
- goal: `Goal877 polygon overlap OptiX phase profiler`
- Codex verdict: `ACCEPT_LOCAL`
- Claude verdict: `ACCEPT_WITH_CAVEATS`
- consensus: `ACCEPT_AS_LOCAL_PHASE_CONTRACT`

## Decision

Goal877 is accepted as the local phase contract for the Goal876 polygon
overlap/Jaccard OptiX native-assisted surfaces.

The accepted boundary:

- OptiX candidate discovery is timed separately.
- CPU exact area/Jaccard refinement is timed separately.
- The cloud manifest entries are deferred.
- Claims are limited to candidate discovery.
- No full polygon-area/Jaccard RTX speedup claim is authorized.

Claude's Jaccard helper caveat was addressed by adding and using the app-level
`_exact_jaccard_rows_for_candidates(...)` helper.

Real Linux/RTX execution remains required before any performance claim or
readiness promotion.
