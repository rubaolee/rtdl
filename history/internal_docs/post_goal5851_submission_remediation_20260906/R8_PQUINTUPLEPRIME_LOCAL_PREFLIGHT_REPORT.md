# R8 P-Quintuple-Prime Author-Side Local Preflight

Date: 2026-09-07 America/New_York.

Status: `AUTHOR_LOCAL_PREFLIGHT_PASSED__R7_AND_EXTERNAL_SUBMISSION_ACTIONS_PENDING`.

This report records author-side checks of exact P-quintuple-prime. It is not an
independent content or anonymity review, upload authorization, or submission
receipt. R7 remains 0/2.

## 1. Exact object under preflight

| Object | Exact identity |
| --- | --- |
| Candidate commit | `41bbec66c6f9f8f770d18075fb9dacbed16d499d` |
| Candidate tree | `135f2bc214927acdb305cf2edd2c5ef98690b4a2` |
| Candidate parent | `8b4475893a7a4486fb89fa35f1ce2470fb2d13f4` |
| `main.tex` | 45,064 bytes; SHA-256 `537efb44319297733f8c94717be2769dbea88fdee738d8e7ac7c7e185bb58430` |
| `references.bib` | 21,088 bytes; SHA-256 `71c379b4ea23a8eaa08e97f94a3c9569d703ea7cb99186b81e0df0f00d5e4dd6` |
| Exact PDF | 154,295 bytes; SHA-256 `34dad89878f7a283662e51059d1b81c4d266198657e0d4db065f0c3df2c41385` |
| Source bundle | 23,637 bytes; SHA-256 `f9e70fd7e709eeb611ba740628654379866e638d3534c9ddb94a3b8c0f3ea30a` |
| Unchanged F2 | 180,308 bytes; SHA-256 `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |

Commit-object extraction reproduced all six file identities. Both PDF paths
are byte-identical. The candidate-parent diff is empty under `src/`,
`include/`, `experiments/`, `scripts/`, `tests/`, and
`paper/cgo2027/artifact_post_goal5851/`.

## 2. Manuscript and PDF checks

The exact candidate has:

| Check | Result |
| --- | --- |
| Cached Tectonic build | PASS, exit 0 |
| Page count and size | 9 pages, 612 x 792 pt, US Letter |
| Paper/delivery PDF identity | Byte-identical |
| Horizontal/vertical overfull boxes | 0 / 0 |
| Unresolved citations/references | 0 |
| Embedded/subset/Unicode fonts | 12/12 / 12/12 / 12/12 |
| Visual rendering | All 9 exact pages rendered and inspected |
| Visual defects | 0 clipping, overlap, blank pages, missing glyphs, or unreadable tables |
| Review layout | Anonymous ACM review layout retained |

A PDF text scan found no private filesystem path, local username, pod/SSH
host, key name, internal Goal ID, agent name, or author identity. The scan and
visual inspection are author-side and do not replace independent anonymity
review.

One preflight command first used an obsolete cached wrapper path for
`pdffonts` and an awk variable colliding with a built-in function. It failed
before producing a font result and changed no file. The check was rerun using
the installed Poppler binary under the current dependency tree and reported
12/12 embedded, subset, Unicode-mapped fonts. The failed invocation is not
counted as evidence.

## 3. Source custody and buildability

Two normalized ustar source archives, with fixed owner/group, modes, and
timestamps and `gzip -n`, were byte-identical. The official source bundle has
only normalized directory entries plus exact `main.tex` and
`references.bib`. Extraction into a foreign path containing spaces preserved
both source hashes and compiled successfully with cached Tectonic to a
nine-page Letter PDF.

This establishes source custody and buildability, not cross-environment
byte-for-byte PDF reproducibility.

## 4. Evidence and test scope

No compiler/runtime/native source, experiment, test, workload, timer,
threshold, or F2 byte changed from the P-quadruple-prime control base. The lead
directive explicitly prohibited reopening engineering or rerunning checks
whose inputs were unchanged. Therefore no GPU ran and no test suite was rerun
in this pass.

The earlier P-quadruple-prime author pass recorded 4/4 W1--W3 component checks
and 14/14 frozen-evidence checks normally and under `python -O`. They remain
historical evidence over unchanged executable/F2 inputs, not a new
P-quintuple-prime execution claim and not independent acceptance.

## 5. Three-question closure check

Direct source/PDF inspection confirms:

- Table 1 uses explicit reject, generate, and select actions with evidence
  boundaries;
- Section 3.2 connects the general Numba leaf route and exact standard-count
  specialization to the same known increment-and-continue behavior, while
  keeping recognizer and lowerer trusted; and
- Related Work says the increment is the implemented result-obligation-to-
  admission/lowering/publication connection, not different predicate names,
  and states the restricted-expressiveness/topology-TCB cost.

The paper continues to attribute OptiX mechanisms to prior practice, treats
the `+2` test as a selection-boundary test rather than GPU equivalence, and
does not infer inability from silence in prior-system materials.

## 6. Claim and disclosure checks

- `CLAIM_LEDGER.json` at the candidate commit parses with 24 claims and zero
  authorized flags.
- No numerical cell, denominator, receipt count, M/E/F2 identity, or adverse
  result changed.
- The receipt gap, adverse post-import and predecessor observations, A-only
  instrumentation, topology-specific code cost, finite-checker miss, provider
  and fork limits, zero independent-user evidence, and offline-only artifact
  boundary remain visible.
- P-quintuple-prime has zero independent acceptances. Earlier reviews cannot
  transfer to changed bytes.

## 7. Remaining R8 gate

The following remain open:

- two independent R7 acceptances of the exact PDF and unchanged F2;
- independent anonymity, bibliography, and link review of final bytes;
- authenticated submission-form, category, author, topic, conflict, deadline,
  and time-zone verification;
- authorized upload of the exact deliverables;
- downloaded-byte hash comparison; and
- a real submission ID/receipt.

The correct state is `NOT_SUBMITTED`; all claims remain unauthorized, and this
report does not permit upload.
