# RTDL V4.0 Design — The Three-Tier Fused Architecture

Date: 2026-06-24
Author: Claude (independent reviewer), hardening the Codex/architecture-pivot dialogue
Status: **design proposal for architecture review — not a release/POD authorization, not a performance claim.**
Supersedes as the *performance* architecture: `rtdl_v4_0_design_review_packet_2026-06-19.md` was the *embedding/C-ABI* boundary; this doc is the *performance* architecture. They are complementary layers, not competitors (see §9).

## 0. One-paragraph thesis

V3 proved that a Python-orchestrated runtime (traverse → buffer → partner kernel) cannot beat V2.14: it can only remove its own overhead and asymptotes to parity, because the heavy compute is the OptiX/Embree backend shared with V2. Near-OptiX performance lives in **fusion** — running the app's reduction logic inside the traversal kernel, on-device, with no intermediate materialization. Every mature system (OS, Postgres) reaches peak performance the same way: a **generic fallback**, a **fused fast path**, and an **open extension**. RTDL V4.0 adopts that three-tier model and abandons the "100% app-agnostic native engine" dogma that forbade fusion. Crucially, the fused kernels **already exist** in the codebase (shelved as "primitives"); V4.0 promotes them from special-forces to main force.

## 1. The Fusion Gap (the physics V4 must cross)

Hand-written OptiX is fast for two reasons: (1) RT cores do BVH traversal in hardware — RTDL already uses this, same OptiX; (2) **fusion** — the any-hit/closest-hit shader does the app work inline, in registers, in the same launch, no intermediate.

RTDL's V3 architecture keeps (1) and loses (2): it traverses (launch 1), emits a candidate stream to memory, then runs a separate partner kernel (launch 2). V3's residency work removed the *host* round-trip (→ parity) but cannot remove the structural fact of **two kernels with an intermediate buffer**. Hand-written OptiX has **one** kernel and register passing.

> The distance from V3 to OptiX performance **is** this fusion gap. It cannot be closed in the orchestration layer; it can only be closed inside the kernel.

"Use CUDA cores and RT cores at the same time" is literally the definition of a fused OptiX shader (RT cores traverse while SM cores run the shader). The orchestration model can only do "one then the other with a buffer between." This is why V4 must fuse.

## 2. The principle from mature systems (abandon the purity fantasy)

No system reaches peak performance with a single pure decoupled framework. Peak performance always comes from breaking layer purity and fusing.

| Tier | Postgres | OS | RTDL V4.0 |
| --- | --- | --- | --- |
| **1. Generic fallback** (general, slow, parity) | Volcano iterator interpretation | syscall + page cache (two copies) | **Separate-kernel partner path** (current V3) — traverse → buffer → CuPy/Numba |
| **2. Fused fast path** (official, peak) | LLVM JIT operator fusion | zero-copy / sendfile / DPDK | **Fused Native Primitives** — RTDL-authored OptiX kernels; reduction fused into traversal |
| **3. Open extension** (user fast path) | C UDF (.so) | eBPF | **Numba→PTX→OptiX module linking** — user injects device logic into the traversal shell |

The V3 mistake was trying to reach Tier-2 performance with a Tier-1 architecture, justified by purity. The fix is to build Tiers 2 and 3.

## 3. The new architectural rule (precise replacement for the purity dogma)

The old rule — "the native engine must be 100% app-agnostic, must not perceive application logic" — is **retired**; it was the cause of the V3 performance failure. Its precise replacement:

> **The native engine MAY contain fused kernels for generic *continuation operators* (sum, count, min/max, argmin, knn-collect, threshold/early-stop). It MUST NOT contain *application identity* (no "DBSCAN kernel", no "Barnes-Hut kernel", no "RayJoin kernel").** Fusion is permitted at the relational/reduction-operator layer and forbidden at the application-semantics layer.

This permits Tier-2 fusion while preventing the engine from metastasizing into app-specific hacks. The push-down model (§4) enforces it naturally: you push down *recognized operators*, and the operator library is app-agnostic even though it is fused.

## 4. Programming model: Operator Push-down (so RTDL is not a wrapper)

The conflict: OptiX is control-flow / event-callback (on hit → action); RTDL's ITRE is data-flow / relational (traverse → emit → reduce). Exposing OptiX callbacks to Python users would make RTDL "a Python skin over OptiX" — a failure.

