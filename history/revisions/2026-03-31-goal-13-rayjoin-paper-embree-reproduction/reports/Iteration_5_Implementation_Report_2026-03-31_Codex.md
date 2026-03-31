# Iteration 5 Implementation Report (Codex)

## Objective

Analyze RayJoin paper Section 5.6 scalability support in the current RTDL
baseline, determine whether the repository can execute those experiments now,
and either run them or revise the code to support them.

## Support Decision

The repository did **not** previously support Section 5.6 as an executable
experiment.

What existed before:

- `lsi` and `pip` workload support,
- planning notes for Figure 13 and Figure 14 in Goal 13 docs,
- existing Embree evaluation infrastructure.

What was missing:

- deterministic uniform / gaussian scalability generators,
- a fixed-`R` / varying-`S` experiment runner,
- Figure 13 / Figure 14 analogue generation,
- and a dedicated report path for Section 5.6.

## Revisions Implemented

### New experiment module

- `src/rtdsl/section_5_6_scalability.py`

Added:

- deterministic synthetic polygon generation for `uniform` and `gaussian`
  distributions,
- polygon-to-segment conversion for `lsi`,
- polygon-centroid probe-point generation for `pip`,
- Embree timing loops for Section 5.6 analogue runs,
- reduced CPU-vs-Embree parity checks on representative smaller samples,
- Figure 13 / Figure 14 analogue SVG generation,
- markdown and PDF report generation.

### Public API exports

- `src/rtdsl/__init__.py`

Added exports for:

- `ScalabilityConfig`
- `generate_synthetic_polygons`
- `polygons_to_segments`
- `polygon_probe_points`
- `run_section_5_6`
- `generate_section_5_6_artifacts`

### Tests

- `tests/section_5_6_scalability_test.py`

Added:

- deterministic generator test,
- artifact-generation smoke test.

### Commands and docs

Updated:

- `Makefile`
- `README.md`
- `docs/goal_13_rayjoin_paper_embree_plan.md`
- `docs/rayjoin_paper_reproduction_checklist.md`
- `docs/rayjoin_paper_reproduction_matrix.md`
- `docs/rayjoin_paper_dataset_provenance.md`

### Generated artifacts

Produced:

- `build/section_5_6_scalability/section_5_6_scalability.json`
- `build/section_5_6_scalability/figures/figure13_lsi_scalability.svg`
- `build/section_5_6_scalability/figures/figure14_pip_scalability.svg`
- `build/section_5_6_scalability/section_5_6_scalability_report.md`
- `build/section_5_6_scalability/section_5_6_scalability_report.pdf`
- published copies in `docs/reports/section_5_6_scalability_report_2026-03-31.{md,pdf}`

## Experimental Boundary

This is an **Embree-phase scaled analogue** of RayJoin Section 5.6, not the
original 5M / 1M..5M RT-core experiment.

Final implemented local scale:

- fixed build side: `R = 800 polygons`
- varying probe side: `S = 160, 320, 480, 640, 800 polygons`
- distributions: `uniform`, `gaussian`
- iterations: `2`
- warmup: `1`

## Verification

Executed successfully:

- `PYTHONPATH=src:. python3 -m unittest tests.section_5_6_scalability_test`
- `PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py'`
- direct artifact generation through `rtdsl.generate_section_5_6_artifacts(...)`

Published report paths:

- `docs/reports/section_5_6_scalability_report_2026-03-31.md`
- `docs/reports/section_5_6_scalability_report_2026-03-31.pdf`

## Request For Review

Review for:

- honesty of the support decision,
- consistency of the scaled-analogue claim,
- correctness of the generated artifact/report boundary,
- and alignment between code, docs, and produced results.
