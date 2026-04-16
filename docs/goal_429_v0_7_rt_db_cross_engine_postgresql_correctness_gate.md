# Goal 429: v0.7 RT DB Cross-Engine PostgreSQL Correctness Gate

## Goal

Close correctness for the first bounded `v0.7` DB workload family across all
implemented engines against PostgreSQL.

## Required outcome

- parity against PostgreSQL for:
  - Python truth
  - native/oracle CPU
  - Embree
  - OptiX
  - Vulkan
- keep claims row-exact and bounded

## Review requirement

This goal requires at least 2-AI consensus before closure.
