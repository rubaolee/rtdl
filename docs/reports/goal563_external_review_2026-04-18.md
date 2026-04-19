# Goal 563: v0.9 Documentation Audit — External Review

Date: 2026-04-18

Reviewer: Claude (external gate)

## Verdict

ACCEPT

## Evidence Checked

**Stale wording scan (live grep across public docs and examples):**

No matches for any of the stale-wording patterns (`experimental HIPRT`,
`HIPRT preview`, `HIPRT-preview`, `preview backend`, `only for 3D`,
`one workload only`, `narrow single-workload`) in:

- `README.md`
- `docs/README.md`
- `docs/current_architecture.md`
- `docs/capability_boundaries.md`
- `docs/quick_tutorial.md`
- `docs/release_facing_examples.md`
- `docs/rtdl_feature_guide.md`
- `docs/tutorials/README.md`
- `examples/README.md`
- `examples/rtdl_hiprt_ray_triangle_hitcount.py`
- `docs/release_reports/v0_9/README.md`
- `docs/release_reports/v0_9/support_matrix.md`

The two fixes claimed in the audit report are confirmed present in the live
files: the example file's scope string reads "v0.9 HIPRT candidate
prepared-path example" (not "experimental HIPRT dispatch"), and
`docs/current_architecture.md` contains no `HIPRT-preview` phrase.

**Release-boundary honesty:**

All checked docs consistently state:

- current released version is `v0.8.0`
- HIPRT is an active `v0.9` backend candidate, not a released `v0.9.0` surface
- `run_hiprt` covers the 18-workload Linux HIPRT matrix; `prepare_hiprt` is
  limited to prepared 3D ray/triangle
- HIPRT validation is on Linux NVIDIA/CUDA/Orochi, not AMD GPU
- no RT-core speedup claim for GTX 1070 path
- no HIPRT CPU fallback claimed

`docs/release_reports/v0_9/support_matrix.md` exists, is current, and its
status line reads "active candidate, not released as `v0.9.0`".

**Local link check:**

All v0.9 release-report files referenced in the audit exist on disk. No broken
local links detected in the audited file set.

**Audit scope:**

The 12-file audit scope matches the public-facing + v0.9-specific doc set. No
material omissions found.

## Summary

The Goal 563 documentation audit is sufficient. Stale HIPRT preview wording was
cleaned up, public links are intact, and the v0.9 candidate/release boundary is
honestly represented across all audited files. The audit gate passes.
