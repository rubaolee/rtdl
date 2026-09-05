# Goal5846 engineering log

## Scope

Eliminate the exact V4 bounded-relation warm-cache fresh-process setup debt
against the inherited pinned PyOptiX contract without weakening public safety,
regressing Goal5845 steady execution, or adding app-specific engine logic.

## Implementation

- Added canonical content-addressed complete-executable persistence.
- Added manifest-bound logical hit-only cache admission and mutation checks.
- Added one-shot verified executable transfer into generic native prepare.
- Added target-bound asynchronous CUDA/OptiX initialization and generic warm
  ABI.
- Fixed cold native context ordering with `std::call_once` before context
  query.
- Removed duplicate validation only at exact internal verified-token edges.
- Rejected global provider-source hash memoization during self-review.
- Committed and pushed implementation as
  `a6f395cc9411cbed3045c11145d92eda3bc2f502`.

## Premeasurement

- Frozen preregistration seal:
  `53111d83efc13497edae9f2721edaad5255b0bc8f268f721289f2752183d541b`.
- Built a clean DSO from the exact source commit; DSO SHA-256:
  `c56343fad27b4084566febbafeddca19f89c04fc66a0b878ca94417b64d2163e`.
- First-ever cache fill: 36.982403737 s; registered sample: false.
- Sealed hit-only replay: 127.638632 ms.
- First preflight invocation failed before importing RTDL because remote
  `PYTHONPATH` was absent. It created no worker or GPU result and did not create
  the formal output root.
- Corrected unregistered preflight passed both arms with identical output:
  RTDL 569.902 ms setup-plus-first, PyOptiX 701.996 ms.

## Formal transaction

- Endpoint: `root@213.173.108.40:37784` using the established RTDL pod key.
- Hardware: RTX 2000 Ada Generation, UUID
  `GPU-4b436f5f-bf8f-1d8c-0202-98e6e7b387e9`, driver 580.159.04.
- Design: eight balanced blocks, 16 fresh processes, 1,024 steady samples per
  arm, no discarded samples.
- Controller exit: 0; controller stderr: empty.
- Primary paired setup ratio: 0.9909571144584037.
- Worst block ratio: 1.1323427380891558.
- Pooled steady medians: RTDL 364,985 ns; PyOptiX 3,487,496 ns.
- Exact output and all traversal/cache/source gates passed.

## Post-formal audit

- First affected-suite run: 232 tests, two environment errors because the pod
  shallow clone lacked historical commit
  `04305fc820290cc183a599376f13d2fb48175233`.
- Fetched only that Git object; HEAD/tree and source status remained unchanged.
- Second identical affected-suite run: 232/232 passed.
- DSO hash, size, required warm/relation symbols, cache manifests, clean source,
  and empty competing-compute-process snapshot were rechecked.
- Downloaded 92 evidence files (about 968 KiB) to Git, excluding only the DSO
  bytes while retaining complete build/hash/symbol provenance.
- Added a standard-library-only independent authority builder and mutation
  tests. Initial builder failures exposed two verifier assumptions and were
  fixed before authority creation: outer cache-fill timing includes 11.83 us of
  orchestration beyond named phases, and the shallow-clone fatal text did not
  include a `cat-file` subprocess stderr string.
- Stored internal authority seal:
  `7ccf6b63f8df173c6909c641d4e30810f32be102ed6e6f71e8fb7b2b61dbc27a`.

## Review state

Strict Codex hostile self-review is complete. External review and consensus
were intentionally not attempted under the current travel constraint. Public
or manuscript performance wording remains unauthorized.
