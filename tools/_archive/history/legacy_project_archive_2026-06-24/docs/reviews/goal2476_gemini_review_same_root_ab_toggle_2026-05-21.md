Warning: Basic terminal detected (TERM=dumb). Visual rendering will be limited. For the best experience, use a terminal emulator with truecolor support.
Warning: 256-color support not detected. Using a terminal with at least 256-color support is recommended for a better visual experience.
Ripgrep is not available. Falling back to GrepTool.
(node:32389) [DEP0190] DeprecationWarning: Passing args to a child process with shell option true can lead to security vulnerabilities, as the arguments are not escaped, only concatenated.
(Use `node --trace-deprecation ...` to show where the warning was created)
RTDL Goal2476 Review for correctness and evidence discipline:

### Verdict: Acceptable
Goal2476 successfully transitions the same-root grouped-union intersection cull from a hardcoded internal optimization into a controlled A/B engineering surface. The implementation is correct, maintains default behavior, and adheres to strict evidence discipline.

### Blocking Issues
- None.

### Non-blocking Issues
- **Performance Optimization Opportunity:** In `__intersection__frn3d_grouped_union_isect` (`src/native/optix/rtdl_optix_core.cpp`), the `same_root_culling` check is performed after the distance calculation. Moving it before the distance calculation (when `parent_union_candidate` is true) could save some floating-point operations, though `find_grouped_union_root_readonly` has its own cost. This is not a correctness issue.

### Evidence Assessment
- **Controlled A/B Testing:** The report `docs/reports/goal2476_same_root_culling_ab_toggle_2026-05-21.md` provides a clean comparison between `same_root_ab_on` and `same_root_ab_off`.
- **Signature Integrity:** I verified that both `summary.json` files for the A/B test branches show identical `signature` results for the `clustered3d` dataset, confirming that the optimization does not change the resulting cluster structure.
- **Speedup Verification:** The pod evidence shows a measurable performance benefit when culling is enabled (e.g., `clustered3d_65536` median sec: ~0.042s with culling vs ~0.048s without), justifying its preservation as the default.

### Required Wording Boundary
- **Internal Only:** All performance claims in this goal must be explicitly marked as "internal-only same-build engineering comparisons."
- **Public Claim Block:** The `_metadata` in `partner_adapters.py` and the benchmark app correctly set `rt_core_speedup_claim_authorized: False` and `release_claim_authorized: False`.
- **Wording Constraint:** Do not use "RT-DBSCAN" in native vocabulary or public-facing documentation for this grouped-union step; keep the focus on "generic grouped-union same-root culling" as an engine primitive.
