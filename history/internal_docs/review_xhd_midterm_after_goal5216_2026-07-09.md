# External Review: X-HD Midterm Report After Goal5216

Date: 2026-07-09
Reviewer: external review (Claude)
Document under review: history/internal_docs/xhd_midterm_report_after_goal5216_2026-07-09.md

## Verdict

```text
approve_with_required_amendments
```

The machine-readable evidence is impeccably honest (`exact_paper_dataset_identity_proved=false`,
`paper_log_min_abs_diff=1.937e-7`, `per_source_witness_exact=false`,
`global_bound_early_break_count=409376`, all ratio/parity flags false, warm separated with
warmup excluded). The Level-B status, the exact-dataset blocker, and the plan are sound. The
problem is that the report's prose is looser than its own evidence in three places, and states a
narrow achievement in broad terms. Not fabrication — precision must be tightened before this
report becomes the stable X-HD handoff.

## Blocking findings

- None. The evidence supports every Level-B claim; no Level-C, ratio, or parity overclaim is
  actually asserted in the machine-readable artifacts.

## Required amendments

- RA-1 (approximate witnesses under-disclosed). The Level-B route uses `global_bound_early_break`;
  the evidence shows 409,376 of 437,645 sources (93.5%) early-abort and `per_source_witness_exact=false`.
  The route computes the exact directed-Hausdorff maximum value, but the per-source nearest
  witnesses are approximate for ~93.5% of sources. Goal5211 discloses this and forbids treating the
  witnesses as exact; the midterm report omits it entirely from its "matches author HDResult"
  narrative. The report must state: the Level-B route is exact-value-only, with ~93.5% approximate
  per-source witnesses, correctness limited to the directed-HD scalar.

