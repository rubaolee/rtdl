# Goal4886 Review Debt

Date: 2026-07-03

## Goal

`Goal4886`: first Numba partner engineering pass for the RayJoin
paper-reproduction app.

## Current Evidence

Primary report:

```text
history/internal_docs/goal4886_rayjoin_numba_partner_acceleration_report_2026-07-03.md
```

Call for review:

```text
history/internal_docs/call_for_review_goal4886_rayjoin_numba_partner_acceleration_2026-07-03.md
```

Antigravity review:

```text
history/internal_docs/antigravity_goal4886_rayjoin_numba_partner_acceleration_review_2026-07-03.md
verdict: approve_goal4886_numba_writer_skip_speedup_bounded_australia
```

Antigravity re-review:

```text
history/internal_docs/antigravity_goal4886_authorofficial_wall_boundary_rereview_2026-07-03.md
verdict: approve_goal4886_authorofficial_wall_boundary_honest
```

## Result Needing Additional Review

On the Australia representative Section 5.7 public-primitives route:

```text
Current RTDL repeat: 117.258 s, byte-equal
RTDL+Numba writer skip repeat: 100.531 s, byte-equal
bounded speedup: 1.166x
writer phase: 16.525 s -> 1.811 s

RTDL+Numba explicit skip-decision run: 103.786 s, byte-equal
bounded speedup: 1.130x
writer phase: 16.525 s -> 2.040 s
```

The first writer-skip repeat is the best measured wall result. The explicit
skip-decision run is the better-specified implementation evidence because it
routes the skip condition through a dedicated Numba parity-tested decision
kernel.

AuthorOfficial wall-time note:

```text
Final AuthorOfficial comparator phase timings exist.
Final AuthorOfficial wall time is unavailable.
Two Goal4886 wall reruns failed to reproduce the final comparator SHA and are
therefore invalid as wall baselines.
```

The claim is bounded to this representative route. It does not authorize broad
RayJoin speedup, full hidden-input eight-pair claims, or AuthorOfficial wall
time claims.

## Open Debt

The project rule requires goal-level completion to receive multi-AI review.
Antigravity has reviewed and approved. Claude was not available from the
current PATH (`claude` / `claude.exe` not found), so Claude review remains
open debt.

## Requested Future Claude Check

Claude should review:

1. whether the writer skip plan is semantically safe;
2. whether byte-equality plus two POD runs are enough for this bounded claim;
3. whether the speedup wording is correctly bounded;
4. whether the AuthorOfficial wall-boundary handling is honest;
5. whether Goal4886 may close under:

```text
completed_numba_partner_writer_skip_speedup__byte_equal__bounded_australia_representative
```

## Non-Authorization

This debt file does not authorize:

- broad RayJoin speedup claims;
- full eight-pair Section 5.7 claims;
- hidden-input paper reproduction claims;
- changes to `src/rtdsl/**` or `src/native/**`;
- treating Numba as correctness-critical for prior 5.2/5.3/5.7 evidence;
- treating AuthorOfficial logged phase timings as a full wall-time baseline.
