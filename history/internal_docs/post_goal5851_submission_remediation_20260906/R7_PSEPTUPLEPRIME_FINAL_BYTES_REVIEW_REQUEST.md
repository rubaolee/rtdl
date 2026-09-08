# R7 P-Septuple-Prime Exact Final-Bytes Review Request

Date: 2026-09-08 America/New_York.

Status: `REQUEST_READY__ZERO_OF_TWO_INDEPENDENT_ACCEPTANCES`.

Please perform an independent hostile review of the exact P-septuple-prime
manuscript bytes and unchanged F2 evidence archive below. Review the candidate
commit and deliverables, not this author summary. P-septuple-prime changes the
paper and source-package bytes after P-sextuple-prime by integrating the final
selected-stage application comparison against public PyOptiX. No earlier
review transfers. Author analysis, local QA, pod replay, and this request count
as zero independent acceptances.

## 1. Project and exact identities

RTDL is a restricted-Python DSL/compiler for bounded computations that
repurpose ray-tracing hardware. Authors choose the RT formulation and own the
application semantics. For supported fixed families, RTDL connects declared
result obligations to typed roles/effects, semantic and physical contracts,
trusted traversal-action generation, executable identity, and fail-closed
publication.

| Object | Commit | Tree |
| --- | --- | --- |
| Measured two-task implementation M | `d653fe4ad170c5b51fee309d653c9565944dcf2e` | `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b` |
| Frozen predecessor E | `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8` | `aa8b9b12a7bf9cf4395cb71e4fb8e6eb0f169ab6` |
| Frozen tooling F2 | `9771facece4ccd807e26c15b21892b9d0a701d32` | `11c62c28bdebcc7d437f8ab3326635af0832ce48` |
| Final application measurement source | `c5c8be48b743aa001e9c16c3344cc97c200600d1` | `e3bb0001f4c2d1e3171ab0431c0479500dfc7136` |
| Superseded P-sextuple-prime | `7959b325e4f42efc42b773fd363d3c5e9dedb1e1` | `b6f738e135050cafb8923c84ef33aa2665e2b749` |
| **P-septuple-prime under review** | **`72d60cb392031134dd3064a8da5cb603bde18e47`** | **`759cc1246830b785a8d30e98704b51266033194a`** |

The candidate parent is
`700b3165ba2a0bca15981aa273c9f02ed9a63992`. The parent-to-candidate
diff changes exactly five paper/delivery files and is empty under `src/`,
`include/`, `experiments/`, `scripts/`, `tests/`, and
`paper/cgo2027/artifact_post_goal5851/`. No executable implementation,
experiment, workload, timer, estimator, threshold, raw evidence, or F2 byte
changed in this candidate commit.

## 2. Exact deliverables

