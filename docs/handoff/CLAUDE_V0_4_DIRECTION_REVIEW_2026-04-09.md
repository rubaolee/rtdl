# Claude v0.4 Direction Review Request

Start by reading these files from the current repo checkout:

- `README.md`
- `docs/README.md`
- `docs/release_reports/v0_3/release_statement.md`
- `docs/reports/goal193_v0_4_direction_decision_2026-04-09.md`
- `docs/reports/goal194_v0_4_content_package_2026-04-09.md`

Task:

- review the revised `v0.4` package
- challenge it sharply
- decide whether replacing the earlier 3D-first draft with a nearest-neighbor
  workload release is the right move
- identify the strongest remaining weakness in the revised plan

Requirements for your response:

- write the response to:
  - `docs/reports/claude_v0_4_direction_review_2026-04-09.md`
- use exactly three short sections:
  - `Verdict`
  - `Findings`
  - `Summary`
- be direct
- surface real disagreements, not polite restatements

Important context:

- RTDL must remain positioned as a non-graphical geometric-query runtime
- the visual demos are preserved proof material only, not the center of `v0.4`
- the revised package is nearest-neighbor-first, with:
  - `fixed_radius_neighbors` as the first accepted workload
  - `knn_rows` as the second workload in the same family
- the question is whether this revised package is the right `v0.4` plan
