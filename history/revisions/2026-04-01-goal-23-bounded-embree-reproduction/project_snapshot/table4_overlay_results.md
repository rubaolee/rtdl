# Goal 23 Table 4 Overlay Results

These rows are bounded local overlay-seed analogues, not full overlay materialization results from the paper datasets.

| Local Case | Fidelity | Execution Status | CPU Mean (s) | Embree Mean (s) | Speedup | Note |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `overlay_fixture_subset` | `overlay-seed analogue / fixture-subset` | `executed-overlay-seed-analogue` | 0.000102 | 0.000114 | 0.89x | Current local public sample pair, not a paper-original overlay pair. |
| `overlay_tiled_x8` | `overlay-seed analogue / derived-input` | `executed-overlay-seed-analogue` | 0.000231 | 0.000173 | 1.34x | Deterministic enlargement from the current local public sample pair. |
