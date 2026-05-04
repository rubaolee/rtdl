I will start by reading the requested documentation and test files to understand the scope and details of the v1.0 post-release sanity fix.

The review of the Goal1254 v1.0 post-release sanity fix is complete. The correction accurately reflects the current state of the repository, which lacks packaging metadata (`setup.py` or `pyproject.toml`) and instead relies on source-tree execution via `PYTHONPATH`.

```text
VERDICT: ACCEPT

Reasons:
- Technical Accuracy: The removal of `python3 -m pip install -e .` from README.md is correct because the repository does not contain the necessary packaging files for an editable install.
- Usage Contract: Explicitly stating the requirement for `PYTHONPATH=src:.` aligns the documentation with the actual functional requirement for running examples and tests in v1.0.
- Regression Testing: The addition of `test_root_quickstart_matches_source_tree_usage_contract` to `tests/goal646_public_front_page_doc_consistency_test.py` ensures this unsupported command isn't reintroduced accidentally.
- Claim Preservation: The change is strictly limited to setup/usage instructions and does not alter any performance or feature claims established for the v1.0 release.
- Release Integrity: It is acceptable to apply this as a documentation fix on `main`. Since it does not change the codebase logic or the verified "v1.0" software state, maintaining the existing tag while correcting the public-facing instructions is appropriate.

Required fixes:
- None.
```
