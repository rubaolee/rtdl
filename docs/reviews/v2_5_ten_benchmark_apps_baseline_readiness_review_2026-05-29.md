# Review: Are the 10 Pre-Triton Benchmark Apps Ready as v2.5 New-Partner Performance Baselines?

Reviewer: Claude (fresh independent reviewer)
Date: 2026-05-29
Task context: the 10 benchmark apps were finished and polished before Triton was introduced in v2.4. In parallel with the v2.5 new-partner (Triton) work, review how each is implemented, what was and wasn't optimized, and whether each is ready to serve as a baseline for measuring performance under the new partner.

Scope: `examples/v2_0/research_benchmarks/{barnes_hut, contact_manifold, hausdorff_xhd, librts_spatial_index, raydb_style, robot_collision, rtnn, rt_dbscan, spatial_rayjoin, triangle_counting}` plus their `scripts/` perf runners. READMEs, app source, backend menus, partner hooks, timing harnesses, and parity wiring were inspected directly.

## 1. Headline verdict

**One of ten apps (RayDB) is actually ready to baseline against the new Triton partner today. The other nine were polished against a different model — CuPy/Torch partners, or no continuation partner at all — and are not drop-in v2.5 partner baselines.** Most are excellent *correctness* baselines and several are excellent *RT-core / CuPy-partner* baselines, but "ready to test perf in v2.5 with the new partner" is a narrower bar that only RayDB currently clears.

Two structural facts drive everything below:

- **Only `raydb_style` contains any Triton integration** (67 references; all 9 others have zero). Partner usage elsewhere is CuPy (6 apps) and/or Torch (5 apps), which is the pre-v2.4 partner model.
- **The v2.5 Triton partner surface in use is segmented scalar reductions** (`count`/`sum`/`min`/`max`/`sum_count`, per the RayDB path and `execute_v2_5_partner_continuation_reference`). That shape matches only a subset of the suite. Four apps need partner operations Triton does not yet expose, and three apps have no continuation-partner phase at all.

So baseline-readiness for the new partner is really three different questions, and the suite splits cleanly into three tiers.

## 2. Readiness tiers (the actionable summary)

| Tier | Meaning for the v2.5 partner campaign | Apps |
| --- | --- | --- |
| **A — Triton-baseline-able now** | Continuation is a grouped/scalar reduction that the current Triton surface already supports; needs wiring + a run, not new partner ops | `raydb_style` (done), `triangle_counting`, `spatial_rayjoin` (count/parity), `librts_spatial_index` (count) |
| **B — Needs new Triton ops first** | Has a real continuation phase, but its shape is not in the Triton surface yet; these define the v2.5 partner-op backlog | `rt_dbscan` (grouped union-find), `rtnn` (bounded top-k / ranked summary), `barnes_hut` (grouped vector sum), `hausdorff_xhd` (grouped max + witness argmax) |
| **C — Not partner benchmarks** | No continuation-partner phase; they are RT-core / bounded-collection / count baselines and should be measured as such, not forced onto a partner | `contact_manifold` (bounded witness rows), `robot_collision` (any-hit flags) |

`librts` sits in A only because its work is count-only — it has no partner phase either, but its scalar count maps trivially onto a Triton reduction if one wants a partner row at all; realistically it belongs with the RT-core baselines too.

## 3. Cross-cutting findings

**F1 — The Triton partner surface is the binding constraint, not the apps.** The apps are mostly fine; the new partner only implements grouped scalar reductions. The suite implies a concrete partner-op backlog that v2.5 must deliver before Tier B apps can be partner baselines: grouped **union-find / connected components** (DBSCAN), **bounded top-k / ranked summary** (RTNN), grouped **vector sum** (Barnes-Hut force), and grouped **max with argmax/witness index** (Hausdorff). This list is arguably the most useful output of this review: it is the real v2.5 partner workload definition, derived from the benchmark suite rather than from RayDB alone.

**F2 — Perf-harness fragmentation undermines reproducibility.** The real warm/repeat/phase-separated timing for several flagship apps lives in dozens of one-off `scripts/goalXXXX_*.py` rather than in the app: Barnes-Hut has 15 such scripts, RayJoin 12, RayDB 8, Hausdorff 5, RTNN 4, DBSCAN 3, robot 3. The app files for `barnes_hut`, `rt_dbscan`, `librts`, and `rtnn` have effectively no in-app warm/median/phase timing (timing/phase counters near zero). A baseline you cannot re-run with one canonical command is weak as a baseline; the v2.5 campaign needs one re-runnable harness per app, not a goal-script archaeology dig.