- RA-2 ("matches the paper-branch log" is an overclaim). The number chain: author `hd_exec` on
  public data = 0.12572988867759705; paper-branch log = 0.12572969496250153 (differ by 1.937e-7);
  RTDL = 0.12572988629271128, which matches the author re-run to 2.4e-9 but differs from the paper
  log by ~1.9e-7. So RTDL matches the author binary re-run on public data, NOT the paper log; the
  author re-run itself differs from the paper log by ~1.9e-7 (100x looser than RTDL-to-author-rerun),
  and that gap is itself a fingerprint of public input non-identity. The Executive Summary ("the
  author result also matches the pinned paper-branch author log") and the Allowed summary ("both
  match the author paper-branch HDResult") must be requantified: matches the author re-run on public
  same-source data; the re-run differs from the paper log by ~1.9e-7, consistent with input
  non-identity.

- RA-3 (narrow "Level-B" scope). The entire Level-B rests on ONE directed-HD scalar on ONE public
  graphics pair (Dragon->HappyBuddha). The paper spans MRI (BraTS, 494 images), geospatial (many),
  and graphics (4 meshes). The report itself admits "figures require more than one representative
  graphics workload," yet still frames the state as a "Level-B representative reproduction packet."
  Reword to "one Level-B same-source representative workload matched (Dragon->HappyBuddha, directed)",
  not broad Level-B reproduction.

## Non-blocking notes

- No independent exact oracle at scale. At 437,645 x 543,652, materialized pairwise is infeasible,
  so large-scale correctness rests on author agreement only; independent exact-reference agreement
  exists only at the small Level-A gates. State this: large-scale value correctness = author
  agreement (+ small-scale exact reference), not an independent exact check. Shared systematic bias
  between the RTDL grid route and the author RT route is unlikely for a max but should be acknowledged.
- Cross-document timing inconsistency: fresh route wall is 0.849s (Goal5211 table) / 0.8517s
  (consolidation) / 0.852s (midterm); "full total incl load" is ~1.531s (midterm) vs 1.752s (Goal5211).
  Unify or cite the source run.
- Warm (0.288s) is correctly not the headline (fresh 0.852s / full 1.531s lead), warmup excluded,
  full-incl-warmup 1.808s reported separately. Honest; keep.

## Answers to review questions

1. Yes. Level-B vs Level-C is clearly distinguished (`exact_paper_dataset_identity_proved=false`;
   Level-C blocked).
2. Mostly. No full-paper/exact-identity/parity/ratio claim; the only boundary-adjacent wording is
   "matches paper log" (RA-2).
3. Yes. Regimes are labeled (fresh / full-incl-load / explicit-warm with warmup separate); warm is
   not the headline.
4. Partial. The blocker is described strongly (counts/family/HDResult are explicitly stated as
   insufficient for byte identity), but the report's own "matches paper log" violates that spirit — RA-2.
5. Yes. RTDL owns generic nearest/frontier/reduction/traversal; the app owns inputs/wrappers/
   tolerance/comparator (Goal5128 supplies a non-Hausdorff consumer).
6. No — the main defect. The midterm does not fairly characterize Goal5211 as an exact-value-only
   optimization with ~93.5% approximate per-source witnesses; Goal5211 itself does, the midterm does
   not. RA-1.
7. Yes. The plan correctly prioritizes review, Level-B stabilization, and exact-dataset provenance
   over route micro-optimization (Step 3 explicitly stops micro-optimization).
8. Useful but must be careful: the same-POD matrix separates five denominators and refuses ratios
   unless aligned; it should also flag the algorithmic-regime mismatch (author RT-core vs RTDL grid
   route) so even same-machine, same-data numbers are not read as like-for-like.
9. Yes, three facts already in the JSON are missing from the prose and must be added:
   `per_source_witness_exact=false`, `early_break_count=409,376/437,645`, and
   `paper_log_min_abs_diff=1.937e-7` (RA-1/RA-2).
10. Yes, but only with tightened wording: close as "one Level-B same-source representative workload +
    system extraction, exact paper reproduction blocked on data," carrying RA-1/RA-2/RA-3. Not as a
    broad "Level-B reproduction complete."

## Rulings on Claims A-E

- Claim A (Level-B not full): holds, but "Level-B" must be scoped to a single workload (RA-3).
- Claim B (matches author HDResult, exact identity unproved): half-holds. It matches the author
  re-run (2.4e-9), not the paper log (1.9e-7); exact identity correctly unproved. Fix per RA-2.
- Claim C (generic components, not an X-HD primitive): holds (native cell-MBR/early-break contracts
  are generic; non-Hausdorff consumer exists).
- Claim D (numbers are not author-vs-RTDL ratios/parity/speedup): holds (ratio/parity flags false;
  no ratio computed).
- Claim E (next blocker is exact input provenance, not micro-optimization): holds and correct.

## Allowed final summary

RTDL has matched the author `hd_exec` directed-Hausdorff value on one Level-B same-source
representative workload (public Stanford Dragon->HappyBuddha) to ~2.4e-9, using a generic
grid/cell-MBR route with an optional global-bound early break that yields the exact directed-HD
value but approximate per-source witnesses for ~93.5% of early-aborted sources. The author binary
re-run on public data differs from the paper-branch log by ~1.9e-7, consistent with the public
inputs not being byte-identical to the paper datasets; exact paper dataset identity is unproved and
blocked on missing input files/hashes/provenance. Fresh route wall ~0.852s, full gate incl. load
~1.531s, explicit-warm ~0.288s (warmup separate). No author-vs-RTDL ratio, parity, speedup,
exact-paper, or figure reproduction is claimed.

## Forbidden summaries

- "RTDL matches the paper(-branch) X-HD result / paper log." (It matches the author re-run; it is
  ~1.9e-7 off the paper log.)
- "Level-B representative reproduction complete." (Without the single-workload scope.)
- "RTDL computes the exact nearest witnesses / exact X-HD." (93.5% of witnesses are approximate.)
- Any author-vs-RTDL ratio / parity / speedup / warm-only headline / exact-paper / figure
  reproduction.

## Bottom line

This is one of the most honest reports in the series at the evidence level, but the prose sells a
narrow result too broadly: it states "matches the paper log" when it matches the author re-run
(1.9e-7 off the log), "matches author HDResult" while hiding that 93.5% of per-source witnesses are
approximate, and "Level-B reproduction" off a single workload. Tighten those three, and the Level-B
handoff can be approved.
