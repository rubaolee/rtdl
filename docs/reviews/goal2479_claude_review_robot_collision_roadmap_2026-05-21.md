---

## Goal2479 Robot Collision Benchmark Roadmap — Claude Review

**Date:** 2026-05-21

---

### Verdict: Approved

No blockers. Goal2479 scoping deliverables (roadmap + tests) are complete. Goal2480 implementation can start.

---

### Blocking Issues

None.

---

### Non-Blocking Issues

**1. Vacuous test assertion (`test_roadmap_sequences_cpu_reference_before_native_work`, line 39)**
`self.assertIn("existing", roadmap)` is never discriminating — "existing" appears many times. The intent is clearly to verify that compact output format is anchored to "existing RTDL buffer and tensor conventions," but splitting it into two separate `assertIn` calls leaves the first one meaningless. Suggest collapsing to a single `assertIn("existing\nRTDL buffer and tensor conventions", roadmap)` or, better, `assertIn("existing RTDL buffer and tensor conventions", roadmap)` in a single call. The second check already passes, so this is low risk, but the first check provides no policy protection.

**2. Paper anchor is title-free**
The roadmap references "*Hardware-Accelerated Ray Tracing for Discrete and Continuous Collision Detection on GPUs*, ICRA 2025 direction" without authors or DOI. This is intentional given unverified availability, but it leaves the anchor ambiguous if multiple ICRA 2025 papers touch this topic. A parenthetical "(tentative; full citation to be confirmed in Goal2480 scope)" would make the uncertainty explicit without imposing a blocker.

**3. Goal2484 warmup protocol is underspecified**
"Repeat probe drops first warmup row" does not say how many warmup rows, or whether the warm state is verified (e.g., by checking that row N and row N+1 are within a tolerance). This is fine for the roadmap level but should be tightened in Goal2484's implementation scope before measurement is done.

**4. No explicit "authors' code becomes available" protocol**
The claim boundary correctly blocks comparison until code/data are verified, but the roadmap has no explicit decision path for what to do if the ICRA authors publish code between now and Goal2485. A one-line non-goal such as "If authors' code becomes available, comparison requires a separate scoping goal before any claims" would close the gap without adding complexity.

---

### Boundary Assessment

The app-agnostic native boundary is well-enforced at both the document and test levels.

- The forbidden vocabulary list (`robot`, `link`, `pose`, `joint`, `kinematics`, `planner`) and the extended `collision`-avoidance rule are explicit, and the tests assert every token.
- The allowed native vocabulary (`intersection`, `overlap`, `hit`, `any_hit`, `prepared/reused build acceleration structures`, `batched query groups`, `compact per-query output columns`) is precise and reusable beyond robot collision — it fits CAD interference, game physics, or any dynamic-transformed-geometry workload.
- Python ownership of robot semantics (pose generation, transform matrices, collision policy, per-link summaries) is unambiguous.
- Goal2481's open design question on compact output format (byte-per-query vs. bit-packed vs. typed partner/native column) is correctly framed as an alignment decision against existing RTDL buffer/tensor conventions, not a robot-link convenience choice. Gemini's suggestion was incorporated and is visible in both the roadmap (lines 110–112) and the test (line 38).

The boundary is among the cleaner ones in the RTDL roadmap corpus.

---

### Sequencing Assessment

The eight-goal sequence is technically coherent and appropriately risk-averse.

| Goal | Stage | Gate |
|---|---|---|
| 2479 | Scope + claim policy | This document; complete |
| 2480 | CPU reference app | No native code touched |
| 2481 | Generic contract design | Native work blocked until reviewed |
| 2482 | Embree prototype | Correctness against CPU reference |
| 2483 | OptiX prototype | Pod correctness artifacts required |
| 2484 | Prepared/reused execution | Phase-separated timing; warmup dropped |
| 2485 | Performance matrix | Internal only; no public speedup wording |
| 2486 | Continuous collision feasibility | Design-only unless primitive is clearly small/generic |
| 2487 | Closeout | External review of app-agnostic boundary |

The explicit gate "Do not start native Embree/OptiX work until the CPU reference app and generic contract design are reviewed" (roadmap line 242) is present and tested. The continuous collision deferral in Goal2486 is correct — swept/interval primitives are a distinct design question that should not block the discrete contract.

**On robot collision vs. RayDB ordering:** The argument is sound. The existing RTDL app corpus (RayJoin, RTNN, Hausdorff/X-HD, RT-DBSCAN) establishes static-scene traversal and batched nearest-neighbor patterns. Robot collision introduces genuinely new design pressure: dynamic transformed query geometry submitted against a prepared static build, compact any-hit flags as a first-class output, and eventually continuous swept queries. RayDB would primarily exercise range/join patterns already exercised by RayJoin-style work. The ordering is justified.
