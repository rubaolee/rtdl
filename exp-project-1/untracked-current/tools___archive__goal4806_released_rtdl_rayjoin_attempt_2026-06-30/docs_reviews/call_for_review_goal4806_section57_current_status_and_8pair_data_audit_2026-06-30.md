# Call For Review: Goal4806 Section 5.7 Current Status And 8-Pair Data Audit

Date: 2026-06-30

Please review:

`docs/reports/goal4806_rayjoin_section57_current_status_and_8pair_data_audit_2026-06-30.md`

Supporting data-acquisition audit:

- `scripts/rayjoin_section57_data_acquisition_audit.py`
- `docs/reports/goal4806_section57_data_acquisition_audit_current_2026-06-30.json`
- `docs/reports/goal4806_section57_data_acquisition_audit_network_2026-06-30.json`

## Review Question

Is the current Goal4806 status recorded honestly and technically correctly:

- Section 5.7 reproduction should be a language/system-stack swap only;
- County x Zipcode full overlay is byte-equal and therefore a real correctness
  slice;
- V4+Numba has only candidate-stage evidence, not full overlay speed evidence;
- all-eight-pair completion is currently blocked by missing exact CDB inputs;
- historical V2.14 evidence covers two pairs, not the full Section 5.7 suite?

## Required Checks

1. Does the report correctly preserve the RayJoin paper/author-code contract:
   same data, same LSI/PIP/output-chain semantics, same precision/SOS rules, and
   only changed implementation stack?
2. Does the byte-equal County x Zipcode evidence justify a correctness-slice
   claim, but not a high-performance claim?
3. Is the V4+Numba measurement correctly classified as candidate-stage
   post-traversal continuation evidence rather than full overlay evidence?
4. Is the fresh POD setup result interpreted correctly: author binaries and GPU
   are ready, but only one of eight exact Section 5.7 CDB input pairs is present?
5. Is the historical V2.14 matrix interpreted correctly as 2/8 complete, not
   8/8 complete?
6. Does the new data-acquisition audit correctly distinguish:
   - exact paper-preprocessed CDB coverage;
   - U.S. same-source regenerated CDB coverage;
   - missing Lakes/Parks source-target coverage?
7. Is it correct that the live ArcGIS FeatureServer route can support a U.S.
   same-source 2/8 engineering slice, while not authorizing a recovered
   paper-preprocessed-CDB claim?
8. Are the listed next paths honest and sufficient?
9. Should Goal4806 proceed by acquiring/regenerating missing CDB inputs, by
   externally closing the County x Zipcode slice, or by first optimizing the
   County x Zipcode full-output path?

## Non-Authorization

This review request does not authorize:

- public Section 5.7 high-performance claims;
- V4+Numba RayJoin release claims;
- replacing same-machine author-code comparison with paper-table numbers;
- changing the workload after seeing results;
- treating one pair as all-eight-pair completion;
- treating candidate-stage Numba evidence as full polygon-overlay speedup.
