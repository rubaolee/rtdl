I now have enough detail for a complete external review. Here is the assessment:

---

## External Review: `RTDL_OPTIX_COLLECT_K_LEVEL_GRAPH_REPLAY=1`

**Scope reviewed:** `src/native/optix/rtdl_optix_api.cpp` (lines 1262–1517 and surrounding merge loop), Goal 1557 probe, Goal 1558 plan, Goal 1559 diagnostic.

---

### Verdict

The production candidate is correctly structured and bounded. It is **not yet acceptable for accepting timing measurements**. The Goal 1557/1559 diagnostics prove graphability and parameter-update feasibility on controlled buffers; they do not prove production parity or measure production-scale speedup. The Goal 1558 acceptance criteria (same rows, same emitted count, same overflow, timing vs. the accepted Goal 1552 stack at 65537 and 131072 candidates) are explicitly listed as unmet requirements and remain open.

---

### Risks

**R1 — Production correctness unverified (blocking for measurements)**
The implementation has never been exercised with real candidate data at production scale. There is no evidence that emitted count, overflow flag, and row content are identical to the accepted direct-launch path under `65537` or `131072` candidates. Goal 1559 used controlled dummy buffers. This is the primary gap between the current candidate and a measurement-acceptable state.

**R2 — Double-execute hazard on post-launch sync failure (low probability, architecturally unclear)**
At lines 1508–1516, if `cuGraphLaunch` succeeds but `cuStreamSynchronize(collect_k_level_graph.stream)` throws, the catch block calls `reset_after_failure()` and falls through to the direct-launch path. The four kernels from the graph would then be re-executed on already-written device buffers (`final_merged_rows`, `final_marks`, `final_block_counts`, `final_block_offsets`). In practice, a sync failure on a non-blocking stream implies a device-level error that would also make the direct fallback fail, but the re-execution window exists and is not explicitly closed. A `disabled = true` set immediately after a successful launch (before sync) would remove the hazard.

**R3 — Profile `merge_launches` count is inaccurate for graph-replay levels (minor, profiling validity)**
At lines 1801–1802, `merge_launches` and `profile.merge_launches` are incremented by 4 (one per kernel) even when graph replay submits all four kernels as a single graph launch. Any profiling analysis that divides latency by launch count, or compares graph-replay profiles to direct-launch profiles, will see an inflated launch count for the graph path. This contaminates comparative profile reading.

**R4 — Graph capture overhead not amortized across calls (measurement scope)**
`CollectKLevelGraphReplayState` is local to each call to `rtdl_optix_collect_k_bounded_i64_device`. The capture + `cuGraphInstantiate` cost is paid on the first eligible level of every call. Goal 1557 measured warm-replay benefit in isolation; it did not measure end-to-end call latency including capture setup. Production measurements must include this cost to be comparable to the accepted direct-launch stack.

**R5 — `CU_STREAM_CAPTURE_MODE_GLOBAL` captures any concurrent stream (narrow but present)**
Line 1390 uses `CU_STREAM_CAPTURE_MODE_GLOBAL`. Any CUDA API call from any thread during the capture window would be incorporated into the graph. The window is narrow (only `launch_graph_sequence` on the capture stream) and a `cuStreamSynchronize(nullptr)` precedes it (line 1386), but in a multi-context or multi-thread scenario this mode is the more dangerous choice. `CU_STREAM_CAPTURE_MODE_THREAD_LOCAL` would constrain capture to the calling thread and is the safer option for future hardening.

---

### Required Safeguards

The following must be resolved before accepting production timing measurements from this candidate:

1. **Parity test at production scale.** Run `RTDL_OPTIX_COLLECT_K_LEVEL_GRAPH_REPLAY=1` with the full accepted flag stack against the direct-launch baseline on 65537 and 131072 candidates. Assert: identical emitted count, identical overflow flag, identical row content (or equivalent sort order). This is the explicit acceptance criterion from Goal 1558 and is currently unmet.

2. **Fix or document the post-launch sync-failure double-execute window.** Either set `disabled = true` immediately after a successful `cuGraphLaunch` (before sync), or document that fallback is only safe in pre-launch failure modes. Leaving the current behavior is acceptable as a known-edge-case annotation provided the risk level is recorded.

3. **Fix profile `merge_launches` accounting for graph-replay levels.** Graph-replay levels should increment a separate counter (e.g., `graph_replay_launches` or a boolean per merge level) rather than adding 4 to the direct-launch count. This prevents misleading comparative profile output.

4. **Do not accept timing numbers from this candidate as final until (1) passes.** Timing collected before parity is established could be accepted on incorrect output, which would require the entire measurement cycle to be repeated.

---

### Recommendation

**Hold measurements.** The candidate implementation is well-bounded, correctly falls back on failure, and matches the Goal 1558 design exactly. The guard chain (`use_device_level_counts && use_device_prefix_compact && use_derived_level_descriptors && total_blocks <= 512`) is correct; the flag is off by default; RAII cleanup is complete; the final two-segment path is excluded as specified. None of these structural elements need to change before running the next diagnostic.

The required next step is the production-scale parity and timing run described in Goal 1558. Run with the full accepted stack, verify row parity first, then compare latency against the Goal 1552 baseline at 65537 and 131072. If parity fails, that is a correctness bug to fix before any timing is reported. If timing does not beat the accepted stack, record it as a negative result and revert to default. Either outcome is acceptable; unverified measurements are not.
