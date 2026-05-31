# Goal2847 Current-Head Canonical Harness Refresh

Date: 2026-05-31

Verdict: **accept-with-boundary**

This goal reran the seven canonical v2.5 harnesses on the live RTX pod after
Goal2843 and Goal2845, using current `main` at:

`23b047e5d44bfda7e535ca7ba78d94f195e2be86`

All artifacts report `source_dirty: []`, `status: pass`, and GPU
`NVIDIA RTX A5000, 570.211.01`.

This is **not a v2.5 release authorization** and not a public speedup claim. It
is a current-head health refresh showing that the canonical benchmark packet
still runs cleanly after the execution-path policy and readiness refresh.

## Artifact Set

Artifacts are stored under:

`docs/reports/goal2847_current_head_canonical_harness_pod/`

| Harness | App / surface | Status | Boundary |
| --- | --- | --- | --- |
| `goal2797_triangle_counting.json` | triangle counting | pass | canonical app harness only |
| `goal2798_librts.json` | LibRTS predicates | pass | no partner/RT public claim |
| `goal2799_spatial_rayjoin.json` | spatial RayJoin count/parity primitives | pass | prepared OptiX count path, not full RayJoin reproduction |
| `goal2800_rtnn.json` | RTNN ranked-summary aggregate | pass | mixed vs CuPy by distribution |
| `goal2801_hausdorff_xhd.json` | exact Hausdorff X-HD-inspired entrypoint | pass | RTDL uses RT cores but remains slower than optimized CuPy grid |
| `goal2802_rt_dbscan.json` | RT-DBSCAN grouped stream continuation | pass | strong grouped-stream evidence, no paper reproduction claim |
| `goal2803_barnes_hut.json` | Barnes-Hut membership and partner vector sum | pass | RT membership win, Triton vector path not promoted |
| `goal2847_summary.json` | packet summary | all pass | summarizes the seven harnesses |

## Key Measurements

### Spatial RayJoin

Goal2799 used prepared OptiX RT count/parity paths. All three rows matched CPU
reference:

| Workload | Observed count | Prepared query median |
| --- | ---: | ---: |
| `pip` | 6 | 0.130922 ms |
| `lsi` | 1 | 0.142855 ms |
| `overlay_seed` | 0 | 0.006891 ms |

This remains evidence for generic point/shape, segment-pair, and shape-pair
count contracts, not for complete RayJoin paper reproduction.

### RTNN

Goal2800 stayed exact against the CuPy grid same-contract opponent, but the
performance signal is distribution-dependent:

| Distribution | RTDL median | CuPy grid median | CuPy / RTDL ratio |
| --- | ---: | ---: | ---: |
| `uniform` | 0.000095849 s | 0.000084213 s | 0.879x |
| `clustered` | 0.004747057 s | 0.011967996 s | 2.521x |
| `shell` | 0.000133681 s | 0.000275903 s | 2.064x |

RTNN remains distribution-dependent: clustered and shell favor the RTDL prepared
aggregate path, while uniform is slightly slower than the CuPy grid opponent.
The artifact keeps `rtdl_beats_cupy_grid_claim_authorized: false`.

### Hausdorff

Goal2801 confirmed exactness and RT-core use, but the current RTDL path is not
the fastest exact implementation in this packet:

| Path | Median |
| --- | ---: |
| Optimized CuPy grouped grid rawkernel | 0.004484454 s |
| RTDL OptiX grouped adaptive nearest witness | 0.073494629 s |
| RTDL / CuPy ratio | 16.389x slower |

Hausdorff remains slower than the optimized CuPy baseline. The useful boundary
is still architectural: RTDL can express the RT-core nearest-witness path, but
the current v2.5 implementation is not authorized to claim it beats the CUDA
grid baseline.

### RT-DBSCAN

Goal2802 is the strongest current-head grouped stream signal:

| Points | Grouped stream speedup vs prepared CuPy grid |
| ---: | ---: |
| 32,768 | 3.697x |
| 65,536 | 4.857x |
| 131,072 | 4.677x |

The grouped stream path avoids materializing neighbor rows or the full directed
adjacency stream and reports RT-core acceleration.

### Barnes-Hut

Goal2803 confirmed that OptiX membership has a large subpath win over Embree as
problem size grows:

| Bodies | OptiX total speedup vs Embree | OptiX membership speedup vs Embree |
| ---: | ---: | ---: |
| 512 | 1.204x | 8.059x |
| 2,048 | 1.520x | 24.089x |
| 8,192 | 4.994x | 153.447x |

The partner vector-sum probe matched Torch, but Triton remained slower:
`triton_over_torch_ratio = 3.377x`. Therefore Triton auto-selection remains
disabled for this path.

Barnes-Hut needs better progress logging: the 8,192-body case spent about
342 seconds inside a quiet CPU-heavy comparison window before printing its
completion line. That is acceptable for this evidence run, but future pod
harnesses should log per-repeat progress or add bounded sub-step timeouts.

## Claim Boundary

Every artifact keeps the release/public claim keys fail-closed. In particular:

- no whole-app speedup claim is authorized,
- no paper reproduction claim is authorized,
- no broad public speedup claim is authorized,
- Hausdorff does not claim to beat the optimized CuPy grid baseline,
- RTNN does not claim to beat CuPy generally,
- Barnes-Hut does not promote Triton vector sum auto-selection.

## Conclusion

Goal2847 accepts the current-head canonical v2.5 harness refresh as clean
evidence that the seven-harness packet still executes on the RTX A5000 pod at
the post-Goal2845 head. The boundary remains important: this packet supports
continued v2.5 development and readiness tracking, but it is not final release
consensus and it does not authorize public performance claims beyond the exact
subpaths stated above.
