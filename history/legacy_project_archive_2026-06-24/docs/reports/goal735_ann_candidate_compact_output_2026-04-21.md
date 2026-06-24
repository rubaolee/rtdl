# Goal 735: ANN Candidate Embree Compact Rerank Output

Date: 2026-04-21

## Scope

Goal 735 improves the public ANN candidate-search app surface:

- `examples/rtdl_ann_candidate_app.py` now supports
  `--output-mode full|rerank_summary|quality_summary`.
- The default remains `full`, preserving approximate rows, exact rows,
  comparison rows, recall, and distance-ratio metrics.
- `rerank_summary` measures only the RTDL candidate-subset KNN reranking slice.
- `quality_summary` keeps recall and distance metrics but omits heavy row
  payloads.

This separates the Embree-owned nearest-neighbor reranking work from Python
exact full-set comparison used to evaluate ANN quality.

## Output Modes

| Mode | What it returns | Boundary |
| --- | --- | --- |
| `full` | approximate rows, exact rows, comparison rows, recall, distance ratio | original app behavior |
| `rerank_summary` | approximate row count, query coverage, max rank | measures RTDL candidate-subset KNN reranking only |
| `quality_summary` | compact recall and distance metrics | still runs Python exact full-set comparison |

## Correctness

Focused tests verify:

- default full output preserves quality rows;
- `rerank_summary` omits exact-quality work and heavy rows;
- `quality_summary` omits rows but preserves metrics;
- Embree `rerank_summary` matches CPU Python reference summary;
- invalid output modes are rejected.

Commands:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal735_ann_candidate_compact_output_test \
  tests.goal520_dbscan_clustering_app_test \
  tests.goal505_v0_8_app_suite_test
```

Results:

- macOS: 16 focused/app tests passed.
- Linux: 16 focused/app tests passed.

## Performance Evidence

Measurement:

- `run_app(...)` plus `json.dumps(...)`
- CPU Python reference `rerank_summary` versus Embree `rerank_summary`
- `quality_summary` capped to 256 copies because it includes Python exact
  full-set comparison
- 3 repeats

macOS:

| Copies | CPU rerank summary | Embree rerank summary | Embree / CPU speedup | Embree quality summary |
| ---: | ---: | ---: | ---: | ---: |
| 256 | 0.1297s | 0.0065s | 19.84x | 0.1511s |
| 1024 | 2.5969s | 0.0405s | 64.19x | skipped |

Linux:

| Copies | CPU rerank summary | Embree rerank summary | Embree / CPU speedup | Embree quality summary |
| ---: | ---: | ---: | ---: | ---: |
| 256 | 0.2341s | 0.0146s | 16.04x | 0.3237s |
| 1024 | 4.3918s | 0.1156s | 38.00x | skipped |

Raw evidence:

- `docs/reports/goal735_ann_candidate_compact_output_perf_local_2026-04-21.json`
- `docs/reports/goal735_ann_candidate_compact_output_perf_linux_2026-04-21.json`

## Conclusion

The ANN candidate app now has a reasonable Embree performance mode for the
part RTDL owns today: candidate-subset KNN reranking. This mode avoids exact
full-set quality comparison and heavy row payloads.

Do not claim this is a full ANN index, a training system, or a general
recall/latency optimizer. `quality_summary` still runs Python exact full-set
comparison for recall and distance metrics.
