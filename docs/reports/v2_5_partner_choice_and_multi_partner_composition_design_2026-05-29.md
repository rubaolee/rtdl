# RTDL Design Report: Partner Choice Belongs to the App, and Multi-Partner Composition Is First-Class

Author: Claude (independent design analysis)
Date: 2026-05-29
Status: design position / prerequisites note for the v2.5 runtime
Companion docs:
- `docs/reviews/v2_5_goal_scoping_triton_runtime_and_tiered_benchmark_parity_2026-05-29.md`
- `docs/reviews/v2_5_ten_benchmark_apps_baseline_readiness_review_2026-05-29.md`
- `docs/reviews/goal2689_claude_rereview_goal2688_hit_stream_contract_hardening_2026-05-29.md`

## 1. Thesis

RTDL is a language. The language's job is to let an app author (call them X) express a workload over generic, app-agnostic engine primitives and then *choose* how each phase is continued. Three principles follow, and this report argues all three are correct, shows what each one actually requires to be true, and flags where the current v2.5 code does not yet satisfy them.

1. **Partner selection is the app's choice.** The engine and the runtime must not pick X's continuation partner.
2. **No partner is ever forced.** If a partner (e.g., Triton) is unsuitable for an app or a phase, the language must never compel X to use it, and the app must still run.
3. **Multi-partner composition is first-class.** A single app may use different partners for different phases (native traversal, Triton reduction, CuPy union-find, …), composed over neutral handoff contracts.

These are not aspirational extras. They are the direct logical consequence of RTDL's foundational rule — *the native engine is app-agnostic and Python owns orchestration*. An engine that does not know the app has no business choosing the app's partner, and a language that forces one partner has silently re-coupled itself to a specific runtime.

## 2. Why these follow from the existing architecture

RTDL already commits to: app-agnostic native engines; a partner-continuation protocol where RT traversal stays native and continuation moves to a partner; generic data contracts at the boundary (`RtdlBufferDescriptor`, typed hit-stream/payload columns); and a universal CPU/reference path (`cpu_python_reference`, `allow_reference_fallback`). The three principles are just that architecture taken to its conclusion:

- If the engine is app-agnostic, partner choice cannot live in the engine → it lives with X (Principle 1).
- If there is always a reference path, no partner is structurally mandatory → forcing one is a regression, not a requirement (Principle 2).
- If the boundary is a generic contract, the output of one partner can be the input of the engine or another partner → phases can mix partners (Principle 3).

So the design question is not *whether* to adopt these principles, but *what they require to be real* — because stating them is easy and delivering them is not.

## 3. Principle 1 — Partner selection is the app's choice

### 3.1 What it means
X declares *what* each phase computes (a generic primitive: traversal, reduction, components, top-k) and *which partner* executes the continuation. The runtime supplies good defaults and the information to choose, but never overrides X and never hardcodes a partner inside a primitive or an app path.

### 3.2 What it requires
A **partner-neutral handoff**. The engine's output must be expressible as a buffer any partner can consume — CuPy, Torch/Triton, a raw CUDA kernel, or the CPU reference — without the seam assuming one of them. The right mechanism is a neutral device-buffer descriptor (DLPack and/or `__cuda_array_interface__`) plus typed column metadata, which is exactly what `RtdlBufferDescriptor` (dtype, shape, device, `data_ptr`, `source_protocol`, lifetime) was started to be.

### 3.3 Where the current code violates it
The v2.5 hit-stream handoff does **not** yet hand out a neutral buffer. `_maybe_torch_column` (`src/rtdsl/hit_stream_handoff.py`, ~lines 526–551) coerces every column to a torch tensor, and `gather_typed_payload_columns_for_hit_stream` (~lines 343–394) branches on `_is_torch_tensor(...)` and does `torch.as_tensor(...)`. The contract advertises `source_protocol` values for `numpy`/`cupy`/`cuda_array_interface`, but the actual data handling is torch-centric. The practical effect: a CuPy or raw-kernel partner is run through a torch conversion that may not be zero-copy, and "X's free choice of partner" is quietly narrowed to "torch/Triton, or pay a conversion." This is a real, fixable leak, and it must be closed for Principle 1 to hold rather than merely be claimed.

## 4. Principle 2 — No partner is ever forced

### 4.1 What it means
Triton is one partner, not the partner. If an app or a phase is a poor fit for Triton, the language must let X pick something else, and the app must still execute end-to-end.

