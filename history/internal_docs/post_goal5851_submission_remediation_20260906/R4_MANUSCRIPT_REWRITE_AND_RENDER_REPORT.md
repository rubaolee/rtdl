# R4 manuscript rewrite and render report

Date: 2026-09-06

Status: `CLOSED_WITH_EVIDENCE__FINAL_BYTES_PENDING_R7_REVIEW`

This report records the actual R4 rewrite and mechanical review. It does not
authorize a public claim, substitute for R7 independent final-byte review, or
record submission.

## 1. Frozen inputs and ownership

- Measured implementation M remained
  `d653fe4ad170c5b51fee309d653c9565944dcf2e`, tree
  `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b`.
- Predecessor E remained
  `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8`, tree
  `aa8b9b12a7bf9cf4395cb71e4fb8e6eb0f169ab6`.
- Final tooling F2 remained
  `9771facece4ccd807e26c15b21892b9d0a701d32`, tree
  `11c62c28bdebcc7d437f8ab3326635af0832ce48`.
- The lead AI held exclusive write ownership of `paper/cgo2027/main.tex`.
- No production, native, experiment, workload, estimator, threshold, raw
  evidence, or frozen artifact-tool byte was edited during R4.

## 2. Rewritten thesis and scope

The obsolete 17-page manuscript was replaced rather than patched with layers
of contradictory caveats. The final candidate is organized around one thesis:

> RTDL admits a bounded whole ray-tracing protocol across restricted source,
> role/effect rules, semantic and physical ABI, topology-specific lowering,
> executable identity, and lifecycle state.

The manuscript has four contributions. It explicitly says that:

- the canonical plan is non-executable;
- executable lowering is topology-specific and remains in the TCB;
- arbitrary Python, arbitrary Callback IR, arbitrary topology, topology-generic
  lowering, intrinsic speedup, broad parity, usability, and prevalence are not
  established;
- two stable public constructors are distinct from the broader bounded V4
  route corpus;
- the stable surface has 2/6 build-input-kind and 2/4 leaf-kind presence, while
  the full bounded V4 corpus has 4/6 and 4/4 kind presence, not complete OptiX
  feature coverage;
- independent external-human authoring evidence and prevalence evidence remain
  zero.

The paper adds a concrete executed semantic-ABI counterexample, the restricted
AST/IR boundary, seven role responsibilities, explanatory fail-closed
judgments, declaration-to-target authority mapping, and an architecture figure
that separates shared admission, trusted topology-specific lowering, runtime
publication gates, and the separate offline checker.

## 3. Claim-ledger mapping

All 21 ledger entries are visible in the following paper locations. The ledger
retains `claim_authorized=false` and `external_final_bytes_review=PENDING_R7`.

| Claim IDs | Actual destination | R4 disposition |
| --- | --- | --- |
| `ARCH-...-001` | Abstract, Introduction, Sections 3-4 | bounded wording retained |
| `ARCH-...-002` | Sections 3.4 and 3.6, Figure 1 | loaded-image and lifecycle qualifiers retained |
| `ARCH-...-003` | Sections 3.5 and 4, Figure 1, Threats | topology-specific TCB limitation mandatory and visible |
| `EVAL-...-004` | Section 5.2 and Threats | one narrow composition, unbiased new application remains zero |
| `EVAL-...-005` | Section 5.2 | curve row is eligible/not selected; exact sphere row is selected |
| `EVAL-...-006` | Section 5.3 and Threats | finite 3-route/4-mode/5-class/20-application/15-mutation scope retained |
| `PERF-...-007` through `010` | Section 5.5, Table 5 | four exact prepared A/D rows retained; no A/D max gate invented |
| `PERF-...-011` | Sections 5.4 and 5.6, Table 6 | both confounded endpoints and adverse post-import rows retained |
| `PERF-...-012` | Section 5.6, Table 6 | adverse first-result A/E regressions retained as post hoc, non-gating |
| `PERF-...-013` | Section 5.6 | C/B competence retained without global-optimality wording |
| `METHOD-...-014` | Section 5.6 and Threats | instrumentation explicitly Arm A only |
| `METHOD-...-015` | Sections 3.6, 5.6, and Threats | original detailed per-execution receipt requirement disclosed as unmet |
| `METHOD-...-016` | Sections 5.4 and Threats | task adaptation and non-confirmatory scope disclosed |
| `METHOD-...-017` | Section 5.5 | 20 AOT observations retained with cache-hit boundary |
| `LIMIT-...-018` | Section 2.3 and Threats | provider double-fault limitation visible |
| `LIMIT-...-019` | Section 2.3 and Threats | fork claim limited to Python-managed use |
| `ARTIFACT-...-020` | Section 8 and Threats | offline projection recount distinguished from GPU rerun/product install |
| `LIMIT-...-021` | Table 4 and Threats | human usability and prevalence remain zero |

The updated ledger SHA-256 at this report's input was
`476b623eecb92bdf30432623b95966c884ee13523ea57b88398f3369ab863006`.

## 4. Mandatory adverse disclosure

