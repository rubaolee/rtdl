# Goal593 Public Examples Smoke — External Review

Date: 2026-04-19
Reviewer: Claude (claude-sonnet-4-6)

## Verdict: ACCEPT

The smoke evidence is sufficient and honestly bounded.

## Findings

**Coverage matches reality.**
29 files on disk (`examples/rtdl_*.py`) exactly matches 29 reported in the smoke run. No discrepancy.

**All examples exit 0 with clean stderr.**
Every JSON entry shows `returncode: 0` and an empty `stderr_tail`. Execution times (0.12–0.19 s each) are consistent with CPU Python reference backend — no GPU required, no flaky timing.

**Backend-unavailability is handled gracefully and reported honestly.**
- `rtdl_hiprt_ray_triangle_hitcount.py`: HIPRT library absent on this machine; the code wraps `rt.run_hiprt` in a `try/except (FileNotFoundError, OSError, RuntimeError)`, sets `hiprt_available: false`, and exits 0. The error message is informative ("build it with `make build-hiprt`"). This is correct bounded behavior, not a silent skip.
- `rtdl_apple_rt_closest_hit.py`: Apple RT available on the Apple M4; `apple_rt_available: true`, `parity: true`, numerical agreement within float32 tolerance. Code uses an analogous try/except pattern for machines where Apple RT is absent.

**Outputs are semantically plausible.**
Spot-checked stdout for hello_world (`"hello, world"`), knn/radius neighbors (distances consistent with authored coordinates), DBSCAN (correct core/border/noise classification against oracle), Apple RT closest-hit (t=1.2 matches geometry). No fabricated or copy-pasted results detected.

**Scope boundary is clearly stated.**
The `.md` report says: *"This is a macOS local smoke, not Linux/Windows full release validation."* That is the correct and honest scope for this goal. Linux/Windows coverage is a known gap, not a hidden one.

## Notes

No blocking issues found. The one thing worth flagging for context (not a block): all 29 examples run on `cpu_python_reference` or Apple RT — no CUDA/ROCm/HIPRT path was exercised. That is expected given the machine, and the report documents it transparently.
