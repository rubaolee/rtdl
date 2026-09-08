# R7 P-Decuple-Prime Exact Final-Bytes Review Request

Date: 2026-09-08 America/New_York.

Status: `REQUEST_READY__ZERO_OF_TWO_INDEPENDENT_ACCEPTANCES`.

Perform an independent hostile review of the exact candidate below. Inspect the
candidate commit and exact deliverables rather than accepting this author-side
summary as evidence. P-decuple-prime substantially changes manuscript,
bibliography, figures, PDF, and source-package bytes after P-nonuple-prime. No
earlier review transfers. Author analysis, local QA, clean-Pod replay, and this
request count as zero independent acceptances.

This request authorizes review only. It does not authorize a public claim,
upload, or submission.

## 1. Project and exact identities

RTDL is a restricted-Python DSL/compiler for bounded computations that
repurpose ray-tracing hardware. The application author chooses the geometric
mapping and owns application semantics. For supported fixed families, RTDL
connects declared result obligations to typed roles/effects, semantic and
physical contracts, trusted traversal-action generation, executable identity,
and fail-closed publication. The paper does not claim arbitrary Python,
automatic discovery of an RT formulation, arbitrary Callback IR,
arbitrary-topology synthesis, independent-user ease of use, or broad
performance superiority.

| Object | Commit | Tree |
| --- | --- | --- |
| Measured two-task implementation M | `d653fe4ad170c5b51fee309d653c9565944dcf2e` | `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b` |
| Frozen predecessor E | `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8` | `aa8b9b12a7bf9cf4395cb71e4fb8e6eb0f169ab6` |
| Frozen tooling F2 | `9771facece4ccd807e26c15b21892b9d0a701d32` | `11c62c28bdebcc7d437f8ab3326635af0832ce48` |
| Long-workload successor | `02e84374fc092d2bb916cca633eda9592b4ecf07` | `8aad15d686bbc9e1c3b11df998898a0a063a01f1` |
| Superseded P-nonuple-prime | `d20a0eb322c13ad17b591007116f8da616a5e60e` | `cec8fb10374943b757d205cb82daf04e4e768bba` |
| Manuscript/evidence parent | `ed4df9330a3c47c116912cb5a817fd7a84dccdfe` | `d4bede2eea645716fe6749de479b69c9413da2bc` |
| Source-package assembly | `c0c23e20ee325fb246c769ba1920566474d869c6` | `c25914560f096175630f89453e33bcd42019992e` |
| **P-decuple-prime under review** | **`8a485a6aae353e0d1dbfee7ce5a96610cee5d31d`** | **`b59d795819f489d4e53f34f264eb46d31f1ec45f`** |

The candidate-parent diff changes only `paper/cgo2027/README.md`. The source-
package assembly differs from the manuscript/evidence parent only in the
normalized source archive. The manuscript/evidence commit adds only manuscript,
bibliography, figure, deterministic figure-generator, and delivery-PDF bytes;
it changes no production source, native source, experiment, workload, timer,
estimator, threshold, or test.

## 2. Exact deliverables

