I will start by listing the contents of the relevant directories to confirm the existence of all files mentioned in the review request.
I will read the Goal 28B Spec and Implementation Report to understand the context and the stated closure boundaries.
I will read the new dataset registry and query helpers in `src/rtdsl/datasets.py` and their exports in `src/rtdsl/__init__.py`.
I will read the staging script `scripts/goal28b_stage_uscounty_zipcode.py` to ensure it is reproducible and correctly handles the staging process.
I will read the test file `tests/goal28b_staging_test.py` to verify that the staging process is correctly tested.
I will re-read `src/rtdsl/datasets.py` to check if `build_arcgis_query_url` exists, as it was called in the test file.
I will grep for the function names in `src/rtdsl/datasets.py` to clarify their exact names and ensure consistency with the tests.
I will re-check `src/rtdsl/__init__.py` to see if `build_arcgis_query_url` is exported, as its absence would cause the test to fail.
I will run the tests in `tests/goal28b_staging_test.py` to ensure that the implementation is correct and the tests pass as reported.
