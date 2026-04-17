# Goal 402: v0.6 RT Graph Final Correctness And Performance Closure

## Objective

Package the corrected RT `v0.6` graph line into one final closure slice that
states, with bounded honesty, that:

- RTDL can express and execute the graph workloads through the RT kernel path.
- correctness is closed on the validated bounded and large-batch slices.
- performance evidence exists on real public graph datasets.
- the repo contains a final report plus a 3-agent consensus trail.

## Required evidence

1. Correctness:
   - PostgreSQL-backed all-engine bounded correctness gate already closed.
   - large-batch triangle-count Embree regression fixed and revalidated.
   - large-batch correctness report must state exact row/hash evidence where used.
2. Performance:
   - Linux large-scale timings for Embree, OptiX, Vulkan, and PostgreSQL.
   - at least two real public graph datasets beyond the initial tiny test slices.
3. Consensus:
   - Mac Codex final audit/report
   - Windows Codex benchmark handoff/report
   - Gemini review chain from the correctness/performance gates

## Honesty boundary

- This closure is about the corrected RT `v0.6` graph line, not public-branch release packaging.
- The comparisons remain workload-shape aware:
  - RTDL bounded BFS expansion and triangle probe are not identical to every external baseline workload.
- Claims must stay precise:
  - RTDL graph is real and performance-credible.
  - RTDL graph is not claimed to dominate specialized graph systems universally.
