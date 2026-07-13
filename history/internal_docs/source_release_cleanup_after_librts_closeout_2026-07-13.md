# Source Release Cleanup After LibRTS Closeout

Date: 2026-07-13

## Decision

Publish the externally reviewed LibRTS scoped closeout without changing the
current `v2.14.1` source-tree version marker or moving the existing `v2.14` tag.
The later v2.14.4 API work is release-staging evidence, but this cleanup does
not invent a new public version claim or speedup claim.

## Verification

- source-tree doctor: pass; optional native/partner warnings only;
- v2.14.4 API preflight: `ready_for_public_release_staging`;
- LibRTS Goal5453-Goal5525 test range: 208 passed, 5 skipped because the local
  OptiX runtime is unavailable;
- final LibRTS external review: unconditional `approve`;
- working tree: clean before publication.

## Removed From The Source Release

- Goal4971 `rtdl_packed_cache/`: reproducible NumPy packed caches totaling about
  792 MB, including individual blobs above GitHub's 100 MB hard limit;
- RT-DBSCAN 16K raw author stdout: 36.7 MB dominated by repeated `callNum`
  diagnostics.

The corresponding compact JSON summaries, JSONL payload, environment record,
hashes, scripts, tests, and reviewed reports remain in the source tree. These
removals do not change the recorded evidence or claim boundaries.

## Publication Model

The detailed unpublished development history remains on the local audit branch.
The public branch is produced as one squash commit based on `origin/main`, so
historical oversized blobs are not transported to GitHub. This is a history
packaging decision, not a rewrite of any already published tag or remote commit.
