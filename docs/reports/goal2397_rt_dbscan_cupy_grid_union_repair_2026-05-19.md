# Goal2397 RT-DBSCAN CuPy Grid Union Repair

Date: 2026-05-19

Status: implementation repair before clean pod evidence

## Why This Goal Exists

The first A5000 pod attempt exposed a real weakness in the Goal2394 generic
CuPy device-grid component primitive. The host-bucket rows completed, but the
`partner_cupy_grid_components_3d` path timed out on the `clustered3d` 4096-point
row. A smaller probe showed that 1024 points completed, while the old 2048-point
path exceeded a 120-second timeout.

The bottleneck was not a DBSCAN-specific rule. It was the generic radius-graph
component continuation used after candidate discovery.

## Repair

The CuPy raw-kernel component union now uses a monotonic atomic-min root policy:

```text
find_root_readonly(...)
atomicMin(parent + high, low)
```

The previous helper performed path-compression writes while other threads were
also atomically linking roots. Under dense clustered contention, that policy
could become pathological. The new policy keeps parent links monotonically
decreasing and avoids concurrent path-compression writes inside the union
kernel. The union kernel also skips duplicate undirected core edges with:

```text
other <= point
```

This remains app-agnostic: the primitive is still a generic 3-D radius-graph
component labeler, not a DBSCAN native ABI.

## Claim Boundary

This repair is CUDA-core partner work, not RT-core evidence. It improves the fair
CuPy baseline and makes the pod evidence runner practical again. RT-core claims
remain limited to the OptiX prepared-row artifacts until a generic device-output
to device-resident grouped/component continuation exists.

## Next Evidence

After this repair is committed and pushed, the pod runner should be rerun from a
clean checkout so `environment.txt` records the exact source commit used for the
evidence artifacts.
