# Goal 1428 v1.5.1 COLLECT_K_BOUNDED Adapter Parity Rerun

## Verdict

Post-adapter polygon-pair parity is accepted for Embree and still pending for
OptiX.

This is not a stable promotion, not built generic i64 symbol validation, not a
speedup claim, not a zero-copy claim, not a whole-app claim, and not a release
action.

## Accepted Evidence

Windows optional rerun:

- Artifact:
  `docs/reports/goal1428_v1_5_1_collect_k_adapter_parity_windows_optional_2026-05-06.md`
- Git HEAD: `0bea4a23a6e105a5baca6ad2f8730eb7566d071d`
- Result: accepted
- Embree: pass=4, fail=0, skipped=0
- OptiX: pass=0, fail=0, skipped=4
- OptiX skip reason: `librtdl_optix not found`

Linux required-Embree rerun on `192.168.1.20`:

- Artifact:
  `docs/reports/goal1428_v1_5_1_collect_k_adapter_parity_linux_embree_2026-05-06.md`
- Git HEAD: `0bea4a23a6e105a5baca6ad2f8730eb7566d071d`
- Result: accepted
- Embree: pass=4, fail=0, skipped=0
- Required backend skips: none

## Not Accepted

Linux required-OptiX rerun on `192.168.1.20`:

- Artifact:
  `docs/reports/goal1428_v1_5_1_collect_k_adapter_parity_linux_optix_2026-05-06.md`
- Git HEAD: `0bea4a23a6e105a5baca6ad2f8730eb7566d071d`
- Result: not accepted
- OptiX: pass=0, fail=0, skipped=4
- Exact blocker: `librtdl_optix not found. Build it with 'make build-optix' or set RTDL_OPTIX_LIB=/path/to/lib.`

The previously used NVIDIA pod endpoint
`root@213.173.102.217 -p 25443 -i Z:\rtdl-dev\id_ed25519_rtdl_codex`
was checked and returned `Connection refused`, so no fresh post-adapter OptiX
pod parity evidence was collected in this step.

## Next Fixes

- Start or provide a reachable NVIDIA/OptiX environment.
- Build or expose `librtdl_optix`.
- Rerun:

```sh
PYTHONPATH=src:. python3 scripts/goal1416_v1_5_1_collect_k_native_parity.py --backend optix --require-backend optix --json-out docs/reports/goal1428_v1_5_1_collect_k_adapter_parity_optix_required_2026-05-06.json --markdown-out docs/reports/goal1428_v1_5_1_collect_k_adapter_parity_optix_required_2026-05-06.md
```

- Only after required OptiX passes should the remaining adapter parity work be
  marked complete.
