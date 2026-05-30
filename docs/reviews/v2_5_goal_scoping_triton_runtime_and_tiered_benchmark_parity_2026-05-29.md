# v2.5 Goal Scoping: Triton Runtime + Tiered Benchmark Parity

Author: Claude (independent review/scoping)
Date: 2026-05-29
Companion analysis: `docs/reviews/v2_5_ten_benchmark_apps_baseline_readiness_review_2026-05-29.md`

## The proposed v2.5 goal (as stated)

1. Finish the optimized `Python + RTDL + Triton` language/runtime.
2. Have it well-support the 10 benchmark apps — after careful rewriting/optimization for new app versions — at *similar high performance* to the old partner/design in v2.4.

## Verdict

Goal (1) is reasonable and well-scoped. Goal (2), as a single blanket "all 10 apps at v2.4 parity," is over-committed and should be **split into tiered, tolerance-defined, same-contract parity targets**. The risk is not the runtime; it is promising uniform v2.4-parity across four irregular workloads Triton is not naturally good at, plus two apps that never used a continuation partner at all. Aiming for *parity rather than superiority* is the right, honest bar and should be kept.

## Goal (1): finish the Triton runtime — accept

A bounded engineering goal. The substrate already exists (partner-continuation protocol, generic hit-stream handoff, typed payload columns, buffer descriptors, claim-gating discipline). The current Triton surface is **segmented scalar reductions** (`count`, `sum`, `min`, `max`, `sum_count`). Finishing the runtime mostly means hardening that surface and adding the partner ops the benchmark suite actually needs (see the backlog below) — not open-ended research. Keep this as goal (1), and keep the existing fail-closed / `*_authorized=False` claim discipline through the optimization work.

## Goal (2): restate as tiered same-contract parity

"The 10 apps" are not one workload, and v2.4's "old partner/design" was mostly hand-written CuPy RawKernels and prepared OptiX device paths. Matching those with Triton is workload-dependent. Split the apps into three tiers and give each a different target.

### Tier A — parity is realistic now (Triton's sweet spot)

Continuation is a grouped/scalar reduction, which Triton routinely matches or beats versus CuPy.

| App | Continuation shape | Target |
| --- | --- | --- |
| `raydb_style` | grouped count/sum/min/max/sum_count | Already wired; confirm parity on pod |
| `triangle_counting` | grouped/scalar weighted sum | Wire to Triton; **also fix streaming/OOM** or large datasets can't run |
| `spatial_rayjoin` (count/parity) | scalar count/parity | Route count path through Triton |
| `librts_spatial_index` (count) | scalar count | Optional partner row; mainly an RT-core baseline |

Target: **measured parity within the tolerance band** (below), holding the workload/contract fixed.

### Tier B — per-app parity *bets*, not assumptions

Each needs a partner op Triton does not have yet, and each must be re-optimized to match an already hand-tuned CuPy/Torch version. Treat each as an explicit bet with its own risk.

| App | Needed Triton op | Parity risk vs v2.4 | Note |
| --- | --- | --- | --- |
| `rt_dbscan` | grouped **union-find / connected components** | **High** | Hardest claim in the plan; see fallback below |
| `hausdorff_xhd` | grouped **max + argmax (witness index)** | Medium | Device-side reduction with index tracking |
| `barnes_hut` | grouped **weighted vector sum** | Medium | Vector (not scalar) reduction; fused frontier→sum |
| `rtnn` | bounded **top-k / ranked summary** | Medium | Also needs a live harness, not frozen evidence |

Target: per-app parity **or a documented, accepted miss with a fallback path**. Do not gate the whole v2.5 release on all four reaching parity.

### Tier C — reframe: not partner benchmarks

No continuation-partner phase; the measured work is RT traversal + bounded collection / boolean flags.

| App | Measured work | Correct v2.5 target |
| --- | --- | --- |
| `contact_manifold` | bounded witness rows (`COLLECT_K_BOUNDED`) + AABB broadphase | **No regression**; Triton not on critical path |
| `robot_collision` | grouped any-hit flags | **No regression**; Triton not on critical path |

"Triton matches the old partner" is a category error here — there is nothing to port. The honest target is no-regression on the RT path.