**F3 — Some "baselines" are frozen evidence, not live harnesses.** `rtnn` explicitly reuses completed Goal2388 pod evidence; `barnes_hut` and `rt_dbscan` lean on prior pod runs and external scripts for their headline numbers. Frozen pod numbers are fine as historical context but cannot be the baseline you compare a *new* Triton run against on the same hardware in the same session.

**F4 — Category confusion risk.** Not all 10 are partner benchmarks. Treating `contact_manifold` and `robot_collision` (and arguably `librts`) as "partner perf" tests is a category error — their measured work is RT traversal + bounded collection / boolean flags / scalar counts, which is exact and small and does not hand work to a continuation partner. The campaign should explicitly separate an "RT-core baseline" track from a "partner-continuation baseline" track.

**F5 — Hardware gate, unchanged from the v2.5 contract reviews.** Triton needs `sm_70+`; the dev GPU (GTX 1070, sm_61) cannot run it, and even RayDB's hit-stream/Triton path still lacks accepted modern-pod evidence (see the Goal2687/2689 reviews). Every Tier A/B partner-baseline run is gated on a capable pod.

**F6 — Positive: correctness discipline is uniformly strong.** Nearly every app has a CPU/reference parity gate (`matches_cpu_reference`, `parity_vs_cpu_python_reference`, `all_match_*`), fail-closed overflow where relevant, and explicit claim-boundary metadata that blocks public speedup wording. As *correctness* baselines the suite is in good shape even where perf-baseline readiness is not. This is the foundation that makes the partner-swap safe once the harness and partner ops exist.

## 4. Per-app review

### raydb_style — Tier A, READY (the template)
Implementation: the most complete app. Backends span `cpu_python_reference`, `embree`, `optix`, `optix_partner_resident_experimental`, `paper_rt_cpu_reference`, `paper_rt_optix`, `paper_rt_optix_hit_stream_triton`, and the Goal2685 device-hit-stream path. Triton continuation is wired (segmented count/sum/min/max/sum_count). Phase-separated timing (17 phase sites), a duration-driven ~10s steady-state protocol, and external oracles (PostgreSQL/DuckDB/cuDF) are present, plus broad parity wiring.
Optimizations done: typed packed host buffers (no per-row `Triangle3D`/`Ray3D`), prepared payloads and prepared ray batches, device-resident query-ray columns, fused `stats` reduction, reusable app-owned table descriptor.
Not done / caveats: true device-resident hit columns and ownership/lifetime are still pending (Goal2686), no zero-copy, and the Triton/hit-stream path still needs accepted `sm_70+` pod evidence (per Goal2687/2689). It is the only app that is a v2.5-partner baseline today, and it is the correct template for the others.

### triangle_counting — Tier A, READY-WITH-GAPS
Implementation: CPU reference + `rt_graph_2a1`/`rt_graph_1a2` generic ray/triangle mappings, OptiX backend, `--partner cupy` (no Triton). Strong timing (32 sites) and authors-code (RT-Graph `bs_tc`/`rt_tc`) + cuGraph baselines on real paper datasets.
Optimizations done: app-agnostic scalar summary paths that removed row materialization (the first row-returning OptiX path was perf-negative and was dropped), CuPy partner lowering of summary construction.
Not done: no Triton wiring; segmented/streamed lowering is missing, so large datasets (`com-lj`, `soc-LiveJournal1`, `com-orkut`) OOM because two-hop relations are globally materialized; in-file parity is 0 (correctness via relabel adapter + pod evidence).
Baseline readiness: its continuation is a grouped/scalar weighted-sum — a clean fit for the current Triton surface. Ready as a correctness baseline now; to be a *partner* baseline it needs (a) Triton wiring and (b) the streaming fix, or it simply cannot run the large rows the paper cares about.

### spatial_rayjoin — Tier A (count) / Tier C otherwise, READY-WITH-GAPS as RT baseline
Implementation: PIP / LSI / overlay-seed workloads; `cpu_python_reference`, `embree`, `optix`, and a `prepared_optix` execution route with `--result-mode count|rows` and native phase telemetry (5 phase sites, 6 parity sites). No partner at all; 12 external scripts.
Optimizations done: prepared OptiX route separating query packing / scene prep / query time, bounded vertical point probe (37.9ms→9.4ms historically), raw row-view to avoid Python dict materialization, count-vs-rows modes.
Not done: no partner/Triton; overlay still on the generic dependency-row route awaiting a device-resident continuation; no in-app warm/median timing (timing=0, lives in scripts).
Baseline readiness: a solid RT-core baseline with good phase discipline. Its scalar count/parity could be routed through a Triton reduction, but nothing is wired and it has no partner phase today. Use it as an RT-traversal baseline; treat a partner row as optional.

