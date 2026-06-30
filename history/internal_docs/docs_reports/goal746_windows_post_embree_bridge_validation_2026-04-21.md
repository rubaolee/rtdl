# Goal 746: Windows Post-Embree Bridge Validation

## Verdict

PASS. Windows Codex successfully consumed the shared bridge request and wrote the validation reply back through the bridge. No user relay was required after the read-this-first file was provided.

Source reply:

`/Volumes/192.168.1.20/extra-1/rtdl_codex_bridge/from_windows/GOAL746_WINDOWS_CODEX_VALIDATION_REPLY.md`

Windows reply path:

`Z:\extra-1\rtdl_codex_bridge\from_windows\GOAL746_WINDOWS_CODEX_VALIDATION_REPLY.md`

## Coordination Result

The cross-Codex bridge contract is working:

- Mac/Linux Codex wrote a self-contained request under `to_windows/`.
- Windows Codex read the request from the shared bridge.
- Windows Codex wrote its result under `from_windows/`.
- Windows Codex updated `status/windows_codex_status.md`.
- Windows Codex did not commit or push.

## Commit And Environment

Windows Codex validated:

- repository: `https://github.com/rubaolee/rtdl.git`
- fresh checkout: `C:\Users\Lestat\rtdl_post_embree_validation`
- commit: `52ea183fbd480a5603ceaf001ac6a17f754ad315`
- short commit: `52ea183 Add Windows post-Embree validation handoff`
- host: `Li-1`
- OS: Windows 10 Pro, `Windows-10-10.0.19045-SP0`
- CPU: 2 x Intel Xeon E5-2670, 16 physical cores / 32 logical processors total
- Python: `3.11.9`
- compiler: MSVC `19.44.35224` for x64
- Embree prefix: `C:\Users\Lestat\vendor`
- Embree version observed by RTDL: `(4, 4, 0)`

## Required Checks

| Check | Result |
|---|---|
| Goal742/743 focused tests | PASS, 2 tests OK |
| Public entry smoke | PASS, `valid: true` |
| Public command truth audit | PASS, `valid: true`, 248 commands across 14 docs |
| Large Goal743 Embree benchmark | PASS, all parity fields true |

## Large Benchmark Summary

Windows artifact:

`C:\Users\Lestat\rtdl_post_embree_validation\docs\reports\windows_goal746_lsi_pip_large_perf_2026-04-21.json`

| Workload | Rows | Auto dict median sec | Prepared raw median sec | Prepared speedup vs auto dict | Parity |
|---|---:|---:|---:|---:|---|
| LSI sparse | 100,000 | 0.280563 | 0.051443 | 5.45x | true |
| LSI dense | 1,000,000 | 1.880484 | 0.053491 | 35.15x | true |
| PIP positive | 200,000 | 0.507533 | 0.264082 | 1.92x | true |

## Windows Notes

- `C:\Users\Lestat\vendor` is the valid Embree root on this machine; the longer example path was not present.
- `RTDL_VCVARS64` was needed so `cl` was available for x64 native extension builds.
- `py -3 -m ensurepip --upgrade` was needed because the Python install initially had no `pip`.
- Python printed `Could not find platform independent libraries <prefix>` noise on each invocation, but this did not block imports, native Embree compilation, tests, smoke checks, audits, or benchmarks.
- Native extension build warnings were non-blocking.

## Decision

Goal746 is closed with no blocker. The Windows post-Embree validation supports the Goal745 decision to close the Embree optimization phase and pivot primary development effort to NVIDIA/OptiX app-performance work.
