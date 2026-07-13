# Claude Review — Goal4997→Goal5004 v2.14.3 Binary Route Workstream (critical)

Date: 2026-07-05
Reviewer: Claude (strict)
Under review: Goals4997/4998/4999/5001/5002/5003/5004 + interim/response docs.

## Verdict

```text
revise_goal4997_to_goal5004_before_goal5005_docs_boundary
```

Do not proceed to Goal5005 documentation yet. The regime honesty is now genuinely good and
I credit it. But the workstream is about to headline v2.14.3 fresh at ~5.0 s **without
disclosing that this is ~0.78 s slower than a route that already existed** (goal4985
fast-pack, ~4.22 s), and the "accounting-corrected" fresh number is misattributed and
reported at false precision. Both must be fixed before Goal5005 writes the public number.

## The negative finding the workstream does not confront: device-residency regressed fresh

Same top4 input, same anchors (`lsi_row_count=428322`, `descriptor_pairs=15014`):

```text
goal4985 fast-pack route (no --device-resident-carrier):
  fresh ~4.220 s = LSI ~2.7 s + downstream ~1.48 s

goal5001 device-resident-carrier route:
  fresh  4.816 s = LSI 2.588 s + downstream 2.366 s
goal5004 device-resident-carrier route:
  fresh  5.004 s = LSI 2.629 s + downstream 2.375 s
```

The LSI is essentially unchanged (~2.6–2.7 s). **The entire fresh regression lives in
downstream: 1.48 s → 2.37 s, ~+0.9 s.** The `--device-resident-carrier` path pays first-call
device-kernel compile / prepared-session setup / device-scatter cost in the one-shot regime
that the simpler host-carrier fast-pack route did not. Its benefit appears **only** in the
0.33 s prepared-replay diagnostic — the regime the team itself (correctly) says is not a
product result.

So, stated plainly: **measured in the product-relevant fresh regime, the Goal4998/4999
device-residency campaign made v2.14.3 slower, not faster.** The goal5004 matrix shows
fresh 5.00 s / prewarm 4.58 s / replay 0.33 s — but omits the goal4985 fast-pack fresh
4.22 s, which is faster, correct (same anchors), and still available (it is just the same
route without the `--device-resident-carrier` flag). Headlining v2.14.3 at 5.00 s while a
correct 4.22 s route exists is choosing the worse number.

**Required before Goal5005:**
- Put both fresh numbers in the matrix: device-resident-carrier ~5.0 s **and** fast-pack
  ~4.22 s, same input, same regime.
- State explicitly that device-residency currently **costs** ~0.78 s in fresh one-shot
  (all in downstream) and that its payoff is confined to warm/replay (and a not-yet-
  demonstrated query-many).
- Decide and justify the v2.14.3 default. If the device-resident route is kept as the
  headline for architectural reasons, say so and show it is slower; do not present 5.00 s
  as progress without the 4.22 s comparator.

This is not an argument against the device-resident architecture — it is a legitimate
forward investment whose ceiling (0.33 s replay) is real. It is an argument against
shipping a fresh regression as if it were the win, unlabeled.

## The accounting-fix delta is misattributed and over-precise

