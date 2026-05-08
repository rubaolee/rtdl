I now have all the data I need. Here is the full external review.

---

## External Review: RTDL Goal1557–Goal1560 — CUDA Graph Replay for `COLLECT_K_BOUNDED`

---

### Verdict

The per-call, per-level graph replay path (`RTDL_OPTIX_COLLECT_K_LEVEL_GRAPH_REPLAY=1`) is correctly rejected. The diagnostic chain (Goals 1555–1559) was sound and the negative result (Goal 1560) is credible. The issue is not that CUDA graph replay is wrong for this workload — it measurably reduces GPU execution time. The issue is that the per-level parameter update API cost recurs every call and is not amortized, which more than cancels the GPU benefit for the long cases.

If graph work continues, it must change the amortization structure. If it does not, it should be closed now.

---

### Rationale

The diagnostic probes (Goals 1557, 1559) produced genuine 1.12–1.19× speedups because they replayed the same topology 5,000 consecutive times, fully amortizing `cuGraphCreate + cuGraphInstantiate` across those replays. The production candidate in Goal 1560 reversed that structure: it captures and instantiates once per call, then calls `cuGraphExecKernelNodeSetParams` four times (once per kernel node) for each of the 23 merge levels before replaying. For the long cases, this is 92 parameter-update API calls per `rtdl_optix_collect_k_bounded` invocation — paid fresh every call with no carry-forward.

The data confirms this precisely. For the 65537-candidate case:

| Metric | Control | Candidate | Delta |
|---|---|---|---|
| merge_launch_ms | 0.086 | 0.199 | +0.113 ms |
| merge_sync_ms | 0.083 | 0.008 | −0.075 ms |
| total_ms | 0.285 | 0.328 | +0.043 ms |

The GPU executed more efficiently (sync_ms dropped 10×). The CPU-side parameter update API overhead was 1.23 µs per call × 92 calls = ~113 µs extra, which outweighs the 75 µs of GPU sync savings. The net is a 15% regression on long cases.

For 131072, the structure is nearly identical: 142 µs of extra CPU overhead against 110 µs of GPU savings. Both long cases regressed for the same root cause.

The Goal 1557/1559 probes showed that graph update API calls cost approximately 1.23 µs each in this environment. Direct kernel launches cost approximately 3.7 µs per four-kernel group. The parameter update approach replaces each 3.7 µs launch group with a 4 × 1.23 µs = 4.9 µs update-then-launch sequence — it is slower per level, not faster. The isolated probe results were misleading because the update cost was paid once and the replay benefit accumulated over 5,000 iterations.

---

### Risks

**R1 — Persistent cross-call cache may not remove the binding obstacle.**
The primary bottleneck in Goal 1560 is `merge_launch_ms` inflation from per-level parameter update calls, not `cuGraphInstantiate` (paid once). A cross-call cache that stores instantiated graph executables would eliminate the re-instantiate cost but would still require `cuGraphExecKernelNodeSetParams × 4` per level unless the topology exactly matches a cached entry and no update is needed. The benefit of caching is real only when the same `(pair_count, blocks_per_pair, segment_capacity)` tuple repeats across calls. Whether that happens at useful frequency is an open empirical question: it is true whenever the caller repeats the same k and the same input-count, but unknown for the real workload distribution.

**R2 — Kernel fusion carries its own complexity ceiling.**
The four-kernel compact-level sequence has a device-prefix step between mark and compact. This step requires a device-wide scan that communicates across thread blocks, which means it cannot be fused into a single contiguous kernel without cooperative launch support. Fusing materialize+mark (trivially parallel) into one kernel while keeping prefix+compact separate halves the launch count per level (23 levels × 2 launches = 46 vs. 92). That does not require graph APIs and is measurably worthwhile if `merge_launch_ms` is the bottleneck — but requires careful implementation to avoid register pressure and occupancy loss.

**R3 — Profile accounting remains corrupted for graph-replay levels.**
Goal 1560's `merge_launches` counter is incremented by 4 (one per kernel) even when graph replay submits all four as a single `cuGraphLaunch`. Any analysis that divides timing by launch count to get per-launch cost will be wrong for the graph path. This must be corrected before any future graph diagnostic is treated as a fair comparative measurement.

**R4 — The small-case improvement (4097 candidates) is real but not decision-relevant.**
Graph replay improved the 4097 case from 0.179 ms to 0.151 ms (−15%). This is a genuine improvement, but the 4097 case has only 7 merge launches, so the parameter update overhead is smaller relative to the sync savings. Any approach that regresses the 65537/131072 cases to win on 4097 is not acceptable by the existing acceptance criteria.

---

### Recommended Next Diagnostic

Choose one of two paths based on what is known about the workload's call distribution.

**Path A — Persistent topology cache (lower risk, conditional payoff).**
Before any implementation, instrument the existing production path to log the tuple `(pair_count, blocks_per_pair, segment_capacity)` for every non-final compact level across a representative batch of 100–500 `rtdl_optix_collect_k_bounded` calls drawn from real or realistic input sequences. Compute the hit rate: for what fraction of non-final levels does an exact-match tuple appear in a prior call in the same process session? If the hit rate is ≥80%, implement a per-topology `CUgraphExec` cache keyed on those three parameters, storing the instantiated executable and the four retained node handles. On a cache hit, skip parameter update entirely and issue only `cuGraphLaunch`. This eliminates both the update API cost and the re-instantiate cost and recovers the full ~1.15–1.19× per-level benefit from Goals 1557/1559. If the hit rate is below 80%, close this path.

**Path B — Two-kernel compact-level fusion (higher risk, unconditional payoff if it works).**
Prototype a merge of `materialize_level_counts + mark_counts_level_counts` into a single kernel (these are both element-wise operations on the same address space with no inter-thread communication). This reduces launches from 4 per level to 3 per level, cutting 23 × 4 = 92 total launches to 69 without any graph infrastructure. Measure `merge_launch_ms` and `total_ms` vs. the Goal 1552 baseline at 65537 and 131072. If the two-kernel split delivers a ≥10% reduction in `merge_launch_ms` (the binding bottleneck at ~0.086 ms for 65537 control), continue further fusion investigation. If not, the bottleneck has shifted to GPU execution time and further launch reduction will not help.

Of the two paths, **Path B is the cleaner bet** because it reduces the source of overhead directly rather than working around it with caching infrastructure of uncertain hit rate. It also avoids all CUDA graph API complexity and produces a simpler production implementation. Path A is worth attempting only if there is already evidence that the application presents highly repetitive input sizes across calls.

---

### Stop Conditions

- **Stop all graph work** if Path A's topology hit-rate diagnostic returns below 80% for the representative call sequence. The per-level parameter update overhead is architectural in the current integration design and cannot be overcome by amortization at lower hit rates.
- **Stop kernel fusion work** if a two-kernel compact-level probe shows less than 10% improvement in `merge_launch_ms` vs. the four-kernel control. At that point, `merge_launch_ms` is not the binding bottleneck and reducing launch count will not yield further gains.
- **Stop all further collect-k optimization** and accept the current 0.285–0.308 ms baseline as the performance plateau if both diagnostics above fail their conditions. The engineering cost of finding and implementing the next lever exceeds the measurable benefit at that point. The series from Goals 1550–1560 has already produced real improvements (device-level counts, device-prefix compact, derived descriptors, batch compact level), and a negative result here does not invalidate those gains.
- **Do not accept any candidate** that regresses the 4097-candidate case below 0.179 ms (the pre-Goal 1560 control baseline) in pursuit of long-case improvement.
