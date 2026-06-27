# Goal 215 Report: v0.4 GPU Re-work Proposal

Date: 2026-04-10
Status: completed

## Result

The repository now has a formal proposal to reopen `v0.4` under a stricter GPU
closure bar.

Main proposal:

- OptiX is mandatory for the new nearest-neighbor workload family
- Vulkan is also mandatory as a runnable/parity-clean backend
- CPU/oracle plus Embree alone are no longer treated as sufficient final
  closure for `v0.4`

## Why this change is proposed

The earlier `v0.4` line closed correctly under a CPU/Embree interpretation, but
that interpretation is too weak if RTDL is judged against one of its central
purposes:

- using GPU RT cores for geometric-query workloads

Under that stronger identity, `fixed_radius_neighbors` and `knn_rows` must
reach GPU backends before `v0.4` can be honestly called complete.

## Proposed new goal ladder

The proposal adds a reopened suffix to the milestone:

1. Goal 215: reopen and freeze the corrected release bar
2. Goal 216: OptiX `fixed_radius_neighbors`
3. Goal 217: OptiX `knn_rows`
4. Goal 218: Vulkan `fixed_radius_neighbors`
5. Goal 219: Vulkan `knn_rows`
6. Goal 220: GPU benchmark/support-matrix refresh
7. Goal 221: final `v0.4` re-audit

## Honest interpretation

This proposal does not claim the GPU work is already done.

It says:

- the earlier `v0.4` closure bar should be treated as insufficient
- the line should be reopened before final release
- OptiX is the first real blocker
- Vulkan correctness/runnability is the second real blocker

## Next step requested

This proposal should now receive `2+` AI review before becoming the canonical
`v0.4` working definition.
