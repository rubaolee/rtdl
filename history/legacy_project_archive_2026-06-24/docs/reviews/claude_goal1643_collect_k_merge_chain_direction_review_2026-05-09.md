No prior memory. Analyzing the evidence directly.

---

**Verdict**

Yes, the data support shifting the primary optimization target to the merge chain. The final-pair mark path is substantially understood and its GPU-side cost is confirmed small; the remaining bottleneck is now the merge sequence.

---

**Why**

- **Mark-path GPU work is cheap.** Goal1637/1641 show `final_pair_mark_event_ms` = 0.015 ms in both runs. That is the actual GPU kernel cost. The accompanying host-wait figures (0.314 ms and 0.274 ms) are synchronization overhead, not kernel work — the GPU finishes quickly; the CPU waits.
- **Pre-mark wait is stable, not shrinking.** `final_pair_pre_mark_wait_ms` is 0.274–0.276 ms across Goal1641 and Goal1642. It has converged to a floor, indicating the pipeline stall upstream is structural, not a tuning artifact. Further mark-path work has no leverage here.
- **Merge chain is now the dominant wall-clock term.** Goal1642 shows `merge_launch_ms` = 0.481 ms and `merge_event_ms` = 0.382 ms against a `total_ms` = 0.692 ms. The merge sequence alone accounts for ~55–70 % of total time. `merge_sync_ms` = 0.015 ms confirms the GPU finishes fast; the cost is launch overhead and pre-launch stall.
- **Graph replay is already beneficial at full scale.** Goal1640 shows graph execution at 107 µs vs. direct 119 µs (1.11×), and graph-update cost has narrowed to ~3 µs delta. The graph infrastructure is proven and can be extended to the merge chain.

---

**Next Candidate**

**Capture the merge chain into a CUDA graph, isolated and measured before integration.**

Concretely:
1. Add an opt-in diagnostic path (matching the existing event-opt-in pattern) that replays the merge kernel sequence via graph and records `merge_graph_event_ms` alongside the existing `merge_event_ms`.
2. Target the same isolation setup used in Goal1640 (fixed `pair_count=1`, `segment_capacity=131072`) to get a clean baseline ratio before touching the hot path.
3. If the graph replay shows ≥ 1.05× on merge, promote to a flag-guarded production path — mirroring the existing graph-replay flag pattern referenced in the evidence.

This is the safest candidate because: (a) it reuses proven graph infrastructure, (b) the measurement is additive and opt-in so it cannot regress production, and (c) `merge_sync_ms` = 0.015 ms confirms the GPU kernel itself is fast enough that launch-overhead elimination is the realistic win vector.

---

**Risks**

- **merge_launch_ms includes CPU-side setup cost** that graph replay does not eliminate (argument marshalling, dependency checks). The 0.481 ms figure may not compress as much as the 119→107 µs mark-path result did; expect a smaller ratio.
- **pre_mark_wait structural floor** (0.274–0.276 ms) may re-emerge as the binding constraint once merge is accelerated, shifting the bottleneck rather than eliminating it. Instrument both concurrently.
- **Graph update cost on merge** will differ from the mark path because merge likely has more kernel nodes and potentially conditional logic. `graph-update` overhead needs its own measurement before claiming the approach scales.
- **Row/count parity confirmed true in Goal1642** removes correctness risk from the merge path specifically, but any new graph path needs its own parity check before production promotion.

---

**Claim Boundary**

These conclusions hold within the Goal1637–1642 measurement regime: single-pair, isolated, opt-in diagnostics, `segment_capacity=131072`. Extrapolation to multi-pair or production-scale merge behavior is not yet supported by this data. The 1.11× graph-replay advantage from Goal1640 applies to the mark kernel, not merge — do not carry that ratio forward as a merge prediction.
