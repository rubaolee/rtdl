# Phoenix V3 RTDBSCAN M3.4 Focused Pod A/B

Status: `rtdbscan_component_signature_runner_m3_4_pod_ab_collected_not_release`.

- dataset: `clustered3d`
- point counts: `65536, 262144`
- repeat/warmup: `7` / `2`
- samples per variant per scale: `3`
- geomean runner vs legacy: `0.997557675600175`
- geomean runner vs Embree: `2.941644953697829`
- legacy parity recovered: `True`
- material Set-A candidate: `False`

Measurement note: runner elapsed includes measured repeat timing plus
column-signature extraction; legacy elapsed uses the comparable native
call plus signature perf-counter window.

This focused packet does not authorize release, public speedup wording,
broad V3-over-V2 wording, true-zero-copy wording, or all-app rerun.
