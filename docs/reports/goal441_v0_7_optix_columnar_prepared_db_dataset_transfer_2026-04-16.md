# Goal 441: v0.7 OptiX Columnar Prepared DB Dataset Transfer

Date: 2026-04-16

## Verdict

Goal 441 is implemented and ready for external review.

This goal adds the native columnar prepared DB dataset transfer path to the
OptiX backend. The existing row-struct compatibility transfer remains intact,
and the new path is opt-in through `transfer="columnar"`.

## Implemented Surface

Native OptiX ABI:

- `RtdlDbColumn`
- `rtdl_optix_db_dataset_create_columnar`

Python API:

```python
rt.prepare_optix_db_dataset(table_rows, primary_fields=(...), transfer="columnar")
```

Compatibility path remains:

```python
rt.prepare_optix_db_dataset(table_rows, primary_fields=(...), transfer="row")
```

The default remains `transfer="row"` so existing callers are not changed.

## Correctness Evidence

Local macOS syntax gate:

```text
python3 -m py_compile src/rtdsl/optix_runtime.py tests/goal441_v0_7_optix_columnar_prepared_db_dataset_transfer_test.py scripts/goal441_optix_columnar_transfer_perf_gate.py
```

Linux `lestat-lx1` native rebuild:

```text
make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev CUDA_PREFIX=/usr NVCC=/usr/bin/nvcc
```

Linux `lestat-lx1` correctness gate:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal441_v0_7_optix_columnar_prepared_db_dataset_transfer_test -v
Ran 4 tests
OK
```

The test suite verifies row-transfer, columnar-transfer, and Python-truth parity
for:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

It also verifies invalid transfer mode rejection.

## Linux Prepare-Time Gate

Command:

```text
PYTHONPATH=src:. python3 scripts/goal441_optix_columnar_transfer_perf_gate.py --row-count 200000 --repeats 5
```

Raw JSON:

```text
/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal441_optix_columnar_transfer_perf_linux_2026-04-16.json
```

| Workload | Row-transfer median prepare | Columnar-transfer median prepare | Columnar speedup |
|---|---:|---:|---:|
| `conjunctive_scan` | 2.702394 s | 0.799623 s | 3.38x |
| `grouped_count` | 2.609348 s | 0.795885 s | 3.28x |
| `grouped_sum` | 2.509595 s | 0.790796 s | 3.17x |

The row hashes match the existing DB truth hashes:

- `conjunctive_scan`: `19461bddd250025c3d24a174f82e5f66046e40dded85ef27614143a08c9590c8`
- `grouped_count`: `869ed487d7eda66115bb00dceaf75df016fac2e2e0a6d75119f993d63137a77b`
- `grouped_sum`: `123b2f6fc6fa9f69e2df8da24441116549271314ef3b602482467c6ad47ed330`

## Interpretation

This closes the OptiX part of the compatibility row-ingestion caveat. It follows
the Goal 440 Embree pattern while preserving the row-transfer ABI for backward
compatibility.

The justified claim is:

- OptiX now has a native columnar prepared DB dataset creation path.
- The path preserves correctness for the bounded DB family.
- On the Linux 200k-row prepare gate, columnar transfer reduces OptiX prepare
  time by about 3.17x to 3.38x against the row-struct transfer path.

The excluded claims are:

- Vulkan columnar transfer is not implemented yet.
- RTDL is still not a DBMS.
- This does not add arbitrary SQL support.
- This does not by itself prove final large-table ingestion across every backend.

## Follow-Up

Next reasonable goals:

- add the same columnar prepared DB dataset transfer ABI to Vulkan
- refresh the cross-backend repeated-query gate after all three RT backends use
  columnar transfer
