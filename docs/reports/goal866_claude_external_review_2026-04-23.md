# Goal866 External Review — Claude

Date: 2026-04-23
Reviewer: Claude (Sonnet 4.6)

## Verdict: ACCEPT

## Reasoning

The split is both correct and honest.

**Compact modes** (`segment_flags`, `segment_counts`) depend solely on the native
segment-polygon hit-count primitive. Their status correctly flows from the Goal864
gate: currently `needs_segment_polygon_real_optix_artifact` because `librtdl_optix`
is not built on this machine. When Goal864 reaches `ready_for_review`, compact modes
can inherit that readiness — no additional capability is required.

**Rows mode** requires a distinct capability that compact modes do not: a native
OptiX any-hit *row emitter* that produces full pair-row output. That emitter does
not exist yet. Blocking rows mode with `needs_native_pair_row_emitter` is accurate
and independent of the compact-mode gate path. The blocker cannot be cleared simply
by building the OptiX library.

**The packet does not promote anything.** The boundary statement is explicit and
correctly scoped: no RTX claim is being made today, and the rows mode claim is
explicitly forbidden. The test suite covers all three compact-mode upstream states
and confirms that rows mode is always `needs_native_pair_row_emitter` regardless
of upstream state — which is the correct invariant.

No misrepresentation found. The split reflects real architectural differences between
the two output surfaces.
