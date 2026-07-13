# Ease Comparison Template — RTDL User Program vs Author C++/CUDA/OptiX

Date: 2026-07-05
Task: RayJoin Section 5.7 polygon overlay, same input (top4 County x Zipcode), byte-equal output.
Purpose: the scoreboard for Decision A. Main AI fills every `TBD`. This measures the ONE
thing that matters now — how much the user has to write and understand.

## Table 1 — Program size (fill author column; RTDL seeded from real counts)

| Program | File(s) | Total lines | Non-blank/non-comment lines | Who wrote it |
|---|---|---:|---:|---|
| RTDL paper-text route | `section57_overlay.py` | 964 | TBD | user/app |
| RTDL Numba route | `section57_overlay_numba.py` + `rayjoin_numba_overlay_kernels.py` | 487 + 371 = 858 | TBD | user/app |
| RTDL writer-free binary route | `section57_overlay_columnar_binary.py` | **3660** | TBD | user/app |
| Author C++/CUDA/OptiX overlay | (cloned author repo `polyover_exec` sources) | TBD | TBD | author |

Seed observation: the RTDL "writer-free binary" program a user must maintain is **3,660
lines**. The ease promise ("write it in Python instead of C++/CUDA/OptiX") is not met if the
Python is the same size or larger than the C++. Fill the author number and state the ratio.

## Table 2 — Where the RTDL lines go (the key diagnostic)

Break `section57_overlay_columnar_binary.py` (3660 lines) into categories. Category B is the
plumbing that Decision A says must move INTO RTDL. Category A is what a user should actually
write.

| Category | What it is | Lines | Should the USER write this? |
|---|---|---:|---|
| A. Spatial logic | load maps, LSI, PIP, overlay composition, emit | TBD | Yes — this is the user's job |
| B. Device/CUDA plumbing | Numba CUDA kernels, device columns, bitonic sort, scatter, carrier construction, memory/lifetime | TBD | **No — must live in RTDL** |
| C. Measurement / CLI scaffolding | argparse, timing, repeat protocol, regime flags, summary JSON | TBD | No — not part of the program |
| D. Writer / format | author text output-chain formatting | TBD | Only if the user wants paper text output |

Ease target: after moving Category B into RTDL primitives, the user's program is **Category A
only** — a small number of lines of plain Python. State the target line count.

## Table 3 — Concept checklist (does the user have to touch it?)

For each low-level concept, mark whether the user's program currently forces it, and whether
it should. "Yes" in the "forced now" column that should be "No" is an ease defect to fix.

| Low-level concept | Forced on user now? | Should be? | In author C++? |
|---|---|---|---|
| Write a CUDA kernel by hand (Numba `@cuda.jit`) | TBD | No | Yes |
| Configure/prepare an OptiX pipeline | TBD | No | Yes |
| Manage device columns / CUDA array interface | TBD | No | Yes |
| Write/choose a GPU sort (bitonic etc.) | TBD | No | Yes |
| Device scatter / gather indexing | TBD | No | Yes |
| Build a grouped carrier / descriptor buffer | TBD | No | Yes |
| Device memory allocation / lifetime / `.close()` | TBD | No | Yes |
| Scale-domain / coordinate scaling constants | TBD | Maybe | Yes |
| Prepared-session / workspace management | TBD | No | Yes |
| Author text output-chain format | TBD | Only if paper output wanted | Yes |

The value of RTDL is every row where the author C++ says "Yes" but the RTDL user says "No" —
that is complexity RTDL absorbed. Any row where the RTDL user still says "Yes" is unfinished
ease work.

## Table 4 — The honest ease verdict (fill after Tables 1–3)

```text
RTDL user program (spatial-logic lines, Category A):   TBD
Author C++/CUDA/OptiX program (lines):                 TBD
Ease ratio (RTDL user lines / author lines):           TBD   (target: << 1)
Low-level concepts the user still hand-writes:         TBD   (target: 0 kernels/pipelines)
Byte-equal output preserved:                            TBD (yes/no)
Accepted performance cost (frozen, disclosed):         ~10-14x slower end-to-end
```

## Counting rules (so this cannot be gamed)

- Count non-blank, non-comment lines.
- "User program" = only the app code a user writes/maintains for the task. RTDL internal
  primitives (`src/rtdsl/**`, `src/native/**`) are NOT user lines — they are what RTDL
  provides. (Moving plumbing from the app into `src/rtdsl` is exactly the win.)
- Measurement/CLI scaffolding (Category C) is reported separately and does NOT count toward
  the spatial-logic ease number, but it must be listed so it is not used to inflate "how much
  RTDL does for you."
- The author baseline is the cloned author overlay source (the actual `polyover_exec`
  program), counted the same way.

## What "done" looks like for this template

The next ease goals succeed when Table 4 shows: RTDL user program is a small multiple
(ideally a fraction) of the author line count, with **zero** hand-written CUDA/OptiX in the
user's program, byte-equal output, at the frozen ~10x cost. Until then, every line in
Category B is a concrete, named target to move into RTDL.
