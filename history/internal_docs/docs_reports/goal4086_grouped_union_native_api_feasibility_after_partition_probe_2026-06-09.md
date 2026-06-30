# Goal4086 Grouped-Union Native API Feasibility After Partition Probe

Date: 2026-06-09

## Verdict

`accept-with-boundary`

Goal4086 inspects the current OptiX grouped-union native surface after the
Goal4085 partition-summary build probe. The conclusion is precise: the current
API cannot become a fast partition-aware route through a thin wrapper. A real
performance step requires a new generic native/runtime entry point that consumes
partition work streams or produces the necessary partition metadata cheaply.

## Evidence Chain

| Evidence | Result |
| --- | --- |
| Goal4079 | Current grouped-union route still visits tens to hundreds of millions of candidate hits and performs roughly two root reads per candidate. |
| Goal4080 | External reviewers accepted the direction: reduce candidate/root work with a generic fixed-radius grouped-union primitive, not app-specific DBSCAN logic. |
| Goal4084 | Acceptance bars now require at least 50% lower candidate hits or root calls on claimed rows, no material `ngsim_dense_65536` regression, and measured partition-build overhead. |
| Goal4085 | Current CuPy partition-summary preview build cost is too high for a naive route: 0.219861s clustered, 0.201510s road, 0.367637s ngsim at 65K before union or ambiguous traversal. |

## Current Native Surface

The current OptiX grouped-union ABI exposes these useful but insufficient
shapes:

- all-item self query:
  `rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs...`
- contiguous self query ranges:
  `rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_range_device_outputs...`
- external query buffers with a contiguous `query_index_offset`:
  `rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_device_outputs...`

The kernel parameter block contains:

- prepared traversable handle;
- query/search point columns;
- optional predicate flags;
- parent and fallback workspaces;
- telemetry;
- `query_count`;
- `query_index_offset`;
- `item_count`;
- execution booleans for all-predicate, same-root culling, and direct side
  effect;
- radius and trace range.

It does not contain partition ids, partition offsets, partition-pair ranges,
safe-full/ambiguous streams, or precomputed partition AABBs/counts.

## Feasibility Finding

Contiguous query-range blocking is not enough. It changes launch shape, but it
does not reduce the search region each ray traverses, does not feed safe-full
partition unions directly, and does not avoid the same-root root-read storm
shown by Goal4079. Goal4074 already measured the blocked grouped-stream mode and
found it slower than the recommended unblocked route.

The current partition preview contains the right semantic signal, but Goal4085
shows that building the complete visible partition-pair table in CuPy is more
expensive than the current production route on the important 65K clustered and
road rows. Therefore the next native candidate must avoid full partition-pair
materialization on the critical path or amortize it across repeated runs.

## Required New Generic Contract

The next implementable candidate remains:

`prepared_fixed_radius_partition_convergence_grouped_union_3d`

It should be a generic runtime primitive, not an app-specific route. The minimum
contract should include:

1. prepared point storage and radius/max-radius metadata;
2. device-resident partition summary columns, either provided by a prepared
   handle or produced by a cheaper native/device producer;
3. compact streams for safe-full partition work and ambiguous boundary work;
4. safe-full grouped union without point-pair materialization;
5. exact RT traversal only for ambiguous partition work;
6. component parent/signature outputs compatible with the existing grouped-union
   continuation;
7. telemetry for partition-build time, partition counts, safe-full work,
   ambiguous traversal hits, candidate hits, root calls, parent-link steps,
   overflow, and completeness.

## Recommended Implementation Shape

The next code step should not modify the accepted default route. It should build
a candidate-only primitive behind explicit naming and fail-closed metadata:

1. **Prepared summary handle path:** support repeated-run amortization first,
   because Goal4085 proves one-shot build cost is too high.
2. **Native summary producer experiment:** prototype a cheaper producer that
   emits only safe-full and ambiguous work streams, not a complete visible pair
   table.
3. **Ambiguous-only RT path:** add a launch shape that can restrict traversal to
   ambiguous partition work; reusing only `query_start/query_count` is
   insufficient.
4. **Promotion gate:** require Goal4084 bars plus Goal4085 build-cost
   accounting before any default-route or public-performance wording.

## App-Agnostic Boundary

Allowed native/runtime vocabulary: fixed-radius, partition, summary, pair,
safe-full, ambiguous, grouped-union, component, root, parent, candidate, AABB,
traversal, stream, prepared.

Forbidden native/runtime vocabulary: DBSCAN, cluster, epsilon, min-points, road,
trajectory, benchmark app names, or hidden app-specific dispatch.

## Boundary

This report does not add a native ABI, promote a candidate, change default
routing, authorize release wording, public speedup wording, broad RT-core
wording, whole-app acceleration wording, paper-reproduction wording, true
zero-copy wording, automatic partner selection, or app-specific native-engine logic.
