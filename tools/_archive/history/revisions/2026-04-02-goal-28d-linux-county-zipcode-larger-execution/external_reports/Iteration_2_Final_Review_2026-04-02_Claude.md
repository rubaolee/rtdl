**Technical correctness review:**

**Staging (goal28b_stage_uscounty_zipcode.py):**
- Resume logic is correct: tries to read existing page, catches `json.JSONDecodeError` and `OSError`, falls back to re-fetch on failure. Matches the corrupt-tail claim.
- `reused_existing` flag is tracked per-page and reflected in the manifest. Test coverage is direct and complete for both the happy-path reuse and corrupt-fallback cases.
- One minor note: `reused_existing` is set `True` before the try-block but reassigned `False` inside the except. The logic is sound; `decoded` is also populated in the success case so the rest of the loop body is safe.

**Slice selection (goal28d_complete_and_run_county_zipcode.py):**
- `face_records` correctly uses `left_face_id` to group chains into face-level records. Bbox merge and overlap check logic are standard and correct.
- `select_county_zipcode_slice` picks the minimum estimated-segment-cost county that meets `min_zip_matches`, then takes the `target_zip_matches` lowest-cost overlapping zipcodes. This matches the documented co-location selection method.
- Test covers both the preferring-overlapping-low-cost-candidate case and the subset-by-face-id filter. The test geometry is realistic: one county in [0,4]² with two in-bounds zipcodes vs. one remote zipcode at [101,102]² — correctly expects the in-bounds county and the two in-bounds zipcodes only.
- Execution driver correctly writes JSON + Markdown summaries, times via `perf_counter`, separates CPU and Embree runs.

**Report honesty:**
- The report explicitly states the `1×5`, `1×6`, `1×8` exploratory runs were not parity-clean for `lsi` and excludes them from accepted results.
- The accepted `1×4` slice (631 estimated segments) is modestly larger than Goal 28C's first-page proof. The boundary section states this is not paper-scale reproduction, which is accurate.
- The `lsi` result of 2 CPU rows / 2 Embree rows is plausible for a 1-county × 4-zipcode slice (small number of actual intersecting segment pairs).

**Scope match against goal definition:**
- Full `Zipcode` staging complete: documented (32294 features, 130 pages). ✓
- Resumable acquisition added: implemented and tested. ✓
- Larger co-located execution slice run on Linux: done. ✓
- CPU/Embree parity for accepted slice: `lsi` `true`, `pip` `true`. ✓
- Claims bounded by what the host can actually execute: exploratory failures honestly disclosed, only parity-clean slice accepted. ✓

**No remaining blockers.**

Approved
