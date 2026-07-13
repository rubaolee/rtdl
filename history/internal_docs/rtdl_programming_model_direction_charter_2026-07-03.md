# RTDL Programming-Model Direction Charter (post-v2.14)

Date: 2026-07-03
Status: direction charter — **not** a release, implementation, or performance
authorization. It states where the language should evolve and why.

## 0. One-sentence thesis

RTDL is not trying to become an OptiX you can call from Python. RTDL is trying to
become **a spatial language where the user writes a data-flow program and a
compiler decides what gets fused into the ray-traversal kernel.** That compiler is
the entire moat.

## 1. The one fundamental difference (everything else is language/ergonomics)

The root difference between `Python + partner + RTDL` and `C++/CUDA/OptiX` is
**where user computation runs relative to the traversal kernel**:

- **OptiX (event / callback model):** user code runs **inside** traversal, at each
  ray event (any-hit / closest-hit / miss), on-device, in registers. The user's
  code *is* part of the traversal kernel.
- **RTDL (data-flow / ITRE model):** user code runs **after** traversal, in a
  separate stage, over materialized rows. `traverse` is fixed; `refine`/`reduce`/
  `emit` are downstream.

"No custom callback" is the **symptom**. "User computation is outside the
traversal kernel" is the **root**. Python vs C++, Numba vs raw CUDA, prepared
sessions — all of that is language/ergonomics and does not change the compute
locus.

Precise form: RTDL today has a **fixed, closed** set of in-traversal behaviors
(its fused primitives); OptiX has an **open** set (user shaders). This is the OS
analogy exactly: OptiX = write your own eBPF/kernel module; RTDL = a fixed set of
syscalls with user code in userland.

## 2. The two gaps this root produces (do not conflate them)

1. **Expressiveness gap:** users cannot put custom per-hit logic into traversal.
2. **Performance gap (the fusion gap):** results must be materialized and cross
   the traversal↔continuation boundary — this is the source of the large
   author-vs-RTDL hot-path gap. It is a *kernel/locus* problem, not an
   orchestration problem, and cannot be closed by faster Python or prepared
   sessions alone.

Both flow from the same root. Closing either means moving user computation into,
or closer to, the traversal kernel.

## 3. The moat and identity

The strategic bet, stated as a language:

> **The user writes data-flow (ITRE). The compiler decides WHERE each stage runs —
> fused into traversal, or downstream — and HOW.**

This separates **WHAT** (the data-flow program) from **WHERE/HOW** (fusion vs
downstream), which is the Halide / Triton / Postgres-LLVM-JIT pattern. It is what
lets a *language* beat a raw *API*: not more knobs, but a compiler that hides the
fusion decision. Keeping the data-flow surface is the identity; the compiler is
the moat.

## 4. The three attack points (in priority order)

### Attack 1 — Programming model: the ITRE → traversal compiler (the moat, the real answer to "callbacks")
Do **not** expose raw callbacks (that turns RTDL into Pythonic-OptiX and forfeits
the data-engine identity). Instead, open in-traversal computation **through** the
data-flow abstraction, by compilation:

- **Recognized patterns** (sum / count / min-max / knn / threshold): **operator
  push-down** — lower the `refine`/`reduce` into the shader (fixed fused
  primitives; the curated "syscall" set, grown carefully).
- **Custom user reduces:** user writes the reduce in **Numba** (data-flow, still
  Python); RTDL extracts PTX and **injects** it into the traversal shell (the
  falsifiable Tier-3 spike). The user never writes a callback; the compiler fuses
  their reduce.

The user's programming model does not change. The compiler gets smarter about
lowering more of ITRE into the kernel.

### Attack 2 — System implementation: make the downstream part cheap (near-term, bounded)
For stages that stay downstream, remove the boundary tax: **device residency (no
host round-trip), no materialization of unused rows (count-/mask-only),
same-CUDA-stream device-to-device continuation, traversal↔continuation overlap.**
This cannot reach OptiX (the kernel floor remains), but it converts
"orchestration with host round-trips" into a "device-resident pipeline" — a real
win for multi-stage workloads. **Gate: measure the current phase breakdown before
setting any target; the RT-core kernel is the immovable floor.**

### Attack 3 — Architecture: choose the battlefield where data-flow structurally wins
Do not fight OptiX on a single fused kernel — OptiX wins that, always. Win where
the data-flow model is structurally superior:
- composable **multi-stage** spatial pipelines (compose primitives + partner
  reductions instead of hand-writing one monster shader);
- **heavy continuation** using mature partners (CuPy / Numba / PyTorch) that a
  C++ OptiX program cannot easily reach;
- **portability** (same program on OptiX / Embree / CPU);
- **developer velocity** (Python vs C++/CUDA/SBT).

## 5. The one rule that protects the identity

> Open in-traversal computation **only** through the data-flow surface + the
> compiler. Never expose raw any-hit/closest-hit/miss callbacks as the user API.

Corollary governance (carried from the syscall/eBPF discussion):
- **User-authored** in-traversal reduces (Numba) are cheap and liberal — the user
  owns them, RTDL does not vouch for them.
- **Curated ("收录") primitives** are rare and high-bar — like adding a syscall:
  correctness + safety verifier + genericity (no app identity) + performance
  evidence + version maintenance. High bar precisely because RTDL owns them
  forever.

## 6. What this is NOT

- Not "expose OptiX shaders in Python" (that is Pythonic-OptiX; identity lost).
- Not "beat hand-written OptiX on a single fused kernel" (unreachable without
  in-traversal fusion; and even then, bounded).
- Not a promise that the compiler exists yet — Attack 1's Tier-3 injection is an
  unproven, falsifiable spike (Numba→PTX→OptiX linking; real ABI/toolchain risk).

## 7. Sequencing and gates

1. **Now (v2.14, reliable):** primitives + Numba partner continuation, correctness
   first (RayJoin reproduction is the current bounded validation).
2. **Attack 2 first, gated by measurement:** device-resident / no-materialization /
   same-stream continuation — but only after a phase breakdown proves where the
   time is; never target a number below the measured RT-kernel floor.
3. **Attack 1 as the falsifiable R&D bet:** prove Numba→PTX→OptiX linking on one
   minimal reduce, measure the callable/occupancy overhead honestly, kill it if it
   does not clear a real bar. Push-down (fixed patterns) is the safer first half.
4. **Attack 3 continuously:** frame and market RTDL by the workloads where
   data-flow wins, not by single-kernel benchmarks against OptiX.

## 8. Non-authorization

This charter authorizes no implementation, no performance claim, no raw-callback
API, no app-identity kernel, and no Tier-3 productization before the injection
spike clears a measured bar. It sets direction only.

## Bottom line

The fundamental difference is real and it is singular: **user computation is
outside the traversal kernel.** The winning move is not to import OptiX's callback
model — it is to build the **compiler that lowers a data-flow program into the
kernel**, keep the clean ITRE surface, make the downstream path cheap where fusion
is not yet possible, and compete on the workloads a language beats a raw API at.
The compiler is the moat and the direction.