### 4.2 What it requires
- **A universal partner-free path.** Every primitive needs a CPU/reference continuation so an app runs with no partner, an unavailable partner, or a deliberately chosen non-GPU partner. RTDL already has this pattern (`cpu_python_reference`, `allow_reference_fallback`); the requirement is to keep it *universal* — every new partner op must ship with its reference path.
- **No partner hardcoded in a primitive or app path.** Partner selection must be a parameter at the continuation boundary, never a constant inside the engine or the lowering.

### 4.3 Why this resolves the DBSCAN tension cleanly
The earlier scoping doc framed DBSCAN keeping CuPy union-find as a "fallback" or an "accepted miss." Under Principle 2 that framing is wrong: DBSCAN using CuPy for its union-find phase is **X choosing the right partner for that phase** — the language working as designed, not a concession. The same applies to the two non-partner apps (`contact_manifold`, `robot_collision`): they choose *no* continuation partner because their work is exact bounded collection / any-hit flags. None of these are gaps. Forcing Triton onto any of them would be the actual defect, because it would contradict the language's own premise.

## 5. Principle 3 — Multi-partner composition is first-class

### 5.1 What it means
A realistic app is already multi-partner across phases. Example pipeline:

```
native OptiX RT traversal           (engine)
  -> generic (ray_id, primitive_id) hit columns        [neutral handoff]
  -> Triton grouped sum/count                            (partner A)
  -> generic grouped columns                            [neutral handoff]
  -> CuPy union-find / components                        (partner B)
  -> app result                                          (Python)
```

The language should let X select the partner at each continuation boundary independently, composing over the generic columns.

### 5.2 What it requires (the hard part)
This is the least *free* of the three principles, because composition multiplies the obligations:

1. **Cross-partner lifetime/ownership.** This is the unsolved problem from the Goal2689 review, amplified. With a single producer it is already only metadata (`ownership_lifetime_model = "native_owner_state_machine_required_before_promotion"`). With mixed partners it becomes cross-framework: if phase A produces CuPy buffers and phase B is Triton/torch, who allocates, who retains across the boundary, who frees, and is the handoff zero-copy or a silent copy? Multi-partner apps cannot be shipped honestly until there is an ownership model at the boundary that spans frameworks.
2. **A neutral data contract at *every* handoff.** Principle 3 is Principle 1 applied at each internal boundary, not just at the engine edge. Each partner's output must be re-expressible as a neutral buffer the next partner (or the engine) can take. This is the same DLPack/CUDA-array-interface requirement, repeated per boundary.
3. **A declared, conformance-tested support matrix.** "X's choice" must mean "X's choice among (partner × op × backend) combinations the runtime declares and tests," not "anything goes." Free composition without a declared matrix is undefined behavior. The matrix is the boundary between honest freedom and a combinatorial test gap.
4. **Capability and cost metadata + plan/explain.** X must be able to see what each partner is good at, or "your choice" is choosing blind — a usability failure. The seeds already exist: per-run claim metadata, and the `planned_rt_dbscan` / `planned_rt_dbscan_continuation` plan/explain modes that record selected mode, reason, and evidence. Generalize that into a partner-capability/cost surface so X (or an optional planner) can reason per phase.

### 5.3 The freedom-vs-conformance tension
Maximal composition freedom multiplies the conformance surface: every (partner, op, backend) is a test cell, and every cross-partner boundary is a lifetime/transfer case. The resolution is not to restrict X's choice but to **declare** the supported cells and test them, and to mark unsupported compositions as explicitly out-of-contract rather than silently broken. Freedom is only honest when its supported envelope is published.

## 6. The two prerequisites that block this today

Everything above reduces to two pieces of engineering that v2.5 currently lacks:

| Prerequisite | Current state | Consequence if unmet |
| --- | --- | --- |
| **Neutral buffer seam** (DLPack / `__cuda_array_interface__` at every handoff, no torch coercion) | Partially present as `RtdlBufferDescriptor`; violated by torch-coercion in `hit_stream_handoff.py` | "X's choice" and multi-partner mixing are narrowed to torch, or pay hidden copies |
| **Cross-partner ownership/lifetime model** | Metadata-only string; no state machine even for one producer | Multi-partner apps risk use-after-free / double-free / silent copies; cannot be shipped honestly |

Neither is exotic, but neither is free, and both are *upstream* of the per-app parity work. Sequencing the parity campaign before these are in place would build measurements on a seam that still assumes one partner.

