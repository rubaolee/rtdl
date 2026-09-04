# Goal5842R1 V3/V4 Pre-Output Failures

Date: 2026-09-04

Source commit: `1e1188b72274f50ede2df3d1d61f88d78dda20ec`

Hardware: NVIDIA RTX A6000, compute capability 8.6, UUID
`GPU-6457d4af-a4bb-bff5-a9d2-02f251ceca27`, driver 550.127.08.

Neither attempt produced an accepted result JSON or an accepted timing row.
Both attempt directories remain on the Pod and were not reused.

## V3

The remote shell command omitted `PYTHONPATH=src:.`. Python failed while
importing `experiments` before constructing a target or touching the GPU. The
process exited normally with `ModuleNotFoundError`.

## V4

The corrected command passed the primary weighted scalar/diagnostic workload
and reached the additional cross-family validation. That validation constructed
an unweighted `TriangleReductionBatch` without its required explicit empty
`query_metadata`. Python raised `TypeError` before preparing or executing that
additional owner. During interpreter cleanup after the uncaught exception, the
process also reported exit status 139; the traceback identifies the preceding
deterministic Python construction error.

The repair is limited to supplying `query_metadata={}` to that public batch
constructor. It does not change the workload, oracle, scalar ABI, cache policy,
native library, or Goal5842 V12 evidence. A later attempt must use a fresh
directory and a new clean Git commit.
