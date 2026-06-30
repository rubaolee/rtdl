---

## Verdict

**Do not revive the existing compact-level CUDA graph replay path. Do not blanket-avoid graph replay. The only production-relevant candidate is a prepared end-to-end stable-topology graph covering the real final-pair chain.**

The evidence chain is internally consistent across Goals 1634–1638. The mark kernel GPU time is 0.015 ms. The host-visible stream wait is 0.314 ms — roughly 21× larger. The bottleneck is stream dependency accounting and dispatch scheduling in the merge→mark→prefix→compact pipeline, not the kernel itself. Goals 1560/1561 previously rejected per-call/per-level graph replay because it regressed long cases; Goal1638 shows the existing probe path produces only 1.04× at a diagnostically undersized scale (segment_capacity=65536 instead of the actual 131072 target), and cannot even run at production scale due to the internal block-count guardrail capped at 512. Reviving the old path unchanged solves a different problem from the one measured.

---

## Risk

| Risk | Severity |
|---|---|
| Existing graph probe blocked by block-count guardrail at segment_capacity=131072 | High — cannot validate production scale without a new graph design |
| 1.04× at undersized scale does not extrapolate to meaningful gain at 2× larger input | Medium — may be launch-overhead dominated only at tiny sizes |
| Stream wait may be partly driven by host-side final-pair-count dependency (CPU→GPU sync), which graph replay cannot eliminate | Medium — graph dispatch skips launch overhead but cannot remove host data dependencies |
| Goals 1560/1561 regression in long cases if old replay path re-enabled | High — historical rejection stands; must not re-enable without new evidence at full scale |

---

## Next Probe

**Prepared end-to-end stable-topology CUDA graph for the final-pair chain at production scale.**

Specifically:
- Build a new graph capturing merge→mark→device-prefix→compact with `pair_count=1`, `segment_capacity=131072` (the actual current production target, not the guardrail-limited 65536).
- The graph must use a fixed topology with updatable node params (kernel args, buffer pointers) to simulate the real steady-state replay scenario.
- Measure: `graph_per_replay_us` vs `direct_per_replay_us` at repeats=1000. The key question is whether host-visible sync time in Goal1637 (0.314 ms) is substantially reduced or whether a host-side dependency (e.g., final pair count readback) blocks regardless of graph dispatch.
- If host-side readback of the final pair count is inside the measured critical path, isolate that first — graph replay cannot remove a CPU-blocking device→host transfer.

Do not change any production-path code until this probe produces a positive result at full scale.

---

## Claim Boundary

No public speedup claims, no "true zero-copy" wording, no stable `COLLECT_K_BOUNDED` promotion, no broad RTX/GPU generalization, no whole-application speedup claims, no release tags or release actions are authorized from Goals 1637 or 1638. All results remain internal diagnostic evidence only. The 1.04× figure at bounded scale is not a publishable result and must not be cited externally.
