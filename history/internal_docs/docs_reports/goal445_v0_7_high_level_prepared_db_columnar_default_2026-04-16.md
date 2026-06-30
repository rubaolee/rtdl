# Goal 445: v0.7 High-Level Prepared DB Columnar Default

Date: 2026-04-16

## Verdict

Goal 445 is implemented and ready for external review.

The high-level prepared-kernel API now uses columnar prepared DB dataset
transfer for the bounded DB workload family:

- `prepare_embree(kernel).bind(...)`
- `prepare_optix(kernel).bind(...)`
- `prepare_vulkan(kernel).bind(...)`

The direct prepared dataset APIs keep their backward-compatible row-transfer
default:

- `prepare_embree_db_dataset(..., transfer="row")`
- `prepare_optix_db_dataset(..., transfer="row")`
- `prepare_vulkan_db_dataset(..., transfer="row")`

## Implemented Change

The internal DB preparation helpers now call the columnar dataset ABI for:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

Runtime files changed:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/embree_runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/optix_runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/vulkan_runtime.py`

The low-level prepared dataset handle now records its transfer mode as
`dataset.transfer`, allowing the regression test to prove the high-level bind
path is using columnar transfer.

## Correctness Evidence

Local macOS:

```text
python3 -m py_compile src/rtdsl/embree_runtime.py src/rtdsl/optix_runtime.py src/rtdsl/vulkan_runtime.py tests/goal445_v0_7_high_level_prepared_db_columnar_default_test.py
PYTHONPATH=src:. python3 -m unittest tests.goal445_v0_7_high_level_prepared_db_columnar_default_test -v
Ran 4 tests
OK (skipped=2)
```

The local skips are expected because OptiX and Vulkan backend libraries are not
built in the local macOS checkout.

Linux `lestat-lx1`:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal445_v0_7_high_level_prepared_db_columnar_default_test -v
Ran 4 tests
OK
```

The Linux suite verifies:

- Embree high-level prepared DB workloads use `transfer == "columnar"`
- OptiX high-level prepared DB workloads use `transfer == "columnar"`
- Vulkan high-level prepared DB workloads use `transfer == "columnar"`
- all high-level prepared DB outputs match Python truth
- direct `prepare_embree_db_dataset(...)` still defaults to row transfer

## Boundary

This goal does not remove row-transfer compatibility from the direct prepared
dataset API. It only makes the high-level prepared-kernel DB path use the
columnar implementation accepted in Goals 440-442.
