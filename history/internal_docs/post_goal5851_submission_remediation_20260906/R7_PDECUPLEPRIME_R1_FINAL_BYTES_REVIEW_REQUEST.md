# R7 P-Decuple-Prime-R1 Exact Final-Bytes Review Request

Date: 2026-09-08 America/New_York.

Status: `REQUEST_READY__ZERO_OF_TWO_INDEPENDENT_ACCEPTANCES`.

Perform an independent hostile review of the exact candidate below. Inspect the
candidate commit and exact deliverables rather than accepting this author-side
summary as evidence. P-decuple-prime-r1 replaces one dead NVIDIA OptiX
bibliography URL and therefore changes bibliography, PDF, and source-package
bytes after P-decuple-prime. No earlier review transfers. Author analysis,
local QA, clean-Pod replay, and this request count as zero independent
acceptances.

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
| Superseded P-decuple-prime | `8a485a6aae353e0d1dbfee7ce5a96610cee5d31d` | `b59d795819f489d4e53f34f264eb46d31f1ec45f` |
| Manuscript/bibliography parent | `f377500fd85d4477529433fde282be59d60d7a81` | `f9471e81ce097d87ba27f5782cee4505ddbb81be` |
| Source-package assembly | `a9e6a76802e7f91b95935201d93ccddf19c844f6` | `299de87bba09cf3ab7c480dbc37a1dbf9077d3fd` |
| **P-decuple-prime-r1 under review** | **`7c7dfce8e2aad8621d86246b58bb142ab9ed2329`** | **`25d8d07d26ccba02d65711eb671d9324e433cb41`** |

The candidate-parent diff changes only `paper/cgo2027/README.md`. The source-
package assembly differs from the manuscript/bibliography parent only in the
normalized source archive. Compared with superseded P-decuple-prime, the only
semantic source edit is this bibliography URL replacement:

```text
old: https://raytracing-docs.nvidia.com/optix9/guide/optix_guide.250130.A4.pdf
new: https://github.com/NVIDIA/optix-sdk/blob/v9.0.0/doc/OptiX_Programming_Guide_9.0.0.pdf
```

The old endpoint returned HTTP 404; the new endpoint is in NVIDIA's official
v9.0.0 tag. Verify this independently. No executable or experiment source
changed.

## 2. Exact deliverables

