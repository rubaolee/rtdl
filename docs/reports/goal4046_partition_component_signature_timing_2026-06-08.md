# Goal4046 Partition Component Signature Timing

Date: 2026-06-08

## Purpose

Goal4046 measures the Goal4045 component-size-signature continuation against
the full component-label continuation over the same reused
`partition_convergence_hybrid` summary.

This is a generic contract comparison:

- full labels return one component label per point;
- signature-only returns sorted component sizes.

For benchmark paths that only need a component-size signature, full compact
labels are unnecessary materialization. Goal4046 tests whether the narrower
generic output contract helps.

Pod evidence was collected from:

`ssh root@213.173.108.27 -p 15138 -i id_ed25519_rtdl_codex`

Git head on the pod:

`0c2da426`

Artifacts:

- `docs/reports/goal4046_partition_component_signature_timing_pod.json`
- `docs/reports/goal4046_partition_component_signature_timing_pod.stdout.txt`

## Results

`Labels / Signature Min` greater than `1.0x` means signature-only is faster.

| Profile | Points | Components | Ambiguous Pairs | Labels Min (s) | Signature Min (s) | Labels / Signature Min |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| clustered3d_1024 | 1,024 | 5 | 16 | 0.001709 | 0.001366 | 1.251x |
| road3d_1024 | 1,024 | 1 | 132 | 0.001718 | 0.001350 | 1.272x |
| clustered3d_2048 | 2,048 | 4 | 0 | 0.002651 | 0.001411 | 1.879x |
| road3d_2048 | 2,048 | 1 | 257 | 0.003033 | 0.001877 | 1.616x |
| clustered3d_4096 | 4,096 | 5 | 7 | 0.005853 | 0.003205 | 1.826x |
| road3d_4096 | 4,096 | 1 | 497 | 0.005754 | 0.003207 | 1.794x |
| clustered3d_8192 | 8,192 | 4 | 0 | 0.010294 | 0.004283 | 2.404x |
| road3d_8192 | 8,192 | 1 | 1,017 | 0.011255 | 0.005625 | 2.001x |

Every row matched the full-label component-size signature.

## Interpretation

This is the first positive partition-convergence follow-up after Goal4041:
signature-only wins on all eight rows because it avoids full host compact-label
materialization when the consumer only needs a summary.

This does not promote `partition_convergence_hybrid` as the default
RT-DBSCAN-style route. The current grouped-stream route still remains the
promoted benchmark path. But Goal4046 does prove that a narrower, generic output
contract can turn part of the partition line into useful performance, which is
exactly the language/runtime lesson:

Expose the smallest generic output contract the user actually needs.

## Boundary

This is internal subpath timing for signature-only versus full component-label
materialization over the partition-convergence candidate. It does not promote
`partition_convergence_hybrid`, authorize release action, authorize public
speedup wording, authorize broad RT-core wording, authorize whole-app benchmark
wording, authorize hidden dispatch, authorize automatic partner selection,
authorize app-specific native-engine logic, authorize a native ABI addition, or
authorize true-zero-copy wording.

