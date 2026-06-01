# Gemini Review: Goal2981 v2.5 Closeout Positioning and External Review Packet

Date: 2026-06-01
Status: Reviewed and verified; **not release-authorizing**

## Verdict

**`accept-with-boundary`**

The Goal2981 closeout packet (`docs/reports/goal2981_v2_5_closeout_positioning_and_external_review_packet_2026-06-01.md` plus Goals 2978-2980) is accepted under the strict condition that it remains an internal engineering assessment and **does not constitute release authorization**. The positioning of v2.5 is verified as honest, evidence-supported, and appropriately bounded.

---

## 1. Positioning Verification

The v2.5 positioning is verified as:
* **Primitive-first**: Fused native RTDL primitive execution is the fast path when a fused generic primitive exactly expresses the requested continuation.
* **Partner-only-for-unfused**: Typed hit-stream and partner continuations are reserved strictly for unfused/irregular work or explicit user/app choice.
* **Neutral-seam-scope-out**: Full partner-neutral composition and DLPack/CUDA-array-interface integration are scoped out, acknowledging that multi-partner composition is scaffolded but not delivered in v2.5.

This is a major and necessary shift from the original "Triton-first" framing, which is now disconfirmed by empirical performance evidence.

---

## 2. Evidence Consistency (Goal2979)

The RTX 4000 Ada pod results from Goal2979 fully support the primitive-first selection doctrine:
* **RayDB scalar grouped reduction**: Forcing the typed hit-stream + Triton path yields a **28.5x to 175.1x slowdown** compared to the native primitive-first path (`0.000384s` vs `0.016848s` for 250k count, and `0.001984s` vs `0.347557s` for 250k sum). This validates that primitive-first must remain the default when native fusion is possible.
* **RT-DBSCAN grouped-stream continuation**: Under an unfused shape, the partner route is necessary and correct, demonstrating a **3.8x to 4.9x speedup** over the prepared CuPy grid baseline while successfully avoiding full neighbor-row/adjacency-stream materialization.
* **Grouped vector-sum partner choice**: A same-contract head-to-head comparison shows CuPy `add_at` is the winner (`0.000381s` median), while Triton JIT is significantly slower (`0.004901s`), reinforcing the policy that partner choice must be evidence-driven and Triton is never auto-selected simply because it is available.

---

## 3. Seam Decision Evaluation (Goal2980)

Goal2980's decision to choose option **C-3b (Scope Out)** is accepted as the most honest engineering choice for v2.5. Rather than claiming full multi-partner zero-copy composition, the codebase explicitly registers that:
* PyTorch acts as a bounded launch carrier for Triton-only paths, rather than a neutral interface.
* Non-Triton partners route through descriptors.
* Full partner-neutral composition and native device-resident hit-stream output are formally deferred to v3.0, aligning with the "residency-first" roadmap.

---

## 4. Overclaim and Boundary Audit

There are **zero overclaims** identified in the reviewed reports. All strict boundaries are correctly maintained:
* **Release Status**: Clearly marked as "no release authorization."
* **Wording Blocks**: The following claims remain strictly blocked:
  - Automatic Triton selection or Triton performance wins.
  - Public speedup claims.
  - Broad GPU/RT-core speedup claims.
  - Whole-app performance speedups.
  - True zero-copy claims.
  - Paper-reproduction claims.
  - Package-installation promises.
* **App-Agnosticism**: No application-specific native customization has leaked into the core engine.

---

## 5. Remaining Work Before Release

To progress from this closeout review to a formal release packet:
1. **Resolve the Goal2977 second-architecture packet gap**: Decide on a canonical solution for the Barnes-Hut 8192-body Embree CPU baseline bottleneck to ensure we have a clean release packet.
2. **Compile the v2.5 Release Packet**: Gather all triaged benchmarks (including the 10-app triage state) and verify toolchain scope conformity.
3. **Execute 3-AI Consensus Pass**: Trigger the final consensus review between Codex, Claude, and Gemini.

---

## Formal Release Boundary Notice

> [!WARNING]
> This review is an internal technical assessment of Goals 2978-2981. It does **NOT** authorize a v2.5 release, does not permit the creation of a release tag, and does not authorize any public speedup, zero-copy, or broad hardware-acceleration claims.
