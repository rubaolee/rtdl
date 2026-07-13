# External Review: X-HD Comprehensive Midterm Status After Goal5408

Date: 2026-07-10
Reviewer: external review (Claude)
Document under review: history/internal_docs/xhd_comprehensive_midterm_status_after_goal5408_2026-07-10.md

## Verdict

```text
approve_with_required_amendments
```

As a document, this report is honest, evidence-backed, free of overclaim, and incorporates the
amendments from the prior (after-Goal5216) review — it is approvable. As a project midterm
assessment, it omits a self-assessment of its single biggest problem: after the dataset blocker was
confirmed negative, and after two prior directives (the Goal5129 plan and my after-5216 review) both
said "datasets first, stop route micro-optimization," the project still spent ~164 goals on
`-lb`/full-cover/native/route micro-engineering — reverse-engineering an author 27.1M-row
implementation-level offload stream whose only consumer (Figure 7) is itself blocked on the
unavailable datasets. That must be confronted in the report.

## Verified (the honest, accurate parts)

- `-lb` non-parity is disclosed faithfully: `hash_parity=false`
  (9732286907904247845 != 4333109858711462591); author sample rows present neither as compact nor
  original; `explicit_lb_support_authorized`, `row_count_parity_with_author_claimed`, and
  `hash_sample_parity_with_author_claimed` all false; the Forbidden list includes explicit -lb
  support and row/hash parity. Arithmetic is exact and self-consistent (62 = 56 + 6, x 437,645 =
  27,133,990 / 24,508,120 / 2,625,870).
- Prior-review amendments incorporated: the executive summary now states "exact for final value, but
  early-aborted per-source witnesses may be approximate" (prior RA-1); no "matches paper log" claim
  (prior RA-2), only author `hd_exec` at 2.38e-9; dataset blocker says "matching counts/bbox/Gini/
  HDResult is not exact input identity."
- Dataset provenance was genuinely and thoroughly searched (goals 5214, 5218, 5270, 5295, 5297,
  5301, 5317-5321, ...) and honestly concluded negative ("exact paper datasets = not proven"). This
  part followed the Goal5129 "datasets first" discipline.
- Level A (bounded value reproduction) and the generic system extraction are externally reviewed
  (I approved 5110-5128); Hausdorff-as-app-level-composition holds.
- Claim boundary (narrow Allowed, comprehensive Forbidden) is accurate; no full-paper / exact /
  ratio / parity / warm-headline / X-HD-core leak.

## Blocking findings

- None. The report makes no overclaim; the evidence supports every positive and negative conclusion.

## Required amendments

- RA-1 (central): the report must add an honest self-assessment of the `-lb`/route
  micro-engineering spend. Facts: the dataset blocker was negative from 5214/5215 and re-confirmed
  through 5270/5295/5317-5321, which blocks Level-C, Figures 5-11, Figure 7, and all `-lb` figures.
  Goal5129 (reviewed) said "do not write more route code until input provenance is answered," and my
  after-5216 review said "stop route micro-optimization unless new generic evidence appears." Yet
  ~164 of the ~200 goals from 5217-5408 went into lb/offload/full_cover/status/cell_mbr/native/
  frontier/route/grid work, much of it reverse-engineering the author 27.1M-row offload stream
  (hash still false, rows still not a subset, now conceded to possibly need "author-only option
  semantics or X-HD constants"). This stream is not required for the paper's scientific result (the
  HD value, already at Level-B); it only serves Figure 7, which is blocked on the unavailable
  datasets. The report must record that this work (a) ran against two prior directives, (b) chased an
  implementation artifact rather than a scientific result, (c) shows clear diminishing returns, and
  (d) risks the X-HD-specific reverse-engineering the project forbids.

- RA-2: Goal5409's Branch A / Branch B must not be presented as an even choice. On the evidence
  (8+ dedicated goals, hash still false), the report should recommend Branch B (fail-close `-lb` as
  unsupported). The bar for Branch A (continue) must match the genericity bar used everywhere else:
  name an app-neutral status transition, show it is not X-HD-specific, and provide a non-X-HD
  consumer (as Goal5128 did for max-nearest). Absent that, continuing is sunk cost.

## Non-blocking notes

- The report never explains what `-lb` is or why its raw rows matter. State once that `-lb` is the
  author's load-balance / heavy-cell offload option, that the "raw offload rows" are an
  implementation artifact, and that reproducing them only matters for Figure 7, which is gated on
  unavailable datasets. This makes Branch B legible as the rational choice.
- The status label is a 6-segment underscore string: honest but unwieldy. Shorten the headline
  label; keep details in the body.
- Single-workload scope (prior RA-3) can still be sharper: Level-B rests on Dragon->HappyBuddha
  alone; "Level-B scalar line = strong" should read "one public workload."
- Documentation churn: a report per goal plus a comprehensive midterm per goal (5407 and 5408 both
  have one) is heavy; produce the comprehensive midterm per batch, not per goal.
- Sandbox shell instability prevented re-running `Ran 20 tests OK`; conclusions rest on direct reads
  of the Goal5408 JSON, filename statistics, and the report.

## Project midterm assessment (comprehensive view)

Genuinely achieved and defensible: bounded directed-HD value reproduction (Level A, reviewed); real
generic system extraction (nearest/witness/max-nearest/cell-MBR, with a non-X-HD consumer);
Level-B scalar HD value on one public workload (2.4e-9 vs the author binary, exact-value-only with
~93.5% approximate per-source witnesses).

Not achieved, honestly labeled: exact datasets (exhaustively searched, negative), full paper, any
Figure, `-lb` / row / hash parity, performance ratio.

The largest midterm problem the report must self-assess: after the core blocker (datasets) was
negative and two prior directives said to pivot, the project spent ~164 goals on route/`-lb`
micro-engineering, chasing an author implementation artifact that is scientifically unnecessary and
whose target figure is already blocked by the missing data. This is not a honesty problem (the
report is honest); it is a resource-allocation and stop-loss discipline problem. The correct midterm
action is: freeze Level-B, fail-close `-lb` per Branch B (unless a named generic transition + a
non-X-HD consumer can be produced), and reserve remaining effort for the "wait for exact data, then
Level-C/figures" holding state.

## Allowed final summary

X-HD has achieved: bounded directed-HD value reproduction (reviewed) + real generic system
extraction (with a non-X-HD consumer) + a Level-B scalar HD value on one public same-source workload
(Dragon->HappyBuddha) matching the author binary to 2.4e-9 (exact-value-only; ~93.5% of early-aborted
per-source witnesses approximate). Exact paper datasets were exhaustively searched and are
unavailable, so Level-C, all figures, `-lb`, and performance ratios are not achieved and are blocked
on data. The `-lb` raw stream has no row/hash parity with the author; the recommendation is to
fail-close `-lb` as unsupported unless a named app-neutral status transition with a non-X-HD consumer
appears.

## Forbidden summaries

- full paper / exact dataset / any figure reproduction;
- explicit `-lb` support or row/hash parity with the author raw stream;
- author-vs-RTDL performance ratio or parity;
- warm/diagnostic numbers as a fresh headline;
- "Level-B reproduction complete" without the single-workload scope;
- "exact nearest witnesses".

## Bottom line

The report is honest and approvable as a document. But a comprehensive midterm review must name what
the report will not: after the datasets were confirmed unavailable and two prior directives said to
pivot, the project spent ~164 goals reverse-engineering a scientifically unnecessary author
implementation artifact. Add the self-assessment and recommend fail-closing `-lb`, and the midterm
status can stand as the honest, stop-loss-disciplined handoff it should be.
