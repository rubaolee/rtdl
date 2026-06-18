# RTDL v3.0 Tag Record

Status: released as `v3.0`.

Date: 2026-06-18

## Release Boundary

The `v3.0` tag represents the V3 source-tree major release:

- current docs identify V3.0 as the active release;
- all ten benchmark-app current routes are closed by Goal4614;
- the V3 app-author strategy is learner-facing;
- embedding, C ABI, SDK packaging, generated bindings, zero-copy, and external
  runtime integration are excluded as V4.0 scope;
- source-tree doctor and `v3_current` validation pass;
- public wording remains bounded by this release packet.

## Requirements Satisfied Before Tag

- Completed V3 current-scope completion gate.
- Completed V3 completion review consensus.
- Completed V3 source-tree doctor and test-matrix gates.
- Completed V3 release packet polish.
- Updated `VERSION` from `v2.14` to `v3.0`.
- Updated editable metadata from `2.14.0` to `3.0.0`.
- Saved final publication authorization in the user request on 2026-06-18.

## Tag Commands

The release action uses:

```bash
git tag -a v3.0 -m "Release RTDL v3.0"
git push origin main
git push origin v3.0
```

## Boundary

This file records the tag procedure. It does not widen the V3.0 claim scope
beyond [Public Wording Boundaries](public_wording_boundaries.md).
