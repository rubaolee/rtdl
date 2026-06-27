# RTDL v3.0.1 Tag Record

Status: ready to tag as `v3.0.1`.

Date: 2026-06-18

## Release Boundary

The `v3.0.1` tag represents the current V3 source-tree patch release:

- current docs identify V3.0.1 as the active release;
- all ten benchmark-app current routes are closed by Goal4614;
- the V3 app-author strategy is learner-facing;
- embedding, C ABI, SDK packaging, generated bindings, zero-copy, and external
  runtime integration are excluded as V4.0 scope;
- source-tree doctor, `v3_release`, `v3_current`, and separate `v4_prep`
  validation pass;
- public wording remains bounded by this release packet.

## Requirements Satisfied Before Tag

- Completed V3 current-scope completion gate.
- Completed V3 completion review consensus.
- Completed V3 source-tree doctor and test-matrix gates.
- Completed V3 release packet polish.
- Updated `VERSION` from `v3.0` to `v3.0.1`.
- Updated editable metadata from `3.0.0` to `3.0.1`.
- Preserved the existing `v3.0` tag and published v3.0.1 as a new patch tag.
- Saved final publication authorization in the user request on 2026-06-18.

## Tag Commands

The release action uses:

```bash
git tag -a v3.0.1 -m "Release RTDL v3.0.1"
git push origin main
git push origin v3.0.1
```

## Boundary

This file records the tag procedure. It does not widen the V3.0 claim scope
beyond [Public Wording Boundaries](public_wording_boundaries.md).
