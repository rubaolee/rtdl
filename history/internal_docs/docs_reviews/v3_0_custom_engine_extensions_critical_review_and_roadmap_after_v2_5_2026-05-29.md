# Critical Review of RTDL v3.0 and a Roadmap To It (Assuming v2.5 Partner-Triton Work Is Complete)

Reviewer: Claude (fresh independent reviewer)
Date: 2026-05-29
Premise set by the request: treat the v2.5 `Python + RTDL + Triton` partner-continuation work as finished and validated.

Primary v3.0 sources read:
- `docs/reports/v3_0_custom_engine_extensions_concept.md` (2026-05-11, "Exploratory / Long-Term Planning")
- `docs/reviews/v3_0_custom_engine_extensions_concept_claude_analysis_2026-05-11.md`
- `docs/reports/v3_0_frechet_lab_lessons_after_v1_8_2026-05-12.md` and its consensus (`..._consensus_2026-05-12.md`)
- `docs/research/future_version_to_do_list.md` (the "v3.0+ Architecture Ideas" section and the per-family "does not require v3.0 shader injection" boundaries)

v2.5 substrate read for grounding: `src/rtdsl/hit_stream_handoff.py`, the Goal2684/2685/2688 reports, the primitive catalog, and prior reviews `goal2687_...` / `goal2689_...`.

## 1. What "v3.0" actually means in the old docs

There is one consistent v3.0 thesis across the documents: **Custom Engine Extensions** — user-authored, hardware-accelerated ray-tracing logic injected into a "pristine, app-agnostic" native engine. The concept doc frames five ingredients:

1. A "pure motherboard" native core that only does device/memory management, BVH build, and ray dispatch.
2. Payload "slots" — `columnar_payload` reused as a standardized memory layout users pack arbitrary data into.
3. Dynamic custom shader injection — user OptiX PTX, Vulkan SPIR-V, Metal `.metallib`.
4. A Python extension API (`rt.load_extension(...)`, `rt.create_columnar_payload(...)`, `rt.run_custom_scan(...)`).
5. A long-term Python→PTX/SPV JIT ("Triton for ray tracing").

The causal claim is that the v1.6–v1.8 vocabulary-stripping ("removing `db`/`polygon`/`knn`") is what makes this possible: "A polluted core engine could never support third-party plugins."

The Fréchet lab note (2026-05-12) already softened this into a more honest mental model: `Extension = typed device payload contract + backend shader entry contract + compact output contract + conformance tests + cost-model/fallback story`, and explicitly flagged that "shader injection alone is not enough." The future-version to-do list repeatedly tags concrete work (RTNN neighbor search, RT-DBSCAN continuation, RayJoin first-hit, Hausdorff) as *not* needing v3.0 shader injection — i.e., the team has been careful to keep v3.0 narrowly scoped to user-defined predicates, not as a catch-all.

So the canonical v3.0 goal, stated tightly: **let third-party users inject custom device-side intersection/any-hit predicates and typed payloads into the RTDL pipeline across backends, with a safe, versioned, conformance-tested contract — and eventually JIT them from Python.**

## 2. Verdict

**needs-more-evidence; keep v3.0 exploratory, and re-scope it around the partner-vs-extension boundary before any engineering hours are committed.** Direction is sound; framing and sequencing are wrong for where the project now is.

The 2026-05-11 review parked v3.0 until "v1.8 and v2.0 ship with hardware evidence and the v2.5 product checkpoint clears." With v2.5 now assumed complete, that gate is nominally met — but completing v2.5 has *changed the case for v3.0 more than it has advanced it*. Three things follow from the v2.5 work that the original concept did not anticipate:

- v2.5's partner-continuation model is a **competing and safer answer** to most of what v3.0 set out to enable, which shrinks v3.0's justified scope to a narrow band (intra-traversal custom predicates).
- The v2.5 evidence base reinforces that **RT traversal is not the bottleneck** for RTDL's target workloads, which undercuts v3.0's core value proposition (let users go faster by injecting RT-core shaders).
- v2.5 demonstrated, on its own much smaller contract, that the **hard parts of v3.0 (ownership/lifetime, hardware proof, claim discipline, contract stability) remain unsolved** — so v3.0 inherits unsolved problems, not a cleared runway.

Details below, then a roadmap that treats v3.0 as the end of a gated sequence rather than a next release.

## 3. What completing v2.5 genuinely strengthens

Crediting the progress honestly: v2.5 built several of the exact ingredients the 2026-05-11 review listed as *missing* for an honest v3.0.

