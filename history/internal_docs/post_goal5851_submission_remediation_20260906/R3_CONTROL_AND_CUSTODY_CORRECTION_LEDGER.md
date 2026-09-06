# R3 current-control and historical-custody correction ledger

Date: 2026-09-06

Status: `CLOSED_WITH_EVIDENCE`

This is an additive execution record. It does not rewrite any historical
authority, raw evidence, archive, review, call-for-review, or failed run. When
an earlier document is wrong or stale, the original bytes remain preserved and
this ledger supplies the controlling replacement fact for current manuscript,
artifact, and submission work.

## 1. Controlling identities and scope

- Measured implementation M is commit
  `d653fe4ad170c5b51fee309d653c9565944dcf2e`, tree
  `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b`.
- Predecessor E is commit
  `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8`, tree
  `aa8b9b12a7bf9cf4395cb71e4fb8e6eb0f169ab6`.
- Candidate tooling snapshot F has not yet been committed. R2 is a successful
  pre-F rehearsal and must be repeated from a clean checkout of final F.
- Paper snapshot P has not yet been created.
- The original written per-execution receipt requirement was not fulfilled.
  The machine numerical contract passed and no wrong output was observed in
  the retained final GPU samples. These are distinct findings.
- Public and manuscript claim authorization remains false. Reviews already
  received concern pre-final bytes; they are not R7 review of the final PDF and
  package. External human authoring observations remain zero.

## 2. Correction ledger