## Definition of "similar high performance"

Make it measurable before the work starts, or the claim is unfalsifiable:

- **Same-contract comparison.** Hold the workload, fixture, and output contract fixed; change only the partner/runtime (v2.4 CuPy/Torch/OptiX path vs v2.5 Triton path). If apps are rewritten, the workload definition must not change with them.
- **Named opponent per app.** Compare against the *specific* v2.4 baseline (e.g., DBSCAN's CuPy device-grid continuation), not against CPU and not a strawman.
- **Tolerance band.** Define "similar" as within a stated band — suggest **±10–15%** of the v2.4 same-contract number — measured as a warm median over N repeats with warmup, on **sm_70+** hardware.
- **Phase-separated timing.** Report scene build / query prep / RT traversal / handoff / partner continuation / host materialization / total, so parity claims are attributed to the right phase.

## The hollow-parity caveat

v2.5 evidence (RayDB: ~4.8 ms RT traversal vs ~810 ms host materialization) shows the partner is often **not** the bottleneck. Two consequences:

- Whole-app parity may come almost "for free" because the continuation is a small slice — easy to match v2.4, but a slightly hollow win.
- The real lever for whole-app speed is **device-residency / materialization**, not which partner runs the reduction. If the rewrite doesn't tackle that, a fast Triton continuation won't move whole-app numbers — in either direction.

Decide explicitly whether v2.5 is claiming continuation-phase parity (achievable, modest) or whole-app parity (depends on materialization work that is largely out of Triton's hands).

## DBSCAN union-find: highest-risk target + required fallback

DBSCAN's continuation is grouped union-find/components. The existing CuPy version reached its performance only after ~40 goals (Goal2430–2475) fighting global-atomic pressure, intersection-program culling, and stream/chunk policy. Re-deriving that in Triton at CuPy parity is **novel kernel research, not wiring**, and Triton is weakest exactly here (irregular, data-dependent, atomic-heavy).

Required mitigation before committing:

- **Fallback by design.** Allow the Triton continuation to call out to a non-Triton union-find step (the existing CuPy components path) if Triton-native cannot reach the band. v2.5 parity should be satisfiable by "Triton continuation + a permitted components op," not blocked on a pure-Triton union-find.
- **Decouple it from the release gate.** Pure-Triton union-find at parity should be a stretch goal, not a v2.5 exit criterion.
- **Time-box the attempt.** Set an explicit budget; if unmet, ship the fallback and record the miss honestly.

## Triton partner-op backlog (the real content of goal (1))

Derived from the suite, in suggested order:

1. Grouped scalar reductions — **done** (harden + pod-validate).
2. Grouped **vector sum** (Barnes-Hut) — extension of existing reductions; lower risk.
3. Bounded **top-k / ranked summary** (RTNN) — medium.
4. Grouped **max + argmax** (Hausdorff) — medium.
5. Grouped **union-find / components** (DBSCAN) — high risk; fallback-backed.

This list, not "all 10 apps," is the honest definition of what the runtime must deliver.

## Suggested acceptance gates for v2.5

- Goal (1): the runtime exposes ops 1–4 above with conformance tests and fail-closed behavior; op 5 is delivered as Triton-native-or-fallback.
- Goal (2): Tier A apps measured at parity (±band, same-contract, sm_70+); Tier B apps each either at parity or shipping a documented fallback with an accepted miss; Tier C apps show no regression on the RT path.
- One re-runnable phase-timed harness per app (fold the scattered `goalXXXX_*.py` numbers in), and a baseline manifest naming each app's command, fixture, opponent, parity gate, and hardware.
- All runs preserve the existing claim-gating; no public speedup wording without the separate exact-wording review.

## Bottom line

Reasonable as a direction; over-committed as a single pass/fail goal. Keep goal (1). Re-cast goal (2) as tiered, tolerance-defined, same-contract parity: realistic for Tier A, per-app bets for Tier B (with DBSCAN union-find time-boxed and fallback-backed), and "no regression" for the two non-partner apps. Define "similar" with a number and a named opponent before starting, and be explicit about whether the parity claim is continuation-phase or whole-app — because the bottleneck evidence says those are very different promises.
