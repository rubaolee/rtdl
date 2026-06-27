# Goal 568: HIPRT Prepared DB Table Reuse and Performance

Date: 2026-04-18

Status: accepted by Codex, Claude, and Gemini Flash.

## Scope

Goal 568 adds a prepared HIPRT execution path for the v0.9 bounded DB workloads:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

The goal is not to make RTDL a DBMS. The prepared path reuses the HIPRT table geometry, row-value device buffer, function table, and compiled match kernel across repeated query probes. Aggregation for `grouped_count` and `grouped_sum` remains host-side after RT candidate row discovery.

## Implementation Summary

Changed files:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_hiprt.cpp`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/hiprt_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- `/Users/rl2025/rtdl_python_only/tests/goal568_hiprt_prepared_db_test.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal568_hiprt_prepared_db_perf.py`

Native changes:

- Added `PreparedDbTable` to own HIPRT runtime state, row-value device memory, row AABB geometry, function table, and match kernel.
- Added C ABI entry points for `rtdl_hiprt_prepare_db_table`, prepared scan/count/sum execution, and prepared handle destruction.
- Changed the DB match kernel from a single-threaded all-row traversal to a per-row ray traversal.
- Corrected DB row AABB placement so row `i` is represented at `x=i`.
- Widened DB row AABB epsilon to `0.25f` to avoid float-collapse misses at larger row IDs.

Python changes:

- Added `PreparedHiprtDbTable`.
- Added `prepare_hiprt_db_table(table_rows)`.
- Added high-level `rt.prepare_hiprt(...)` support for DB kernels with table as the prepared build input and predicates/query as the runtime probe input.
- Added stable prepared-table string encoding and text group-key decoding.

## Correctness Evidence

Linux command:

```bash
cd /tmp/rtdl_goal568
export RTDL_HIPRT_LIB=$PWD/build/librtdl_hiprt.so
export LD_LIBRARY_PATH=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54/hiprt/linux64:${LD_LIBRARY_PATH:-}
PYTHONPATH=src python3 -m unittest tests.goal568_hiprt_prepared_db_test tests.goal559_hiprt_db_workloads_test
```

Result:

```text
Ran 14 tests in 6.873s
OK
```

The test suite covers:

- direct prepared table scan reuse with multiple predicates;
- prepared `grouped_count` and `grouped_sum` with text group-key decoding;
- high-level `rt.prepare_hiprt(...)` for scan/count/sum kernels;
- empty prepared table behavior;
- preservation of existing one-shot HIPRT DB workload parity.

## Linux Performance Evidence

Raw JSON:

`/Users/rl2025/rtdl_python_only/docs/reports/goal568_hiprt_prepared_db_perf_linux_2026-04-18.json`

Host:

- `lx1`
- Linux `6.17.0-20-generic`
- Python `3.12.3`
- rows: `100000`
- iterations: `3`
- PostgreSQL DSN: `dbname=postgres`

### Performance Summary

| Workload | CPU Python | Embree | OptiX | Vulkan | HIPRT one-shot | HIPRT prepare | HIPRT prepared query | PostgreSQL setup/index | PostgreSQL indexed query |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `conjunctive_scan` | 0.149934s | 1.255419s | 1.244690s | 1.236268s | 1.910673s | 1.825620s | 0.001839s | 5.734930s | 0.003271s |
| `grouped_count` | 0.157173s | 1.282286s | 1.253724s | 1.249557s | 1.833957s | 1.819266s | 0.002289s | 5.644232s | 0.010592s |
| `grouped_sum` | 0.162835s | 1.276566s | 1.248788s | 1.259069s | 1.822728s | 1.790839s | 0.002445s | 5.117464s | 0.011181s |

All measured backends matched CPU output.

### HIPRT Reuse Speedup

| Workload | HIPRT one-shot | HIPRT prepared query | Speedup vs one-shot |
|---|---:|---:|---:|
| `conjunctive_scan` | 1.910673s | 0.001839s | 1039.25x |
| `grouped_count` | 1.833957s | 0.002289s | 801.27x |
| `grouped_sum` | 1.822728s | 0.002445s | 745.51x |

## Honest Interpretation

This goal fixes the major HIPRT DB performance pathology for repeated queries: rebuilding the HIPRT table and recompiling the match kernel on every query. With prepared reuse, HIPRT query latency becomes milliseconds on this bounded 100k-row fixture.

This does not mean RTDL is faster than a full database system in general. PostgreSQL is still the correct baseline for DB semantics, indexing, SQL planning, persistence, concurrency, joins, and unbounded tables. The fair claim is narrower:

- RTDL HIPRT prepared DB can accelerate bounded analytical row-candidate discovery for repeated queries on an already prepared table.
- In this fixture, HIPRT prepared query time is faster than PostgreSQL indexed query time, while HIPRT prepare time is lower than PostgreSQL table/index setup time.
- RTDL still owns only the RT-style workload kernel path; Python owns app orchestration; PostgreSQL remains the DB correctness/performance baseline.

## Non-Blocking Limits

- `grouped_count` and `grouped_sum` still aggregate on the host after GPU row discovery.
- Text fields are encoded into ordered integer domains at prepare time.
- Prepared string range predicates are bounded by the prepared table's string domain.
- The performance result is a synthetic deterministic 100k-row fixture, not a general database benchmark.
- The Linux GPU used here still has no NVIDIA RT cores, so the result validates HIPRT/CUDA execution and reuse behavior, not RT-core hardware acceleration.

## Codex Verdict

ACCEPT for Goal 568: correctness is proven against CPU references and existing one-shot DB tests, performance evidence includes HIPRT, OptiX, Vulkan, Embree, CPU, and indexed PostgreSQL, and the claims remain within RTDL's bounded-language/runtime scope.

## External Consensus

- Claude review: `/Users/rl2025/rtdl_python_only/docs/reports/goal568_external_review_2026-04-18.md`
- Gemini Flash review: `/Users/rl2025/rtdl_python_only/docs/reports/goal568_gemini_flash_review_2026-04-18.md`

Consensus verdict: ACCEPT, no blockers.
