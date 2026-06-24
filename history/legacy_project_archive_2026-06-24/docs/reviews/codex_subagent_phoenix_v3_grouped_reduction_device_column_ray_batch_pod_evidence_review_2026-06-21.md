# Codex Subagent Review: Phoenix V3 Grouped-Reduction Device-Column Ray-Batch POD Evidence

Date: 2026-06-21

Reviewer: Mencius, independent Codex subagent review.

Verdict: approve-with-required-fixes

## Review Basis

Read the requested packet files, the four raw POD evidence JSONs, the
candidate/work-queue notes, the POD evidence test, and the evidence builder
script.

Verification run by reviewer:

```text
py -3 -m unittest tests.v3_phoenix_grouped_reduction_device_column_pod_evidence_test
6 tests OK

py -3 -m unittest tests.v3_phoenix_next_engine_work_queue_test tests.v3_release_wording_gate_test tests.v3_phoenix_release_readiness_gate_test tests.v3_phoenix_grouped_reduction_device_column_pod_evidence_test
17 tests OK
```

## Findings

This is genuinely V3 generic-engine optimization evidence, not RayDB-specific
tuning. The evidence exercises the generic prepared ray-batch device-column ABI
and the generic ray/triangle grouped i64 reduction path. RayDB is acting as the
evidence harness. The claim must remain scoped to prepared `grouped_sum`, not
all RayDB or all grouped reductions.

The comparisons are broadly honest. The packet reports host-packed OptiX versus
device-column OptiX before quoting Embree/OptiX ratios, and the host/device
OptiX comparison uses the same rows, groups, logical ray counts, warmup, repeat,
hardware, and CPU-reference parity. The evidence also makes clear that hot
OptiX query time is essentially unchanged; the win is cold/build/input-path
removal, not a faster RT kernel.

The Embree versus OptiX-device-column ratios are acceptable as same-contract
backend context, but not as a pure backend-only comparison, because Embree
remains host-packed while OptiX uses device columns. The packet wording mostly
handles this correctly and should keep doing so.

The evidence is sufficient to reopen M7 review, but not to promote
automatically. The cold prepare and cold-plus-loop improvements are material:
host-packed/device-column OptiX cold-plus-loop is `3.599x` at 262,144 rows and
`73.586x` at 524,288 rows. CPU reference parity, logical ray counts,
warmup/repeat, and hardware gates are present.

This should become a new exact M7 candidate row, keyed explicitly by
`ray_batch_layout=cupy_device_columns`. It should not silently supersede
`grouped_reduction_sum_scalar_broadcast_repeat100_262144`. The older row can be
retained or later retired/annotated, but replacing it requires explicit
regenerated public wording and review. This should not remain internal-only once
the P0s below are resolved.

## P0 Issues

P0-1: Source provenance gap must be recorded before consensus or promotion.
All raw evidence JSONs report `git_head: fatal: not a git repository...`. A
`source_manifest.sha256` exists, but the top-level packet does not explicitly
document that this manifest is the source traceability record. Before Codex
writes 2-AI consensus, the consensus or packet must bind the row to that
manifest and acknowledge the missing git HEAD, as prior M7 grouped-reduction
review did.

P0-2: Exact row identity and public boundary must be fixed before promotion.
The consensus must define the new exact row id or ids, including
`cupy_device_columns`, generated rows/groups, logical rays, warmup=3,
repeat=100, RTX 4000 Ada pod, and prepared grouped-sum scope. It must also
state that release, whole-app, broad V3-over-V2, true zero-copy, and
all-grouped-reduction claims remain false.

## P1 Issues

P1-1: Tighten phase attribution. The largest 524,288-row cold-prepare speedup
is mostly from `workload_build_sec` collapsing from `142.852s` to `0.105s`,
while `prepared_ray_batch_sec` improves from `2.510s` to `0.305s`. Public
wording should avoid implying the entire `218.248x` cold-prepare win is only
ray-batch preparation.

P1-2: Carry forward the pre-dedup hit-event explanation. Embree and OptiX
pre-dedup hit counts differ, but both match CPU reference after reduction. This
is not a blocker, but the final M7 packet should preserve that explanation.

P1-3: Strengthen tests if this is promoted. The current tests validate packet
self-consistency and thresholds. Add checks that promotion wording documents the
missing git HEAD/source manifest and that any promoted row id includes the
device-column layout.

## Final Recommendation

Approve reopening M7 review after the P0 fixes. Treat this as a new exact
row-scoped device-column prepared grouped-sum candidate, not a broad release
claim and not an implicit replacement of the already approved
host-packed/scalar-broadcast row.
