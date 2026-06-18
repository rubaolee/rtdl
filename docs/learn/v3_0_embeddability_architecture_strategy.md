# RTDL Embeddability Architecture Strategy

**Status:** V3 architecture review input, not a frozen ABI contract · **Author:** independent technical review (Claude) · **Date:** 2026-06-17

RTDL project boundary: this document is retained as design guidance for the
post-v2.14/V3 embeddability track. It does not by itself authorize a stable C
ABI, DLPack support, external stream/context support, device-callable fusion,
release wording, or performance claims. Those require separate implementation
and validation gates.

## Current Implementation Progress

As of Goal4561, the first control-plane embedding slice exists in the source
tree:

- Draft public header: `include/rtdl/rtdl.h`.
- Source-tree shared-library target: `make build-c-api`.
- Export audit for the current lifecycle/query symbols.
- Non-Python C client validation.
- A narrow host `F32` AABB2 overlap query proof returning host `U64`
  `(query_id, primitive_id)` pairs.
- A readable source-tree example:
  `examples/current/embedding/c_api_aabb2_overlap_client.c`.
- A documented current AABB2 buffer/result contract in
  [V3.0 C ABI Draft](v3_0_c_abi_draft.md).

Still not authorized: frozen ABI compatibility, packaged SDK wording, DLPack,
`__cuda_array_interface__`, external CUDA stream semantics, OptiX/Embree query
execution through the C ABI, language bindings, device-callable fusion, or V3
release wording.

**Purpose:** Define how RTDL prepares *now* to be embedded later inside other languages and runtimes — called from Python, C/C++, Rust, Julia, C#, and fused into GPU frameworks like PyTorch, JAX, CuPy, and Numba — without rewriting the core each time a new host shows up.

**Relationship to the prior doc:** This supersedes the "Reverse PTX Linkage" framing as the *foundation*. That doc made on-device PTX/OptiX callable fusion the load-bearing strategy. I think that's the wrong base layer: it is the hardest, least portable, and least proven path, and most of its stated benefits (zero-overhead inlining, register-only data flow, perfect RT/CUDA pipelining) do not hold on current OptiX hardware. Embeddability is won first by a **stable boundary and zero-copy data interop**, and only later, optionally, by device-code fusion. PTX callables are retained here as an advanced track, not the floor.

---

## 1. What "embedded in other languages" actually means

Two different problems hide under one phrase. Separating them is the whole point of this doc.

- **Control-plane embedding (the common case).** A host program in some language calls RTDL to build an index, run spatial queries, and get results back. The host owns the program; RTDL is a library it links against. This is 90% of real embedding demand and is solved by a clean ABI and data interop — no compiler tricks required.
- **Data-plane fusion (the hard case).** User-defined math (a force kernel, a cluster update) runs *inside* the RT traversal on-device, so intersection results never round-trip through global memory. This is the original doc's PTX-callable idea. It is valuable but narrow, fragile across toolchains, and should never gate the common case.

A strategy that conflates these ends up making every host pay the cost of the hard case. We keep them in separate layers so a Rust or Julia user can embed RTDL with zero knowledge of OptiX callables.

---

## 2. The core principle: a narrow, stable C ABI is the embedding contract

Every language that matters can call C. None of them can reliably call C++ across a binary boundary (no stable C++ ABI), and none should be exposed to OptiX, CUDA driver types, or RTDL internals. So the single most important preparation step is to **define and freeze a narrow C ABI** — call it `rtdl.h` — that is the only surface anything else binds to.

Design rules for that boundary:

- **Opaque handles only.** `rtdl_context`, `rtdl_index`, `rtdl_query` are opaque pointers. No struct layouts, no C++ types, no STL, no templates cross the line.
- **No exceptions, no `std::` across the boundary.** Every call returns an `rtdl_status` error code; errors are retrievable as strings via a separate call. Exceptions are caught at the boundary and converted.
- **Explicit ownership and lifetimes.** Every `create` has a matching `destroy`. The caller is told, per pointer, who frees it. No hidden global state, no singletons that assume one host.
- **Caller-supplied context and stream.** RTDL accepts an external CUDA context and stream rather than creating its own. A host embedding RTDL inside PyTorch must be able to hand RTDL *its* stream so work orders correctly. This one decision is the difference between "composable" and "fights the host."
- **Versioned ABI.** A `rtdl_abi_version()` and semantic-versioned symbol policy so a host built against v1 keeps working when the core moves to v1.x.
- **Reentrancy and thread-safety stated explicitly.** Which calls are thread-safe, which need external synchronization. Embedding hosts are frequently multithreaded.

Everything else in this document sits on top of this boundary.

---

