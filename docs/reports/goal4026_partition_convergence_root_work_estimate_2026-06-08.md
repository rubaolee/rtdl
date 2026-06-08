# Goal4026 Partition Convergence Root-Work Estimate

Date: 2026-06-08

## Purpose

Goal4026 combines the existing Goal4014 compressed partition-enumeration evidence with Goal4007 grouped-union root-read telemetry.

This is diagnostic only. It is not a timing claim, not a speedup claim, and not a release claim.

## Estimator

For each profile, the estimator keeps the current grouped-union `root_find_invocations` from Goal4007 and estimates a conservative partition-convergence upper bound:

`ambiguous root reads + 2 root reads per safe-full partition pair`.

This intentionally charges each safe-full partition pair some root work rather than pretending safe-full partitions are free. Ambiguous root reads are estimated from the Goal4014 ambiguous-of-near-pair ratio.

## Result

See `docs/reports/goal4026_partition_convergence_root_work_estimate.json`.

The estimate shows a positive root-read reduction opportunity for all three 65,536-point profiles, with clustered3d and road3d above 50% under this conservative model.

## Boundary

This goal does not add a native ABI. It does not make `partition_convergence_hybrid` executable. It does not authorize public speedup wording, RT-core speedup wording, whole-app benchmark wording, release wording, or true zero-copy wording.

