# Call For Review: Goal4806 RayJoin Section 5.7 County x Zipcode Completion Slice

Date: 2026-06-30

Please review:

`docs/reports/goal4806_rayjoin_section57_county_zipcode_byte_equal_and_numba_candidate_2026-06-30.md`

## Requested Verdict

Please choose one:

- `approve_goal4806_county_zipcode_slice_complete_continue_all_pairs`
- `approve_correctness_only_numba_candidate_needs_more_work`
- `block_due_to_missing_evidence`
- `reject_due_to_wrong_claim_boundary`

## Questions

1. Does the byte-equal County x Zipcode evidence prove RTDL native OptiX
   correctness for that Section 5.7 pair?
2. Is it correct to say this does not authorize author-code speed parity or a
   high-performance Section 5.7 public claim?
3. Is disabling the zero-length midpoint correction justified by the evidence
   recorded in the report?
4. Is the Numba PTX issue correctly handled as a CUDA toolkit/driver mismatch,
   now repaired with CUDA 12.4 NVVM in the temporary POD venv?
5. Is `v4_numba_post_traversal_segmented_counts` the correct selected candidate
   among the measured rows, given the no-host-hot-path selector rule?
6. Does the report correctly reject the faster `mask_compact` row for selector
   purposes because it uses host materialization?
7. Should Goal4806 be considered complete for the County x Zipcode slice, or
   must it continue immediately to all eight Section 5.7 pairs before closure?

## Non-Authorization

This request does not authorize:

- public RayJoin Section 5.7 high-performance claims;
- V4+Numba full-overlay speed claims;
- replacing same-machine author-code comparison with paper-table numbers;
- changing the workload semantics after measurement;
- treating a post-traversal candidate-stage result as full overlay performance.