### contact_manifold — Tier C, READY as RT/collection baseline (N/A for partner)
Implementation: tests `COLLECT_K_BOUNDED` + generic `AABB_INDEX_QUERY_2D` broadphase; CPU reference + Embree + OptiX discovery backends; `cpp_baseline` and `baseline_comparison` modes. Best-in-class in-app timing (41 sites), 6 phase sites, 9 parity sites, fail-closed overflow tests. No partner; 0 external scripts (self-contained).
Optimizations done: AABB broadphase replacing Python all-pairs discovery, OptiX native row output with fail-closed overflow, prepared discovery.
Not done: no partner/Triton — and arguably shouldn't have one: exact triangle-intersection refinement is exact, bounded host work.
Baseline readiness: a well-polished, self-contained RT + bounded-collection baseline. It is a category mismatch for a "new partner" perf test unless the exact refinement step is deliberately offloaded to a partner (not currently the design). Keep it in the RT-core track.

### robot_collision — Tier C, READY as prepared-RT baseline (N/A for partner)
Implementation: CPU reference + `embree_prepared` + `embree_prepared_buffers` + OptiX + a `--matrix` CLI. Strongest timing harness in the suite (54 sites), 7 phase sites, repeat/warmup built in. Output is compact any-hit flags. No partner; 3 scripts.
Optimizations done: prepared static scene reuse, prepared host ctypes buffers that remove repeated Python packing/allocation, sampled finite-segment probe.
Not done: OptiX still uploads query segments per run (no device-buffer reuse / zero-copy, explicitly disclaimed); no partner; CPU reference is 2D only and the 3D native contract is undecided.
Baseline readiness: a clean, well-instrumented prepared-RT baseline for any-hit flags. No continuation phase to hand a partner, so it is not a v2.5-partner test. Excellent RT-core-track baseline.

### rt_dbscan — Tier B, NOT-YET for the new partner
Implementation: the richest continuation app — `cpu_reference`, `rtdl_cpu_rows`, multiple CuPy/Torch partner modes, OptiX RT count-threshold device columns feeding CuPy grid/adjacency/grouped-stream/microcell continuations, plus two plan/explain modes. `--partner cupy|torch`, no Triton. In-app timing=0/phase=0: steady-state fairness depends on external `goal2403_rt_dbscan_repeat_probe.py`.
Optimizations done: an enormous, well-documented body — prepared RT count-threshold columns, prepared CuPy grid, directed adjacency stream, chunked/grouped-stream continuations, degree/edge-budget planner, and intersection-program culling (Goal2465/2474/2475).
Not done: no Triton — and the blocker is fundamental: its continuation is **grouped union-find / connected components**, which the v2.5 segmented-reduction surface does not implement. The fair perf number also lives in scripts, not the app.
Baseline readiness: the strongest *CuPy-partner* baseline in the suite and the most important Tier B case. It cannot be a Triton baseline until Triton gains a grouped union-find/components primitive. Its CuPy modes are the right opponent to measure any future Triton continuation against.

### rtnn — Tier B, NOT-YET
Implementation: thin (241 lines) front-door wrapper over the Goal2388 RTNN campaign; `--partner torch|cupy` (no Triton); modes are `scope`, `ann_cpu_quality`, `rtnn_known_results`. Phase=1, timing=0, parity=0; it surfaces frozen pod evidence rather than running a live perf harness.
Optimizations done (upstream): prepared uniform-cell neighbor search, ranked-summary rows avoiding neighbor-row materialization, prepared search structures, same-contract CuPy all-pairs baseline.
Not done: no Triton; bounded top-k / ranked-summary is not in the Triton surface; the app is not a re-runnable perf harness (F3).
Baseline readiness: not ready on two axes — it needs a live harness (not a wrapper over old evidence) and Triton needs a top-k/ranked-summary partner op. Good source of a same-contract CuPy opponent once a live harness exists.

### barnes_hut — Tier B, NOT-YET
Implementation: by far the largest mode menu (~20 modes from `scope`/`cpu_reference` through bucketized tree, opening frontier, `AGGREGATE_FRONTIER_COLLECT_2D`, expanded-membership Embree/OptiX, fused frontier-force-sum, prepared OptiX node coverage, and `partner_exact_force` via CuPy/Torch). `--partner torch|cupy`, no Triton. In-app timing=0/phase=0; the real CUDA timing lives in 15 `goal254x` scripts.
Optimizations done: a strong, well-measured progression — Morton/bucketized tree, DFS subtree containment (32K: 37.0ms→3.97ms), prepared resident state (3.57ms), float32 lever (0.47ms), fused frontier→vector-sum avoiding row materialization; force law correctly kept out of the engine (Goal2549 rejection).
Not done: no Triton; its continuation is a **grouped weighted vector sum**, not a scalar reduction, so the current Triton surface cannot serve it; the polished perf work is scattered across one-off scripts rather than a unified harness.
Baseline readiness: not a Triton baseline until a grouped vector-sum partner op exists; consolidate the script-based numbers into one harness. Strong CuPy/Torch baseline.

