# R8 P-Quadruple-Prime Author-Side Local Preflight

Date: 2026-09-07 America/New_York

Status: `AUTHOR_LOCAL_PREFLIGHT_PASSED__R7_AND_EXTERNAL_SUBMISSION_ACTIONS_PENDING`.

This report records local checks of P-quadruple-prime. It is not an independent
anonymity review, final-byte acceptance, upload authorization, or submission
receipt. R7 remains 0/2.

## 1. Exact object under preflight

| Object | Exact identity |
| --- | --- |
| Candidate commit | `70a081e90c4c50ecf92d24741529de9859841c70` |
| Candidate tree | `b4b1628345536976e2ed8fbb67ab5b4ff21fc802` |
| Candidate parent | `b608f9aa5e4e04d083d8a2963d552e00287b47cd` |
| PDF | 153,809 bytes; SHA-256 `bb957c0969bbd92c6a4be952c4e40a4ce5a183bf565c5f54a19b410102c77aca` |
| Source bundle | 23,504 bytes; SHA-256 `e845010a64f8373dc40ac65f8cc42e4c4024687ce6fd1eb80b8fd4067a623266` |
| Unchanged F2 | 180,308 bytes; SHA-256 `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |

Commit-object extraction reproduced the manuscript, both PDF, source bundle,
and F2 hashes. The candidate-parent diff is empty under all executable and
frozen-tool paths checked: `src/`, `include/`, `experiments/`, `scripts/`,
`tests/`, and `paper/cgo2027/artifact_post_goal5851/`.

## 2. Manuscript and PDF checks

The cached Tectonic build completed with exit 0. The exact candidate has:

| Check | Result |
| --- | --- |
| Page count and size | 9 pages, 612 x 792 pt, US Letter |
| Paper/delivery PDF identity | Byte-identical |
| Horizontal/vertical overfull boxes | 0 / 0 |
| Unresolved citations/references | 0 |
| Embedded fonts / ToUnicode mappings | 12/12 / 12/12 |
| Visual rendering | All 9 exact pages rendered and inspected |
| Visual defects found | 0 clipping, overlap, blank pages, missing glyphs, or unreadable tables |
| Review mode | Anonymous ACM review layout retained |

The text/metadata scan found no private filesystem paths, local usernames,
pod hosts, SSH keys, internal Goal IDs, agent names, or author identities in
the PDF. The source scan found one author surname in unused third-party
bibliography entries, but those entries do not appear in the PDF and are
ordinary bibliographic metadata, not project identity. This author-side scan
does not replace the two required independent anonymity scans.

The currently checked official CGO 2027 call permits eleven content pages
excluding references and lists the second-round deadline as September 10,
2026 AoE. The candidate uses nine content pages. The authenticated submission
form, paper category, author/topic/conflict fields, and final displayed
deadline have not yet been checked and remain R8 actions.

## 3. Source custody and buildability

Two independently staged normalized ustar archives were built with fixed
owner/group, modes, and timestamps, then compressed with `gzip -n`. They were
byte-identical. The committed source archive contains only normalized
directory entries and exact candidate `main.tex` and `references.bib`.

Extraction into `/tmp/RTDL PQUAD source` preserved exact source identities and
compiled successfully with cached Tectonic from a path containing spaces. The
rebuilt PDF had nine US-Letter pages. This proves source custody/buildability,
not byte-for-byte PDF reproducibility across TeX environments.

## 4. Existing evidence and witness replay

The following four existing tests were replayed without source changes:

```text
tests.goal5759_v4_triangle_reduction_target_test.Goal5759TriangleReductionTargetTests.test_count_intrinsic_requires_the_exact_standard_callback_ir
tests.goal5760_v4_bounded_relation_test.Goal5760BoundedRelationTests.test_schema_and_wrapper_are_deterministic_app_neutral_true_optix
tests.goal5760_v4_bounded_relation_test.Goal5760BoundedRelationTests.test_capacity_overflow_rejects_partial_result
tests.goal5760_v4_bounded_relation_test.Goal5760BoundedRelationTests.test_duplicate_policy_is_explicit_and_canonical
```

Result: 4/4 PASS, exit 0, 0.017 seconds. This is source-to-wrapper and bounded
CPU/component evidence only; no GPU ran in this pass.

The frozen submission-evidence suite passed 14/14 in normal Python and 14/14
under `python -O`. The F2 archive remains the exact nine-member archive. Its
complete R5 rehearsal was inherited rather than rerun because F2 and frozen
tooling did not change.

## 5. Claim and scope checks

- `CLAIM_LEDGER.json` parses and contains exactly 24 claims.
- Every `claim_authorized` value remains `false`.
- No performance cell, denominator, M/E/F2 identity, receipt count, native or
  production source, test, timer, workload, estimator, threshold, or GPU result
  changed.
- The paper retains the receipt gap, all adverse post-import and M/E
  first-result observations, instrumentation scope, TCB expansion, finite
  checker miss, two provider/fork defects, zero independent-user evidence, and
  offline-only artifact boundary.
- P-quadruple-prime has zero independent acceptances. P-triple-prime and older
  reviews cannot be transferred to these changed bytes.

## 6. Retained process failures

Failures encountered during the author pass are retained rather than relabeled
as successful checks:

1. The first P-quadruple-prime PDF build completed but had five overfull boxes.
   It was rejected. Content-level edits removed all overfull boxes without
   changing the ACM format or deleting adverse evidence.
2. Initial source archives made directly with `tar -czf` differed because gzip
   headers contained build-time metadata. They were rejected. Normalized ustar
   creation followed by `gzip -n` produced byte-identical archives.
3. One orchestration JavaScript invocation was syntactically incomplete and
   failed before invoking any nested tool. It changed no file and produced no
   scientific evidence.

No failed command was counted as evidence. No GPU or remote pod was used.

## 7. Remaining R8 gate

The following remain open and cannot be completed by this author-side report:

- two independent R7 acceptances of the exact candidate PDF and unchanged F2;
- two independent anonymity, bibliography, and link checks of final bytes;
- authenticated submission-form, category, author, topic, conflict, deadline,
  and time-zone verification;
- authorized upload of the exact PDF/artifact pair;
- download and hash verification of the uploaded bytes; and
- a real submission ID/receipt.

Therefore the correct state is `NOT_SUBMITTED`, claims remain unauthorized,
and this report does not permit upload.