## 7. Implications for the v2.5 goal

These principles improve and re-scope the stated v2.5 goal ("make the 10 apps run on Triton at v2.4 parity"):

- The honest goal is **not** "the 10 apps on Triton." It is "**Triton is one well-optimized partner; each app composes the best partner(s) per phase over neutral handoff contracts**, and v2.5 proves Triton is excellent for the reduction-shaped phases and composes cleanly with others."
- **Tier C apps** (`contact_manifold`, `robot_collision`) choosing no partner is the design working, not a coverage gap.
- **DBSCAN** keeping CuPy union-find is X's correct per-phase choice, not a fallback.
- **Tier A apps** (raydb, triangle_counting, rayjoin-count, librts-count) are where Triton-as-chosen-partner is demonstrated at parity.
- Parity claims should therefore be **per-phase and per-partner**, not per-app-monolithic: "Triton matches CuPy on the grouped-reduction phase," not "Triton matches the app."

## 8. Concrete recommendations

1. **Close the neutral-buffer seam first.** Replace torch coercion in the hit-stream/payload handoff with a neutral descriptor (DLPack + `__cuda_array_interface__`) and make every partner adapter consume that, including a zero-copy path where the protocol allows and an explicit, labeled copy where it does not. Until this lands, "X's choice" is not real.
2. **Specify a cross-partner ownership/lifetime model** before wiring multi-partner pipelines: allocation owner, retention across each boundary, release point, overflow/failure cleanup, and whether each boundary is zero-copy or a declared copy. Make the copy/zero-copy status machine-readable, consistent with the existing `*_authorized=False` discipline.
3. **Make partner selection an explicit per-boundary parameter** in the app/runtime API, defaulting sensibly but never hardcoded in a primitive. Keep the CPU/reference continuation universal for every op.
4. **Publish a declared support matrix** of (partner × op × backend) cells with conformance tests; mark everything else out-of-contract rather than silently failing.
5. **Generalize plan/explain into a partner-capability/cost surface** so X can choose per phase with guidance, and so an optional planner can suggest (never impose) a composition. Reuse the rt_dbscan plan/explain precedent.
6. **State parity per phase/partner**, not per app, in the benchmark campaign, and name the same-contract opponent for each phase.

## 9. Acceptance criteria (what "done" looks like)

- Any benchmark app can run a phase on CPU-reference, Triton, or CuPy by changing one explicit selection parameter, with identical results within the contract's tolerance.
- A single app demonstrably runs two different partners in two phases (e.g., Triton reduction → CuPy components) with a documented, enforced ownership/lifetime model and machine-readable copy/zero-copy status at the boundary.
- No primitive or app path contains a hardcoded partner; removing all partners still yields a correct (if slower) run.
- The supported (partner × op × backend) matrix is published and conformance-tested; unsupported cells fail closed with a clear message, not undefined behavior.
- The handoff seam carries a neutral buffer; no partner is privileged by a silent conversion.

## 10. Risks and tensions

- **Cross-framework copies masquerading as zero-copy.** The biggest honesty risk: a "neutral" handoff that silently copies between frameworks. Must be measured and labeled, never assumed.
- **Conformance combinatorics.** The (partner × op × backend) matrix grows fast; manage it by declaring a supported subset, not by chasing every cell.
- **Planner overreach.** A cost-model planner must *advise*, never *impose* — the moment it forces a partner it violates Principles 1–2. Keep it opt-in and explainable (the existing plan/explain pattern is the right shape).
- **Lifetime bugs are the dangerous failure mode.** Cross-partner use-after-free/double-free are correctness/safety bugs, not perf bugs; gate multi-partner composition on the ownership model, not on benchmark numbers.

## 11. Bottom line

All three principles are correct and they are the natural endpoint of RTDL's app-agnostic-engine philosophy: partner choice is X's, no partner is ever forced, and one app may mix partners across phases. Adopting them sharpens the v2.5 goal — Triton becomes one excellent, freely-chosen partner rather than a mandatory runtime, and the apps that pick another partner or no partner are the design working, not gaps. But the principles are far more demanding to *deliver* than to *state*. Two prerequisites are upstream of everything else and are not satisfied today: a genuinely neutral buffer seam (the current handoff leaks toward torch) and a cross-partner ownership/lifetime model (currently metadata-only). Build those two first; then per-phase, per-partner parity over neutral contracts becomes a measurable, honest claim instead of an architectural promise.