| ID | Preserved original location | Original or ambiguous statement | Controlling replacement fact | Evidence |
| --- | --- | --- | --- | --- |
| R3-E01 | `history/internal_docs/call_for_review_post_goal5851_cgo2027_20260906.md:228`; `history/internal_docs/strict_self_review_since_last_claude_goal5848_goal5851_20260906.md:308` | Ada archive digest is a 63-character value missing one `2`. | Correct archive SHA-256 is `c9128bae15da7ed3262c0bad96799e8cc56d1292c14f9af8713ea174cfc2cced`. The malformed transcription is not a second artifact identity. | R0 recomputed local archive hash; 2,405-member manifest check had zero failures. |
| R3-E02 | Earlier revision retained and identified by `history/internal_docs/goal5850_generation_a_final_report_20260906.md:11-14` | Only two Ada Goal5850 triangle A/D blocks exceeded `1.35x`. | Three blocks exceeded `1.35x`: `1.452162x`, `1.394327x`, and `1.401147x`. | Same report lines 184-188 and raw retained block values. |
| R3-E03 | Historical repair/report prose identified by `history/internal_docs/codex_review_post_goal5851_cgo2027_20260906.md:152-158` | `1.35x` was described as an A/D public/Direct worst-block gate. | A/D has only a median gate at `1.20x`; there is no registered A/D worst-block gate. `1.35x` belongs to A/C implementation-entry worst block. A/D maxima remain descriptive and must be reported, not relabeled as pass/fail criteria. | Frozen Goal5848 contract; R2 recount report Section 5. |
| R3-E04 | `history/internal_docs/strict_self_review_since_last_claude_goal5848_goal5851_20260906.md:627-630` | The formal evidence workers materialize and bind detailed receipts after every timed sample. | Across 32 Arm-A formal workers there are 4,096 timed A calls but only 32 separate diagnostic receipts. Timed workers have `latest_output_sha256=null`; the original complete per-execution detailed-receipt requirement was not met. Synchronous native status, compact status, and explicit output-oracle checks still protect the observed output path. | `PROTOCOL_SCOPE_ADJUDICATION.md`; `RECEIPT_CLAIM_CORRECTION.md`; R1 raw recount. |
| R3-E05 | `history/internal_docs/review_post_goal5851_cgo2027_20260906.md:166` and similar broad readings of the 512-worker statement | Instrumentation overhead was measured for all formal arms or both RTDL/PyOptix arms. | The formal arm policy is symmetric, but the separate paired ON/OFF instrumentation qualification executed Arm A only: 512 workers per generation, 1,024 total endpoint observations. It does not empirically qualify B or C overhead. | R2 projection and recount; `CLAIM_LEDGER.json` instrumentation claim. |
| R3-E06 | `history/internal_docs/review_post_goal5851_cgo2027_20260906.md:188`; earlier review discussion of constructor counts | Goal5837 or Goal5838 should mechanically increase the stable public constructor count. | The stable `rtdsl.v4` fixed-constructor count remains two. Goal5837 is an additional root-exported closed successor route, not a third stable constructor. Goal5838 contributes one bounded prospective composition exam; unbiased new-application exam count remains zero. | Goal5837 authority; Goal5838 final authority; current public exports. |
| R3-E07 | Broad Goal5840 descriptions corrected at `history/internal_docs/strict_self_review_since_last_claude_goal5848_goal5851_20260906.md:556-575` | Goal5840 establishes general partial evaluation or general semantic compiler refinement. | Goal5840 is a separately implemented finite structural checker over its exact registered route groups, four modes, five properties, 20 applications, and 15 unique mutations. It is not a general soundness theorem or proof for arbitrary callbacks. | Goal5840 final authority and independent checker source. |
| R3-E08 | `history/internal_docs/review_post_goal5851_cgo2027_20260906.md:156`; `history/internal_docs/review_since_last_claude_goal5830_goal5848_20260905.md:178-180` | All ten Goal5838 candidates share one four-role topology. | Seven built-in candidates have four roles. Three custom-primitive candidates additionally require `bounds` and `intersection`, for six roles. All ten do share a per-query result-count relation, but that does not erase the role-set distinction. | `history/internal_docs/goal5838_generic_core_exam_20260902/CHALLENGE_TABLE.json`. |
| R3-E09 | Earlier action-plan wording corrected by strict review; denominator discussion at `history/internal_docs/review_since_last_claude_goal5830_goal5848_20260905.md:315-319` | Curve any-hit-terminate was the selected Goal5838 item or made the denominator nine. | `builtin_round_linear_curve::any_hit_terminate_bool_per_query` is an eligible candidate. The actual selected item is `builtin_sphere::any_hit_count_continue_u64_per_query`. The older curve Boolean route used closest-hit, so the distinct any-hit-terminate candidate keeps the eligible denominator at ten. | Goal5838 challenge table, selection result, and final authority. |
| R3-E10 | `history/internal_docs/review_post_goal5851_cgo2027_20260906.md:1063` | The review session could not recount the performance evidence. | The same review reports a completed recount in Sections 1.1 and 9, including reconstructed lifecycle and performance values. The final-paragraph qualification is internally inconsistent and must not be copied into current prose. R2 subsequently reconstructed all 160 cells and 20,480 samples independently. | Review Sections 1.1/9; R2 report and projection. |
| R3-E11 | `history/internal_docs/review_post_goal5851_cgo2027_20260906.md:223-228` | The current Goal5848 Arm-C import is the historical `5.206 s` PyOptix import. | `5.206 s` is a Goal5847 complete-process observation. Current Goal5848 Arm-C import medians are approximately 467-578 ms across the four generation/task rows. The historical value may explain lineage, not quantify the current experiment. | R2 lifecycle table reconstructed from current raw workers. |
| R3-E12 | `history/internal_docs/review_post_goal5851_cgo2027_20260906.md:278-282`, reiterated at lines 827-829 | The Ampere relation entry spread proves module loading caused the dispersion. | Import is a documented component and both endpoints are lifecycle-confounded, but one outlier/range does not identify a unique causal source of dispersion. Current prose may report the decomposition and range, not a causal proof without controlled attribution. | R2 per-worker lifecycle decomposition; no dedicated causal intervention. |
| R3-E13 | Current Goal5851 completion summaries that say all frozen checks passed without qualification | A machine PASS proves the complete original written protocol, including detailed receipts for every timed execution. | Machine numerical gates passed at M, but the original written per-execution receipt clause did not. Current wording must explicitly separate numerical/output observations from the unmet evidence-retention clause. | R1 protocol-scope adjudication and claim ledger. |
| R3-E14 | Current success-path architecture summaries that imply universal fail-closed cleanup | All native forks and provider bind/close double faults preserve original error and retry ownership. | Cached-PID checks do not cover native forks that bypass Python at-fork hooks. Provider bind/close double faults can overwrite the first error or lose retry ownership. These implementation defects remain unrepaired; the submission claim is narrowed to supported successful paths and tested single-fault envelopes. | Source audit recorded in the post-Goal5851 reviews and R1 ledger. |

