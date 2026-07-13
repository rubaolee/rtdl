# Call For Review: Goal5326 X-HD External Artifact Request Package

Please strictly review Goal5326.

## Files To Review

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5326_external_artifact_request_package.json
tests/goal5326_xhd_external_artifact_request_package_test.py
history/internal_docs/goal5326_xhd_external_artifact_request_package_result_2026-07-09.md
```

Supporting context:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5324_exact_input_acquisition_and_equivalence_decision_packet.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5325_public_web_supplement_artifact_sweep.json
history/internal_docs/call_for_review_goals5318_5324_xhd_exact_provenance_blocker_and_acquisition_decision_packet_2026-07-09.md
history/internal_docs/call_for_review_goal5325_xhd_public_web_supplement_artifact_sweep_2026-07-09.md
```

## Goal5326 Summary

Goal5326 converts the current exact-input blocker into a sendable request
package.

Request targets:

```text
paper_authors;
acm_access_reviewer;
owner_or_external_review.
```

It asks for:

```text
author input files or hashes;
byte-identical regeneration scripts;
converted point-set hashes;
command/config details;
ACM `ics26-106.zip` file listing and artifact contents;
an explicit WaterBodies/BG exact-equivalence decision if artifacts are absent.
```

Exit label:

```text
external_artifact_request_package_ready__await_owner_send_or_external_response
```

## Review Questions

1. Is preparing an external artifact request package the correct next step
   after Goals5318-5325 classified exact input provenance as the blocker?
2. Does the author request cover the required graphics, geo, BraTS, conversion,
   hash, and command/config evidence?
3. Does the ACM supplement request correctly treat `ics26-106.zip` as unresolved
   rather than known-positive or known-negative?
4. Are the minimum acceptable response types complete and actionable?
5. Is the WaterBodies/BG exact-equivalence question framed fail-closed?
6. Is it correct that Goal5326 does not use POD?
7. Are claim boundaries complete: no sent-request claim, no acquired-artifact
   claim, no ACM-content claim, no Figure 5/full-paper/performance claim?
8. Is the exit label acceptable?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goal5326_external_artifact_request_package_ready
or
Verdict: approve_with_required_amendments
or
Verdict: block_goal5326

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
