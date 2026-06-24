# Goal4041 Partition Device Ambiguous Union Timing

Date: 2026-06-08

## Purpose

Goal4041 measures the Goal4040 device ambiguous-partition union path after the
zero-ambiguous skip refinement.

The question is narrow: once a fixed-radius partition summary is already built
and reused, should `ambiguous_union_execution="cupy_partition_points"` replace
the host ambiguous-pair classifier as the default component-label continuation?

The answer from this pod run is no. The device path is useful because it keeps
the ambiguous classification resident and preserves correctness, but it is not
yet a universal speed win. It should remain an optional resident continuation,
not a promoted default route.

Pod evidence was collected from:

`ssh root@213.173.108.27 -p 15138 -i id_ed25519_rtdl_codex`

Git head on the pod:

`42462c3e`

Artifacts:

- `docs/reports/goal4041_partition_device_ambiguous_union_timing_pod.json`
- `docs/reports/goal4041_partition_device_ambiguous_union_timing_pod.stdout.txt`

## Results

`Host / Device Min` greater than `1.0x` means the device ambiguous continuation
was faster for the repeated component-label run over a reused partition summary.

| Profile | Points | Ambiguous Pairs | Host Min (s) | Device Min (s) | Host / Device Min | Device Used | Skip Reason |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| clustered3d_1024 | 1,024 | 16 | 0.001690 | 0.001742 | 0.971x | true | - |
| road3d_1024 | 1,024 | 132 | 0.001845 | 0.001746 | 1.057x | true | - |
| clustered3d_2048 | 2,048 | 0 | 0.002864 | 0.002673 | 1.071x | false | no_ambiguous_partition_pairs |
| road3d_2048 | 2,048 | 257 | 0.003175 | 0.003149 | 1.008x | true | - |
| clustered3d_4096 | 4,096 | 7 | 0.005652 | 0.006225 | 0.908x | true | - |
| road3d_4096 | 4,096 | 497 | 0.006197 | 0.005985 | 1.035x | true | - |
| clustered3d_8192 | 8,192 | 0 | 0.010855 | 0.010473 | 1.036x | false | no_ambiguous_partition_pairs |
| road3d_8192 | 8,192 | 1,017 | 0.011485 | 0.011372 | 1.010x | true | - |

Every row had matching component-size signatures against the host ambiguous
path.

## Interpretation

The refined behavior is better than the first probe:

- rows with no ambiguous partition pairs now skip the device classifier and no
  longer pay the old extra-kernel penalty;
- road-like rows with many ambiguous pairs show small wins or near parity;
- the clustered row with only seven ambiguous pairs still loses because the
  extra device classification launch costs more than the tiny host classifier.

That means this path solves a residency/design problem more than a performance
problem. It gives the fixed-radius component continuation a generic way to keep
ambiguous pair classification on the device, but the current launch structure is
too small-grained to promote it as a default for all inputs.

The next real performance target is a larger fused resident continuation: either
fold safe-full and ambiguous classification into one device component-label pass,
or move this into a prepared native/partner route where the device classifier is
amortized over many requests. More Python-side toggling is not the main route to
large gains.

## Boundary

This artifact is internal subpath timing for host versus device ambiguous
partition-union continuation. It does not promote `partition_convergence_hybrid`,
authorize public speedup wording, authorize broad RT-core wording, authorize
whole-app benchmark wording, authorize release wording, authorize hidden dispatch
or automatic partner selection, authorize app-specific native-engine logic,
authorize a native ABI addition, or authorize true-zero-copy wording.

