# Goal3512 v2.8 Closeout Goal Sequence And Consensus Plan

Date: 2026-06-05

## Verdict

`needs-external-review`.

This document is Codex's proposed goal-mode sequence for closing RTDL v2.8 as an
internal version. It is not a release packet and does not authorize release,
public speedup wording, broad RT-core speedup wording, RayJoin paper reproduction
claims, `rtdl beats RayJoin` wording, true zero-copy wording, or full overlay
claims.

The requested consensus target is 3-AI:

- Codex: this proposal and implementation owner.
- Claude: independent review requested via
  `docs/handoff/HANDOFF_CLAUDE_GOAL3512_V2_8_CLOSEOUT_GOAL_SEQUENCE_REVIEW_2026-06-05.md`.
- Gemini: independent review requested via
  `docs/handoff/HANDOFF_GEMINI_GOAL3512_V2_8_CLOSEOUT_GOAL_SEQUENCE_REVIEW_2026-06-05.md`.

## Current Position

The recent overlay/RayJoin v2.8 lane moved from "large setup-heavy prototype" to
a measured prepared-execution story:

| Evidence | Result | Boundary |
| --- | ---: | --- |
| Goal3505 best 8-worker rebuild | `1.441s` geometry+payload prep | pod/dataset-specific CPU prep |
| Goal3507 JSON cache read | `0.355s` prep reload | host-side cache, not zero-copy |
| Goal3509 binary cache read | `0.171s` prep reload | host-side `.npz` cache, not device persistence |
| Goal3511 steady relation stream | `0.00387s` final active relation device-column pass | steady-state after warmup; not full-app speedup |
| Goal3511 tile executor | `0.0143s` best repeat | prepared simple-polygon tile tasks only |

Interpretation: the next serious v2.8 target is not another RT traversal tweak.
The resident relation-column primitive is already millisecond-scale after
warmup. v2.8 should close around a clean prepared-execution user story:
explicit setup, reusable handles/caches/columns, steady-state timing, benchmark
matrix, docs, audits, and 3-AI consensus.

## Goal-Mode Sequence

### `/goal 3512: approve or revise the v2.8 closeout sequence`

Purpose: get 3-AI agreement on this goal order before turning it into a closeout
packet.

Required outputs:

- Claude review in `docs/reviews/goal3513_claude_review_goal3512_v2_8_closeout_sequence_2026-06-05.md`.
- Gemini review in `docs/reviews/goal3514_gemini_review_goal3512_v2_8_closeout_sequence_2026-06-05.md`.
- If both reviews accept or accept-with-boundary, write a consensus file:
  `docs/reports/goal3515_v2_8_closeout_goal_sequence_3ai_consensus_2026-06-05.md`.

Acceptance bar:

- The sequence must preserve app-agnostic engine boundaries.
- It must not treat internal v2.8 closeout as a public release.
- It must distinguish setup, cache load, resident relation streaming, planner,
  executor, and validation oracle costs.
- It must identify which remaining steps need pod evidence.

### `/goal 3516: close current evidence bookkeeping`

Purpose: finish the already-produced evidence trail before new engineering.

Tasks:

- Commit and push Goal3511 report/artifacts/test if still uncommitted.
- Intake Claude reviews for Goal3507 and Goal3509.
- Request and intake review for Goal3511 steady-state relation-stream evidence.
- Record any required fixes before the closeout packet.

Acceptance bar:

- Goal3511 tests pass locally.
- Goal3507/3509/3511 review files exist or failures are recorded honestly.
- No claim boundary is expanded.

Pod requirement: no new pod needed unless a reviewer requests rerun evidence.

### `/goal 3517: define the prepared-execution user pattern`

Purpose: make the v2.8 user-facing workflow explicit and reproducible:
`prepare -> pack/cache -> run steady-state -> explain timings`.

Tasks:

- Document or add a thin public helper pattern for prepared execution without
  hidden dispatch.
- The pattern must expose setup time, cache load time, warmup count, steady-state
  relation stream time, planner time, executor time, and validation time.
- The pattern must keep partner choice explicit and must not auto-select Triton,
  CuPy, Numba, or Torch.

Acceptance bar:

- A learner can see how to reuse prepared right-side scenes, packed left columns,
  binary prepared-payload cache, relation columns, and continuation inputs.
- The native engine remains generic; app interpretation remains in examples or
  Python orchestration.
- No release or public speedup wording is introduced.

Pod requirement: likely one targeted pod artifact after implementation.

