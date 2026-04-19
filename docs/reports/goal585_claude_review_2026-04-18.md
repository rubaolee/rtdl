# Goal585 External Review

**Verdict: ACCEPT**

Date: 2026-04-18

Reviewer: Claude Sonnet 4.6 (external AI review)

## Summary

Goal585 honestly establishes the adaptive backend skeleton without overclaiming native performance. The implementation is clean and the honesty is structural, not just documented.

## Evidence

**No false acceleration claims.** Every entry in `_ADAPTIVE_WORKLOADS` has `native=False` and `mode=ADAPTIVE_COMPAT_MODE` (`"cpu_reference_compat"`). `run_adaptive` delegates directly to `run_cpu_python_reference` after workload validation — no bypass, no silent upgrade path.

**PreparedAdaptiveExecution does not fabricate speedups.** `prepare_adaptive` captures kernel and inputs into a frozen dataclass; `.run()` calls `run_adaptive`, which calls the reference path. No prepared-context acceleration is claimed or implied.

**Mode metadata is caller-visible by design.** `adaptive_predicate_mode` returns a dict with explicit `native`, `mode`, and `prepared_context` fields. Callers can inspect the compat status programmatically.

**Dimensional classification is correct.** `_classify_dimensional_workload` dispatches 2D/3D variants by inspecting compiled input layout names. The `bounded_knn_rows` 2D guard (raises rather than silently dispatching an unsupported path) is appropriate.

**Tests are adequate for a skeleton.** The two tests verify matrix cardinality (exactly 18), that every row is `cpu_reference_compat` and non-native, and that `run_adaptive` and `prepare_adaptive(...).run()` match `run_cpu_python_reference` for all 18 workloads using representative inputs. This is the right test scope for a compatibility shim.

**Dirty Apple RT files are acknowledged and scoped out.** The report notes the unrelated `apple_rt_runtime.py` / `rtdl_apple_rt.mm` changes must not be included in the Goal585 commit. No action required from this review, but the commit gating must enforce the boundary.

## Minor Observations (non-blocking)

- `bfs_discover` thread-safety note reads `"read-only graph; per-call visited/frontier scratch only"` — correctly distinguishes mutable per-call scratch from shared state. Consistent with the design.
- The `_WORKLOADS_BY_PREDICATE` builder loop at module level uses tuple concatenation (`+`). For 18 rows this is fine; a future reviewer expanding the matrix should note this is O(n²) per predicate group if that group grows large.

## Conclusion

The goal achieves its stated purpose: a stable public API surface that makes the compatibility mode explicit and leaves a clean insertion point for native kernels in Goal586+. No overclaiming. No hidden native paths. ACCEPT.