## 3. Exact-snapshot custody replay performed in R3

The current-tree commands were executed with Python 3.12 and failed as already
reported:

```text
Goal5837 --verify-stored: exit 1, Goal5837Error: AUTHORITY_CURRENT_INPUT_MISMATCH
Goal5843 --verify-stored: exit 1, Goal5843ContractError: preregistration differs from canonical builder
```

Two new local clones were then switched to their exact historical commits.
Neither historical file was copied over the current tree or resealed.

| Check | Exact commit/tree | Result |
| --- | --- | --- |
| Goal5837 stored classification | `0f5c9d4297f73e412732e5a8ab133423fe4cfd21` / `5b80f7f07807679a7ea9eae5e7b29b303ab387ed` | exit 0; authority self-seal `025090252ac60b722cc398402297656877405a998024d221592e18aa888f0465` |
| Goal5843 final authority | `75b2b34fad1f0280a43ce6cbc00e99d4b9d9d937` / `50fc7f1b60fbbf1ecbf65cd99c02f5c39b6717f8` | exit 0; authority self-seal `c40b9fe5d3ace2f58fe29a1a39363ce25373332f774f3c36ffa839ce650bdba8` |

The commands, expected current failures, exact commits, and historical success
conditions are now in `KNOWN_STALE_CUSTODY_CHECKS.md`. Goal5832 remains
different: its historical manifest declares no valid complete Git commit.
Goal5838/5840 remain different again: their historical Git snapshots exist but
named native/raw bytes remain outside Git.

## 4. Current-document rule

Current entry documents must say all of the following together:

1. The bounded whole-protocol contribution uses schema-parametric
   admission/identity/lifecycle plus topology-specific trusted lowering.
2. The prepared A/D observations are retained at exact task/hardware scope;
   implementation entry is not a positive performance claim.
3. Post-import is adverse, reaches `2.377129x`, and both first-result endpoints
   are confounded. Relative to E, first-result medians regress about 8%-22% at
   entry and 16%-31% post-import; those rows are post hoc and non-gating.
4. Instrumentation qualification measured A only.
5. Per-execution detailed receipt retention, native-fork coverage, and provider
   double-fault cleanup are not claimed complete.
6. R2 is a pre-F artifact rehearsal. Final F clean-checkout replay, rewritten
   manuscript, final package, final-byte review, and submission remain open.

Any later current document that conflicts with this list must be narrowed or
added to this ledger before use in the paper or artifact.

## 5. R3 validation

The following checks were executed after the current-document updates:

```text
relative Markdown links in changed control documents: 7 checked, 0 missing
Goal5838 challenge recount: 10 eligible, 7 four-role, 3 six-role
Goal5838 selected ID: builtin_sphere::any_hit_count_continue_u64_per_query
git diff --check: PASS
git diff M -- src include experiments: empty
active-current malformed Ada hash reuse: 0
stale 324-worker / 7,128-timing / 18-row paper-README text: 0
```

The current-tree Goal5837 and Goal5843 failures and their exact-snapshot passes
were actual executions, not inferred status labels. The two temporary clones
were clean after replay. No historical authority, raw evidence, archive,
review, production source, native source, or experiment source was modified.

R3 is closed at the current-control/custody scope. It does not close F replay,
the manuscript, the final anonymous artifact, final-byte review, claim
authorization, or submission.
