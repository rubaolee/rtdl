# Call for Review: Goals5480-5481 LibRTS Exact Point-Contains

Please strictly review the first exact official-input LibRTS gate.

Primary report:

`history/internal_docs/goal5480_5481_librts_exact_point_contains_result_2026-07-11.md`

Machine evidence:

- `Paper-reproduction-apps/librts-paper/results/librts_goal5479_pod_download_verified.json`
- `Paper-reproduction-apps/librts-paper/results/librts_goal5479_archive_inventory.json`
- `Paper-reproduction-apps/librts-paper/results/librts_goal5480_point_contains_subset_extraction.json`
- `Paper-reproduction-apps/librts-paper/results/librts_goal5481_exact_point_contains.json`

Implementation/tests:

- `extract_verified_ae_archive.py`
- `extract_verified_ae_subset.py`
- `run_exact_point_contains_count_gate.py`
- `tests/goal5475_librts_safe_archive_extraction_test.py`
- `tests/goal5478_librts_exact_point_contains_runner_contract_test.py`
- `tests/goal5480_librts_safe_subset_extraction_test.py`

Review questions:

1. Is reusing a completed size/MD5/safe-inventory evidence file acceptable for
   selected-member extraction while still revalidating selected paths/types?
2. Does atomic selected-member extraction honestly solve the hidden POD quota
   without claiming full archive extraction?
3. Are member size and SHA-256 sufficient to bind the two exact inputs back to
   the verified official archive?
4. Does MULTIPOLYGON expansion correctly explain and close the 3,143 WKT rows
   versus 12,234 author polygon records mismatch?
5. Does `136475 == 136475` establish bounded exact-input count correctness?
6. Is it correct to refuse pair-row equality because the standard author binary
   exposes count only?
7. Is the RTDL route genuinely generic and app-neutral?
8. Are timing denominators kept separate enough to forbid a performance ratio?
9. Do claims correctly stop short of Figure 6 and full-paper reproduction?
10. May Goals5480-5481 close as the first exact official-input correctness row?

Requested verdict:

```text
approve_goal5480_5481_librts_exact_point_contains_count_gate
```
