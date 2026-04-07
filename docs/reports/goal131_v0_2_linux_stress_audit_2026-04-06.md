# Goal 131 Report: v0.2 Linux Stress Audit

Date: 2026-04-06
Status: accepted

## Summary

Goal 131 pushed the two closed v0.2 workload families beyond the earlier
`x1024` line on the Linux/PostGIS platform:

- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`

Accepted stress rows:

- `x64`
- `x256`
- `x512`
- `x1024`
- `x2048`
- `x4096`

Host:

- `lestat@192.168.1.20`

Artifacts:

- [goal131_v0_2_linux_stress_artifacts_2026-04-06](/Users/rl2025/rtdl_python_only/docs/reports/goal131_v0_2_linux_stress_artifacts_2026-04-06)

## Correctness result

No correctness mismatch was found.

Both workload families stayed parity-clean against PostGIS across:

- `cpu`
- `embree`
- `optix`
- `vulkan`

through the full accepted `x4096` row.

## `segment_polygon_hitcount`

Key rows:

- `x1024`
  - PostGIS `0.311780 s`
  - CPU `0.033339 s`
  - Embree `0.029067 s`
  - OptiX `0.029157 s`
  - Vulkan `0.039540 s`
- `x2048`
  - PostGIS `0.663881 s`
  - CPU `0.076424 s`
  - Embree `0.070444 s`
  - OptiX `0.067085 s`
  - Vulkan `0.075168 s`
- `x4096`
  - PostGIS `1.167043 s`
  - CPU `0.149339 s`
  - Embree `0.133990 s`
  - OptiX `0.135224 s`
  - Vulkan `0.150495 s`

Interpretation:

- large-row competitiveness remains strong through `x4096`
- OptiX is strongest at `x2048`
- Embree is marginally strongest at `x4096`
- Vulkan remains within the accepted “must work, must not be very slow” band
  even though it is not the flagship optimized backend

## `segment_polygon_anyhit_rows`

Key rows:

- `x1024`
  - PostGIS `0.052019 s`
  - CPU `0.034223 s`
  - Embree `0.038180 s`
  - OptiX `0.037047 s`
  - Vulkan `0.028797 s`
- `x2048`
  - PostGIS `0.147442 s`
  - CPU `0.078248 s`
  - Embree `0.070950 s`
  - OptiX `0.071373 s`
  - Vulkan `0.071137 s`
- `x4096`
  - PostGIS `0.419224 s`
  - CPU `0.154114 s`
  - Embree `0.143328 s`
  - OptiX `0.140265 s`
  - Vulkan `0.136616 s`

Interpretation:

- large-row competitiveness also remains strong through `x4096`
- Vulkan becomes the strongest backend at `x1024` and `x4096`
- backend ordering is workload-sensitive; there is no single permanent winner

## Prepared-path note

Prepared-path evidence was intentionally kept at:

- `x64`
- `x256`

That is still enough to confirm the prepared reuse contract where it is
supported:

- `embree`
- `optix`

CPU and Vulkan do not claim prepared reuse support here, and their markdown
rendering correctly remains `n/a`.

## Problems found

No new blocking correctness defect was found.

The remaining non-blocking issues are:

- small-row overhead still matters, especially where PostGIS wins at `x64`
- backend ordering changes by workload and scale
- prepared-path support remains limited to Embree and OptiX

## Final read

Goal 131 strengthens the current v0.2 line.

It shows that both closed workload families:

- remain parity-clean against PostGIS
- scale cleanly through `x4096`
- stay competitively fast on the accepted Linux platform

This still does not prove that every backend is a fully mature RT-core-native
story. It proves that the current v0.2 feature line is operationally strong on
its accepted Linux/PostGIS validation platform.