Goal5004 attributes the change `4.816 s → 5.004 s` (+0.19 s) to fixing a
`writer_free_hot_sec` key omission (device midpoint query-point phases were not counted).
But those phases are ~0.003 s total (goal4999: ~0.0015 s + ~0.0017 s + ~0.0002 s prepares).
**~0.003 s cannot explain +0.19 s.** goal5001 (4.816 s) and goal5004 (5.004 s) are *different
POD runs*, and this route has ~4–20 % run-to-run variance (established earlier: the "public
rows" baseline itself swung 7.851 s↔9.387 s). So most of the +0.19 s is almost certainly
**run variance mislabeled as an accounting correction.**

**Required:**
- Isolate the true accounting delta by re-running the **same** command **before and after**
  the key fix in one session; report that delta (expected ~0.003 s), not a cross-run diff.
- Stop reporting fresh as `5.003915 s`. Microsecond precision on a number with ~±0.2 s run
  variance is false precision. Report `~5.0 s (single run; ±~0.2 s run variance)` or a
  median-of-N.

## Re-audit all device-route numbers with the corrected accounting

The buggy `writer_free_hot_keys` affected **every** `--device-resident-carrier` number
reported before goal5004 — goal4998, goal4999's `0.3295 s` replay, goal5001's `4.816 s`.
The fix was applied to the fresh headline, but the matrix's replay `0.332861 s` and
prewarm `4.584897 s` rows must be confirmed to use the **corrected** key list, or they are
still undercounted. Re-audit and label each matrix cell as pre- or post-fix accounting.

## What is genuinely right (credit — this is negative-but-correct, not just negative)

- **Regime honesty is now real and adopted from the prior reviews.** Fresh (~5.0 s) is the
  headline, not 0.33 s; replay and compile-prewarm are labeled diagnostic; no query-many
  claim; no top4 author ratio; the CLI "query-many" wording is flagged as naming debt to
  fix before release. This is the correction I demanded, and it held.
- **Goal5002 confirms the compile is prewarmable** (`exact_pipeline_ensure +
  split_kernel_ensure` ~0.99 s → ~6e-7 s via a tiny generic `prepare_planar_map_lsi_2d_optix`)
  and correctly refuses to headline it (prewarm must be outside the window). This
  implements my prior N2 and is generic, not RayJoin-specific.
- **Goal5003 confirms the ~1.67 s per-input workspace is scale-domain-dependent and
  intrinsic** (changed-scale-domain probe rebuilds ~1.47 s), and keeps it in fresh. This
  implements my prior N1 and is honest.
- **The team caught its own undercounting** in goal5004 and the fix made the number *worse*
  — self-correction against its own interest is exactly the behavior this process wants.
- **Genericity preserved:** app-layer route, no RayJoin core primitive, device-query API
  generically named (legacy `PreparedRayjoinCdb*` internal naming debt still noted, not new).

## Answers to the review questions

1. RTDL-generic / RayJoin-app principle preserved? **Yes** (legacy internal naming debt persists).
2. Hidden RayJoin core semantics added? **No.**
3. Goal4998 a legitimate writer-free binary route, not paper-text? **Yes.**
4. Goal4999 device-query API generic? **Yes** (naming generic; forwards into legacy rayjoin-named internals).
5. Goal5001 correctly targeted fresh LSI first over downstream micro-work? **Yes — correct call.**
6. Goal5002 proves compile is prewarmable, refuses fresh headline? **Yes.**
7. Goal5003 proves workspace is scale-domain-dependent, kept in fresh? **Yes.**
8. Goal5004 accounting fix correct and sufficient? **Direction yes; magnitude misattributed
   and over-precise (see above) — not sufficient as reported.**
9. Fresh headline `5.003915 s` rather than `4.8 s` or `0.33 s`? **Fresh ~5.0 s is right vs
   0.33 s. But `5.003915 s` is false precision, the +0.19 s vs 4.816 s is mostly variance,
   and the number must be shown next to the faster 4.22 s fast-pack route.**
10. Close and proceed to Goal5005 docs? **No — revise first (the fresh-comparison disclosure,
    the accounting isolation, the re-audit).**

## Claims: approve / reject adjustments

Of the "claims to approve," these need edits before Goal5005 uses them:
- Claim 3 ("fresh top4 is 5.003915 s") → "fresh top4 device-resident-carrier route is
  ~5.0 s (±~0.2 s); the host-carrier fast-pack route is ~4.22 s — device-residency currently
  costs ~0.78 s in fresh."
- Claim 4 (prewarm 4.584897 s) and Claim 5 (replay 0.332861 s) → confirm post-fix accounting
  and drop the false precision.

The "claims not to approve" list is correct and I endorse it (no 0.33 s fresh, no query-many,
no author parity, no author ratio, no byte-equality, no zero-copy, no workspace-solved, no
RayJoin core primitive).

## Non-authorization

No Goal5005 documentation using 5.00 s as the unqualified v2.14.3 fresh headline until the
4.22 s fast-pack comparison is disclosed and the default is justified; no false-precision
fresh number; no matrix cells whose accounting basis (pre/post key fix) is unstated; no
public release; no author parity/ratio; no query-many; no RayJoin-specific core semantics.
The honest current state: v2.14.3's writer-free binary route is ~4.22 s fresh with the
host-carrier fast-pack path and ~5.0 s fresh with the device-resident-carrier path — the
device-resident path is an architectural investment that currently **regresses** fresh and
pays off only in warm/replay, which is not yet a product regime.
