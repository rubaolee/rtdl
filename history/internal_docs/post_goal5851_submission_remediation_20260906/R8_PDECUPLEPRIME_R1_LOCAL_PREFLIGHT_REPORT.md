# R8 P-Decuple-Prime-R1 Author-Side Local and Clean-Pod Preflight

Date: 2026-09-08 America/New_York.

Status:
`AUTHOR_PREFLIGHT_PASSED__R7_AND_AUTHENTICATED_SUBMISSION_ACTIONS_PENDING`.

This is an author-side preflight of exact P-decuple-prime-r1. It is not an
independent content, novelty, bibliography, anonymity, or final-byte review;
public-claim authorization; upload authorization; or a submission receipt. R7
remains 0/2. No GPU experiment was run in this preflight.

## 1. Why a new candidate was required

The superseded P-decuple-prime bibliography pointed to a legacy NVIDIA OptiX
guide URL that returned HTTP 404. The corrected entry points to the official
NVIDIA `optix-sdk` v9.0.0 tagged programming-guide PDF. An author-side scan
checked all 30 explicit bibliography URLs/DOIs; no second definite dead link
was found. Bot-blocked publisher endpoints were not misclassified as missing.

Because the bibliography changes PDF and source-package bytes, no review of an
older candidate transfers. P-decuple-prime-r1 changes no production, compiler,
native, experiment, workload, timer, estimator, threshold, or test source. The
research claims and all adverse evidence are unchanged.

## 2. Exact object under preflight

| Object | Exact identity |
| --- | --- |
| Candidate | commit `7c7dfce8e2aad8621d86246b58bb142ab9ed2329`; tree `25d8d07d26ccba02d65711eb671d9324e433cb41` |
| Source-package assembly | commit `a9e6a76802e7f91b95935201d93ccddf19c844f6`; tree `299de87bba09cf3ab7c480dbc37a1dbf9077d3fd` |
| Manuscript/bibliography parent | commit `f377500fd85d4477529433fde282be59d60d7a81`; tree `f9471e81ce097d87ba27f5782cee4505ddbb81be` |
| Superseded P-decuple-prime | commit `8a485a6aae353e0d1dbfee7ce5a96610cee5d31d`; tree `b59d795819f489d4e53f34f264eb46d31f1ec45f` |
| Long-workload successor | commit `02e84374fc092d2bb916cca633eda9592b4ecf07`; tree `8aad15d686bbc9e1c3b11df998898a0a063a01f1` |

The candidate differs from its source-package assembly only in
`paper/cgo2027/README.md`; submission bytes are unchanged. The assembly differs
from its parent only in the normalized source archive. That archive was built
from exact parent-commit Git blobs rather than dirty-worktree files.

