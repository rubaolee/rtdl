# Goal 719: Embree Prepared App Cross-Machine Performance Check

Date: 2026-04-21

## Verdict

ACCEPT as cross-machine evidence for the prepared Embree app-summary path, with one important caveat:

- Linux `lx1` is the cleanest benchmark evidence collected in this round.
- Windows `Li-1` passed correctness and produced large-scale timing data, but the host was a loaded desktop with Chrome/YouTube-class background activity visible, so its timings must not be used as clean release-level performance claims.

## Scope

This goal validates the Goal718 prepared Embree app modes outside the local Mac:

- Outlier prepared mode: `--embree-summary-mode rt_count_threshold_prepared`
- DBSCAN prepared mode: `--embree-summary-mode rt_core_flags_prepared`

The benchmark measures repeated app summary phases:

- native Embree fixed-radius count-threshold traversal
- Python conversion from count rows into density/core flags

The benchmark excludes:

- full CLI JSON output
- oracle computation
- end-to-end service/application latency

## Linux Evidence

Raw file:

`/Users/rl2025/rtdl_python_only/docs/reports/goal718_embree_prepared_app_batch_perf_linux_auto_2026-04-21.json`

Host:

- `lx1`
- Linux `6.17.0-20-generic`
- Python `3.12.3`
- Embree `4.3.0`
- `RTDL_EMBREE_THREADS=auto`, effective threads `8`

Correctness:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal718_embree_prepared_app_modes_test \
  tests.goal717_embree_prepared_fixed_radius_summary_test \
  tests.goal715_embree_fixed_radius_summary_test

Ran 7 tests in 7.182s
OK
```

Performance:

| copies | points | outlier prepared speedup | DBSCAN prepared speedup |
|---:|---:|---:|---:|
| 32,768 | 262,144 | 1.39x | 1.41x |
| 131,072 | 1,048,576 | 1.37x | 1.42x |

Interpretation:

Prepared Embree summary mode gives a consistent repeated-query speedup on Linux by avoiding repeated Embree BVH construction for the same search-point set.

## Windows Evidence

Raw file:

`/Users/rl2025/rtdl_python_only/docs/reports/goal718_embree_prepared_app_batch_perf_windows_auto_2026-04-21.json`

Loaded-host process snapshot:

`/Users/rl2025/rtdl_python_only/docs/reports/goal718_windows_loaded_desktop_process_snapshot_2026-04-21.txt`

Host:

- `Li-1`
- Windows `10.0.19045`
- Python `3.11.9`
- Embree `4.4.0`
- `RTDL_EMBREE_THREADS=auto`, effective threads `32`

Correctness:

```text
PYTHONPATH=src:. py -3 -m unittest -v \
  tests.goal718_embree_prepared_app_modes_test \
  tests.goal717_embree_prepared_fixed_radius_summary_test \
  tests.goal715_embree_fixed_radius_summary_test

Ran 7 tests in 14.363s
OK
```

Performance:

| copies | points | outlier prepared speedup | DBSCAN prepared speedup |
|---:|---:|---:|---:|
| 32,768 | 262,144 | 1.50x | 1.34x |
| 131,072 | 1,048,576 | 1.33x | 1.78x |

Important caveat:

The Windows process snapshot showed active `chrome`, `dwm`, `AdobeCollabSync`, `MsMpEng`, and multiple `Codex` processes. These numbers show the prepared mode still works and is faster than the one-shot summary path on that host, but they are loaded-desktop evidence only. They should not be used for clean scaling claims or direct comparison against Linux.

## Conclusion

Goal718’s prepared Embree app path is now validated on:

- macOS local development host
- Linux `lx1`
- Windows `Li-1`

The strongest clean performance conclusion is:

> For repeated outlier/DBSCAN app-summary phases over a reused point dataset, prepared Embree summary mode consistently improves over one-shot Embree summary mode by avoiding repeated BVH construction.

Bounded performance range observed:

- Linux clean-ish host: about `1.37x-1.42x`
- Windows loaded desktop: about `1.33x-1.78x`, caveated
- macOS local host from Goal718: about `1.36x-1.69x`

This does not prove full application speedup for one-shot CLI runs.

## Next Step

If we need clean Windows scaling evidence, rerun after closing browser/media/background workloads and record an idle process snapshot before the benchmark.