| Deliverable | Bytes | SHA-256 |
| --- | ---: | --- |
| `output/pdf/rtdl_cgo2027_submission_candidate.pdf` | 183,938 | `32189aec5d5ebda4956c83dfe948128bef8dd50e3dbbeb308290988a2acaea07` |
| `paper/cgo2027/main.pdf` | 183,938 | `32189aec5d5ebda4956c83dfe948128bef8dd50e3dbbeb308290988a2acaea07` |
| `paper/cgo2027/main.tex` | 61,234 | `0dd724df5b1d64051e28ce7ee31f09f4e3e5adccf389a0775fa9be7ef36c6076` |
| `paper/cgo2027/references.bib` | 21,640 | `d27ce8c5db0a6855e9879b90a38e98fb07f56ecf993ee4fe2eaddea5b57619f5` |
| `output/source/rtdl-cgo2027-source.tar.gz` | 29,743 | `e4a291f9e86b125438f2b1c9a5334110a035a36b4a88955267ea319a4e596f6f` |
| unchanged `output/artifact/rtdl-cgo2027-artifact.tar.gz` | 180,308 | `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |

Commit-object extraction reproduces every identity. The two PDFs are the same
Git blob and byte-identical. The normalized source archive has five directory
or file members and contains only exact `main.tex` and `references.bib` source
files under normalized directory entries.

## 3. What changed after P-sextuple-prime

The paper now incorporates the final frozen application cost transaction,
compresses the nine-mapping historical table, and preserves the DSL/compiler
argument within the official 11-page text limit. It does not replace the
two-task M evaluation or pool the two evidence populations.

The new application text must be read as selected-stage feasibility and cost
evidence, not complete raw-domain application end to end, a broad benchmark
result, a productivity study, or a causal measurement of language checking.
The abstract, evaluation, threats, artifact scope, and conclusion all say the
application evidence is adverse and limited to selected stages from three of
nine mappings.

Three bibliography notes with nonstandard experimental commentary were
removed. No cited author, title, venue, year, DOI, or URL was removed by that
cleanup. BibTeX still emits disclosed nonfatal completeness warnings; this is
not a zero-warning claim.

## 4. Final application evidence under review

The measured application source is pre-freeze commit `c5c8be48b...`, not the
paper candidate and not two-task source M. Its final frozen transaction ran on
one NVIDIA RTX A4500, CC 8.6, UUID
`GPU-5dbda20d-af85-650e-7250-10b265a77143`, driver 550.127.05, OptiX 8.0,
and PyOptiX 9.1.

It covers selected stages from three of nine mappings and four operation
units: one Particle Tracking transition, Triangle RT-2A1 on `com-dblp`, and
LibRTS point/range count. Every unit has eight paired fresh-process blocks at
three registered endpoints. All 192 workers, 96 pairs, and 12 evaluations
passed with zero retry or discard; all 96 individual block ratios exceed one.

| Unit | Complete ratio | First-execute ratio | Prepared ratio |
| --- | ---: | ---: | ---: |
| Particle | 10.208260x | 75.533295x | 37.927723x |
| Triangle RT-2A1 | 3.410621x | 2.731653x | 1.379226x |
| LibRTS point | 1.311772x | 12.058793x | 38.466788x |
| LibRTS range | 1.079542x | 13.421842x | 39.083145x |

Ratios are medians of paired block ratios. The V4 and PyOptiX arm times shown
in the paper are separate medians and need not divide to the displayed ratio.
The output contracts matched: an ordered 5,000-by-3 U32 Particle matrix and
checked U64 counts 2,224,385, 112,729, and 105,826.

The endpoint and route limits are mandatory review targets:

- `complete` starts after shared domain preprocessing and includes
  prepare/execute/close; it is not raw-domain end to end.
- `first execute` starts after `_prepare_case`; it is not cold process start or
  pure native launch.
- `prepared` adds one untimed warmup; timed calls still include synchronous
  status/oracle checks, digesting, and compact evidence projection.
- Particle V4 canonicalizes ignored any-hit candidates before one logical
  closest hit; PyOptiX uses native closest hit.
- Per graph segment, V4 rebuilds GAS and pipeline state, while PyOptiX retains
  pipeline objects but rebuilds geometry/GAS.
- LibRTS compares a general AoS multi-operation V4 route with compact SoA
  handwritten CUDA/PTX kernels. The PyOptiX code is not a Numba baseline.

These differences are source-established path costs, not a causal allocation
to the DSL or proof that the observed overhead is unavoidable.

The final authority files are:

| Evidence object | SHA-256 |
| --- | --- |
| `FORMAL_SUMMARY.json` | `67a353cd796080b06442dcef64624bd176f65c513d185e0198aca0b7640df4bf` |
| `INDEPENDENT_RECOUNT_c5c8be48b.json` | `667cafd0f3599b62b77aab96f92e18eaac4cb925832c077004b1ced2b09d7b64` |
| complete application archive | `2d7dc4413639e46994ca74251d230b74d5e9d775a23b457336cb00f9df80f4ff` |

## 5. Central contribution and prior-art audit

Review whether the paper remains a coherent DSL/compiler contribution rather
than an evidence report with language terminology added afterward. A reader
must be able to identify restricted source forms, records, roles, effects,
manifest, typed Callback IR, whole-protocol admission, generated Numba leaves,
trusted topology wrappers, exact-IR specialization, prepared binding, and the
author/compiler responsibility split.

The paper must continue to credit RTNN, RayJoin, RayDB, LibRTS, OptiX, OSL,
CrossRT, Luisa, Dr.Jit, Slang/SlangPy, Shader Components, Scion, PyOptiX/OWL,
and TTA/TTA+. Reject any first/only/impossibility statement, inference from
source silence, arbitrary-Python or arbitrary-topology implication, or claim
that rendering lacks protocols.

The concrete increment remains bounded: selected result obligations affect
fixed-family effect admission, physical traversal action, exact-IR
specialization, identity binding, and interface-specific fail-closed return.
All topology lowerers and specializers remain in the TCB; the finite checker is
not a proof.

## 6. Existing performance and adverse evidence

Verify that the exact paper retains all earlier limits:

- prepared RTDL/Direct medians are 1.077--1.175x, not speedups;
- all four post-import rows are adverse and reach a 2.377x worst block;
- first-result predecessor comparisons are post hoc and lifecycle-confounded;
- 4,096 timed Arm-A calls have only 32 separate diagnostic receipts;
- paired instrumentation qualifies Arm A only;
- the sphere route required about 2,635 topology-specific TCB lines;
- the finite checker missed an early-return probe;
- provider double-fault and native-fork limits remain disclosed;
- no independent-user authoring or productivity evidence exists; and
- the F2 artifact performs offline recount only.

The selected-stage application study is an additional adverse population. It
does not repair the receipt shortfall, establish broad practical performance,
or convert the historical nine-mapping portfolio into nine current benchmark
applications.

## 7. Exact-byte and format checks

Verify from candidate commit `72d60cb392031134dd3064a8da5cb603bde18e47`:

- both PDF paths have the stated hash and are byte-identical;
- the PDF is anonymous, 12 US-Letter pages, with text ending on page 11 and
  references starting on page 11;
- no clipping, overlap, blank page, missing glyph, unreadable table, unresolved
  citation/reference, or overfull box exists;
- all 12 fonts are embedded, subset, and Unicode mapped;
- private paths, usernames, hosts, keys, internal Goal IDs, agent names, and
  author identities are absent;
- the source archive contains only normalized directory entries and the two
  exact source files and builds from a foreign path;
- F2 contains nine members with the unchanged stated hash; and
- the candidate-parent executable/experiment/test/F2 diff is empty.

## 8. Required review output

Report each finding with severity, exact PDF page or source location, evidence,
required action, and affected claim. Explicitly answer:

1. Is this a coherent DSL/compiler paper from title through conclusion?
2. Is the result-obligation problem important and accurately attributed?
3. Is the bounded compiler increment concrete and nontrivial enough for CGO?
4. Does the new selected-stage PyOptiX comparison use honest endpoint names,
   preserve all adverse results, and avoid causal overclaiming?
5. Is the nine-mapping evidence still represented within its custody limits?
6. Does any central sentence exceed source, execution, or prior-art evidence?
7. Are the exact bytes ready for submission-side R8?

End with exactly one verdict:

```text
ACCEPT_PSEPTUPLEPRIME_FINAL_BYTES
REVISE_AND_REREVIEW_CHANGED_BYTES
REJECT_CLAIM_OR_SUBMISSION_SCOPE
```

An acceptance must repeat the exact candidate commit/tree, PDF SHA-256, and F2
SHA-256. Two independent acceptances of these exact bytes are required. This
request authorizes no public claim, upload, or submission.