The resolution is **not** to expose callbacks. It is **operator push-down**: the user keeps writing ITRE — "find neighbors in radius, sum their weights" — declaratively. The engine *recognizes* that the reduce is a member of its operator library (here, Sum-Reduce) and **pushes it down** into the traversal kernel (any-hit accumulation), executing on-device with zero intermediate. The user's mental model stays relational; the implementation fuses. This is exactly Postgres aggregate/predicate push-down.

**Scope and boundary (the honest part the dialogue under-specified):**
- Push-down works **only for the recognized operator set** (the Tier-2 pattern library). For sum/count/min/max/knn/threshold it is clean and complete.
- **Arbitrary user reduce logic is not push-downable** — that is precisely what Tier 3 (PTX injection) exists for. Do not blur this boundary.
- **There is a class push-down cannot serve at all: genuinely *action-shaped* logic** (on hit, mutate a shared structure; conditionally spawn). This is not a reduce; it is closer to an OptiX callback. V4 must either (a) restrict V4.0 to the reduce/aggregate/filter class and defer action-shaped logic, or (b) accept a controlled, narrow action API in Tier 3 and acknowledge that for that class RTDL *is* closer to a structured OptiX front end. Decide this explicitly; do not pretend push-down covers it.

## 5. Tier 2 — Fused Native Primitives (the main force; assets already exist)

This is the pragmatic 80%-path and the immediate opportunity, because the kernels are **already written and shelved**:

- `fixed_radius_count_threshold` — counter in the ray payload register; each BVH hit increments; early-terminates the ray at threshold; writes one bit. Zero intermediate. (Sales-risk, robot-collision class.)
- `event_ordered_grouped_ray_id_reduction` / `primitive_payload_grouped_sum` — SUM/MIN/MAX fused into the any-hit/closest-hit shader. (Barnes-Hut aggregate force, KNN-aggregate class.)
- Located in `src/rtdsl/generic_primitives.py`, `db_primitives.py`, `rtdl_optix_api.cpp`.

These **are** Tier-2 fused fast paths, authored long ago, then marginalized by the purity dogma in favor of the slow separate-kernel path. V4.0's first move is to **promote them from shelved to the default fast path**, exposed through the push-down operator library, with a documented operator catalog (which patterns are fused).

Honest scoping: "covers 80% of workloads" is **unverified**. The real coverage = the fraction of the app catalog whose continuation maps onto the fused operator set. **Audit the app catalog and report actual coverage** before claiming a number.

## 6. Tier 3 — Numba JIT → PTX → OptiX module linking (the open extension)

For continuations outside the operator library, let the user write the logic in Python and fuse it anyway:

