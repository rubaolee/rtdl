# Goal 78 Claude Plan Brief

Task: produce a technical implementation plan only for the Vulkan positive-hit `pip` redesign.

Current bottleneck in `src/native/rtdl_vulkan.cpp`:

- the `positive_only` branch in `run_pip_vulkan(...)` does a dense host-side full scan
- it iterates all `point_count × poly_count` pairs on the host
- this defeats the purpose of the positive-hit contract on long workloads

Required redesign:

- preserve exact parity
- preserve full-matrix behavior
- for positive-hit mode only:
  - GPU generates sparse candidate pairs
  - host exact-finalizes only those candidate pairs

Do not write code yet.

Output exactly these sections:

1. Proposed Design
2. Exact Files To Change
3. Host/GPU Data Flow
4. Parity Risks
5. Required Tests
6. Recommended First Patch Scope
