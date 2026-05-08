# Goal 1526: Collect/Reduced-Copy Cumulative Rerun

## Verdict

The current v1.5.1 through v1.5.4 collect, prepared-buffer, reduced-copy,
OptiX-readiness, and local safety-guard slice is green on both Windows and the
local Linux validation host after Goal1525.

This is a targeted local/non-pod regression checkpoint only. It does not
authorize stable `COLLECT_K_BOUNDED` promotion, public speedup wording, broad
RTX/GPU wording, true zero-copy wording, whole-app claims, or release action.

## Run Scope

The rerun covered:

- v1.5.1 `COLLECT_K_BOUNDED` contract, native row-buffer, parity, benchmark,
  readiness, release-surface, public-link, native ABI, and adapter gates;
- v1.5.2 collect result-buffer and prepared host-output descriptor/envelope
  gates;
- v1.5.3 reduced-copy and post-review gates;
- v1.5.4 device-buffer packet, OptiX ABI/device-pointer/stub gates, non-pod
  OptiX collect-k readiness gates, emitted-count fail-closed guards, reduced
  copy local regression, and typed-host zero-capacity guard.

## Windows Result

```text
Ran 199 tests in 0.585s
OK
```

## Linux Result

Host: `192.168.1.20`

```text
Ran 199 tests in 0.063s
OK
```

## Claim Boundary

Goal1526 records a named local Windows plus Linux regression slice only. It does
not prove new NVIDIA pod performance, accepted tiled OptiX performance, public
acceleration, true zero-copy, whole-app speedup, stable `COLLECT_K_BOUNDED`
promotion, or release readiness.