### hausdorff_xhd — Tier B, NOT-YET (but best fair-comparison instrumentation)
Implementation: the most sprawling — 4 files (~3,300 lines): a release app, a one-method CLI, a multi-method language lab, and a user-baseline helper. Methods include OpenMP, CUDA C++, CuPy RawKernel(s), `rtdl_v2_user_cuda`, and several RTDL/OptiX grouped witness methods. `--partner torch|cupy`, no Triton.
Optimizations done: X-HD-style seeded/pruned/adaptive grouped witness traversal, device-side max-distance reduction, scale-aware target group sizing. Excellent comparison metadata (`uses_rt_cores`, `exact_value`, `matches_exact_reference`) — the best fairness instrumentation in the suite.
Not done: no Triton; its continuation is a **grouped max with witness argmax**, not in the Triton surface; multiple overlapping entry files mean no single canonical harness.
Baseline readiness: not a Triton baseline until a grouped-max/argmax partner op exists; consolidate to one canonical entry. Its method-metadata pattern should be adopted suite-wide.

### librts_spatial_index — Tier A (count) / Tier C, READY as RT count baseline (N/A for partner)
Implementation: CPU oracle (+WKT), `partner_grid_reference` (generic CPU AABB, not a real partner), `optix_aabb_index` (generic OptiX AABB index for point/range-contains/range-intersects), mutation CPU reference, WKT emit for the authors' `RTSpatial` code. No GPU partner; weakest timing harness (timing=0, phase=0, 1 script).
Optimizations done: prepared-query OptiX AABB index, two-pass range-intersects, real authors-code (`RTSpatial`) pod baseline with same-fixture counts — a genuine paper-code opponent, which most apps lack.
Not done: no partner/Triton (count-only work); no in-app warm/median timing; mutation is CPU-only.
Baseline readiness: valuable specifically because it has an authors-code baseline, but it is count-only with no continuation partner and a thin timing harness. Use it as an RT-core count baseline; add a proper warm/median harness before quoting timings.

## 5. Recommendations for the parallel review/prep task

1. **Adopt RayDB as the harness template and standardize one re-runnable harness per app** (F2/F3): phase-separated timing (scene build / query prep / RT traversal / handoff / partner continuation / host materialization / total), warm median over N repeats with warmup, an in-run CPU-reference parity gate, and claim-boundary metadata. Fold the `goalXXXX_*.py` numbers into it so every baseline has one canonical command.
2. **Treat the Tier B continuation shapes as the v2.5 partner-op backlog** (F1): grouped union-find/components (DBSCAN), bounded top-k/ranked summary (RTNN), grouped vector sum (Barnes-Hut), grouped max+argmax (Hausdorff). Until Triton implements an op, the corresponding app cannot be a partner baseline — sequence the partner work against this list.
3. **Split the campaign into two tracks** (F4): an RT-core baseline track (`contact_manifold`, `robot_collision`, `librts`, `spatial_rayjoin`-rows) and a partner-continuation track (`raydb`, then Tier A reductions, then Tier B as ops land). Do not force partner numbers onto the RT-core apps.
4. **Wire the Tier A apps to Triton now** (`triangle_counting`, `spatial_rayjoin`-count, `librts`-count): their continuation already fits the segmented-reduction surface, so they can join RayDB as partner baselines with modest work — and `triangle_counting` also needs its streaming/OOM fix to run the large datasets.
5. **Build a baseline manifest**: per app, record the canonical command, fixture, backend, parity gate, the CuPy/Torch opponent the Triton run must beat (not just CPU), and the hardware (sm_70+). This makes "perf in v2.5 with the new partner" a measured, reproducible comparison rather than a collection of historical pod numbers.
6. **Keep the existing claim discipline** (F6): every partner-swap run should preserve the fail-closed and `*_authorized=False` gating already present, and compare against the same-contract CuPy/Torch baseline, not a strawman.

## 6. Bottom line

The 10 apps are, with few exceptions, well-built and well-claim-bounded — strong correctness baselines and, for several, strong RT-core or CuPy-partner baselines. But "ready to baseline against the new Triton partner" is a different and narrower property, and only RayDB has it today. Three apps have no partner phase (RT-core track), three more (plus RayDB) fit the current Triton reduction surface and need wiring, and four have continuation shapes the Triton partner does not yet implement — which is the real v2.5 partner-op backlog. Before the suite can measure v2.5 performance fairly, the project needs (a) the missing Triton partner ops, (b) one re-runnable phase-timed harness per app instead of scattered goal-scripts, and (c) an explicit RT-core-vs-partner track split with a baseline manifest naming the right opponent for each app.
