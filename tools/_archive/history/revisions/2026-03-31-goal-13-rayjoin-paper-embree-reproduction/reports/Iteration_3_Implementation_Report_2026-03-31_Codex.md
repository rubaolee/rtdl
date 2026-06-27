# Goal 13 Implementation Report

Date: 2026-03-31
Author: Codex

This step turns the paper-reproduction planning layer into an executable RTDL registry.

New code:
- /Users/rl2025/rtdl_python_only/src/rtdsl/paper_reproduction.py
- /Users/rl2025/rtdl_python_only/tests/paper_reproduction_test.py

Updated docs:
- /Users/rl2025/rtdl_python_only/docs/rayjoin_paper_dataset_provenance.md
- /Users/rl2025/rtdl_python_only/docs/rayjoin_paper_reproduction_matrix.md

Updated exports:
- /Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py

What this step adds:
1. a machine-readable registry of paper targets across Table 3, Figure 13, Figure 14, Table 4, and Figure 15
2. resolved internal dataset handles for the `LKxx ⊲⊳ PKxx` families using RayJoin's own experiment scripts
3. tests that freeze the expected paper-target label set and continent mapping
4. a stable API (`paper_targets(...)`) for later figure/table generators

Verification run:
- `PYTHONPATH=src:. python3 -m unittest tests.paper_reproduction_test`
- `python3 -m unittest discover -s tests -p '*_test.py'`

Review request for Gemini:
- verify that the registry correctly reflects the current Embree-phase reproduction contract,
- verify that the `lakes_parks_<continent>` mapping is represented honestly,
- identify anything missing before we move into actual dataset acquisition and table/figure generators,
- and end with either `Consensus to continue execution` or `Further revision required`.