- **A first device-side payload contract exists.** `RtdlTypedPrimitivePayloadColumns` (typed `primitive_group_ids:int64` / `primitive_values:float64`) plus `RtdlBufferDescriptor` (dtype, shape, device_type/id, `data_ptr`, `source_protocol`, `lifetime`, `mutability`, `capacity_elements`) are the embryo of the "device-side `RtdlExtensionPayload` schema" Section 6 of the old review asked for. The concept doc's claim that `columnar_payload` is already a device payload slot was an overstatement then; v2.5 has now started building the real thing.
- **The partner protocol sharpened the host-side continuation boundary** the Fréchet note said was a prerequisite: RTDL owns traversal, partner owns continuation, buffers are explicitly borrowed/owned, output schema is explicit, and acceleration claims are gated. That is exactly the discipline a healthy extension program needs.
- **A governance model is in place.** The primitive catalog's promotion pipeline (`app code → candidate → experimental → stable`, with app-name-free semantics, typed schemas, overflow policy, backend parity, and mandatory external review) is a ready-made conformance framework that v3.0 extensions could be required to pass.
- **A claim-gating and fail-closed culture exists** (Goal2687/2689 enforced `true_zero_copy_authorized=False`, fail-closed overflow at two layers, machine-checkable maturity flags). This is the right immune system for a feature as over-narratable as "custom shader injection."
- **There is an existence proof that device-side custom predicates are real and valuable.** Goal2465/2474/2475 moved custom culling predicates *into the OptiX intersection program* — reading union-find roots and skipping `optixReportIntersection` for already-connected pairs — for ~19% native gains. That is precisely the "user wants a custom intersection predicate" case, executed by the core team. It is the single strongest motivation for v3.0: let users do what those goals did, without forking the engine.

## 4. Critical weaknesses, updated for the post-v2.5 reality

### 4.1 v2.5 partner continuation is a competing answer; v3.0 must re-justify its narrowed scope
The original concept pitched shader injection as the way to let users add "custom spatial filters, payload handlers, collision algorithms." v2.5 now lets users express a large fraction of that as **partner continuation over generic RT-produced columns** — no device-ABI commitment, no engine pipeline coupling, runs in Triton/torch the user already trusts. The honest consequence: v3.0 is only justified for logic that *must run inside traversal* (custom intersection/any-hit predicates whose work cannot be deferred to a post-traversal continuation without losing the pruning benefit). Everything else should be steered to the partner path. The v3.0 concept does not draw this line; until it does, v3.0 and v2.5 compete for the same conceptual slot, and most candidate use-cases will be better served by the partner track that already ships.

### 4.2 v3.0 accelerates the phase v2.5 evidence says is not the bottleneck
Two independent v2.5-era data points say RT traversal is cheap and the cost is elsewhere: the RayDB 100k case (RT traversal 0.0048 s vs host materialization 0.81 s) and the Fréchet lab (the broadphase added launch/orchestration cost without removing enough downstream work because most free-space cells survived). Custom device-side shader injection speeds up *traversal and intersection* — the already-cheap phase for these analytics-shaped workloads. So v3.0's headline value ("democratize hardware-accelerated BVH compute") collides with the project's own measurements. v3.0 is most valuable exactly where pruning is strong and traversal dominates (classic rendering-like or strong-rejection geometry); it is weakest for the data-analytics workloads RTDL has been benchmarking. This must be stated, or v3.0 will be sold on a benefit the target workloads don't realize.

### 4.3 The ABI-freeze risk is now worse, because the contract is still churning
The 2026-05-11 review's top risk was that publishing an extension ABI freezes the engine. v2.5 makes this sharper: the *generic hit-stream handoff contract itself was reshaped three times in roughly a month* (Goal2684 row contract → Goal2685 typed columns → Goal2688 hardening of metadata/validation/maturity). An engine whose own internal generic contract is iterating weekly is nowhere near able to publish a frozen *device-side, third-party-facing* shader ABI. Contract-stability soak time (multiple releases without breaking change) is a hard precondition for v3.0 that the project has not begun to accrue.

### 4.4 The hardest v2.5 problem — ownership/lifetime — is unsolved and v3.0 amplifies it
v2.5 could not implement a buffer ownership/lifetime state machine even for a single generic hit-stream handoff; it remains metadata-only (`ownership_lifetime_model = "native_owner_state_machine_required_before_promotion"`, per Goal2689). v3.0 requires the engine to manage the lifetime of *user-shader-produced* buffers across pipeline builds, continuations, overflow, and faults — strictly harder than the single-producer case v2.5 has not yet closed. v3.0 cannot start while its prerequisite (a working lifetime model for the simple case) is open.

