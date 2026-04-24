---

## Goal907 External Review — Verdict: **ACCEPT**

### What changed

`app_support_matrix.py` has four graph-analytics entries updated across all four matrices. The generated JSON artifacts (goal848, goal901, goal824) are consistent regenerations. No new execution behavior is introduced.

### Claim boundary checks

| Check | Finding |
|---|---|
| `optix` status in `_APP_MATRIX` | Still `_COMPAT` (`direct_cli_compatibility_fallback`) — correct, native OptiX graph-ray mode is behind a flag, default is host-indexed |
| `benchmark_readiness` | `needs_real_rtx_artifact` — no promotion, no claim |
| `current_status` | `rt_core_partial_ready` — no advancement |
| Embree BFS/triangle-count wording | Described as ray-traversal candidate-generation paths, not as an RTX performance claim |
| OptiX native graph-ray mode wording | Correctly noted as "explicit … behind `RTDL_OPTIX_GRAPH_MODE=native`, but the default remains host-indexed until RTX validation" |
| Excluded claims | Shortest-path, graph database, distributed graph analytics, whole-app graph-system speedup — all absent from every field |
| CPU-side work | Frontier bookkeeping and neighbor-set intersection explicitly kept outside the RT-core claim in `required_action` |

### Combined Goal889/905 gate — still required

Both the `cloud_policy` and `allowed_claim` fields enforce this explicitly:

> "Cloud only in the combined Goal889/905 graph gate; no graph RT-core claim until visibility, native BFS, and native triangle-count row digests pass on RTX hardware."

This gate has not been removed, loosened, or rerouted. It remains the mandatory prerequisite for any NVIDIA graph RT-core claim.

### Artifact consistency

All three regenerated JSON files faithfully reflect the source matrix. The goal901 `valid: true` and goal824 `valid: true` fields confirm the generated artifacts passed their own internal gate tests. The goal759 manifest produced no content diff, which is the expected outcome.

### No issues found

The change does exactly what it says: replaces stale "visibility-only / no BFS / no triangle" language with accurate current state while holding every claim boundary in place. 41 tests OK, py_compile clean, no whitespace errors.
