Both required amendments are verified against the on-disk files. Checking each:

**Required amendment 1 — amendment closure cited in Step 4:**
Protocol line 25 now includes `claude_v4_section8_device_array_frontdoor_amendment_closure_2026-06-24.md` as the third citation in the Torch device-array front door row, and the Result column explicitly records `authorized_next_step = external_review_then_productize_fixed_radius_api_wrapper_before_second_primitive` with "Second primitive work must not start until the fixed-radius API wrapper is productized." ✓

**Required amendment 2 — G3 prerequisite clause:**
Protocol line 61 now reads "before this starts, the fixed-radius device-array API wrapper must be productized per `external_review_then_productize_fixed_radius_api_wrapper_before_second_primitive`" and the status field reads "`missing`; this is `goal4628`, gated by the fixed-radius wrapper productization prerequisite." ✓

**Test coverage of the non-blocking observation:**
The test's `test_protocol_preserves_non_authorization_boundary` now asserts all 10 non-authorization items, including the two previously absent — `"whole-application speedup wording"` and `"public true-zero-copy wording"` (matching the Non-Authorization section's phrasing at line 129). The test also locks in the amendment closure filename and the prerequisite constraint string. All 3 tests reported OK.

---

`accept_goal4626_scorecard_protocol`
