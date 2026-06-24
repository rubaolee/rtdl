# Goal1076 Gemini Review

Date: 2026-04-28

## Verdict

ACCEPT.

## Review

Goal1076 correctly creates a separate Barnes-Hut rich-contract pod candidate. The `scripts/goal1076_barnes_hut_rich_rtx_pod_candidate.py` script and its corresponding test `tests/goal1076_barnes_hut_rich_rtx_pod_candidate_test.py` confirm the following:

- **Separate Validation and Timing Rows:** The `build_manifest` function generates exactly one validation row and one timing row, verified by the `valid` field in the manifest and unit tests.
- **Skip-Validation Preservation:** `--skip-validation` is exclusively applied to the timing row and is absent from the validation row, which is correctly enforced by the `build_manifest` logic and tested.
- **Correct Depth/Body-Count Parameters:**
    - The validation row uses `--barnes-tree-depth 6` and `--body-count 1024`.
    - The timing row uses `--barnes-tree-depth 8` and `--body-count 1000000`.
    These parameters are correctly set in the commands for each row and verified in the tests.
- **Avoids Public RTX Speedup Claims:** The `boundary` statement within the script and the generated markdown report explicitly states that Goal1076 "does not authorize public RTX speedup claims." This commitment is also verified by a unit test.

The overall implementation adheres to the specified requirements, ensuring the candidate pod is appropriately configured and documented with respect to RTX claims.