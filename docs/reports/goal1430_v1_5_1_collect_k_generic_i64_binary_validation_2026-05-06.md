# Goal 1430 v1.5.1 COLLECT_K_BOUNDED Generic I64 Binary Validation

## Verdict

The built Embree and OptiX libraries export the app-name-free generic
`COLLECT_K_BOUNDED` i64 collector symbols and pass direct same-ABI smoke
validation.

This closes the built-library symbol-validation gate for the generic i64
collector ABI. It does not authorize stable primitive promotion, speedup,
zero-copy, whole-app claims, broad workload claims, release action, or release
tag movement.

## Embree Evidence

Host:

- Linux validation host: `192.168.1.20`
- Repo: `/home/lestat/work/rtdl_v1_5_linux_check`
- Git HEAD: `217bd991a1a6cefdd581e4faf43d80192c7dae94`
- Library: `build/librtdl_embree.so`

Dynamic symbol:

```text
000000000002da40 T rtdl_embree_collect_k_bounded_i64
```

Direct ctypes same-ABI smoke:

```json
{"status": 0, "emitted": 2, "overflow": 0, "rows": [1, 10, 2, 20], "error": ""}
{"overflow_status": 0, "emitted": 2, "overflow": 1, "rows": [0, 0], "error": ""}
```

## OptiX Evidence

Pod:

- SSH: `root@69.30.85.196 -p 22030 -i C:\Users\Lestat\.ssh\id_ed25519_rtdl_pod_69_30_85_196`
- GPU: NVIDIA RTX A5000
- Repo: `/workspace/rtdl`
- Git HEAD: `217bd991a1a6cefdd581e4faf43d80192c7dae94`
- Library: `build/librtdl_optix.so`
- Rebuild artifact: `docs/reports/goal1430_v1_5_1_collect_k_rebuild_optix_2026-05-06.txt`

Dynamic symbol:

```text
000000000005ead0 T rtdl_optix_collect_k_bounded_i64
```

Direct ctypes same-ABI smoke:

```json
{"status": 0, "emitted": 2, "overflow": 0, "rows": [1, 10, 2, 20], "error": ""}
{"overflow_status": 0, "emitted": 2, "overflow": 1, "rows": [0, 0], "error": ""}
```

## Semantics Checked

- duplicate rows are deduplicated before successful copy
- output rows are lexicographically canonicalized
- `emitted_count_out` reports the complete canonical row count
- insufficient capacity sets `overflowed_out = 1`
- overflow path does not copy partial result rows

## Still Pending

- Production polygon-pair wrappers still route through the Python generic i64
  adapter rather than directly calling these built generic symbols.
- Stable-promotion review remains required before any stable primitive wording.
- No performance, zero-copy, whole-app, broad workload, or release claim is
  authorized by this validation.