### 4.5 Safety/sandboxing remains unaddressed and the trust model is different from partners
The partner track is comparatively safe: Triton/torch kernels are separate, user-owned, already-trusted code operating on borrowed columns. Shader injection puts arbitrary user device code *inside the engine's own ray pipeline*, sharing occupancy, register pressure, SBT layout, and continuation-stack budgets — with no isolation primitive in OptiX/Vulkan/Metal RT comparable to CUDA stream cancellation. v2.5's fail-closed overflow discipline is a good start, but it governs the engine's own bounded buffers, not arbitrary user shaders that can hang, fault, or read out of bounds. This is an unsolved precondition, not a detail.

### 4.6 Cross-vendor parity has not even begun
v3.0 lists OptiX PTX + Vulkan SPIR-V + Metal `.metallib` as co-equal artifacts. v2.5 evidence is OptiX (NVIDIA) + Embree (CPU reference) only — no Vulkan, no Metal, no HIPRT, and not even a second GPU *vendor*. Cross-vendor shader injection is at least three independent engineering programs plus a shared load/compile harness and a per-backend conformance fabric (per the 2026-05-11 review §4.3, still true). v2.5 has not proven the *generic, non-shader* contract on a second vendor, so cross-vendor shader injection is two abstraction levels ahead of current evidence.

### 4.7 The "PCIe slot" metaphor and the causal claim are still wrong
Unchanged from 2026-05-11 and worth restating because the concept doc still leads with them. Ray-tracing extensibility is shader-binding-table records pulled at pipeline build time, tightly coupled to engine internals — not hot-pluggable PCIe cards. And "v1.8 cleanup unlocked v3.0" is overstated: extension APIs sit on app-shaped engines all the time (PostgreSQL, SQLite, PyTorch C++ extensions). The cleanup reduced the per-extension surface area; it did not unlock a previously impossible capability. v2.5 reinforces the correction: the cleanup's real payoff showed up as the *partner* contract, not as shader plug-ins.

### 4.8 Python JIT is still a separate, later program
Unchanged: Python→PTX/SPV JIT for ray-tracing shaders (intersection/any-hit/recursive ray-tree control flow per backend) is v4.0+ scope and should be split out of v3.0 entirely so v3.0 is evaluable on its own merits.

## 5. Roadmap from "v2.5 complete" to v3.0

The sequence below is gated: each phase must clear before the next earns hours. Phases 0–1 are mandatory before any v3.0-labeled engineering. The whole path is plausibly multi-release; do not compress it into a single version bump.

### Phase 0 — Finish the v2.5 promises that v3.0 depends on (no v3.0 branding)
Preconditions v3.0 cannot proceed without:

1. **Native CUDA device-resident hit columns** (the Goal2686 slice): real OptiX output writing bounded `ray_ids:int64`/`primitive_ids:int64` into CUDA buffers, with `source_mode="native_device_columns"` actually exercised on hardware.
2. **A working ownership/lifetime state machine** for the single-producer case: allocation owner, retention through continuation, release point, overflow cleanup, failure cleanup. This is the §4.4 blocker.
3. **`sm_70+` pod evidence** for the device path across count/sum/min/max/avg with separated phase timings, plus a reduction-tolerance policy so correctness checks survive at scale.
4. **Contract-stability soak**: the generic device-column + typed-payload contract must go ≥2 releases with no breaking change. This buys the right to consider freezing anything third-party-facing (§4.3).

Exit gate: device-resident generic path proven on hardware, lifetime model implemented, contract demonstrably stable. External (distinct-AI) review per the Goal1683 consensus rule.

### Phase 1 — Draw the extension-vs-partner boundary and prove v3.0 is necessary
Before building anything, settle §4.1:

- Write the decision contract: which workloads belong to **partner continuation** (post-traversal, host- or device-side) and which genuinely require **device-side intra-traversal injection**. Default everything to the partner path.
- Produce a concrete existence proof: at least one workload where a custom *intersection/any-hit* predicate (the Goal2474/2475 pattern) beats the best partner-continuation formulation by a margin that justifies a device ABI commitment, *with the §4.2 caveat measured* (show that traversal is actually the bottleneck for that workload).
- If no such workload clears the bar, **v3.0 should remain parked** — the partner track is the answer. This is a real possible outcome and the roadmap should respect it.

Exit gate: a documented boundary plus ≥1 measured workload that needs intra-traversal injection. Distinct-AI review.

