# RTDL v0.1 Archived Baseline

Date: 2026-04-05
Status: archived baseline

## Frozen baseline

RTDL v0.1 is frozen at:

- tag: `v0.1.0`
- tag object: `d82a2c28201ed43cddb3da62ba093d6118a2c84f`
- target commit: `85fcd90a7462ef01137426af7b0224e7da518eb4`
- short target commit: `85fcd90`

This is the stable baseline users should use when they specifically want the
reviewed v0.1 release rather than the evolving v0.2 branch.

## What v0.1 is

RTDL v0.1 is the first bounded, reviewed release slice of the project.

It provides:

- the reviewed RayJoin-centered workload slice
- the accepted bounded package as the trust anchor
- Embree and OptiX as the mature high-performance backends on the accepted
  flagship surface
- Vulkan as the supported parity-clean but slower portable backend

## How to use it

Check out the archived baseline:

```bash
git checkout v0.1.0
```

Or pin directly to the frozen commit:

```bash
git checkout 85fcd90a7462ef01137426af7b0224e7da518eb4
```

## Canonical v0.1 release reports

From the archived baseline, read:

- [v0.1 release-report index](../../release_reports/v0_1/README.md)
- [release statement](../../release_reports/v0_1/release_statement.md)
- [work report](../../release_reports/v0_1/work_report.md)
- [audit report](../../release_reports/v0_1/audit_report.md)
- [final readiness check](../../release_reports/v0_1/final_readiness_check.md)

## Important note

The live `main` branch may continue to accumulate v0.2 planning and
implementation work.

Users who need the stable v0.1 baseline should prefer:

- tag `v0.1.0`

over whichever commit happens to be current on `main`.
