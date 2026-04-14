# Codex Consensus: Goal 375

Goal 375 is closed as the next bounded `cit-Patents` Linux scale-up slice.

Evidence:

- live Linux runs on `lestat-lx1`
- BFS:
  - `max_edges_loaded = 1000000`
  - `python_seconds = 0.1239954199991189`
  - `oracle_seconds = 1.0668449780205265`
  - `postgresql_seconds = 0.00032035697950050235`
  - `postgresql_setup_seconds = 42.83335640496807`
  - `oracle_match = true`
  - `postgresql_match = true`
- triangle count:
  - `max_canonical_edges_loaded = 100000`
  - `python_seconds = 3.8491162119898945`
  - `oracle_seconds = 0.7847236479865387`
  - `postgresql_seconds = 0.02595591504359618`
  - `postgresql_setup_seconds = 4.892115190043114`
  - `oracle_match = true`
  - `postgresql_match = true`
- external review:
  - `docs/reports/gemini_goal375_v0_6_cit_patents_split_bound_eval_review_2026-04-14.md`

Consensus:

- the accepted split-bound scale step executed cleanly
- BFS remains comfortable at the larger bound
- triangle count remains parity-clean and still practical enough for Python timing at this step
