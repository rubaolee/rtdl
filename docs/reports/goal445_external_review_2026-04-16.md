# External Review: Goal 445 (2026-04-16)

## Verdict

ACCEPT

## Evidence Checked

The following evidence was reviewed:

*   **Code Analysis:**
    *   `embree_runtime.py`: Confirmed `self.transfer=transfer` and `direct prepare_embree_db_dataset` default `transfer='row'`.
    *   High-level DB helper logic: Verified use of `_encode_db_table_columnar` passing `transfer='columnar'`.
    *   `optix_runtime.py`: Exhibits the same pattern as `embree_runtime.py`.
    *   `vulkan_runtime.py`: Exhibits the same pattern as `embree_runtime.py`.

*   **Test Execution:**
    *   `tests/goal445_v0_7_high_level_prepared_db_columnar_default_test.py`: Assertions confirm `prepared.dataset.transfer == 'columnar'` and match `rows == Python truth` for Embree, OptiX, and Vulkan across `conjunctive_scan`, `grouped_count`, and `grouped_sum` operations. The test also verifies that `direct prepare_embree_db_dataset` default remains `'row'`.
    *   Linux log (`docs/reports/goal446_post_columnar_db_regression_linux_2026-04-16.log`): Shows all four Goal445 tests passed successfully, with the final output: `'Ran 46 tests in 1.990s OK'`.

## Blockers

None.
