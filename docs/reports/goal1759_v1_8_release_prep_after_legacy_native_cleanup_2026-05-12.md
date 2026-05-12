# Goal1759 v1.8 Release Prep After Legacy Native Cleanup

Date: 2026-05-12

## Verdict

`v1_8_release_prep_ready_for_fresh_external_review`

The v1.8 source-tree Python+RTDL release candidate is now prepared for a fresh
external review pass after Goal1758 removed the remaining known older
multi-backend app-shaped native support symbols from the source/ABI boundary.

This note does not authorize a tag, version bump, package upload, push, or
public release.

## What Is Now Solved

- The tracked native ABI app-shaped families from Goals1668-1705 remain
  migrated or quarantined.
- Goal1758 removed the older Apple RT / HIPRT / Oracle / Vulkan
  `lsi`, `overlay`, and `triangle_probe` native support symbols and internal
  native source vocabulary.
- Python compatibility names remain at the runtime/API layer where they belong;
  they now bind to generic native engine exports.
- The v1.8 release packet, decision-status note, and commit-ready inventory now
  include Goal1758 as part of the evidence chain.

## Current Release Interpretation

The candidate supports this bounded engineering statement:

```text
The v1.8 source-tree Python+RTDL candidate has an app-agnostic native
source/ABI boundary for the tracked release surface, with Python retaining
application semantics and RTDL retaining generic RT-shaped runtime/kernel
responsibilities.
```

The candidate does not support package-install, broad speedup,
whole-application acceleration, universal backend, Python+partner+RTDL,
PyTorch/CuPy, or true zero-copy claims.

## Required Before Release Action

1. Fresh Claude review of the updated Goal1742 / Goal1750 / Goal1758 / Goal1759
   release-prep chain. Completed in Goal1760.
2. Fresh Gemini review of the same updated release-prep chain.
   Completed in Goal1761.
3. Focused v1.8 gate re-run after review files land. Completed before
   Goal1762.
4. Final v1.8 consensus/decision note if Codex, Claude, and Gemini agree.
   Completed in Goal1762.
5. Explicit user authorization before any `VERSION` bump, tag, push, or release
   operation. Still required.

## Protected Files

Do not stage or publish local/protected files:

- `docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz`
- `id_ed25519_rtdl_codex`
- `rtdl_v0_4.tar.gz`
- `scratch/`

## Boundary

Goal1758 removes the known source/ABI blocker for the generic-engine v1.8
claim. Full backend hardware/toolchain validation for frozen proof surfaces
such as HIPRT, Vulkan, and Apple RT remains platform-specific evidence and is
not converted into a universal backend support claim here.