| Deliverable | Bytes | SHA-256 |
| --- | ---: | --- |
| `output/pdf/rtdl_cgo2027_submission_candidate.pdf` | 254,212 | `3f4ec710fa54248dcd8dde0116920d94e75a00ce0424d7b8cf60b8f3e67202e3` |
| `paper/cgo2027/main.pdf` | 254,212 | `3f4ec710fa54248dcd8dde0116920d94e75a00ce0424d7b8cf60b8f3e67202e3` |
| `paper/cgo2027/main.tex` | 57,947 | `81299d0bddd605bdb42694d7204b5898fca3cf4436ff2aeec519038fa97fed52` |
| `paper/cgo2027/references.bib` | 22,538 | `0bd5a31016fc847ef2ac52b45185533e16f0a23e439b83919d1794b9143da948` |
| `paper/cgo2027/figures/reviewed_design_figures.pdf` | 62,908 | `920bc8c2dd7d083df3a13cb8c289e419162966de1fb4d8528d0cfe8d071a5092` |
| `paper/cgo2027/figures/successor_application_performance.pdf` | 27,603 | `3ce0081120db0202a8e2a5a8b623acd27394559e9f42fe2039c96abb2b4454cf` |
| `paper/cgo2027/figures/build_successor_performance.py` | 7,671 | `e34599f8dd3fb1688e8628fa55883ae9246754542014aa71f876c9ee5bec8b55` |
| `output/source/rtdl-cgo2027-source.tar.gz` | 106,838 | `8015a14bdb6af036d45f1500152637a0a5c5f29f56018dc01324992dea240108` |
| unchanged `output/artifact/rtdl-cgo2027-artifact.tar.gz` | 180,308 | `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |
| `output/artifact/rtdl-cgo2027-application-performance.tar.gz` | 84,598 | `d761ce92f55561be656a71712a9f0a78c57f2c7f8165d2ee8d8cb8cf60309e6f` |
| long-workload private raw archive | 730,851 | `ef2ca7890c9d415dc1edbe71966aabc512209c9d8608d4eaf460c7c1fddf8bdc` |
| CPU-sensitivity raw archive | 877,815 | `1f6f25512cbb781df2b75a204e1d3baad1e853179473a6616df6ec39e5629959` |

Commit-object extraction must reproduce every identity. The two PDFs must be
the same Git blob and byte-identical. The normalized USTAR source archive must
have exactly eight members: four directories and the exact manuscript,
bibliography, and two figure PDFs, with fixed owner/group, modes, and
timestamps.

## 3. Central contribution and author/compiler boundary

Review whether the paper is a coherent, nontrivial DSL/compiler contribution
from title through conclusion rather than a collection of workload wrappers.
A reader must be able to answer, from the paper alone:

1. What restricted Python objects does an application author write?
2. What geometric mapping and semantic obligations remain author-owned?
3. What additional facts does the compiler derive, reject, lower, bind, and
   validate?
4. Which behaviors are generated Numba leaves plus a trusted wrapper, and
   which are closed dedicated native routes?
5. Which guarantees are finite admission checks rather than proofs?

The public worked example must be complete enough to expose immutable record
types, role declarations, manifest/result obligation, metadata IDs, physical
plan, public API calls, lifecycle, output, and rejection behavior. Figures 1--3
must agree with that example and the actual implementation routes.

Review the concrete increment narrowly: selected result obligations constrain
admissible callback effects, physical traversal actions, exact-IR
specialization, identity binding, and interface-specific fail-closed return for
supported fixed families. Trusted topology lowerers and specializers remain in
the TCB. The author still discovers the RT mapping. The finite checker is not a
proof. The sphere route required about 2,635 topology-specific physical lines,
plus 23 additions and 5 deletions in an existing compiler file; comments and
blank lines are included, and this is neither semantic LOC nor effort.

Reject wording that turns zero modifications to an earlier canonical planner
into proof of generic lowering. Verify that the paper instead distinguishes the
stable source/IR interface from topology-specific trusted implementation work.

## 4. Prior work and novelty boundary

Verify attribution and nearest-mechanism comparison against RTNN, RayJoin,
RayDB, LibRTS, OptiX, OSL, PyOptiX, OWL, CrossRT, Luisa, Dr.Jit,
Slang/SlangPy, Shader Components, Scion, TTA/TTA+, and Bonsai. The three-row
prior-protocol table for RayJoin, RayDB, and RTNN must accurately distinguish
their paper mechanisms from RTDL's bounded compiler connection.

Reject any first/only/impossibility claim, inference from source silence,
arbitrary-Python implication, statement that rendering lacks protocols, or
claim that PyOptiX cannot express the same device work. PyOptiX differs in
allocation of author/compiler responsibility; inability is not established.

Explicitly decide whether the bounded result-obligation-to-lowering connection
is sufficiently novel and important for CGO when the author must choose the RT
formulation and topology-specific trusted code remains substantial.

## 5. Implementation and evidence honesty

Inspect the implementation rather than relying on paper prose. Determine
whether each stated source construct, IR field, consumer, rejection, lowering,
identity check, and publication check has an executable witness. In particular:

- verify that the source-to-IR path and consumer table name real code;
- verify that the actual authored topology emits Numba leaves and uses a
  trusted wrapper rather than claiming arbitrary wrapper synthesis;
- verify that closed dedicated native routes are not described as authored
  callback lowering;
- verify that exact-IR specialization is guarded and does not masquerade as an
  equivalence proof;
- verify that app formulas and mapping choices remain outside generic compiler
  claims; and
- verify all fail-closed statements against actual rejection/publication
  behavior.

The earlier external concern was that the sealed generic core emitted only a
non-executable plan while topology code hard-coded OptiX behavior. Confirm that
the new manuscript confronts this fact rather than hiding it behind
"canonical" or "generic" terminology.

## 6. Long-workload performance evidence

The separately identified successor ran on one RTX A4500, CC 8.6, driver
550.127.05. It retains 240 fresh workers, 80 paired cells, 1,248 timed samples,
120 warmups, and zero retry, discard, timeout, or output mismatch. Ratios are
medians of eight paired block ratios; the maximum column is the largest
individual registered block ratio.

| Unit and endpoint | RTDL/PyOptiX median | Maximum block |
| --- | ---: | ---: |
| Particle complete | 0.185478x | 0.201120x |
| Particle prepared | 0.772559x | 0.840260x |
| Triangle com-dblp complete | 1.054811x | 1.165425x |
| Triangle com-dblp prepared | 1.099512x | 1.182890x |
| LibRTS point complete | 0.323106x | 0.357454x |
| LibRTS point prepared | 0.998704x | 1.110429x |
| LibRTS range complete | 0.365203x | 0.420269x |
| LibRTS range prepared | 0.984922x | 1.243333x |
| Triangle cit-Patents/4M complete | 1.038065x | 1.057517x |
| Triangle cit-Patents/4M prepared | 1.057361x | 1.083735x |

Every row met the preregistered engineering envelope of paired median at most
1.20x and every block at most 1.35x. The preselected multi-second
cit-Patents/4M prepared row was 9.348 seconds RTDL versus 8.802 seconds
PyOptiX. Only that row is a multi-second prepared natural computation.
Particle is an app-shaped standard-library specialization. Six of nine
application mappings remain unmeasured. Physical routes differ across units,
and the evidence does not isolate intrinsic language cost, productivity, or
portfolio-wide application performance.

The initial application transaction remains adverse evidence: selected stages
from three mappings and four units ranged from `1.080x` to `75.533x`. Verify
that all 12 rows remain visible and that remediation is not presented as
retroactively changing that population.

## 7. Required adverse sensitivity interpretation

The fixed post-formal scan used the same successor and A4500 for Particle and
LibRTS range prepared endpoints across all 48 allowed logical CPUs. It retained
384 workers and 192 paired cells with two blocks per CPU and unit. It is
descriptive, not formal, and is never pooled.

| Sensitivity statistic | Particle | LibRTS range |
| --- | ---: | ---: |
| CPU medians at most 1.20x | 45/48 | 43/48 |
| CPUs with both blocks at most 1.35x | 36/48 | 41/48 |
| CPU-8 scan median | 1.399874x | 0.804614x |
| CPU-8 rank, 1 is lowest | 47/48 | 6/48 |

Particle CPU 8 reversed from the formal `0.772559x` median to `1.399874x`.
CPU order was ascending and therefore confounds CPU identity,
hardware-thread class, and time. GPU clocks were unlocked and no per-worker
clock trace exists. Reject CPU causality, clock causality, hardware-thread
advantage, or use of the scan to filter or strengthen the formal population.

## 8. Earlier evidence that must remain visible

Verify that the paper still discloses all material limits:

- prepared RTDL/Direct medians are `1.077--1.175x` overhead ratios, not
  speedups;
- all four post-import rows are adverse and reach a `2.377x` worst block;
- predecessor first-result comparisons are post hoc and lifecycle-confounded;
- 4,096 timed Arm-A calls have only 32 separate diagnostic receipts;
- paired instrumentation qualifies Arm A only;
- provider double-fault and native-fork limits remain;
- no independent-user authoring or productivity evidence exists;
- only selected stages from three of nine mappings receive the successor
  PyOptiX comparison;
- formal peak memory was not captured; and
- F2 performs offline recount and does not rerun GPU work.

## 9. Exact-byte, artifact, and format checks

Verify from candidate commit `8a485a6aae353e0d1dbfee7ce5a96610cee5d31d`:

- both PDF paths have the stated hash and are byte-identical;
- the PDF is anonymous, 13 US-Letter pages, with text ending on page 11 and
  references beginning on page 12;
- all 18 recursively discovered fonts are embedded, subset, and Unicode
  mapped;
- there is no clipping, overlap, blank page, missing glyph, unreadable table,
  unresolved citation/reference, or horizontal overfull box;
- the final `1.87198pt` vertical event is visually harmless and accurately
  disclosed;
- private paths, usernames, hosts, keys, internal Goal IDs, agent names, and
  candidate identities are absent from submission bytes;
- all bibliography citations and live links are accurate and anonymization
  safe;
- the source archive has the stated eight members, exact payload hashes, and
  compiles from a foreign path;
- F2 has nine members and the unchanged stated hash;
- the application projection reconstructs 240 workers, 80 cells, 1,248 timed
  samples, and all ten evaluations without importing the project; and
- the CPU-sensitivity archive supports exactly the disclosed adverse result.

The author-side Pod replay produced byte-identical normal/optimized outputs:

| Recount | Output SHA-256 | Status |
| --- | --- | --- |
| F2 | `c47aaee24bea18be6b30eaae45a856e30c7a2a74bd5b50fe7daf0f741bdf0ee8` | `PASS__OFFLINE_PROJECTION_RECOUNT` |
| Application projection | `c22a23a782779683385a546634e0d9f3a7dc2cca575dc0c54197c75e0496b4f9` | `PASS__APPLICATION_PROJECTION_RECOUNT` |
| CPU sensitivity | `005caca0475516bafa6834594144a95c445eee771b171d1af0dbb448f80364d0` | `PASS__POST_FORMAL_DESCRIPTIVE_CPU_SENSITIVITY_RECOUNT` |

Also review two portability disclosures. First, Pod system Python lacked Numba;
the extra frozen test suites passed 106/106 normal/optimized only after a
temporary pinned venv installed Numba 0.61.2, NumPy 2.2.6, and llvmlite 0.44.0.
Second, GNU tar 1.35 as container root failed direct extraction of the
application artifact because its `0555` root directory was restored too early;
Python 3.12 `tarfile --filter data` extracted it and both verifier modes passed.
Do not convert these facts into zero-install or universal extraction claims.

Tectonic was not preinstalled on the Pod. Author-side preflight subsequently
verified the official Tectonic 0.17.0 Linux release asset at SHA-256
`1a715688baf591e650c8aeb160ae934e181685eecbb38b317de30b269ac5d606`
and installed it outside the checkout. An online first build and a fresh-path
`--only-cached` build of the exact source package both produced 13 US-Letter
pages with main text ending on page 11, references beginning on page 12, zero
horizontal overfull boxes, the same one `1.87198pt` vertical event, and zero
unresolved citations or references. The committed candidate and both Linux
builds had identical extracted text on all 13 pages, with joined page-text
SHA-256
`14d41d1173e172e6eef9f28a3dd5e1f78df9693fbb7e6099421e0ab7aa6a1a4c`;
the two Linux `.aux`, `.bbl`, and `.out` outputs were byte-identical. The three
PDF byte hashes differ because their creation timestamps differ, so no
cross-build PDF byte identity is claimed. Default release-archive extraction
also first hit the network volume's UID/GID-restoration restriction and passed
only in a new directory with `--no-same-owner`. This remains author-side replay
on the same Pod and counts as zero independent acceptances.

## 10. Required review output

Report every finding with severity, exact PDF page or source location,
evidence, required action, and affected claim. Explicitly answer:

1. Is this a coherent and sufficiently nontrivial DSL/compiler paper for CGO?
2. Is the bounded result-obligation problem important, accurately delimited,
   and correctly distinguished from prior systems?
3. Does the complete authored example make the source-to-physical route clear?
4. Does implementation evidence support the stated increment, or is the work
   primarily manually specialized topology code?
5. Are the two implementation routes described without conflation?
6. Is the RTDL/PyOptiX comparison same-contract and fair for each exact row?
7. Are initial failures and post-formal sensitivity retained without causal or
   broad overclaiming?
8. Are application coverage, custody, TCB, checker, receipt, lifecycle,
   memory, dependency, extraction, and authoring-study limits complete?
9. Does any sentence exceed source, execution, or prior-art evidence?
10. Are the exact PDF, source, figure, and artifact bytes ready for
    submission-side R8?

End with exactly one verdict:

```text
ACCEPT_PDECUPLEPRIME_FINAL_BYTES
REVISE_AND_REREVIEW_CHANGED_BYTES
REJECT_CLAIM_OR_SUBMISSION_SCOPE
```

An acceptance must repeat the exact candidate commit/tree, PDF SHA-256, source
bundle SHA-256, F2 SHA-256, design-figure SHA-256, performance-figure SHA-256,
and application-projection SHA-256. Two independent acceptances of these exact
bytes are required. This request authorizes no public claim, upload, or
submission.
