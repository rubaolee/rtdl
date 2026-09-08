# Dependencies

- CPython 3.11 or newer.
- Python standard library only.
- No network, CUDA, OptiX, RTDL, NumPy, or third-party package is required.

The verifier reads only files below the supplied artifact root. It rejects
unexpected files, symlinks, duplicate JSON keys, non-finite JSON numbers,
identity mismatches, missing rows, changed samples, and changed calculations.
