# Goal1035 Local Baseline Scale-Ramp Summary

Date: 2026-04-26

## Scope

Goal1035 replaces the failed monolithic full local baseline attempt with an incremental scale-ramp runner. The runner executes baseline-ready app commands one command at a time, overrides `--copies`, and writes checkpoint JSON/Markdown after every command.

Artifacts:

- `scripts/goal1035_local_baseline_scale_ramp.py`
- `tests/goal1035_local_baseline_scale_ramp_test.py`
- `docs/reports/goal1035_local_baseline_scale_ramp_2026-04-26.json`
- `docs/reports/goal1035_local_baseline_scale_ramp_2026-04-26.md`
- `docs/reports/goal1035_local_baseline_scale_ramp_2000_2026-04-26.json`
- `docs/reports/goal1035_local_baseline_scale_ramp_2000_2026-04-26.md`

## Why This Was Needed

The first full-mode attempt used the existing Goal1031 runner at manifest scale (`--copies 20000`). That runner reports only after the entire batch finishes. Locally, it reached a long-running `outlier_detection` Embree command after a costly CPU command and had to be stopped. No result file was emitted.

The correct operational fix is not to lower standards, but to make the runner incremental:

- each app/backend/scale row is isolated;
- outputs are checkpointed after every command;
- timeout/failure evidence survives;
- local work can progress without wasting cloud time or hiding the slow row.

## Results

All completed scale-ramp rows passed.

| Copies | Rows | Status |
|---:|---:|---|
| 50, 500 | 24 | `ok` |
| 2000 | 12 | `ok` |

Representative 2000-copy timings:

| App | CPU (s) | Embree (s) | SciPy (s) | Interpretation |
|---|---:|---:|---:|---|
| `outlier_detection` | 15.258467 | 15.267537 | 16.228283 | Correctness and command health pass, but local app-level timing is dominated by shared overhead or semantics outside the prepared RT phase. |
| `dbscan_clustering` | 0.172229 | 0.136282 | 0.482447 | Embree is faster than CPU at this scale for the prepared core-flag summary. |
| `service_coverage_gaps` | 0.197649 | 0.163576 | 0.339601 | Embree is faster than CPU at this scale for the prepared coverage summary. |
| `event_hotspot_screening` | 0.283394 | 0.164967 | 0.396641 | Embree is faster than CPU at this scale for the prepared count summary. |

## Engineering Conclusion

Goal1035 provides a safer local baseline execution method and confirms that the four baseline-ready apps run successfully through CPU, Embree, and SciPy at `50`, `500`, and `2000` copies.

The important performance-development signal is that `outlier_detection` still needs phase-level instrumentation or implementation review before it is useful as a public comparison target. Its app-level local timing does not isolate the prepared RT contribution.

For the other three apps, the ramp gives preliminary local shape only. It does not replace cloud RTX timing, repeated runs, or same-semantics public-review gates.

## Boundary

This is local scale-ramp evidence. It does not authorize public speedup claims, release authorization, or NVIDIA RT-core superiority claims. Public wording still requires same-scale reviewed baselines and the existing RTX public wording matrix.