The main PDF, not only supplemental material, contains all required minimum
disclosures:

- post-import A/C is adverse for all four rows;
- its medians span `1.559788x` to `1.837415x` in the source evidence and are
  rendered as `1.560x` to `1.837x` in the main table;
- the maximum formal diagnostic block is `2.377129x` in the source evidence and
  appears as `2.377x` in the table and prose;
- first-result M/E regressions are approximately 8%-22% at entry and 16%-31%
  post-import, explicitly post hoc and non-gating;
- the implementation-entry endpoint was revised after observing an adverse
  result, and both first-result endpoints are import/lifecycle-confounded;
- 4,096 timed A executions have 32 separate post-loop detailed diagnostic
  receipts, not one detailed receipt per timed execution;
- no wrong output was observed in the final GPU samples, which is explicitly
  not described as a proof or as a repair of the receipt deviation.

## 5. Exact performance population

The paper uses the R2 reconstruction, not the obsolete three-arm projection:

- two exact tasks;
- five arms A/B/C/D/E;
- RTX 4090 Ada and RTX 3090 Ampere;
- eight blocks per generation/task/arm cell;
- 128 steady samples per cell;
- 160 formal cells and 20,480 steady samples total;
- 1,024 A-only instrumentation endpoints;
- 20 AOT observations;
- eight competence records.

The primary A/D table reports medians and observed maxima with a clear
lower-is-better definition. Ratios are described as medians of eight
within-block integer ratios. Raw times are not compared across machines.

## 6. Build and rendered-page validation

Build command, from `paper/cgo2027/`:

```text
/opt/homebrew/bin/tectonic -X compile main.tex \
  --outdir "/tmp/RTDL CGO R4 bibliography build.SOlrme" \
  --keep-logs --keep-intermediates
```

Result: exit 0.

Mechanical result:

| Check | Result |
| --- | --- |
| PDF page size | US Letter, 612 x 792 pt |
| Total pages | 8 |
| Main text limit | main text ends on page 7 before references; below 11-page limit |
| Reference start | page 7 |
| Horizontal overfull boxes | 0 |
| Vertical overfull boxes | one 1.90399pt output-routine vbox at end of document |
| Undefined citations/references | 0 |
| Review line numbers | present |
| Anonymous author | present |
| ACM class warnings | 0 |
| BibTeX warnings | 0 |
| Final visual inspection | every page 1-8 of the exact final bytes inspected at 130 dpi; no clipping, collision, unreadable table, or blank-content defect |

The sole overfull warning is emitted while the end-of-document output routine
is active. It persisted independently of nearby prose shortening and is not a
horizontal text overflow. Inspection of all exact rendered pages found no
visible clipping or overlap; the warning is retained here rather than hidden
through a margin or font-size change.

A final hostile reread also corrected four presentation defects before this
identity was fixed: the artifact section now says that private provenance and
the replay receipt remain separate custodial records rather than package
members; the abstract calls the Goal5840 population 20 registered checker
instances rather than 20 applications; the paper supplies an ACM CCS concept
and figure description; and the bibliography builds without BibTeX warnings.

The current source and PDF identities are:

| File | SHA-256 |
| --- | --- |
| `paper/cgo2027/main.tex` | `612a10d0da5a919626b67401cf2c887bf6d39207e367c5cf663e6cf9f5248601` |
| `paper/cgo2027/references.bib` | `7eda90e69e190c3cbd545f86fbf964fa252b75265bc523a1d8dc06c9c9310c66` |
| `paper/cgo2027/main.pdf` | `4529946fff21edd2e5634792397d5e3af0213f6c2ab2c4ebdf001b9246f73453` |

PDF text and metadata scans found none of the local username, absolute user
path, internal Goal token, private Git commit identities, live SSH endpoints,
or author GitHub identity tested. The PDF metadata contains the title, TeX
creator, producer, and creation date, but no author identity or local source
path.

The official CGO 2027 submission page was checked on 2026-09-06. Its required
class options, US Letter format, line numbers, double-blind mode, English text,
and 11 text-page limit excluding references match this candidate:
`https://2027.cgo.org/track/cgo-2027-papers`.

## 7. Supplemental regression context

The frozen submission-evidence suite passed 14/14 on the candidate tree:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal5852_submission_evidence_test
```

Two unrelated legacy public-document suites were also attempted. They produced
13 missing-file errors and one broken-link failure over 41 old example links.
The exact failure signature reproduced in an untouched detached worktree at
pre-candidate HEAD `63f738f82aaf84ad1be28531f970ff9ca1affe5b`; it is therefore not a
regression from this manuscript/package change. Those stale suites target a
larger historical documentation surface absent from this restricted repository
and were not repaired after the executable freeze. They are not counted as an
R4 or R6 pass.

## 8. Remaining gate

R4 is complete as an internally checked manuscript candidate. R7 must review
the actual PDF and exact artifact bytes and either close each ledger entry or
remove/narrow the affected sentence. Until that review and R8 pass,
`public_or_manuscript_claim_authorized` remains false and the manuscript is not
recorded as submitted.
