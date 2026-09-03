# Goal5837 post-freeze compositional verifier repair

Date: 2026-09-03

Status: `REPAIRED__STORED_AUTHORITY_UNCHANGED`

## Discovery

The final Goal5838 whole-cohort audit exposed a second error in addition to the
known Goal5832 historical custody error. Goal5837's stored authority was valid
and sealed, but `build_authority()` rebuilt its historical `source_inventory`
by hashing the current working tree. `AGENTS.md` was one of those rows.

The Goal5837 authority commit is
`0f5c9d4297f73e412732e5a8ab133423fe4cfd21`. Its stored `AGENTS.md` identity is
146,583 bytes with SHA-256
`238bc9cd37e7f68b42e0d0db880d9979e397e5996e0c5a3fd888f206ebbae6c6`.
The later Goal5838 boundary update at `f5ba21f` legitimately changed
`AGENTS.md`, so the Goal5837 verifier had already become non-compositional
before the final Goal5838 audit.

## Repair

The historical Goal5837 `source_inventory` is now rederived from Git blobs at
the exact authority commit `0f5c9d4`, not from mutable current files. Path
normalization rejects absolute paths and parent traversal, and missing Git
objects fail closed. Current semantic observations, public exports, claim
policy, evidence identities, and root-surface evolution continue to be derived
from their existing current or explicitly historical sources exactly as before.

The stored `GOAL5837_AUTHORITY.json` was not rewritten. All source-inventory
rows at `0f5c9d4` reproduce the existing stored bytes and SHA-256 values.

## Regression

A new test proves that the stored `AGENTS.md` row equals the authority-commit
blob and that rebuilding the historical inventory does not call the
current-tree identity function. The audit separately confirmed that the
legitimately evolved current file differs. All 19 Goal5837 tests pass. The full
Goal583x audit now runs 313 tests and reports only the already disclosed
Goal5832 current-tree custody error: 312 pass, one known historical error.

This repair changes no Goal5838 frozen-core byte, selected topology, provider,
fixture, oracle, native build, GPU artifact, or claim boundary.
