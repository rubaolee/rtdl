# R7 P-Sextuple-Prime Exact Final-Bytes Review Request

Date: 2026-09-07 America/New_York.

Please perform an independent hostile review of the exact P-sextuple-prime
manuscript bytes and unchanged F2 evidence archive below. Review the candidate
commit and exact deliverables, not this author summary. P-sextuple-prime changes
the title, paper organization, application evidence, related work,
bibliography, and PDF bytes after P-quintuple-prime. No earlier review transfers.
Author analysis, local build/QA, and this request count as zero independent
acceptances.

## 1. Project and exact identities

RTDL is a restricted-Python DSL/compiler for authoring bounded computations
that repurpose ray-tracing hardware. Authors select the RT formulation and own
application semantics. For supported fixed families, the compiler relates
declared result obligations to role/effect admission, data and ABI contracts,
trusted traversal-action generation, executable identity, and fail-closed
publication.

| Object | Commit | Tree |
| --- | --- | --- |
| Measured implementation M | `d653fe4ad170c5b51fee309d653c9565944dcf2e` | `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b` |
| Frozen predecessor E | `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8` | `aa8b9b12a7bf9cf4395cb71e4fb8e6eb0f169ab6` |
| Frozen tooling F2 | `9771facece4ccd807e26c15b21892b9d0a701d32` | `11c62c28bdebcc7d437f8ab3326635af0832ce48` |
| Superseded P-quintuple-prime | `41bbec66c6f9f8f770d18075fb9dacbed16d499d` | `135f2bc214927acdb305cf2edd2c5ef98690b4a2` |
| P-quintuple-prime control | `8dfdc810c9c23f259b20c511caf69d250f2b86ce` | `6a46575be693e6935e66c940d66ab2af71c2b68d` |
| **P-sextuple-prime under review** | **`7959b325e4f42efc42b773fd363d3c5e9dedb1e1`** | **`b6f738e135050cafb8923c84ef33aa2665e2b749`** |

The candidate parent is
`8dfdc810c9c23f259b20c511caf69d250f2b86ce`. The parent-to-candidate diff is
empty under `src/`, `include/`, `experiments/`, `scripts/`, `tests/`, and
`paper/cgo2027/artifact_post_goal5851/`. No executable implementation,
measurement, workload, timer, estimator, threshold, or F2 byte changed. No GPU
ran and no unchanged test suite was rerun.

## 2. Exact deliverables

