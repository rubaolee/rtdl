# Goal4191 Claude Review: Goal4190 RT-DBSCAN Counts-Only Mixed-Route Probe

Reviewer: Claude  
Date: 2026-06-09  
Verdict: `accept-with-boundary`

This file preserves the actual Claude review output captured in
`scratch/goal4191_claude.out`. Gemini also wrote a Goal4190 review file during
the same background review window; this Claude file is kept distinct because
strict consensus requires distinct external outputs.

## Findings

**Q1 - Route comparison design:** Correct. `_policy_signatures()` properly
evaluates both contracts per route, and the comparison logic is sound. One
informational note: on road3d at radius=0.003/min_neighbors=16, cluster
distributions are numerically identical across all routes (at 4M there is
effectively one component spanning 99.9% of points). The
`same_policy_bound_component_sizes_as_reference = false` result is driven by the
`border_assignment_policy` label in the signature dict, not by actual cluster
divergence. This is correct contract design, but the road3d data is insensitive
to border-policy tie-breaks. Goal4165/4166 carry the actual cluster-divergence
evidence.

**Q2 - Artifact support:** Fully confirmed. All four JSON artifacts
(262k/1M/2M/4M) show counts-only match and policy-bound mismatch exactly as
claimed. Commit hash and all authorization flags are consistent. No errors in
stderr.

**Q3 - Conservative performance conclusion justified:** Yes, with two notes:
(a) `repeat=1, warmup=0` means the 1.056x at 4M is a single-run observation, not
a measured speedup; (b) the comparison mixes a route switch and a partner switch
(Numba -> CuPy), so the delta cannot be attributed to convergence mode alone.
Neither note changes the "not a major win" conclusion.

**Q4 - Next target correctly identified:** Yes. The "generic predicate-aware
direct-status grouped-union primitive" direction is verbatim consistent with
`future_version_to_do_list.md` and the engine boundary (no DBSCAN ABI, no hidden
dispatch) is intact throughout all artifacts.

**Q5 - Claim boundaries preserved:** Comprehensive. All authorization flags are
hard-coded false in both script and artifacts, tested by the test suite.