| Deliverable | Bytes | SHA-256 |
| --- | ---: | --- |
| `paper/cgo2027/main.tex` | 57,947 | `81299d0bddd605bdb42694d7204b5898fca3cf4436ff2aeec519038fa97fed52` |
| `paper/cgo2027/references.bib` | 22,550 | `55b138e56d1bd748885ab0765002a1fa7c28d9d09b000f93efae67955fa4f3b6` |
| both PDF paths | 254,266 | `a810e3d8c465c6764da06a2ccdefd13fa5444c1c480ecd9441b54adadde26631` |
| design figure | 62,908 | `920bc8c2dd7d083df3a13cb8c289e419162966de1fb4d8528d0cfe8d071a5092` |
| performance figure | 27,603 | `3ce0081120db0202a8e2a5a8b623acd27394559e9f42fe2039c96abb2b4454cf` |
| source bundle | 106,843 | `fc2f42b342843260d02d68884dcae3d1dcaa582a070c4eefde3d412a34876f78` |
| unchanged F2 artifact | 180,308 | `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |
| application projection | 84,598 | `d761ce92f55561be656a71712a9f0a78c57f2c7f8165d2ee8d8cb8cf60309e6f` |
| long-workload raw archive | 730,851 | `ef2ca7890c9d415dc1edbe71966aabc512209c9d8608d4eaf460c7c1fddf8bdc` |
| CPU-sensitivity archive | 877,815 | `1f6f25512cbb781df2b75a204e1d3baad1e853179473a6616df6ec39e5629959` |

The two PDF paths are byte-identical. Commit-object extraction and the Pod
worktree reproduced the identities above.

## 3. Local manuscript and PDF checks

The corrected source was compiled in an isolated directory with Tectonic
0.16.9. All 13 pages were rendered at 130 DPI and visually inspected, with
full-resolution checks of the changed reference pages and the main performance
figure page.

| Check | Result |
| --- | --- |
| Tectonic build | PASS, exit 0 |
| Page count and size | 13 pages, 612 x 792 pt US Letter |
| Main-content boundary | Main text ends on page 11; references begin on page 12 |
| Horizontal overfull boxes | 0 |
| Vertical overfull boxes | One final-output `1.90399pt` event; no visible clipping or overlap |
| Unresolved citations/references | 0 |
| BibTeX completeness warnings | 17 nonfatal inherited warnings |
| Embedded/subset/Unicode fonts | 18/18 / 18/18 / 18/18 |
| Visual defects | 0 clipping, overlap, blank page, missing glyph, or unreadable table |
| Tested private-identity scan | PASS |

The URL change leaves pages 1--11 text-identical to P-decuple-prime. On pages
12--13 only the corrected NVIDIA URL and the consequent reference-line flow
change. The small vertical warning is disclosed rather than called a
zero-warning build.

## 4. Source custody and local frozen tests

Two independent Python processes constructed normalized USTAR/gzip bundles
from exact `f377500fd...` Git blobs. They were byte-identical at SHA-256
`fc2f42b3...`. The bundle has eight members: four directories and four files.
All members use UID/GID zero, empty owner/group names, 2000-01-01 UTC mtimes,
directory mode `0555`, file mode `0444`, USTAR format, and gzip mtime zero.
Every payload was compared byte-for-byte with its parent-commit blob.

The focused frozen suites passed locally under ordinary and optimized Python:

| Suite | Ordinary | Optimized |
| --- | ---: | ---: |
| `tests.goal5852_submission_evidence_test` | 14/14 | 14/14 |
| `v4_long_workload*_test.py` discovery | 39/39 | 39/39 |

Total: 106/106 invocations passed. No source was changed to obtain this result.

## 5. Clean-Pod exact-candidate replay

The supplied endpoint resolved to retained host `4735c6e75b0c`, NVIDIA RTX
A4500, driver 550.127.05. It is the same host used by the earlier preflight and
is not an independent machine or R7 reviewer. The existing verified Git object
store fetched the three small successor commits and materialized a new detached
clean worktree. The worktree matched candidate commit/tree exactly and remained
porcelain-clean before and after replay. A separate full-clone attempt exceeded
the SSH window and was abandoned; it was never used as evidence.

Tectonic 0.17.0 was the previously installed, hash-verified official Linux
binary. Its release asset SHA-256 remains
`1a715688baf591e650c8aeb160ae934e181685eecbb38b317de30b269ac5d606`.
The exact source bundle was extracted through Python 3.12 `tarfile` with the
data filter into two fresh roots.

| Linux build | Bytes | PDF SHA-256 | Result |
| --- | ---: | --- | --- |
| First build | 253,086 | `499021af5d2324e33b7355f589cc33d1e857d056e48e0b435ac6387200ba40d4` | PASS |
| Fresh-root `--only-cached` build | 253,086 | `9708e51b9417735901c896f520abe9d5228a0b8aa47ab3ccb7fc004749b977e3` | PASS |

The committed candidate and both Linux outputs each have 13 US-Letter pages,
main text ending on page 11, and references beginning on page 12. Under pypdf
6.0.0, all 13 page texts were equal across all three PDFs; joined page-text
SHA-256 was
`063d022570868872acacb4f3bdc3e2d97a18ebcef39bad7b4794a0c58d6415fe`.
The two Linux `.aux`, `.bbl`, and `.out` files were byte-identical. PDF-byte
identity is not claimed because creation timestamps differ.

The same external pinned test environment used in the earlier replay (Numba
0.61.2, NumPy 2.2.6, llvmlite 0.44.0) passed the 14-test and 39-test suites
under ordinary and optimized Python: 106/106 total.

## 6. Retained-evidence replays

Three retained-data replays ran under ordinary and optimized Python. Each pair
was byte-identical and reproduced its previous authority:

| Replay | Output SHA-256 | Result |
| --- | --- | --- |
| F2 | `c47aaee24bea18be6b30eaae45a856e30c7a2a74bd5b50fe7daf0f741bdf0ee8` | `PASS__OFFLINE_PROJECTION_RECOUNT` |
| Application projection | `c22a23a782779683385a546634e0d9f3a7dc2cca575dc0c54197c75e0496b4f9` | `PASS__APPLICATION_PROJECTION_RECOUNT` |
| CPU sensitivity | `005caca0475516bafa6834594144a95c445eee771b171d1af0dbb448f80364d0` | `PASS__POST_FORMAL_DESCRIPTIVE_CPU_SENSITIVITY_RECOUNT` |

The CPU recount retained Particle CPU-8 `1.399873664x`, rank 47/48, and
LibRTS-range CPU-8 `0.804614022x`, rank 6/48. No row was filtered or pooled.
The GPU compute-process list was empty after replay. No CUDA/OptiX workload,
timing, or new GPU experiment ran.

## 7. Claim and submission boundary

The successor evidence remains 240 workers, 80 paired cells, 1,248 timed
samples, 120 warmups, and ten registered complete/prepared rows. Only
cit-Patents/4M is a multi-second prepared natural computation. The initial
adverse rows, post-import overhead, receipt shortfall, CPU sensitivity,
six unmeasured mappings, absent formal peak memory, and absent independent-user
authoring study all remain disclosed.

The claim ledger has 31 entries and zero authorized claims. P-decuple-prime-r1
has zero of two required independent exact-final-byte acceptances. Earlier
reviews do not transfer. Authenticated submission-form checks, explicit upload
authorization, upload, downloaded-byte verification, submission ID, and
receipt are absent. Correct state: `NOT_SUBMITTED`.
