# CGO 2027 anonymous manuscript workspace

`main.tex` and `main.pdf` are the P-decuple-prime manuscript candidate. The
paper presents RTDL as a restricted-Python DSL and compiler for bounded
computations that repurpose ray-tracing hardware. The author selects the RT
formulation and owns application semantics. For supported fixed families, RTDL
connects declared result obligations to role/effect admission, typed data and
ABI contracts, trusted traversal-action generation, executable identity, and
fail-closed result publication.

The manuscript makes four bounded contribution claims:

1. a restricted-Python programming model for immutable records, typed role
   functions, and manifests;
2. typed Callback IR plus whole-protocol admission;
3. generated Numba leaves, trusted topology wrappers, exact-IR
   specializations, and prepared runtime binding; and
4. application evidence with explicit source-custody and performance limits.

It does not claim arbitrary Python, arbitrary Callback IR, arbitrary-topology
synthesis, automatic discovery of an RT formulation, independent-user ease of
use, portfolio-wide performance, or that prior systems cannot implement
related guarantees. The two implemented routes are stated separately: authored
Numba leaf callbacks plus a trusted topology wrapper, and closed dedicated
native routes. Whole-protocol/result-route checking is one compiler
contribution inside the DSL story, not the entire paper theme.

P-decuple-prime supersedes P-nonuple-prime for submission consideration. Every
older candidate and all adverse application transactions remain immutable.

## Current exact candidate

