# Goal591 External Review

Date: 2026-04-19

Reviewer: Claude (claude-sonnet-4-6)

Verdict: **ACCEPT**

## Reviewed Files

- `README.md`
- `docs/backend_maturity.md`
- `docs/release_reports/v0_9/support_matrix.md`
- `docs/reports/goal591_post_goal590_release_state_audit_2026-04-19.md`

## What Was Checked

**Internal consistency.** The three native Apple RT slices (3D `ray_triangle_closest_hit`, 3D `ray_triangle_hit_count`, 2D `segment_intersection`) are named consistently across the README "Version Status At A Glance" section, the v0.9 support matrix post-v0.9.1 addendum, `backend_maturity.md`, and the README "Backend Names In Plain English" block. No drift found between documents.

**Honesty of claims.** `backend_maturity.md` explicitly separates implemented / correctness-validated / optimized, names Embree as the only backend currently called optimized, and publishes the Apple M4 Embree-vs-Apple-RT comparison (e.g., hit-count ~1664x slower). No speedup claim is made anywhere. The `cpu_reference_compat` / `native_mps_rt` dispatch distinction is correctly documented and the `native_only=True` escape hatch is noted.

**v0.9 support matrix addendum.** Goals 582, 583, and 590 are all listed correctly. Frozen v0.9.1 release scope is not retroactively widened; post-release work appears only as a labeled mainline addendum.

**Test evidence.** Audit reports 239/239 tests OK and 9/9 Apple RT gate tests OK. Whitespace check reported clean. No conflict with file content reviewed.

**Adaptive engine.** `backend_maturity.md` explicitly parks the adaptive engine as WIP not release evidence. README and support matrix do not cite it.

## One Inconsistency (Non-Blocking)

`README.md` "Current Release State" section contains the bullet:

```
Current release:

- `v0.9.0`
```

The same section's sub-bullet and the rest of the README (intro paragraph, "Version Status At A Glance", "What RTDL Contains") consistently state that `v0.9.1` is the current released version. The stale `v0.9.0` bullet is contradicted by its own surrounding context and by `support_matrix.md` line 5 (`Status: v0.9.1 released`). A reader skimming just that header would see a wrong version number.

This is a minor documentation nit, not a substantive claim error. It does not misrepresent any capability, test boundary, or performance result.

## Summary

The post-Goal590 release-facing state is clean, honest, and internally consistent on all substantive dimensions. Documentation claims are bounded, non-claims are explicit, test evidence is present, and frozen release scope is intact. The stale `v0.9.0` bullet in README "Current Release State" is the only inconsistency found; it should be corrected in a follow-on commit but does not block Goal591 closure.
