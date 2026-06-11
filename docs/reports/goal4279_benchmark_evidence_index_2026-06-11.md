# Goal4279 Benchmark Evidence Index

Status: local benchmark evidence reproducibility cleanup for the current v2.10
source-tree surface.

## Purpose

The ten benchmark apps already have a front-door registry, scale-profile runner,
and pod evidence reports. The problem was discoverability: a reviewer needed to
know which reports to read before understanding the current row for each app.

Goal4279 adds a compact evidence index that points to the current ten-app rows
without creating a new performance claim.

## Delivered

| File | Action | Reason |
| --- | --- | --- |
| `scripts/rtdl_benchmark_evidence_index.py` | Added JSON/Markdown evidence index over the existing front-door registry. | Lets users and reviewers inspect the ten current rows, evidence refs, pod needs, and claim boundaries from one command. |
| `docs/learn/benchmark_evidence_index.md` | Added learner/reviewer-facing evidence map. | Explains current rows, evidence reports, and reading rules without requiring historical report spelunking. |
| `docs/learn/README.md` and `docs/README.md` | Added evidence-index links. | Keeps the current docs door connected to reproducible benchmark evidence. |
| `examples/current/research_benchmarks/README.md` | Added evidence-index pointer. | Makes the benchmark directory explain where the current evidence map lives. |
| `tests/goal4279_benchmark_evidence_index_test.py` | Added focused tests. | Validates 10-app coverage, current paths, existing evidence reports, and non-authorizing claim flags. |

## Boundary

This goal does not run a pod, rerun benchmark timing, authorize public speedup
wording, or change benchmark code. It is an evidence-navigation and
reproducibility cleanup.

## Validation

Focused validation command:

```bash
PYTHONPATH=src:. python -m unittest \
  tests.goal4279_benchmark_evidence_index_test \
  tests.goal4278_source_tree_doctor_test \
  tests.goal4271_v2_10_user_doc_cleanup_test \
  tests.goal4274_current_doc_recheck_test
```

Focused evidence-index gate: 14 tests ran, all passed.

Expanded v2.10 doc/release/navigation gate: 31 tests ran, all passed.
