# v2.0 Pre-Release Candidate Archive

This page is archived. RTDL v2.0 has since released as the source-tree
Python+partner+RTDL milestone. Current users should read the
[v2.0 Release Package](v2_0/README.md).

The former learner-facing facts were:

- Python remains the application layer.
- RTDL owns app-agnostic RT-shaped primitive execution.
- NumPy, PyTorch, and CuPy can own columns for supported partner paths.
- Current OptiX/RT evidence is strong under documented contracts.
- Large witness outputs should prefer streaming witness columns over full
  Python row-table materialization.
- The RayJoin-style LSI/PIP research lane is closed for v2.0 with bounded
  same-query evidence; it is not a claim that RTDL beats the RayJoin paper
  implementation.

Still not allowed in the v2.0 release:

- package-install promises;
- arbitrary PyTorch/CuPy acceleration;
- broad RT-core acceleration;
- arbitrary polygon overlay;
- claims that every user program is faster.

For audit detail, use the streaming witness-column update, the RayJoin closure,
Goal2322 final consensus, and the v2.0 release package.