### Phase 2 — Device-side payload schema (single backend)
Generalize v2.5's typed columns into a true `RtdlExtensionPayload`: typed strides, lane count, alignment contract, optional validity mask, per-backend memory-class hints — distinct from the host-side descriptor. OptiX only. Reuse `RtdlBufferDescriptor` and the catalog promotion pipeline as the governance spine.

Exit gate: payload schema with conformance tests on OptiX + CPU reference; no app vocabulary; fail-closed on malformed payloads.

### Phase 3 — Single-backend shader entry + loading + versioning + safety (OptiX)
The core of v3.0, deliberately one backend first:

- Shader entry signatures (intersection/any-hit/closest-hit/miss) with documented payload-size and continuation-stack budgets.
- A hash-pinned PTX loading contract: artifact discovery, version pinning, mandatory entry-point metadata.
- An **engine-ABI versioning policy** stating how often the pipeline contract may change and what authors can rely on across RTDL versions (directly answers §4.3).
- A **safety story**: shader timeout/hang policy, fault behavior, SBT-exhaustion handling, and explicit, documented disclaimers where recovery is impossible (answers §4.5).
- A per-backend conformance fabric wired into CI, with the partner-style independent-review requirement.

Exit gate: a third party can author, load, version-pin, and run a custom OptiX predicate against a conformance suite, with safety behavior documented and tested. Distinct-AI review + pod evidence.

### Phase 4 — Second backend (the real cross-vendor gate)
Add exactly one more backend — CPU/Embree intersection functions as the conservative choice, or Vulkan SPIR-V if a cross-vendor GPU story is the priority. The point is to prove the Phase 2–3 contracts are genuinely backend-portable rather than OptiX-shaped (§4.6). Treat Metal/HIPRT and any further vendors as separate later increments, each its own program.

Exit gate: the same extension contract passes conformance on two backends with no OptiX-specific assumptions leaking into the public ABI.

### Phase 5 — (Separate concept, v4.0+) Python→shader JIT
Spin out entirely (§4.8). Do not let it gate or define v3.0.

## 6. Risk register (post-v2.5)

| Risk | Severity | Note |
| --- | --- | --- |
| v3.0 duplicates the v2.5 partner track | High | Without the Phase 1 boundary, most use-cases are better served by partner continuation; v3.0 builds a riskier path to the same place. |
| v3.0 optimizes a non-bottleneck for target workloads | High | RayDB/Fréchet evidence: traversal is cheap; materialization/continuation dominate. Value is real only where traversal/pruning dominates. |
| ABI freeze on a still-churning contract | High | The generic handoff changed 3× in a month; freezing a third-party device ABI now would ossify the engine prematurely. |
| Ownership/lifetime unsolved | High | Open even for the single-producer v2.5 case; v3.0 needs it for arbitrary user-shader buffers. |
| User-shader safety / GPU hangs | High | No isolation primitive in OptiX/Vulkan/Metal RT; different trust model from trusted partner kernels. |
| Cross-vendor parity treated as one feature | High | Two abstraction levels ahead of current single-vendor-GPU evidence. |
| Claim-surface explosion | Medium | Per-extension, per-backend perf claims multiply the overclaim risk v2.5 had to police hard. |
| Distraction from finishing v2.5/v2.x | Medium | Phase 0 work is the binding gate; v3.0 attention competes with it. |

## 7. Bottom line

The v3.0 instinct — a clean app-agnostic engine is a better host for third-party extensibility than an app-shaped one — is correct, and v1.8 + v2.5 have built real substrate toward it (device payload embryo, partner boundary, governance pipeline, claim discipline, and an internal existence proof in Goal2474/2475). But completing v2.5 reframes v3.0 rather than greenlighting it: the partner-continuation model now answers most of v3.0's original motivation more safely, the project's own measurements show RT traversal is rarely the bottleneck for its target workloads, and the hard problems (lifetime, hardware proof, contract stability, safety, cross-vendor) are either unsolved or unstarted. Keep v3.0 exploratory. Re-scope it to the narrow, genuinely-justified case of user-defined intra-traversal predicates, gate it behind finishing the v2.5 device path and a lifetime model (Phase 0) and an evidence-backed extension-vs-partner boundary (Phase 1), and build it one backend at a time. Split the Python JIT into a separate v4.0 concept. The honest one-line position: **v2.5 didn't open the door to v3.0 — it showed that most of what walked through that door belongs in the partner track, and that the part that doesn't still needs every prerequisite v3.0 has always needed.**
