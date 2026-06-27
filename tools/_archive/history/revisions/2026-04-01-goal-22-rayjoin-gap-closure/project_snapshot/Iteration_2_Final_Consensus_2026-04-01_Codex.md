# Goal 22 Final Consensus

Claude and Gemini both accepted the first Goal 22 slice.

Accepted result:

- the paper-reproduction registry now includes:
  - machine-readable paper targets,
  - dataset-family status,
  - local profile policies
- the repo now generates current analogue artifacts for:
  - Table 3
  - Table 4
  - Figure 15
- missing datasets are labeled explicitly rather than hidden
- the `overlay-seed analogue` boundary is encoded in the generated artifacts and tests

Still deferred to later Goal 22 work:

- actual public dataset acquisition and conversion for the missing dataset families
- bounded per-pair local profiles once those datasets exist
- real bounded local run results for the newly generated analogue artifacts

Validation executed:

- `PYTHONPATH=src:. python3 -m unittest tests.goal22_reproduction_test tests.paper_reproduction_test`
- `PYTHONPATH=src:. python3 scripts/goal22_generate_reproduction_artifacts.py`

Consensus decision:

Goal 22 first slice accepted by consensus.