1. User writes a device reduce in Python: `@numba.cuda.jit(device=True)` returning the new state from `(hit_distance, props, current_state)`.
2. RTDL extracts the compiled PTX from the Numba function at runtime (Python's dynamic advantage).
3. RTDL links that PTX into a pre-built "hole-left" OptiX traversal shell via the OptiX module-linking API, against a fixed `extern "C" __device__` signature contract.
4. One launch: RT cores traverse, SM cores run the user's Python-defined reduce at each hit.

**Honest caveats (mandatory — do not repeat the "zero-overhead" overclaim):**
- OptiX callables / module-linked device functions are **not free inline**. There is call-boundary overhead, register pressure, and occupancy cost. Tier 3 **approaches** hand-written OptiX; it does not equal it "with zero loss." Every Tier-3 claim must be measured, not asserted.
- The fixed signature contract passes a **small, fixed** set of scalar arguments. Variable-length payloads (neighbor lists) still require memory — the fusion benefit is bounded to register-passable state.
- **ABI / toolchain coupling is fragile**: Numba's PTX target, PTX ISA version, OptiX PTX/OptiX-IR ingestion, and OptiX's restrictions on device code (recursion, intrinsics, allocation) must all line up, with pinned versions. "Does arbitrary Numba PTX link and run as an OptiX module" is a hypothesis to **falsify**, not an assumption.
- Triton does **not** fit (block/tile SPMD ≠ per-hit scalar device function). Tier 3 is **Numba-device-function only**.
- Therefore Tier 3 is a **falsifiable spike**, narrower and riskier than Tier 2, and must not gate V4.0.

## 7. The honest performance ladder

| Path | Who writes the fusion | Performance | Generality |
| --- | --- | --- | --- |
| Tier 2 fused primitive | RTDL (hand-written OptiX) | **≈ near hand-written OptiX** | the recognized operator set |
| Tier 3 PTX injection | user (Numba→PTX) | a *fraction* of OptiX (callable/link overhead), to be measured | arbitrary per-hit scalar reduce |
| Tier 1 partner (current V3) | none (separate kernels) | **parity, not OptiX** | fully general |

Do not present all three as "OptiX performance." Tier 2 genuinely approaches it (it *is* fused OptiX); Tier 3 approaches it less and must prove it; Tier 1 is parity by construction.

## 8. The falsifiable validation experiment (do this first, it is cheap)

Before committing to the V4 build, validate the Tier-2 thesis on an **existing** shelved primitive:

> Take `fixed_radius_count_threshold` (already written). Measure it same-contract, same-hardware against BOTH baselines: (a) the V3 separate-kernel partner path, and (b) a hand-written reference OptiX kernel for the same query. 
> - If the fused primitive **significantly beats the partner path** and **approaches hand-written OptiX** → the Tier-2 thesis is validated; promote the primitive library.
> - If it does not → the fused-primitive premise is wrong and V4 must be reconsidered before any further build.

This is the "go into the kernel" experiment V3 never ran (V3 only tested orchestration). It uses an existing asset, so it is days, not weeks.

## 9. Version relationship (avoid another scope mess)

- **V3 = capability release (Tier 1).** Python gets RT cores without writing OptiX, at honest parity-class performance. This is the orchestration tier and it is real, shippable, and honestly bounded. (This is the current Phase H direction.)
- **V4.0 = performance release (Tier 2 + Tier 3).** Fusion crosses the gap → near-OptiX performance from Python.
- This **reconciles with the earlier V4 vision** ("RT-core lane for the Python GPU ecosystem"): fusion is *how* that lane becomes performant. The earlier V4 embedding/C-ABI work is an **orthogonal** delivery concern (how non-Python or framework hosts call in) and remains deferred; it is not part of this performance architecture and must not be bundled in (that bundling is what broke v3.0).

## 10. Risks, non-goals, and what would falsify this

**Non-goals for V4.0:** no app-identity kernels (only generic operators); no Triton device injection; no "zero-overhead" Tier-3 wording; no public speedup claim before §8 validates; no bundling of the embedding/C-ABI V4.

**Risks:**
- Tier-2 coverage is smaller than hoped (operator set doesn't map to enough apps) → V4 is a narrower performance win than "80%". Mitigate by auditing the catalog (§5).
- Tier-3 PTX linkage proves infeasible/fragile → Tier 3 ships late or never; V4.0 stands on Tier 2 alone (still a real performance release).
- Push-down pattern recognition is harder than it looks for composite reduces → start with single-operator push-down, not arbitrary operator trees.
- Action-shaped logic forces a callback-like API → accept it narrowly in Tier 3 or defer it; do not let it turn the whole engine into a wrapper.

**What would falsify the whole architecture:** if the existing fused primitive (§8) does **not** beat the partner path and approach hand-written OptiX, then fusion does not deliver here either, and the honest conclusion is that V3's capability framing is the ceiling — RTDL stays a parity-class Python RT-core layer, no V4 performance release.

## 11. Build order

1. **(Cheap, first) §8 validation** on the existing `fixed_radius_count_threshold` primitive vs partner path AND hand-written OptiX. Gate everything on this.
2. **Promote the shelved Tier-2 primitives** to the default fast path; publish the fused-operator catalog; audit app-catalog coverage and report the real percentage.
3. **Build the push-down recognizer** for the recognized operator set (single operators first), keeping the ITRE surface unchanged.
4. **Tier-3 spike** (Numba→PTX→OptiX linking) as a falsifiable experiment with the §6 caveats, Numba-only, one route, pinned toolchain.
5. Only after Tier 2 is validated and measured: a performance scorecard (same-contract vs partner path and vs hand-written OptiX), then external review, then any release wording.

## 12. Non-authorization

No release, no POD spend beyond the §8 focused validation, no public/near-OptiX performance wording until §8 + §11.5 produce measured evidence, no Triton injection, no embedding/C-ABI bundling, no app-identity kernels.
