# Goal 743: LSI/PIP Cross-Machine Large Embree Performance Report

## Verdict

`lsi` and `pip` are now credible high-priority Embree root workloads, not just historical primitives.

Across macOS, Linux, and Windows, all large runs preserved deterministic parity. The strongest result is that Embree accelerates the RT part very clearly when the app shape is sparse or positive-hit: sparse LSI gets useful multithreading, PIP positive gets useful multithreading, and prepared raw mode consistently shows that native traversal/row discovery is much faster than Python dict materialization.

The main limitation is equally clear: dense LSI can emit one million rows. RT traversal can discover those rows quickly, but app-visible Python row materialization dominates. This is not an Embree failure; it is a signal that app APIs should prefer compact summaries, flags, counts, or raw native buffers when they do not truly need every pair row.

## Test Inputs

| Workload | Input scale | Expected rows | What it models |
|---|---:|---:|---|
| LSI sparse | `100000` probe segments, `100000` build segments | `100000` | Spatial join where each probe has a small number of true intersections. |
| LSI dense | `1000` probe segments, `1000` build segments | `1000000` | Worst-case row-output pressure where every probe intersects every build segment. |
| PIP positive | `200000` points, `100000` polygons | `200000` | Positive-hit point-in-polygon app shape where each point emits one accepted containment row. |

Large correctness was checked by deterministic expected row counts and stable FNV-64 row hashes. Goal742 separately records smaller CPU-reference parity against the Python reference.

## What Embree Accelerates

For LSI, RTDL now builds an Embree user-geometry scene over build-side segments. Each probe segment is launched as a ray through that scene. The Embree traversal narrows candidate build segments, and the intersection callback performs the segment/segment refinement before emitting accepted rows.

For PIP positive-hit, RTDL builds Embree user geometry over polygons and uses point-query candidate discovery. Candidate polygons are refined with containment checks, and only positive containment rows are emitted.

The table separates three costs:

| Mode | Meaning |
|---|---|
| `1T dict` | Embree native work with one thread, then Python dict-row materialization. |
| `Auto dict` | Embree native work with automatic thread count, then Python dict-row materialization. |
| `Prepared raw` | Prepared Embree path returning native raw rows before Python dict materialization. |

## macOS Results

Host: `Rs-MacBook-Air.local`, platform: `macOS-26.3-arm64-arm-64bit-Mach-O`, Embree auto threads: `10`.

| Workload | Rows | 1T dict s | Auto dict s | Prepared raw s | Auto vs 1T | Raw vs dict | Auto rows/s | Raw rows/s | Parity |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| LSI sparse | `100000` | `0.485738` | `0.130487` | `0.025715` | `3.72x` | `5.07x` | `766,358` | `3,888,705` | true |
| LSI dense | `1000000` | `1.284347` | `1.341152` | `0.017217` | `0.96x` | `77.90x` | `745,628` | `58,082,830` | true |
| PIP positive | `200000` | `0.862683` | `0.381578` | `0.189210` | `2.26x` | `2.02x` | `524,139` | `1,057,029` | true |

## Linux Results

Host: `lx1`, platform: `Linux-6.17.0-20-generic-x86_64-with-glibc2.39`, Embree auto threads: `8`.

| Workload | Rows | 1T dict s | Auto dict s | Prepared raw s | Auto vs 1T | Raw vs dict | Auto rows/s | Raw rows/s | Parity |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| LSI sparse | `100000` | `0.523844` | `0.128772` | `0.025054` | `4.07x` | `5.14x` | `776,564` | `3,991,300` | true |
| LSI dense | `1000000` | `1.043987` | `0.984122` | `0.018277` | `1.06x` | `53.85x` | `1,016,134` | `54,714,002` | true |
| PIP positive | `200000` | `0.930760` | `0.331053` | `0.177893` | `2.81x` | `1.86x` | `604,133` | `1,124,270` | true |

## Windows Results

Host: `Li-1`, platform: `Windows-10-10.0.19045-SP0`, Embree auto threads: `32`.

| Workload | Rows | 1T dict s | Auto dict s | Prepared raw s | Auto vs 1T | Raw vs dict | Auto rows/s | Raw rows/s | Parity |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| LSI sparse | `100000` | `13.314959` | `0.273783` | `0.047766` | `48.63x` | `5.73x` | `365,252` | `2,093,557` | true |
| LSI dense | `1000000` | `1.704204` | `1.763719` | `0.054945` | `0.97x` | `32.10x` | `566,984` | `18,199,952` | true |
| PIP positive | `200000` | `1.568983` | `0.505797` | `0.221698` | `3.10x` | `2.28x` | `395,416` | `902,130` | true |

The Windows sparse-LSI 1-thread time is much slower than macOS/Linux, but the auto-thread path recovers strongly. This should not be treated as a cross-host CPU ranking; it shows that auto-threading is essential on the Windows 32-thread machine.

## Cross-Machine Reading

| Workload | macOS auto dict | Linux auto dict | Windows auto dict | Main lesson |
|---|---:|---:|---:|---|
| LSI sparse | `0.130487 s` | `0.128772 s` | `0.273783 s` | Sparse LSI is the best app-shaped LSI case for RT traversal and auto-threading. |
| LSI dense | `1.341152 s` | `0.984122 s` | `1.763719 s` | Dense all-pairs output is row-materialization-bound; prepared raw exposes fast native discovery. |
| PIP positive | `0.381578 s` | `0.331053 s` | `0.505797 s` | Positive-hit PIP is a good app-facing shape; auto-threading helps, raw rows help further. |

## Key Conclusions

1. Sparse LSI is now a strong Embree root workload. The app-visible path gets `3.72x` to `48.63x` auto-thread speedup over 1-thread depending on host, with parity preserved.

2. PIP positive-hit is a strong Embree root workload. The app-visible path gets `2.26x` to `3.10x` auto-thread speedup over 1-thread, with parity preserved.

3. Dense LSI proves the output-bound problem. Prepared raw is `32x` to `78x` faster than auto dict mode, so the main cost is not native traversal; it is materializing one million Python dictionaries.

4. The public app guidance should prefer sparse/positive/summary outputs. If an app only needs flags, counts, overlap candidates, or summaries, it should not request full pair rows.

5. These results are Embree CPU ray-tracing results. They do not claim NVIDIA RT-core acceleration. They do, however, give a clean optimization template for OptiX, Vulkan, HIPRT, and Apple RT.

## Evidence Files

- macOS JSON: `docs/reports/goal743_lsi_pip_large_perf_macos_2026-04-21.json`
- Linux JSON: `docs/reports/goal743_lsi_pip_large_perf_linux_2026-04-21.json`
- Windows JSON: `docs/reports/goal743_lsi_pip_large_perf_windows_2026-04-21.json`
- Harness: `scripts/goal743_lsi_pip_large_cross_machine_perf.py`
- Quick parity test: `tests/goal743_lsi_pip_large_cross_machine_perf_test.py`
