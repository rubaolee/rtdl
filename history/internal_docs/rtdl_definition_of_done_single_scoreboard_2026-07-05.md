# RTDL Definition of Done — The Only Scoreboard

Date: 2026-07-05
From: owner
Status: governs ALL future goals. A goal that does not move one of the two numbers below
is not authorized and must not be reported.

## The whole point of RTDL (in the user's words)

> Previously you wrote the program in C++/CUDA/OptiX. Now you write it in
> Python/RTDL/Numba. It must be **easy to write** and **high-performance**. Nothing else
> matters.

Everything internal — fresh vs replay, prepared session, device-resident carrier, regime
ladders, descriptor consumers — is plumbing. It is NOT progress and must NOT be reported to
the owner unless it moves one of the two numbers below.

## The only two numbers

### Number 1 — Performance ratio (answers "high-performance?")

```text
ratio = (RTDL Python/Numba, wall-clock) / (author C++/CUDA/OptiX, wall-clock)
```

Rules, non-negotiable:
- **Same task, same input, same machine, same invocation model.**
- The invocation model is a **real single user run** (start the program, do the overlay, get
  the result) — i.e. a genuine one-shot, cold process. Not a warmed-up long-lived process,
  not same-input replay, not a prepared session. If a warm/service model is ever used, the
  author side must be measured the same warm way, and it must be labeled.
- **End-to-end wall-clock**, not a hand-picked inner phase.
- One number. If the author baseline for the input is not measured, the ratio is "not
  measured" — never borrowed from a different input.

### Number 2 — Ease (answers "easy to write?")

```text
lines of user code + concepts the user must touch (does the user write any CUDA/OptiX by hand?)
RTDL Python/Numba  vs  author C++/CUDA/OptiX, same task.
```

## Honest current standing (the baseline these goals must beat)

- Author C++/CUDA/OptiX: overlay compute ~0.04 s; full query+output ~0.84 s.
- RTDL Python/Numba: ~4.22 s warm-process per-overlay; **~11.6 s a real cold one-shot**.
- So today, measured the way the user actually runs it: **RTDL is ~5–100x slower**, and the
  Python route is still hundreds of lines of careful columnar/CUDA code plus a writer.
- **Verdict today: RTDL does not yet meet "high-performance," and "easy to write" is only
  partly met.** State this plainly; do not hide it behind a favorable regime.

## The gate on every future goal

A goal is authorized only if, in its own exit statement, it shows:
- the expected/actual effect on **Number 1** (the author-vs-RTDL ratio, real one-shot), or
- the expected/actual effect on **Number 2** (ease),

measured the honest way. A goal whose only result is an improvement in replay / prepared /
device-resident-internal metrics, with no effect on Number 1 or Number 2, is **not
authorized** — it is plumbing, and plumbing is not reported as progress.

No regime-switching to manufacture progress. No microsecond precision. No "query-many"
without distinct-input measurement. No sub-phase headline. One task, one machine, one
real-run ratio.

## The one strategic decision the owner must make

The honest ceiling of the current approach (generic primitives + Numba partner, "Layers
1–3") is roughly **~2 s** on this task — the LSI per-input workspace and per-overlay costs do
not shrink below that without changing the architecture. Therefore Number 1 cannot approach
the author by continuing the current path. Choose one:

- **A) "Easier but slower."** Accept that RTDL will not match C++/CUDA/OptiX speed. Stop
  grinding performance regimes. Put all effort into Number 2 (make it genuinely trivial to
  write) and report an honest, stable performance ratio without pretending to chase parity.
- **B) "As fast as C++."** Commit to the architecture that can actually close Number 1 —
  in-traversal fusion (running user computation inside the ray-traversal kernel, "Layer 4").
  This is a real, large project, explicitly out of the current Layer 1–3 scope.

Until the owner picks A or B, no more performance micro-goals. The reason progress has felt
slow is that a simple two-part goal was fragmented into internal sub-metrics because the one
honest comparison is unflattering. Fixing that is this document: **one scoreboard, measured
the way the user runs it, and a decision between A and B.**