| Deliverable | Bytes | SHA-256 |
| --- | ---: | --- |
| `output/pdf/rtdl_cgo2027_submission_candidate.pdf` | 182,617 | `a1772fc41809deb91f64466fc0cccb9557023c143d99d361b4f3b9aa38ad36f0` |
| `paper/cgo2027/main.pdf` | 182,617 | `a1772fc41809deb91f64466fc0cccb9557023c143d99d361b4f3b9aa38ad36f0` |
| `paper/cgo2027/main.tex` | 60,755 | `a339ace8ec2f071cd85c2416e9f67b5d76ae533d43a41a96dbfa2f6647be7de0` |
| `paper/cgo2027/references.bib` | 21,953 | `bb0b71ae0fec49492888fbc9252ed412897cb2d4d7f1e33008f902cdb3b74e61` |
| `output/source/rtdl-cgo2027-source.tar.gz` | 29,176 | `a49ea4aedc2b96084eefddf2ee987e20e968b59416c678caa30c5ab0c4606afa` |
| unchanged `output/artifact/rtdl-cgo2027-artifact.tar.gz` | 180,308 | `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |

The candidate-commit versions of the new author controls are:

| Record | SHA-256 |
| --- | --- |
| DSL-first directive | `ddbf047144a1e8641428f84a3588cf50f0171b0babfb0691399994e7efd68edf` |
| Repurposed-RT problem/evidence directive | `ca85675a7321c138603e858794e02aa6fe75b8f8b446a572908a620ea838c3e6` |
| Application evidence matrix | `9ffba6ef1dd5a076febabe742380f1554749bf9a13ebd5d1f25e875a811d9cd3` |
| DSL-first execution report | `11ca44801b228d163c64d884c433ccd3c780f554ae09bea9b37fedd033881b7d` |
| Manuscript change map | `5fef2335dd9707b0d3f45caea6e66ee29b04736e9a34c41ab2d19f28b39fd3cf` |
| Claim ledger | `779297b494cff29c836d86805f35fbb903cc4ad50a0d076533230d9416da857c` |

The candidate claim ledger has 28 entries and zero authorized flags. F2
contains nine members and performs offline evidence recount only. It does not
rerun GPU work, install RTDL, verify novelty, or reconstruct private history.

## 3. Central DSL/compiler contribution

Review whether the paper is now genuinely about the language/compiler rather
than a contract audit with DSL terminology added afterward. A reader should be
able to identify:

1. the restricted source forms, records, roles, effects, and manifest;
2. the author/compiler responsibility boundary;
3. typed Callback IR and whole-protocol admission;
4. generated Numba leaves, trusted topology wrappers, exact-IR
   specializations, and prepared runtime binding;
5. one concrete supported DSL program; and
6. explicit unsupported forms and topology-specific TCB costs.

Reject any wording that implies arbitrary Python, arbitrary Callback IR,
arbitrary-topology synthesis, or user-authored raw traversal/PTX through the
stable interface.

## 4. Repurposed-RT problem and prior art

The bounded compiler problem is: for an author-selected geometric mapping,
make selected application result obligations constrain callbacks, data
interpretation, traversal actions, and result return.

Check whether the paper supports the importance of this problem without
claiming historical priority. It must credit:

- RTNN for result-specific range/nearest maintenance;
- RayJoin for exact filtering plus continue-after-hit enumeration;
- RayDB for primitive identity, repeated-delivery control, and aggregation;
- LibRTS for reusable spatial queries and user count/collect handlers;
- OptiX and OSL for existing cross-stage/event and rendering-domain protocols;
- CrossRT, Luisa, Dr.Jit, Slang/SlangPy, Shader Components, Scion, and
  PyOptiX/OWL for substantial adjacent language/compiler/API capability; and
- TTA/TTA+ for a hardware/interface alternative.

Reject first/only/impossibility wording, inference from source silence, or any
claim that rendering lacks protocol problems. Decide whether the remaining
fixed-family connection is a concrete nontrivial compiler increment after these
concessions.

## 5. Concrete compiler decisions

Trace these decisions to the exact source and stated evidence boundary:

1. **Reject:** one complete bounded-relation route accepts only
   `ACCEPT_CONTINUE`, so locally role-legal alternatives are not admitted for
   that fixed route.
2. **Generate:** all-hit logical acceptance updates the result state and then
   physically ignores the intersection so traversal continues.
3. **Select:** exact standard count `+1` selects the fixed intrinsic, while a
   legal same-shape `+2` callback changes IR identity and exits to the general
   leaf path.
4. **Bind:** accepted source/IR, wrapper/PTX, provider, physical schema, and
   runtime identities are tied to the prepared route.

The first decision is a fixed-family restriction. The second uses established
OptiX mechanisms. The third is a source-to-wrapper test without variant GPU
equivalence. Exact-IR selection is not proof of specialization correctness.
All relevant lowerers and specializers remain trusted.

## 6. Nine historical applications

Audit every row of the application table. The paper distinguishes:

- `E1`: exact historical application-source hash and callback-consumer binding
  are recoverable for Particle, triangle counting, and LibRTS; and
- `E2`: only frozen archive-level path/structural audit records survive for
  RayDB, X-HD, RTNN, RT-DBSCAN, Spatial RayJoin, and RT-BarnesHut.

The actual nine application files and frozen 10.8 MB source archive are absent.
The table must not imply current runnability, unseen authors, full code
generation, elimination of trusted native partners, or that every app stage
ran on RT cores. RayDB must remain the sole private-loader exception. LibRTS
must remain a strong prior abstraction.

The historical 34-row evidence must be reported, if at all, only in full: 464
workers; 16 median passes and 18 failures; 11 clear V4 wins, 10 clear losses,
and 13 uncertain. It is not PyOptiX, not final M, not a broad win, and not
poolable with final M.

## 7. Performance, trust, and adverse evidence

Verify that the manuscript visibly retains:

- prepared RTDL/Direct medians of `1.077--1.175x`, not intrinsic-language
  speedup;
- all four adverse post-import rows and the `2.377x` worst block;
- adverse post-hoc M/E first-result regressions and lifecycle confounding;
- 4,096 timed Arm-A calls versus 32 separate diagnostic receipts;
- Arm-A-only paired instrumentation;
- about 2,635 topology-specific sphere-route lines and 28 compiler changes;
- the finite checker's missed early-return probe;
- provider double-fault and native-fork mock limits;
- zero independent-user authoring evidence; and
- offline-recount-only artifact scope.

The measured tasks are exact-IR specialized relation and triangle routes, not
the general Numba-leaf path and not all nine applications. No positive
implementation-entry performance claim is authorized.

## 8. Exact-byte and format checks

Verify from candidate commit `7959b325e...`, not only from the worktree:

- both PDF paths have the exact stated hash and are byte-identical;
- the PDF is anonymous, 12 US-Letter pages, with main content ending on page 11
  and references occupying the remainder;
- no clipping, overlap, blank page, missing glyph, unreadable table, unresolved
  citation/reference, or overfull box exists;
- all fonts are embedded/subset/Unicode mapped;
- private paths, usernames, hosts, keys, internal Goal IDs, agent names, and
  author identities are absent;
- the source archive contains only normalized directory entries plus exact
  `main.tex` and `references.bib`, and builds from a foreign path;
- F2 has nine members and the exact unchanged hash; and
- the candidate-parent diff is empty for all executable, experiment, test, and
  F2 source roots.

BibTeX emitted nonfatal completeness warnings for several inherited
conference records and the in-press survey. Inspect the rendered references and
classify any metadata problem; do not convert the author's zero-undefined check
into a zero-warning claim.

## 9. Required review output

Report each finding with severity, exact PDF page/source location, evidence,
required action, and affected claim IDs. Explicitly answer:

1. Is this now a coherent DSL/compiler paper from title through conclusion?
2. Is the repurposed-RT result-obligation problem important and accurately
   attributed?
3. Is the implemented compiler increment concrete and nontrivial enough for
   CGO under its bounded scope?
4. Is the nine-application evidence honest and strong enough for how it is
   used?
5. Does any central sentence exceed source, execution, or prior-art evidence?
6. Are adverse results, missing sources, and TCB costs prominent enough?
7. Are these exact bytes ready for submission-side R8?

End with exactly one verdict:

```text
ACCEPT_PSEXTUPLEPRIME_FINAL_BYTES
REVISE_AND_REREVIEW_CHANGED_BYTES
REJECT_CLAIM_OR_SUBMISSION_SCOPE
```

An acceptance must repeat the exact candidate commit/tree, PDF SHA-256, and F2
SHA-256. Two independent acceptances of these exact bytes are required. This
request authorizes no public claim, upload, or submission.
