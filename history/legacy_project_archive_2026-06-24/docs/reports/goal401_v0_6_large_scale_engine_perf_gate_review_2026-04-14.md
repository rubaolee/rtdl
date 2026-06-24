# Goal 401 Internal Review: v0.6 Large-Scale Engine Performance Gate

Date: 2026-04-14
Reviewer: Codex
Status: accepted

## Decision

Goal 401 is accepted.

## Basis

- The corrected RT branch now contains a real bounded large-data graph loader
  and performance harness:
  - `src/rtdsl/graph_datasets.py`
  - `src/rtdsl/graph_perf.py`
  - `scripts/goal401_large_scale_rt_graph_perf.py`
- Local focused tests pass:
  - `tests.goal401_v0_6_large_scale_engine_perf_gate_test`
  - `Ran 7 tests`
  - `OK`
- The existing corrected RT graph line remained green after the slice:
  - integrated graph correctness band plus Goal 400 PostgreSQL tests
  - `Ran 51 tests`
  - `OK`
- Linux `lestat-lx1` live runs produced real large-data timings for:
  - Embree
  - OptiX
  - Vulkan
  - PostgreSQL
- PostgreSQL setup and query time are separated explicitly and honestly.

## Main Finding

The corrected RT graph line now has the first bounded large real-data
performance evidence for both opening workloads:

- `bfs` bounded expand step on `wiki-Talk`
- `triangle_count` bounded probe step on `cit-Patents`

The current evidence is aligned with the actual implementation boundary:

- bounded RT-kernel steps
- not end-to-end whole-graph RT execution

## External Review

External review is present and accepting:

- `docs/reports/gemini_goal401_v0_6_large_scale_engine_perf_gate_review_2026-04-14.md`

## Conclusion

Goal 401 satisfies the current required scope and should be treated as closed.