| Deliverable | Bytes | SHA-256 |
| --- | ---: | --- |
| `output/pdf/rtdl_cgo2027_submission_candidate.pdf` | 254,266 | `a810e3d8c465c6764da06a2ccdefd13fa5444c1c480ecd9441b54adadde26631` |
| `paper/cgo2027/main.pdf` | 254,266 | `a810e3d8c465c6764da06a2ccdefd13fa5444c1c480ecd9441b54adadde26631` |
| `paper/cgo2027/main.tex` | 57,947 | `81299d0bddd605bdb42694d7204b5898fca3cf4436ff2aeec519038fa97fed52` |
| `paper/cgo2027/references.bib` | 22,550 | `55b138e56d1bd748885ab0765002a1fa7c28d9d09b000f93efae67955fa4f3b6` |
| design figure | 62,908 | `920bc8c2dd7d083df3a13cb8c289e419162966de1fb4d8528d0cfe8d071a5092` |
| performance figure | 27,603 | `3ce0081120db0202a8e2a5a8b623acd27394559e9f42fe2039c96abb2b4454cf` |
| source bundle | 106,843 | `fc2f42b342843260d02d68884dcae3d1dcaa582a070c4eefde3d412a34876f78` |
| unchanged F2 artifact | 180,308 | `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |
| application projection | 84,598 | `d761ce92f55561be656a71712a9f0a78c57f2c7f8165d2ee8d8cb8cf60309e6f` |
| long-workload raw archive | 730,851 | `ef2ca7890c9d415dc1edbe71966aabc512209c9d8608d4eaf460c7c1fddf8bdc` |
| CPU-sensitivity archive | 877,815 | `1f6f25512cbb781df2b75a204e1d3baad1e853179473a6616df6ec39e5629959` |

Commit-object extraction must reproduce every identity. The PDFs must be the
same Git blob. The normalized USTAR/gzip source archive must contain exactly
four directories and the exact manuscript, bibliography, and two figure PDFs,
with the documented fixed ownership, modes, and timestamps.

## 3. Central contribution and implementation boundary

Review whether this is a coherent, nontrivial DSL/compiler paper rather than a
collection of workload wrappers. A reader must be able to determine:

1. what restricted Python objects an application author writes;
2. what geometric mapping and semantic obligations remain author-owned;
3. what the compiler derives, rejects, lowers, binds, and validates;
4. which routes use generated Numba leaves plus a trusted topology wrapper;
5. which routes are closed dedicated native paths; and
6. which guarantees are finite admission checks rather than proofs.

The concrete increment is narrow: selected result obligations constrain
admissible callback effects, traversal actions, exact-IR specialization,
identity binding, and fail-closed publication for supported fixed families.
Trusted topology lowerers and specializers remain in the TCB. The author still
discovers the RT mapping. The sphere route required about 2,635 topology-
specific physical lines plus a small existing-compiler edit. Reject any wording
that treats zero changes to an earlier canonical planner as proof of generic
physical lowering.

Inspect implementation witnesses rather than paper prose. Verify that the
source-to-IR path and consumer table name real code; that authored callbacks
produce Numba leaves and use a trusted wrapper rather than arbitrary wrapper
synthesis; that dedicated native routes are not described as callback
lowering; and that app formulas stay outside generic compiler claims.

## 4. Prior work and novelty boundary

Check attribution against RTNN, RayJoin, RayDB, LibRTS, OptiX, OSL, PyOptiX,
OWL, CrossRT, Luisa, Dr.Jit, Slang/SlangPy, Shader Components, Scion,
TTA/TTA+, and Bonsai. Reject first/only/impossibility claims, source-silence
inference, arbitrary-Python implication, or a claim that PyOptiX cannot express
the same device work. Decide explicitly whether connecting bounded result
obligations to admission, lowering, binding, and publication is sufficiently
novel and important for CGO despite author-selected mappings and substantial
trusted topology code.

## 5. Performance and adverse evidence

The separately identified successor ran on one RTX A4500. It retained 240
fresh workers, 80 paired cells, 1,248 timed samples, 120 warmups, and zero
retry/discard/timeout/output mismatch. Ratios are successor RTDL divided by
public PyOptiX.

| Unit and endpoint | Paired median | Largest block |
| --- | ---: | ---: |
| Particle complete / prepared | `0.185478x` / `0.772559x` | `0.201120x` / `0.840260x` |
| Triangle com-dblp complete / prepared | `1.054811x` / `1.099512x` | `1.165425x` / `1.182890x` |
| LibRTS point complete / prepared | `0.323106x` / `0.998704x` | `0.357454x` / `1.110429x` |
| LibRTS range complete / prepared | `0.365203x` / `0.984922x` | `0.420269x` / `1.243333x` |
| Triangle cit-Patents/4M complete / prepared | `1.038065x` / `1.057361x` | `1.057517x` / `1.083735x` |

Every row met the preregistered 1.20-median/1.35-every-block engineering
envelope. Only cit-Patents/4M is a multi-second prepared natural computation:
9.348 s RTDL versus 8.802 s PyOptiX. Particle is an app-shaped standard-library
specialization; six mappings remain unmeasured; formal peak memory was not
captured. These rows do not establish intrinsic language cost, productivity,
or portfolio-wide application superiority.

The initial application transaction remains adverse (`1.080x` to `75.533x`).
The post-formal CPU scan is descriptive and not pooled. Particle CPU 8 reversed
from formal `0.772559x` to scan `1.399874x`; LibRTS range CPU 8 was
`0.804614x`. GPU clocks were unlocked and the CPU scan confounds CPU identity,
hardware-thread class, and time. Reject any causal or filtered interpretation.

Also verify continued disclosure that prepared RTDL/Direct medians are
`1.077--1.175x` overhead ratios, all four post-import rows are adverse and
reach `2.377x`, predecessor comparisons are post hoc/lifecycle-confounded,
4,096 timed Arm-A calls have only 32 separate detailed receipts,
instrumentation qualifies Arm A only, and there is no independent-user study.

## 6. Exact-byte and format checks

Verify from candidate `7c7dfce8e2aad8621d86246b58bb142ab9ed2329`:

- both PDF paths have the stated hash and are byte-identical;
- the PDF is anonymous, 13 US-Letter pages, with text ending on page 11 and
  references beginning on page 12;
- all fonts are embedded, subset, and Unicode mapped;
- no clipping, overlap, blank page, missing glyph, unreadable table,
  unresolved citation/reference, or horizontal overfull box exists;
- the final `1.90399pt` vertical event is visually harmless;
- bibliography citations and live links, especially the repaired NVIDIA URL,
  are accurate and anonymity safe;
- the source archive has the exact member set and builds from a foreign path;
- F2 and application projection reconstruct their stated populations; and
- the CPU-sensitivity archive supports the disclosed adverse result.

Author-side Pod replay, which is not an independent acceptance, reproduced
ordinary/optimized outputs:

| Recount | Output SHA-256 |
| --- | --- |
| F2 | `c47aaee24bea18be6b30eaae45a856e30c7a2a74bd5b50fe7daf0f741bdf0ee8` |
| Application projection | `c22a23a782779683385a546634e0d9f3a7dc2cca575dc0c54197c75e0496b4f9` |
| CPU sensitivity | `005caca0475516bafa6834594144a95c445eee771b171d1af0dbb448f80364d0` |

It also passed 106/106 frozen test invocations and two Linux source-package
builds, including a fresh-root `--only-cached` build. The committed PDF and
both Linux outputs had identical text on 13/13 pages under pypdf 6.0.0. PDF
byte identity across builds is not claimed because creation timestamps differ.
No GPU experiment ran.

## 7. Required review output

Report each finding with severity, exact PDF page or source location, evidence,
required action, and affected claim. Explicitly answer:

1. Is this a coherent and sufficiently nontrivial DSL/compiler paper for CGO?
2. Is the bounded result-obligation problem important and accurately delimited?
3. Does the authored example make the source-to-physical route clear?
4. Does implementation evidence support the increment, or is it primarily
   manually specialized topology code?
5. Are the two implementation routes described without conflation?
6. Is each RTDL/PyOptiX row same-contract and fair?
7. Are failures and sensitivity retained without overclaiming?
8. Are coverage, custody, TCB, checker, receipt, lifecycle, memory, dependency,
   extraction, and authoring-study limits complete?
9. Does any sentence exceed source, execution, or prior-art evidence?
10. Are the exact PDF, source, figures, and artifacts ready for R8?

End with exactly one verdict:

```text
ACCEPT_PDECUPLEPRIME_R1_FINAL_BYTES
REVISE_AND_REREVIEW_CHANGED_BYTES
REJECT_CLAIM_OR_SUBMISSION_SCOPE
```

An acceptance must repeat the exact candidate commit/tree, PDF SHA-256, source
bundle SHA-256, F2 SHA-256, design-figure SHA-256, performance-figure SHA-256,
and application-projection SHA-256. Two independent acceptances of these exact
bytes are required. This request authorizes no public claim, upload, or
submission.
