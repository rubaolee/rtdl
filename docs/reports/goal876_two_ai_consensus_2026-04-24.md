# Goal876 Two-AI Consensus

- date: `2026-04-24`
- goal: `Goal876 polygon overlap OptiX native-assisted app surface`
- Codex verdict: `ACCEPT_LOCAL`
- Claude verdict: `ACCEPT_WITH_CAVEATS`
- consensus: `ACCEPT_AS_LOCAL_NATIVE_ASSISTED_SURFACE`

## Decision

Goal876 is accepted as a local app-surface improvement.

The two polygon-overlap apps now expose OptiX native-assisted candidate
discovery:

- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

The consensus boundary is:

- OptiX can perform LSI/PIP positive candidate discovery.
- CPU/Python performs exact grid-cell area/Jaccard refinement.
- Top-level `rt_core_accelerated` stays `false`.
- `rt_core_candidate_discovery_active` records the narrower OptiX-assisted
  candidate-discovery slice.
- No full polygon-area/Jaccard RTX speedup claim is authorized.
- Real Linux/RTX execution and phase profiling remain required before any
  performance claim.
