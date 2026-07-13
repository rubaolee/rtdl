# Goal5526: RTDL v2.14.4 Source-Tree Release Alignment

Date: 2026-07-13

## Objective

Align the public source-tree version with the already reviewed v2.14.4 API
surface and the completed five-app paper-reproduction portfolio, without
changing algorithms or expanding any claim boundary.

## Changes

- changed `VERSION`, `pyproject.toml`, source-tree doctor, and its tests from
  v2.14.1 to v2.14.4;
- added the v2.14.4 closeout note and updated the release index, front page,
  versioning guidance, and current claim-boundary page;
- recorded the reviewed public API surface and kept `device_group_by` internal;
- closed stale LibRTS TODO entries as absorbed by the externally reviewed final
  ledger instead of pretending each intermediate goal was independently
  reviewed;
- froze the repository as a clean baseline with no active paper-app line.

## Claim Boundary

This is release metadata and governance work. It does not establish new
correctness, performance, zero-copy, author-parity, or full-paper claims.

## Verification

The release gates passed:

- version/doctor, v2.14.4 preflight, and portfolio tests: 12 tests OK;
- complete Goal5043-Goal5062 v2.14.4 API regression: 78 tests OK,
  1 local runtime-dependent skip;
- source-tree doctor with hello-world smoke: required checks pass, optional
  CuPy/OptiX/Embree warnings only;
- v2.14.4 API preflight: `ready_for_public_release_staging`, zero blockers;
- Goal5453-Goal5525 LibRTS regression under `PYTHONPATH=src:.`: 208 tests OK,
  5 local OptiX-runtime-dependent skips;
- `git diff --check`: pass before commit.
