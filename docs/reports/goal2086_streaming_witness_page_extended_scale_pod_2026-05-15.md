# Goal2086 Streaming Witness Page Extended Scale Pod Evidence

Date: 2026-05-15

Pod:

- SSH: `root@213.192.2.122 -p 40153`
- Key that authenticated: `C:/Users/Lestat/.ssh/id_ed25519_rtdl_codex_current_pod`
- GPU: NVIDIA GeForce RTX 3090, driver 580.126.20, 24576 MiB
- Commit base: `2efd4b84e8ac8e0f15c6dc32884e49e0dec6d669`
- Goal2081 overlay files were present in `/root/rtdl_goal2081`.

## Purpose

Goal2083 established that the `segment_polygon_anyhit_rows` weak row was an output-contract problem: the old v2 path materialized full Python witness rows, while the Goal2081 path keeps exact witness IDs in partner-owned device columns.

Goal2086 extends that evidence to larger row counts on the same pod. The goal is not a new release claim; it is a scale sanity check for the bounded streaming witness-column contract.

## Results

| count | v1.8 native OptiX rows sec | old v2 full Python rows sec | new v2 streaming witness columns sec | old v2 / v1.8 | new v2 / v1.8 | new v2 / old v2 | emitted candidates | exact witnesses | overflow |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 32768 | 0.146499 | 0.996326 | 0.001353 | 6.801x | 0.009x | 0.001x | 97664 | 32768 | false |
| 65536 | 0.346873 | 2.055555 | 0.001355 | 5.926x | 0.004x | 0.001x | 202188 | 65536 | false |

Artifacts:

- `docs/reports/goal2086_streaming_witness_page_extended_pod/goal2081_streaming_witness_page_perf_pod_32768_cupy_capacity262144.json`
- `docs/reports/goal2086_streaming_witness_page_extended_pod/goal2081_streaming_witness_page_perf_pod_65536_cupy_capacity524288.json`
- `docs/reports/goal2086_streaming_witness_page_extended_pod/run_32768.console.log`
- `docs/reports/goal2086_streaming_witness_page_extended_pod/run_65536.console.log`
- `docs/reports/goal2086_streaming_witness_page_extended_pod/progress.log`

## Interpretation

The larger run strengthens the Goal2083 diagnosis.

At 32768 and 65536 rows, the old v2 full-Python-row path is slower than v1.8 by roughly 5.9x to 6.8x. That is the bad contract: it crosses the Python object boundary for witness rows.

The streaming path does not cross that boundary. It emits generic native candidate witness pairs, runs the exact app-layer CuPy filter, and keeps the exact witness result as device columns. Its steady-state median stays near 1.35 ms at both scales, with no overflow and exact witness counts preserved.

The first iteration can include setup and warmup cost. The JSON artifacts retain min/median/max, so later reports should distinguish warmup from steady-state instead of treating the max as the per-query contract.

## Boundary

This evidence supports the v2 output-contract direction:

- Native engine contract: generic ray/primitive candidate witness pairs.
- Partner/app contract: exact filter and bounded witness page in partner-owned device columns.
- No claim that the old full Python row contract is fast.
- No v2.0 release authorization.
- No broad whole-app speedup authorization without final release consensus.
