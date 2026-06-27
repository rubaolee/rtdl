# Goal 22 Iteration 3 Final Consensus

Claude and Gemini both accepted the Goal 22 dataset-source and bounded-preparation slice.

Accepted result:

- the repo now contains a machine-readable public-source registry for the missing RayJoin paper dataset families,
- the repo now contains a machine-readable bounded-local preparation registry for the same families,
- deterministic CDB slicing and writing helpers now exist for bounded local preparation once public data is staged,
- generated Goal 22 artifacts now expose:
  - current public-source status,
  - bounded local preparation policy,
  - and the distinction between `source-identified` and `acquired`.

Important accepted boundary:

- this slice does **not** claim that the missing paper datasets are already acquired locally,
- it does **not** claim that the Dryad share or every historical public link is currently downloadable without friction,
- and it intentionally leaves the concrete chain-limit choice to Goal 23 while freezing the deterministic rule shape now.

Validation executed:

- `cd /Users/rl2025/rtdl_python_only && PYTHONPATH=src:. python3 -m unittest tests.goal22_reproduction_test tests.paper_reproduction_test`
- `cd /Users/rl2025/rtdl_python_only && PYTHONPATH=src:. python3 scripts/goal22_generate_reproduction_artifacts.py`
- `cd /Users/rl2025/rtdl_python_only && python3 -m py_compile src/rtdsl/datasets.py src/rtdsl/rayjoin_artifacts.py src/rtdsl/__init__.py`

Consensus decision:

Goal 22 dataset-source slice accepted by consensus.
