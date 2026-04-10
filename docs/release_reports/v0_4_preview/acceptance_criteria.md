# RTDL v0.4 Preview: Acceptance Criteria

`v0.4` should not release until all of the following exist.

## Workload contract

- one explicit public workload contract for `fixed_radius_neighbors`
- clear naming, input layouts, output rows, and documented limitations

## Truth path

- Python reference truth path
- native CPU/oracle truth or bounded correctness support

## Native backend closure

Minimum required:

- Embree

Target stronger closure:

- OptiX
- Vulkan

## Public example chain

- one top-level release-facing example
- one reference example
- one tutorial addition

## Documentation

- feature home
- release-facing example docs
- support matrix
- honest release statement

## Verification

- bounded unit and system tests
- explicit pass/skip/fail accounting
- at least one benchmark or scaling note for the new workload

## Review discipline

- `2+` AI consensus on the goal closures
- final release audit before tagging
