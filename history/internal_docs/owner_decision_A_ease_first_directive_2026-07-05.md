# Owner Decision: A — "Easier, Not Faster"

Date: 2026-07-05
From: owner
Status: governs ALL work from now. Supersedes the performance-chasing track.

The owner has chosen **A**. RTDL will not try to match C++/CUDA/OptiX speed. It competes on
**ease of writing**. The founding promise is restored:

> Just as Numba lets people use CUDA cores without writing CUDA, RTDL lets people write
> spatial/RT workloads in Python without writing C++/CUDA/OptiX.

## 1. Freeze performance. Stop chasing it.

- The 5000-series performance track (device-resident carrier, LSI producer regimes,
  prepared/replay optimization, sort micro-work) is **closed**. No more performance
  micro-goals.
- State the honest performance ratio **once**, stably, and stop:
  - Real one-shot (cold process, the way a user runs it): RTDL ~11.6 s vs author full run
    ~0.84 s ≈ **~10–14x slower end-to-end**; ~100x on pure compute.
  - This is the accepted, disclosed cost of the Python/RTDL/Numba approach. Do not hide it,
    do not chase it, do not re-measure it in a flattering regime.
- Device-resident code stays behind its flag as experimental. No further goals on it.

## 2. The only scoreboard now: ease (Number 2)

For the SAME task (start with RayJoin 5.7 overlay), measure and drive down:

```text
- lines of user-written Python
- number of low-level concepts the user must touch
- specifically: does the user hand-write ANY CUDA kernel, OptiX pipeline,
  device-column layout, sort, scatter, carrier, or memory management?
```

Target state:

> The user writes **only spatial logic** — load maps, LSI, point-location/PIP, compose the
> overlay, emit the result — in plain Python/RTDL primitives, with **Numba only as an
> optional partner for user numeric code**, and **zero hand-written CUDA/OptiX/device
> plumbing**. The program is dramatically shorter and concept-lighter than the author C++.

## 3. The actual work (this is where effort goes)

1. **Write the honest "user program."** Produce the minimal RTDL Python a real user would
   write for RayJoin 5.7. Count its lines and list every low-level concept it forces on the
   user. Put it side-by-side with the author C++/CUDA/OptiX (lines + concepts).
2. **Find every leak of complexity into the user's code.** Today the paper app makes the
   user (or app layer) write Numba CUDA kernels, device-column plumbing, bitonic sort,
   midpoint scatter, carrier construction, a writer. Each of those is a **failure of ease**.
3. **Move that plumbing INTO RTDL generic primitives**, so the user's program shrinks to
   spatial composition only. The device/columnar/sort/carrier machinery must live inside
   RTDL, invoked by a simple Python surface — not copied into every app.
4. **Re-measure ease** (lines + concepts) after each move. That number is the scoreboard.
5. **Ease also means:** install/setup simplicity, clear errors, and docs — but the core
   metric is "no hand-written kernels, short Python, same result."

## 4. Anti-fragmentation guard (so ease does not become the new trivia)

Performance got fragmented into internal regimes because the honest comparison was
unflattering. Do not repeat that with ease:
- Every ease goal must show its effect on **user lines + user concepts** for the real task,
  vs the C++ baseline. A goal that refactors internals without reducing what the user writes
  is **not authorized**.
- No new internal abstraction is "progress" unless it removes something from the user's
  program. Measure the user's program, not the internals.
- Correctness anchor unchanged: the RTDL RayJoin output must stay byte-equal to the author
  (paper text route) — ease may not weaken correctness.

## 5. Definition of done for the ease track

```text
A non-expert can write the RayJoin 5.7 overlay in RTDL Python in a small number of lines,
touching no CUDA/OptiX/device plumbing, get byte-equal output, and accept a stable,
disclosed ~10x-slower performance cost.
```

When that holds for RayJoin, prove it generalizes by writing a SECOND, non-RayJoin spatial
workload with the same ease surface. Ease that only works for RayJoin is not ease.

## One line

Stop selling speed. RTDL's value is: write spatial/RT workloads in short, plain Python with
no hand-written CUDA/OptiX, byte-equal results, at an honest ~10x-slower cost. Every goal
from now must shrink the user's program or it is not authorized.
