# Goal3783 v2.10 HIPRT Parity Closeout Packet

Status: implemented and clean-pod validated on the NVIDIA CUDA/Orochi HIPRT
route.

## Purpose

Goal3783 closes the current v2.10 AMD/HIPRT parity-planning burst after
Goals3763-3782. The packet has one job: make the current position auditable
without overclaiming. The implementation work is real on the NVIDIA CUDA/Orochi
HIPRT route, but this is not AMD hardware evidence and does not authorize AMD
performance wording.

## Current Position

The current v2.10 HIPRT parity map reports 10 / 10 promoted benchmark apps at
`ready_for_amd_functional_pod`:

| app | parity stage | remaining generic HIPRT contract gaps |
| --- | --- | --- |
| `hausdorff_xhd` | `ready_for_amd_functional_pod` | none |
| `spatial_rayjoin` | `ready_for_amd_functional_pod` | none |
| `rt_dbscan` | `ready_for_amd_functional_pod` | none |
| `robot_collision` | `ready_for_amd_functional_pod` | none |
| `contact_manifold` | `ready_for_amd_functional_pod` | none |
| `raydb_style` | `ready_for_amd_functional_pod` | none |
| `barnes_hut` | `ready_for_amd_functional_pod` | none |
| `librts_spatial_index` | `ready_for_amd_functional_pod` | none |
| `rtnn` | `ready_for_amd_functional_pod` | none |
| `triangle_counting` | `ready_for_amd_functional_pod` | none |

The latest parity version is:

`rtdl.v2_10.amd_hiprt_benchmark_parity_after_goal3782.v1`

## Evidence Included

The packet requires A5000/Orochi artifacts for the HIPRT implementation chain,
and the closeout sweep records the current evidence artifact:

`docs/reports/goal3783_v2_10_hiprt_parity_closeout_a5000.json`

The clean-pod closeout evidence records:

- SSH target used: `root@69.30.85.203 -p 22057`.
- GPU/driver: `NVIDIA RTX A5000, 580.126.09`.
- HIPRT SDK: `/root/vendor/hiprt-official/hiprtSdk-2.2.0e68f54`.
- Clean workdir: `/root/rtdl_goal3783_clean_1780855862`.
- Pod log: `/root/goal3783_clean_1780855862.log`.
- Source commit: `e3d4acbc70e80cdf166185bb390ab7a10a3f34bd`.
- Build command:
  `make build-hiprt HIPRT_PREFIX=/root/vendor/hiprt-official/hiprtSdk-2.2.0e68f54`.
- Runtime library:
  `/root/rtdl_goal3783_clean_1780855862/build/librtdl_hiprt.so`.
- Focused pod validation: 22 HIPRT parity modules, `Ran 138 tests in 13.999s`,
  `OK (skipped=1)`.
- Scoped source dirty check: `false`.
- Claim-boundary flags: all `false`.

The packet also requires the earlier per-goal A5000/Orochi artifacts:

- Goal3763 context/build smoke
- Goal3764 robot-collision HIPRT route smoke
- Goal3765 prepared grouped visibility flags
- Goal3766 prepared segment-pair exact count
- Goal3767 prepared shape-pair active count
- Goal3768 fixed-radius threshold count
- Goal3769 fixed-radius grouped stream flags
- Goal3770 prepared AABB index count
- Goal3771 fixed-radius ranked aggregate
- Goal3772 fixed-radius ranked batch sweep
- Goal3773 point-group nearest witness
- Goal3774 point-group nearest output columns
- Goal3775 ray/triangle closest hit 3D
- Goal3776 collect-k bounded i64
- Goal3777 aggregate-frontier collect
- Goal3779 grouped i64 count/sum
- Goal3780 grouped vector sum f64x2
- Goal3781 columnar i64 predicate scan
- Goal3782 graph-cycle scalar count

## Boundary

This packet does not authorize release, AMD performance claims, HIPRT release
claims, public speedup wording, broad RT-core wording, whole-app acceleration
wording, paper-reproduction claims, zero-copy claims, or app-specific native
engine logic. It only says that the NVIDIA CUDA/Orochi HIPRT implementation path
has the app-agnostic generic contracts needed before an AMD functional pod run.

## Validation

Local focused validation target:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3783_v2_10_hiprt_parity_closeout_packet_test tests.goal3753_amd_hiprt_benchmark_parity_plan_test tests.goal3782_hiprt_graph_cycle_count_test
```

Clean pod validation has built HIPRT from a clean checkout, run the HIPRT
focused sweep, and written:

`docs/reports/goal3783_v2_10_hiprt_parity_closeout_a5000.json`

The broad local closeout slice also passed before the pod sweep:

```text
Ran 138 tests
OK (skipped=28)
```
