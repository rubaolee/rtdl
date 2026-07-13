# Call For Review: Goal5328 X-HD External Request Outbox

Please strictly review Goal5328.

## Files To Review

```text
Paper-reproduction-apps/x-hd-paper/requests/README.md
Paper-reproduction-apps/x-hd-paper/requests/author_input_provenance_request.md
Paper-reproduction-apps/x-hd-paper/requests/acm_supplement_inspection_request.md
Paper-reproduction-apps/x-hd-paper/requests/water_bg_exact_equivalence_review_request.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5328_external_request_outbox.json
tests/goal5328_xhd_external_request_outbox_test.py
history/internal_docs/goal5328_xhd_external_request_outbox_result_2026-07-09.md
```

Supporting context:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5326_external_artifact_request_package.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5327_acm_supplement_public_metadata_followup.json
```

## Goal5328 Summary

Goal5328 creates send-ready local request drafts:

```text
author_input_provenance_request.md
acm_supplement_inspection_request.md
water_bg_exact_equivalence_review_request.md
```

It also records public author contact metadata from the paper PDF first page
and preserves a strict not-sent claim boundary.

Exit label:

```text
external_request_outbox_ready__await_owner_send
```

## Review Questions

1. Is turning Goal5326/5327 into a local outbox the right next step toward
   full paper reproduction?
2. Are the author recipients and contact-source boundaries acceptable?
3. Does the author request ask for all relevant exact input provenance across
   graphics, geo, BraTS, hashes, preprocessing, and config?
4. Does the ACM request preserve the unresolved `ics26-106.zip` boundary?
5. Is the WaterBodies/BG exact-equivalence request fail-closed and correctly
   worded?
6. Is it correct that no POD is needed?
7. Are claim boundaries complete: prepared but not sent; no artifacts acquired;
   no ACM contents known; no exact/full-paper/performance claim?
8. Is the exit label acceptable?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goal5328_external_request_outbox_ready
or
Verdict: approve_with_required_amendments
or
Verdict: block_goal5328

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to review questions:
1. ...
2. ...
...
8. ...
```