## 3. Layered architecture

```
L3  Framework adapters   DLPack / __cuda_array_interface__ zero-copy,
                         optional device-callable injection (advanced)
L2  Language bindings     Python, Rust, Julia, C#, ... (thin wrappers over L1)
L1  Stable C ABI          rtdl.h — opaque handles, error codes, external stream/context
L0  Native core           C++/CUDA/OptiX: generic primitives, BVH build, traversal,
                          pipeline orchestration. Knows nothing about any host language.
```

The rule that keeps this honest: **dependencies only point downward, and L0 contains zero app-specific or host-specific code.** If a host language ever needs a change in L0, that's a design smell — the need should be expressible at L1.

- **L0 Native core.** Generic device primitives, acceleration-structure build, traversal, OptiX pipeline assembly. This is where "no app-specific C++/CUDA" must be enforced; the partner/cache lessons from the RayJoin work apply here.
- **L1 C ABI.** Section 2. The contract.
- **L2 Bindings.** Thin and mostly generated. Python via cffi/pybind11 over the C ABI (not a parallel C++ API); Rust via `bindgen`; Julia via `ccall`; C#/Java via P/Invoke/JNI. Thinness is the goal — bindings carry no logic, so a new language is days, not months.
- **L3 Framework adapters.** Where GPU interop lives (Section 4).

---

## 4. Data-plane interop: zero-copy first, device fusion later

This is the section that most changes the original doc's conclusion.

### 4A. Zero-copy array exchange is the real embedding mechanism (do this)

The proven, portable way to embed into the GPU ecosystem is **standard array-exchange protocols**, not PTX injection:

- **DLPack** for framework-neutral tensor handoff (PyTorch, JAX, TensorFlow, CuPy all speak it).
- **`__cuda_array_interface__`** for the Numba/CuPy/Numpy-on-GPU world.

If RTDL accepts and returns device buffers through these protocols, a user can pass a PyTorch CUDA tensor straight into an RTDL query and get results back as a tensor — no copies, no custom glue, no toolchain coupling. This single capability delivers most of the "fusion" value the original doc wanted (avoiding global-memory round-trips between frameworks) with none of the ABI fragility. It works *today* and across every major framework.

The honest cost model: this fuses RTDL with the host framework at the **buffer** level, not the **instruction** level. Results still land in device memory between stages. That is fine — the win is eliminating host copies and redundant allocations, which is exactly what hurt the early RayJoin numbers.

### 4B. On-device callable fusion is an optional advanced track (spike, don't assume)

The original doc's "inject Numba/Triton PTX as an OptiX direct callable" idea is worth a **falsifiable spike**, but it is not the foundation, and the claims must be corrected before anyone plans around it:

- **OptiX direct callables are not inlined.** `optixDirectCall` dispatches through the SBT as an indirect call, with call-boundary overhead and a register/occupancy cost (the pipeline must reserve registers for the worst-case callable). "Zero-overhead inline execution" is not accurate.
- **Register-only data flow is limited.** Callables pass a small fixed set of scalar args; any variable-length payload (neighbor lists, arrays) goes back through global memory via a `void*`. The materialization you were deleting reappears as that pointer.
- **RT and CUDA cores do not pipeline per-ray.** Within one ray, the SM warp parks while the RT core traverses, then resumes. Latency hiding comes from many warps in flight, not a per-ray RT↔SM pipeline; heavy callables can *reduce* overlap by cutting occupancy.
- **Triton does not fit.** Triton is a block/tile SPMD model, not extractable per-thread device functions. Scope any device-fusion spike to **Numba `@cuda.jit(device=True)` only**; treat Triton as an L3 zero-copy consumer (4A), not an injected callable.
- **Toolchain reality.** It's `optixModuleCreate` (PTX or OptiX-IR; `...FromPTX` is deprecated), and OptiX restricts ingested device code (recursion, intrinsics, allocation, ISA/SM target). Whether arbitrary Numba PTX even links as a callable is the hypothesis to *falsify*, with pinned CUDA/Numba/OptiX versions.

**Gate:** the device-fusion track ships only if a Numba-only microbenchmark (e.g. Barnes-Hut force reduction or DBSCAN update) beats the 4A zero-copy path on a real case, with occupancy and register pressure measured. Until then, 4A is the supported answer and the row-emission/zero-copy path stays.

---

## 5. Embedding modes (reframing Solo-Best / Team-Best)

The dual-posture idea from the prior doc survives, but stated as two concrete embedding modes with explicit cost:

- **Embedded-as-library ("host owns the loop").** The host framework drives execution; RTDL supplies index build, traversal, and zero-copy queries through L1/L3. This is the default and the one that must always work. Maps to "Team-Best / Partner."
- **Embedded-as-runtime ("RTDL owns the loop").** For turnkey solvers where RTDL orchestrates the whole pipeline and treats CuPy/Numba as guests. Higher peak performance for specific benchmarks, lower composability. Maps to "Solo-Best / Prime."

The cost the prior doc didn't name: **maintaining both modes is real, ongoing engineering**, and the failure mode of "we don't have to choose" is under-investing in both. The mitigation is that both modes are built on the *same* L0/L1 — the runtime mode is just an extra orchestration layer above the library mode, not a parallel codebase. If they ever diverge below L2, that's the signal we're paying for two architectures.

---

## 6. Memory, streams, and lifetime contract

Embeddability lives or dies here, so it gets its own section:

- RTDL never assumes it owns the CUDA context or the process. It accepts both.
- All async work is submitted on a **caller-provided stream**; RTDL documents its synchronization points and avoids implicit device-wide syncs.
- Buffer ownership is explicit at the ABI: RTDL-allocated vs. borrowed-from-host buffers are distinct and never confused.
- No global mutable state that breaks under multiple hosts, multiple contexts, or multiple threads.
- Deterministic teardown: destroying an `rtdl_context` releases everything it owns and nothing it borrowed.

---

## 7. Preparation directives (what to do now to be ready later)

Concrete, and ordered so nothing risky runs ahead of its proof:

1. **Freeze a draft C ABI (`rtdl.h`).** Opaque handles, error codes, external context/stream, versioning. This is the highest-leverage item; do it first.
2. **Adopt DLPack and `__cuda_array_interface__`** for all data exchange at L3. This is the real "embed into the GPU ecosystem" capability.
3. **Make stream/context external** throughout L0/L1. Stop creating internal contexts/streams where a host one could be accepted.
4. **Prove the ABI from a non-Python language early.** Stand up a minimal Rust *or* C client that builds an index and runs a query through L1. If the ABI only works from Python, it isn't an embedding boundary yet — it's a Python extension.
5. **Build as a clean shared library** with controlled symbol visibility (export only the ABI; hide everything else). No leaking C++/CUDA/OptiX symbols.
6. **Standardize device-callable signatures** *only* as preparation for the optional 4B spike, Numba-only, with the ABI shape documented as provisional.
7. **Run the 4B spike as a falsifiable experiment** with a kill criterion, pinned toolchain versions, and occupancy/register measurement. Do **not** deprecate the working zero-copy/row-emission path until 4B clears its gate.
8. **Write an ABI/version compatibility policy** and a toolchain support matrix (CUDA × OptiX × driver × Numba) before external embedders depend on it.

The one explicit *don't*: do not, per the prior doc's 3B, stop optimizing the current host-side/zero-copy path in anticipation of callable fusion. That deprecates a working capability on the strength of an unproven one. Sequence 7 to gate 6's promotion, and keep zero-copy as the permanent fallback.

---

## 8. Risks and non-goals

- **Non-goal:** a stable C++ API across the binary boundary. There is no stable C++ ABI; C++ stays internal to L0.
- **Non-goal (for now):** Triton device-function injection. Triton embeds as a zero-copy consumer, not an injected callable.
- **Risk:** ABI churn. Mitigated by freezing early, versioning, and the non-Python client test (directive 4) that catches leaks fast.
- **Risk:** toolchain coupling in the 4B track. Mitigated by keeping 4B optional and 4A primary.
- **Risk:** two embedding modes drifting into two codebases. Mitigated by forcing both onto shared L0/L1.

---

## 9. Success criteria

We are "ready to be embedded in other languages" when:

1. A C or Rust program with no Python in sight builds an index and runs a query through `rtdl.h`.
2. A PyTorch (or JAX/CuPy) user passes a device tensor into an RTDL query and gets a device tensor back, zero-copy, on their own stream.
3. Adding a new language binding is a few days of thin wrapper work, not a core change.
4. The core (L0) contains no host-language-specific or app-specific code.
5. The optional device-fusion track has either cleared its benchmark gate or been explicitly shelved with data — not left ambiguous.

---

### One-paragraph summary

RTDL becomes embeddable by getting the **boundary** right first: a narrow, stable, versioned C ABI with external context/stream and explicit lifetimes, plus zero-copy array interop (DLPack / CUDA array interface) so it drops into the GPU framework ecosystem without copies or compiler coupling. On-device PTX/OptiX-IR callable fusion is a genuinely interesting but secondary, Numba-only, falsifiable experiment — not the foundation, and not a reason to deprecate the working path. Win the common case cleanly, keep the hard case optional, and a new host language is a binding, not a rewrite.