### `/goal 3518: refresh the 10-app v2.8 benchmark matrix`

Purpose: produce the v2.8 internal benchmark state in one readable table.

Tasks:

- Cover all 10 benchmark apps.
- For each app, classify:
  primitive-only, partner-needed, or prepared-execution-needed.
- Report setup and steady-state timing separately where applicable.
- Include correctness oracle status and claim-boundary status.
- Include RayJoin/overlay and Hausdorff benchmark rows, but do not claim paper
  reproduction unless a separate reviewed packet authorizes it.

Acceptance bar:

- No `n/a` cells without an explanation.
- No benchmark row collapses setup and steady-state into one ambiguous number.
- Every public-facing claim flag remains false unless separately authorized.

Pod requirement: yes, targeted final timing refresh on current HEAD.

### `/goal 3519: clean v2.8 learner docs and research benchmark docs`

Purpose: make the repo navigable for users without historical clutter.

Tasks:

- Update front-page and learner docs to describe current v2.8 behavior only.
- Move or link older version details into historical paths.
- Ensure research benchmark docs explain how to run the v2.8 examples, what
  results mean, and what claims are not authorized.
- For RayJoin/overlay, explain prepared execution, binary cache, and steady-state
  relation stream clearly.

Acceptance bar:

- Normal users see one current-version story.
- Historical details are accessible but not mixed into the main learning path.
- Links are checked.

Pod requirement: no, except if docs include runnable examples that need RTX
validation.

### `/goal 3520: final claim-boundary and stale-doc audit`

Purpose: block accidental overclaiming before closeout.

Tasks:

- Run claim-boundary scans.
- Search docs/examples for stale version terms, stale partner claims, and
  unsupported package-install claims.
- Check that v2.8 docs do not claim true zero-copy, full RayJoin reproduction,
  broad RT-core speedup, or v2.8 public release.

Acceptance bar:

- Audit report lists each inspected public doc/example group, problem found,
  action taken, and residual risk.
- Any unresolved stale text is either fixed or explicitly quarantined.

Pod requirement: no.

### `/goal 3521: final v2.8 validation packet`

Purpose: collect the final internal closeout evidence at a single clean commit.

Tasks:

- Run focused local tests for v2.8 primitive discovery, partner boundaries,
  prepared execution, overlay/RayJoin, Hausdorff, RTNN, DBSCAN, docs/audit
  tests, and claim-boundary tests.
- Run targeted pod tests only for RTX/OptiX evidence rows that need current-HEAD
  confirmation.
- Produce a packet with commit hash, commands, outputs, artifacts, and residual
  boundaries.

Acceptance bar:

- Every required test command is reproducible.
- Pod use is targeted and time-bounded.
- Failures are not hidden; any skipped row has a reason and next step.

Pod requirement: yes, final targeted pod refresh.

### `/goal 3522: final v2.8 internal closeout consensus`

Purpose: close v2.8 internally after evidence and reviews, without pressing a
public release button.

Tasks:

- Write closeout packet after Goals3516-3521 complete.
- Request fresh Claude and Gemini reviews.
- Write 3-AI consensus only after review files exist.

Acceptance bar:

- Codex + Claude + Gemini agree on the exact boundaries.
- The closeout packet says v2.8 is internal unless the user explicitly asks for
  a public release step.
- Future work is moved to `docs/research/future_version_to_do_list.md`, not left
  only in chat.

Pod requirement: no new pod unless reviewers request more evidence.

## Reviewer Questions

External reviewers should answer:

1. Is this the right goal order to close v2.8 without scope creep?
2. Are any goals missing before a v2.8 internal closeout?
3. Should any goal move earlier, especially prepared-execution docs versus final
   benchmark refresh?
4. Does the sequence preserve the app-agnostic engine boundary?
5. Does it correctly separate setup time, cache load, steady-state relation
   streaming, continuation execution, and validation oracle time?
6. Are the pod requirements sufficiently targeted?
7. Is `accept-with-boundary` the right expected verdict shape, or does any step
   need `needs-more-evidence` before proceeding?

## Codex Position

Codex recommends proceeding in this order after external review:

1. Close evidence bookkeeping.
2. Define the prepared-execution user pattern.
3. Refresh the 10-app v2.8 benchmark matrix.
4. Clean docs and audit claims.
5. Produce a final validation packet.
6. Seek final 3-AI closeout consensus.

This should be enough to close v2.8 as an internal version. It should not become
v3.0 device-residency work, user-defined shader injection, or a public release
unless the user explicitly redirects.
