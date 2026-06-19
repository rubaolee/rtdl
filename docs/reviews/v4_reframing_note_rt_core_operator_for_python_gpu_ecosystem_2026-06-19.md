# V4 Reframing Note: RTDL as the RT-Core Operator for the Python GPU Ecosystem

**Author:** Maintainer intent, captured with Claude · **Date:** 2026-06-19
**Companion to:** `docs/engineering/rtdl_v4_0_design_review_packet_2026-06-19.md`
**Purpose:** Realign the V4 headline and milestone order with the actual product value. The current packet is engineering-correct but front-loads multi-language C/C++/Rust embedding and packaging, while the value users will feel — a CuPy/Numba/PyTorch program getting RT-core acceleration on its own device arrays — is buried at Phase 4. This note proposes the headline, the resequencing, and the one decision that determines how much C ABI to build first.

---

## 0. The pitch: the missing RT-core lane

NVIDIA GPUs have three compute engines: **CUDA cores**, **Tensor cores**, and **RT cores**. The Python accelerator ecosystem owns the first two and has nothing for the third:

| GPU engine | Who drives it from Python today |
| --- | --- |
| CUDA cores | CuPy, Numba, Triton, PyTorch |
| Tensor cores | PyTorch, Triton (and cuBLAS/cuDNN under them) |
| **RT cores** | **nobody — no first-class path** |

RT cores are reachable only through the ray-tracing runtimes (OptiX, DXR, Vulkan RT) — C/C++ graphics APIs that live entirely outside the Python numeric stack. Numba can't emit to them, Triton can't target them, PyTorch and CuPy have no path to them. Calling OptiX from Python (PyOptiX-style bindings) is "drive a graphics API from Python," not "RT cores as a lane in your tensor pipeline."

> **RTDL is the missing RT-core lane for the Python GPU ecosystem.**
>
> PyTorch/Triton do the Tensor-core math, Numba/CuPy do the CUDA-core math, and RTDL does the RT-core spatial/traversal step — all on the *same* device arrays, on the *same* CUDA stream, zero-copy. RTDL completes the trio of engines for the Python actors.

Two honesty notes that keep the pitch defensible:

- "These frameworks can't use RT cores" is the strong, true claim. "Therefore your program is faster" is the *per-route* claim: RT cores help only when the step is genuinely a traversal/spatial problem (nearest-neighbor, range, visibility, overlap, collision) at a scale where BVH traversal beats a brute-force CUDA kernel. The positioning is airtight; the performance statement stays route-specific, exactly as the v3 claim boundaries already require.
- The stage is **Python actors only** (CuPy, Numba, Triton, PyTorch, JAX). There is no C++ host in scope. That single fact answers the §5 scope question below: the full public multi-language C ABI and SDK packaging are V4.x at most — V4.0's real job is device-array zero-copy interop on the caller's stream.

---

## 1. The intended product, in one line

> **V4 makes RTDL the RT-core operator that CuPy / Numba / PyTorch programs call on their own device arrays — zero-copy, on the caller's CUDA stream — so a user adds RT-core spatial queries to an existing GPU program by writing a little RTDL, without leaving Python and without writing OptiX.**

This is the reverse of V3. In V3, RTDL is the host and CuPy/Numba are explicit partners. In V4, the Python GPU ecosystem is the host and **RTDL is the guest** that supplies the one capability that ecosystem lacks: RT-core traversal. The mental model is a hardware-specific island inside a normal Python pipeline — like a `cupy.RawKernel` or a Triton kernel, but for RT cores.

## 2. Why the C ABI felt like the wrong headline

The C ABI is real and useful, but it is **plumbing, not product**. Users never write it. They write Python; the Python binding calls the C ABI internally. Mapped onto the actual use case, the C calls *are* the use case:

| C ABI surface | What it means for a CuPy/Numba user |
| --- | --- |
| `rtdl_buffer_view` / `rtdl_buffer_import` | wrap my CuPy/Numba device array (ptr, shape, dtype, device, stream) so RTDL reads it in place — the zero-copy handoff |
| `rtdl_context_set_external_runtime` | RTDL uses *my* CUDA context and stream, not a private one — composes with my kernels without sync stalls |
| `rtdl_query_execute` | run the RT-core query on that device buffer |
| result `rtdl_buffer` | hand back a device buffer I wrap as a CuPy array and keep computing |

Read top to bottom, those four calls are exactly "CuPy array in → RT cores → CuPy array out." The packet presents this foundation first and the Python/framework layer (its layer L4) later, which inverts the value: the substrate is the headline and the product is a downstream phase.

