# Goal4539 / V3 M140 Triangle Capture-Mode Audit

## Conclusion

Goal4539 confirms that Triangle weighted-replay CUDA graph capture does not become valid by switching CuPy stream-capture mode after a validated device-output stream launch. The non-graph device-output stream executor remains the accepted evidence shape for generic Triangle weighted replay, but this goal does not reclassify the V3 queue and does not authorize M113 graph, public speedup, broad RT-core, automatic partner-selection, or app-specific native-engine wording.

## Runtime

- Expected weighted sum: `20`
- Device-output stream prelaunch sum: `20`
- Device-output stream prelaunch validated: `True`
- Graph capture validated modes: ``
- Graph capture mode-independent reject: `True`

## Capture Modes

| Mode | Status | Replay sum | Error |
| --- | --- | --- | --- |
| `default` | `reject_error` | `None` | RuntimeError: OptiX error: CUDA error |
| `relaxed` | `reject_error` | `None` | RuntimeError: OptiX error: CUDA error |
| `global` | `reject_error` | `None` | RuntimeError: OptiX error: CUDA error |
| `thread_local` | `reject_error` | `None` | RuntimeError: OptiX error: CUDA error |

## Acceptance

- Non-graph stream continuation evidence accepted: `True`
- M113 graph capture still blocked: `True`
- Queue reclassification done: `False`

## Boundary

- No current Triangle Counting route changed.
- No queue reclassification is authorized by this packet.
- No M113 graph promotion, automatic partner selection, public speedup, or RT-core speedup wording is authorized.
