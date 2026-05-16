# Goal2128 Public Hausdorff Linux GTX 1070 Smoke Perf

Date: 2026-05-16

Status: local Linux public-data smoke complete.

## Boundary

This is public-data performance evidence for the Goal2126 harness on local Linux, but it is not final RTX release evidence:

- GPU: `NVIDIA GeForce GTX 1070, 580.126.09`
- Host: `192.168.1.20`
- Commit: `d2c427482320f23647d0f49d0e03d90d00593902`
- RTDL library: locally built `build/librtdl_optix.so`
- Dataset: Stanford Dragon and Happy Buddha public PLY reconstructions.
- Geometry scope: exact 2D point-set Hausdorff on deterministic XY projections of public 3D vertices.
- Not claimed: exact X-HD paper dataset reproduction, 3D surface Hausdorff, RTX RT-core speedup, or release speedup.

The GTX 1070 has no dedicated RT cores. These numbers are useful for correctness, shape, and crossover smoke; they should be rerun on an RTX pod for the public performance claim.

## Results

Lower ratio is better for RTDL. `speedup` is `CuPy seconds / RTDL seconds`.

| case | sample count | CuPy exact sec | RTDL/OptiX grouped-reduced sec | RTDL/CuPy ratio | speedup | parity |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Dragon XY shifted | 8,192 | 0.294197 | 0.897467 | 3.051x | 0.328x | pass |
| Dragon vs Happy XY | 8,192 | 0.020475 | 0.043825 | 2.140x | 0.467x | pass |
| Dragon XY shifted | 32,768 | 0.667625 | 1.069306 | 1.602x | 0.624x | pass |
| Dragon vs Happy XY | 32,768 | 0.405151 | 0.219583 | 0.542x | 1.845x | pass |
| Dragon XY shifted | 65,536 | 1.602876 | 1.392199 | 0.869x | 1.151x | pass |
| Dragon vs Happy XY | 65,536 | 1.322117 | 0.539805 | 0.408x | 2.449x | pass |
| Dragon XY shifted | 131,072 | 5.303005 | 2.422468 | 0.457x | 2.189x | pass |
| Dragon vs Happy XY | 131,072 | 4.875430 | 1.559226 | 0.320x | 3.127x | pass |

Artifacts:

- `docs/reports/goal2126_public_linux_gtx1070/public_hd_8192.json`
- `docs/reports/goal2126_public_linux_gtx1070/public_hd_32768.json`
- `docs/reports/goal2126_public_linux_gtx1070/public_hd_65536.json`
- `docs/reports/goal2126_public_linux_gtx1070/public_hd_131072.json`

## Interpretation

The public-data curve matches the synthetic lesson from Goal2123:

- Small cases are dominated by setup, packing, and OptiX launch/AS overhead.
- As `n` grows, the dense CuPy all-pairs baseline scales toward `O(n^2)`, while the RTDL grouped-bound path asks OptiX to traverse group boxes and scan only the candidate groups that survive those bounds.
- The public Dragon-vs-Happy projected case crosses over earlier than the shifted-copy case because its group bounds prune more effectively.
- The shifted-copy case is intentionally harder because the two point sets are almost identical after a small translation, so many nearby groups remain plausible candidates.

Even on GTX 1070, RTDL/OptiX becomes faster by 65,536 projected points for both public cases and reaches 2.19x to 3.13x speedup at 131,072. This does not prove RTX RT-core speedup, but it is a good sign that the grouped-reduced design is doing real pruning and avoiding row materialization on public geometry.

## Next Required Run

Run the same harness on an RTX pod:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY="$PWD/build/librtdl_optix.so" \
python3 scripts/goal2126_public_hausdorff_dataset_perf.py \
  --sample-count 131072 \
  --json-out docs/reports/goal2126_public_pod_rtx/public_hd_131072.json
```

Recommended pod sweep:

- `--sample-count 131072`
- `--sample-count 262144`
- `--sample-count 524288`

Use progress logging and timeouts. Do not claim exact X-HD paper dataset reproduction or 3D surface Hausdorff from this 2D-projection harness.
