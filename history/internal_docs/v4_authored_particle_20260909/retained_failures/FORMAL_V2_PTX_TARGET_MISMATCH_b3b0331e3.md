# Retained formal v2 PTX target failure

Date: 2026-09-09

Source `b3b0331e351a6c1c7e3d81a022b8c6487f6a6e20` reached formal worker zero
and failed its first RTDL worker with
`CallbackPtxCompositionError: target_identity: make_ray`. No worker completed;
retry and discard counts are zero.

The preserved archive is 7,340 bytes with SHA-256
`ff84ffb4d1108689418460b82f532da8490d9e5475066bdae9bada7deb1d395b`.
It contains the exact preregistration, C-only calibration, command, raw empty
stdout, raw traceback stderr, exit record, append-only ledger and failure
record.

Diagnosis reproduced the failure as NVRTC wrapper PTX 8.4 versus Numba leaf
PTX 8.7 under `/usr/local/cuda-12.8`. The v3 successor binds the compatible
venv CUDA component prefix and retains a real RTDL compatibility probe before
formal worker zero. The failed v2 bytes are immutable and are not pooled with
the successful successor.
