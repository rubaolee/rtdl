# v2.0 Pre-Release Candidate

RTDL v2.0 is a Python+partner+RTDL pre-release candidate. It is not the final
release until the strict 3-AI consensus redline has a fresh Claude-family
review.

Current learner-facing facts:

- Python remains the application layer.
- RTDL owns app-agnostic RT-shaped primitive execution.
- NumPy, PyTorch, and CuPy can own columns for supported partner paths.
- Current OptiX/RT evidence is strong under documented contracts.
- Large witness outputs should prefer streaming witness columns over full
  Python row-table materialization.

Still not allowed:

- final v2.0 release wording;
- package-install promises;
- arbitrary PyTorch/CuPy acceleration;
- broad RT-core acceleration;
- arbitrary polygon overlay;
- claims that every user program is faster.

For audit detail, use the release-report archive entry for the streaming
witness-column update.