| Object | Exact identity |
| --- | --- |
| Source-package assembly commit | `c0c23e20ee325fb246c769ba1920566474d869c6` |
| Source-package assembly tree | `c25914560f096175630f89453e33bcd42019992e` |
| Manuscript/evidence parent commit | `ed4df9330a3c47c116912cb5a817fd7a84dccdfe` |
| Manuscript/evidence parent tree | `d4bede2eea645716fe6749de479b69c9413da2bc` |
| Superseded P-nonuple-prime checkpoint | commit `d20a0eb322c13ad17b591007116f8da616a5e60e`; tree `cec8fb10374943b757d205cb82daf04e4e768bba` |
| Candidate parent / measured successor | commit `02e84374fc092d2bb916cca633eda9592b4ecf07`; tree `8aad15d686bbc9e1c3b11df998898a0a063a01f1` |
| `main.tex` | 57,947 bytes; SHA-256 `81299d0bddd605bdb42694d7204b5898fca3cf4436ff2aeec519038fa97fed52` |
| `references.bib` | 22,538 bytes; SHA-256 `0bd5a31016fc847ef2ac52b45185533e16f0a23e439b83919d1794b9143da948` |
| Exact PDF at both delivery paths | 254,212 bytes; SHA-256 `3f4ec710fa54248dcd8dde0116920d94e75a00ce0424d7b8cf60b8f3e67202e3` |
| Reviewed design-figure PDF | 62,908 bytes; SHA-256 `920bc8c2dd7d083df3a13cb8c289e419162966de1fb4d8528d0cfe8d071a5092` |
| Successor-performance figure PDF | 27,603 bytes; SHA-256 `3ce0081120db0202a8e2a5a8b623acd27394559e9f42fe2039c96abb2b4454cf` |
| Deterministic performance-figure builder | 7,671 bytes; SHA-256 `e34599f8dd3fb1688e8628fa55883ae9246754542014aa71f876c9ee5bec8b55` |
| Source bundle | 106,838 bytes; SHA-256 `8015a14bdb6af036d45f1500152637a0a5c5f29f56018dc01324992dea240108` |
| New performance archive | 730,851 bytes; SHA-256 `ef2ca7890c9d415dc1edbe71966aabc512209c9d8608d4eaf460c7c1fddf8bdc` |
| Post-formal CPU-sensitivity archive | 877,815 bytes; SHA-256 `1f6f25512cbb781df2b75a204e1d3baad1e853179473a6616df6ec39e5629959` |
| Anonymous application projection | 84,598 bytes; SHA-256 `d761ce92f55561be656a71712a9f0a78c57f2c7f8165d2ee8d8cb8cf60309e6f` |
| Unchanged F2 artifact | 180,308 bytes; SHA-256 `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |

The two PDF paths are byte-identical. The final source-package assembly commit
differs from its manuscript/evidence parent only in the normalized source
archive. That archive was built from the exact parent-commit Git blobs, not
from unrelated dirty worktree bytes. It contains four directories and four
regular files: `main.tex`, `references.bib`, and the two referenced figure
PDFs. All members use UID/GID 0, empty owner/group names, fixed 2000-01-01 UTC
timestamps, directory mode `0555`, file mode `0444`, USTAR format, and gzip
mtime 0.

The original measured implementation remains M commit
`d653fe4ad170c5b51fee309d653c9565944dcf2e`, tree
`d53af23a2599f9d6adb4ac0bfff39cd0ab31860b`. Predecessor E remains
`12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8`. Frozen offline tooling F2
remains commit `9771facece4ccd807e26c15b21892b9d0a701d32`, tree
`11c62c28bdebcc7d437f8ab3326635af0832ce48`.

## Evidence boundary

The final M evaluation contains two exact tasks run independently on RTX 4090
Ada and RTX 3090 Ampere. Prepared public RTDL/Direct latency ratios are
`1.077--1.175x`; these are overhead ratios, not intrinsic-language speedups.
The original written per-execution detailed-receipt requirement was not met:
4,096 timed Arm-A calls have 32 separate post-loop diagnostic receipts. All
post-import rows are adverse and reach `2.377129x`; predecessor first-result
comparisons are post hoc and lifecycle-confounded. Instrumentation evidence
qualifies Arm A only.

Historical V4 evidence records nine application mappings and thirteen selected
paper lanes. Current entry points were recovered for all nine; exact historical
per-file custody survives for Particle Tracking, Triangle Counting, and
LibRTS, while the other six retain archive-level audit records only. This does
not establish current runnability for all nine. The separate historical
34-row V2-direct/V4 authority records mixed outcomes and is neither a PyOptiX
comparison nor pooled with final M.

The initial application transaction covers selected stages from three of nine
mappings and four operation units on one RTX A4500. Its 192 workers and 12
endpoint rows remain adverse evidence (`1.080x` to `75.533x`).

The successor adds a fifth, C-only-preselected cit-Patents/4M graph scale and
measures complete/prepared endpoints for all five units. All 240 workers, 80
paired cells, 1,248 timed samples, and 120 warmups passed exact-output and
affinity checks with zero retry/discard/timeout. Every one of the ten rows met
the preregistered successor/PyOptiX engineering envelope: paired median
`<=1.20x`, every block `<=1.35x`. The largest median was `1.099512x`; the
largest block was `1.243333x`. The long cit-Patents prepared row was
`1.057361x` (`9.348 s` RTDL, `8.802 s` PyOptiX). A different clean checkout
reconstructed all raw hashes, journals, cells, and statistics without importing
project modules.

Only cit-Patents/4M is a multi-second prepared natural computation. Particle is
a fixed app-shaped standard-library specialization, six mappings remain
unmeasured, CPU 8 was selected after a disclosed scheduling diagnosis, GPU
clocks were not locked, and formal peak memory was not captured. These results
are not broad performance, productivity, intrinsic-language-cost,
arbitrary-callback, or app-independent-engine evidence.

A fixed post-formal descriptive scan ran the two shortest prepared units across
all 48 allowed logical CPUs. Its CPU-8 Particle ratio reversed from
`0.772559x` in the formal population to `1.399874x`. The scan is not pooled
with formal evidence and shows that the sub-millisecond rows are not stable
performance guarantees.

The nine-member F2 archive performs offline recount of retained evidence. It
does not rerun GPU work, install RTDL, verify novelty, or reconstruct missing
private history. The anonymous application-performance projection retains all
240 formal rows and 1,248 samples and reconstructs the ten successor
evaluations with a standard-library verifier. It omits raw custody and cannot
rerun GPU work; the private 1,049-file archive remains the raw authority.

## Local validation

| Check | Result |
| --- | --- |
| Canonical Tectonic build | PASS |
| Page count and size | 13 pages, 612 x 792 pt US Letter |
| Main-content boundary | Main content ends on page 11; references begin on page 12 |
| Paper/delivery PDF identity | Byte-identical |
| Horizontal overfull boxes | 0 |
| Vertical overfull boxes | One benign final-output `1.87198pt` ACM bibliography-page event; visual inspection shows no clipping |
| Unresolved citations/references | 0 |
| Embedded/subset/Unicode fonts | 18/18 / 18/18 / 18/18, including figure form objects |
| Render inspection | All 13 pages inspected; no clipping, overlap, blank page, missing glyph, or unreadable table |
| Local anonymity scan | PASS for tested private paths, host identities, agents, goals, and candidate names |
| Source custody | Two independent normalized bundles byte-identical; 8 members / 4 regular files; foreign-path build passed |
| Frozen regressions | 53/53 unit tests passed |
| Anonymous application projection | Normal/optimized outputs byte-identical; 240 workers, 80 cells, 1,248 samples, ten evaluations |
| Performance-figure reconstruction | Two independent builds byte-identical to the committed figure and bound to the projection hash |
| Clean-pod replay of this exact checkpoint | Pending; it is a replay gate, not a new GPU experiment |

The source package also compiled from a fresh read-only extraction beneath a
path containing spaces and produced the same 13-page layout. PDF bytes are not
claimed reproducible because the PDF creation timestamp varies.

BibTeX emits 17 nonfatal completeness warnings for inherited conference
records and the in-press survey. That is not a zero-warning build claim.
Independent bibliography, live-link, content, novelty, and anonymity review
remains open.

The CGO 2027 main-conference rule permits up to 11 text pages excluding
references and requires US Letter. This candidate uses 11 text pages and two
reference pages. The authenticated submission form still must be checked; a
public CFP check does not replace that check.

## Review and submission state

The checkpoint commit containing this README changes no submission bytes. An
exact review request must name that immutable checkpoint and therefore belongs
in a later control-only commit.

P-decuple-prime has zero independent exact-final-byte acceptances. No earlier
candidate review transfers to the new manuscript, source package, or figures.
Local build, all-page rendering, anonymity scan, tests, source reconstruction,
and numeric projection checks pass, but all public-claim, upload, and submission
authorization flags remain false. Authenticated submission-form checks,
upload, downloaded-byte verification, and receipt capture remain open. No
upload or submission has occurred.

The hard executable-code freeze began at 2026-09-08 00:00 America/New_York.
Only manuscript, bibliography, claim narrowing, execution of frozen tools,
artifact packaging/replay, review, and submission checks are now allowed.
