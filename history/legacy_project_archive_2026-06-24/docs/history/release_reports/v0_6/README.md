# RTDL v0.6 Release Package

- [Release Statement](release_statement.md)
- [Support Matrix](support_matrix.md)
- [Audit Report](audit_report.md)
- [Tag Preparation](tag_preparation.md)

These documents are the canonical release-facing package for the corrected RT
graph line.

Current honesty boundary:

- package released as `v0.6.1`
- this is the corrected RTDL-kernel graph line, not the earlier mis-scoped
  historical `v0.6.0` line
- Linux is the primary correctness/performance validation platform
- Windows is part of the bounded validation story, especially for Embree
- OptiX results in the main Linux benchmark report are non-RT-core baselines
  because the benchmark GPU was a GTX 1070