## 3. Proposed headline change

Replace the packet's one-line goal:

- **From:** "V4.0 changes RTDL from a Python-hosted runtime that owns the loop into an embeddable library that a host language or framework can call while the host owns the loop."
- **To:** "V4.0 makes RTDL an RT-core operator that the Python GPU ecosystem (CuPy / Numba / PyTorch) can call on its own device arrays, zero-copy and on the caller's stream, with a stable C ABI as the substrate that also lets non-Python hosts in later."

Same architecture; the difference is which audience and which capability lead.

## 4. Proposed milestone resequencing

The packet's order is C/Rust host routes → packaging → device buffers (Phase 4). Reorder around the value:

**Phase 1 — Python device-array RT-core operator (the product).**
- RTDL Python entry point accepts CuPy / Numba / PyTorch device arrays via `__cuda_array_interface__` and DLPack.
- Runs the existing OptiX backend on the caller's CUDA context/stream.
- Returns a device array the host wraps back into CuPy/PyTorch.
- One real route end to end (fixed-radius neighbors or ray/triangle any-hit — a route with actual benchmark pull, not host-only AABB2).
- Evidence: pointer identity, no host stage, stream-order proof, correctness parity. (This is the device-buffer/zero-copy evidence the packet already specifies — just pulled to the front.)

**Phase 2 — Harden the boundary it stands on.**
- Promote the stable C ABI as the internal substrate beneath the Python binding (the binding calls the C ABI; it does not bypass it through private internals).
- Apply the D1–D5 decisions (result-sizing, struct extensibility, capability enum, input validation, 0.x freeze policy).

**Phase 3 — Non-Python hosts (only if they are a real goal — see §5).**
- C, then Rust, then Julia clients over the now-proven C ABI.
- SDK packaging (pkg-config / CMake), symbol manifest, layout audit.

**Phase 4 — Optional advanced track (unchanged).**
- Device-callable fusion remains a Numba-only, falsifiable spike with a kill criterion. Not on the release-critical path.

The reorder keeps every engineering artifact the packet already designed; it only changes which one ships first.

## 5. The one decision that sizes the C ABI

**Is embedding into non-Python hosts (a C++ application, a Rust service, PyTorch's C++ core) an actual V4 goal, or is the goal narrowly "RT-core extension for the Python GPU ecosystem"?**

- **If non-Python hosts are a real goal:** the full public C ABI is the correct durable foundation, and the Python binding sits cleanly on it. Keep the packet's C ABI scope; just resequence per §4 so the Python product proves the device-buffer contract first.
- **If the goal is narrowly Python:** the full public C ABI is more foundation than the immediate goal needs. The minimum viable version of the vision is **device-array zero-copy interop in the existing Python + native stack** — no public C ABI required for users at all. Keep a *thin internal* C boundary for cleanliness, but do not invest in pkg-config/CMake/multi-language packaging until a non-Python host is genuinely on the roadmap.

This is a product-scope question, not an engineering one, and it should be answered before M1 design freeze because it determines how much of the packet's C/Rust/packaging surface is V4.0 versus V4.x.

## 6. What stays exactly as the packet has it

- The zero-copy honesty ladder: descriptor import ≠ device-buffer query ≠ true zero-copy; claims require transfer-counter/pointer-identity/stream-order evidence.
- Device-callable fusion demoted to an optional, Numba-only, falsifiable spike.
- App-agnostic native engine: generic primitives and query contracts, never app semantics.
- Capability-gated, fail-closed routes; host owns the loop.

## 7. One-paragraph version to send to the other AI

> The V4 design packet is engineering-correct but mis-headlined. The product is "RTDL as an RT-core operator that CuPy/Numba/PyTorch programs call on their own device arrays, zero-copy and on the caller's stream" — the reverse-of-V3 partner posture. The C ABI in the packet is the substrate beneath that, not the user-facing deliverable, so it should not be the headline or the first milestone. Reorder so Phase 1 is a real Python device-array RT-core route (with one benchmark-valuable primitive and full zero-copy evidence), Phase 2 hardens the C-ABI substrate beneath the Python binding with the D1–D5 decisions, and non-Python host embedding plus SDK packaging move to Phase 3 — and only if embedding into C++/Rust hosts is actually a goal. If the goal is narrowly the Python ecosystem, the full public C ABI and packaging are likely V4.x, not V4.0. Please review whether this resequencing changes any of your P0/P1 findings, and weigh in on the §5 scope question: are non-Python hosts a real V4 goal or not?
