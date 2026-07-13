# Goal5432 - X-HD Public Artifact Live Refresh

## Verdict

```text
public_artifact_refresh_no_new_exact_input_path__external_response_chain_still_needed
```

Goal5432 performs a live refresh of public X-HD artifact/provenance surfaces
after Goal5431 prepared the WaterBodies->BlockGroups outbox drafts.

It does not run POD, author code, RTDL code, route code, or performance tests.
It does not send any request, receive any response, acquire artifacts, or accept
exact-equivalence.

## Result Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5432_public_artifact_live_refresh.json
```

## Surfaces Refreshed

Goal5432 directly checked:

```text
ACM supplement URLs for ics26-106.zip
Crossref DOI metadata for 10.1145/3797905.3800509
GitHub repo metadata / releases / contents / recursive tree for pwrliang/X-HD
Rubao Lee public PDF URL
Liang Geng publication page URL
```

## Main Findings

ACM supplement:

```text
artifact = ics26-106.zip
HEAD / ranged GET checks = 403 across the checked ACM URLs
zip_magic_observed = false
acm_supplement_inspected = false
```

Crossref:

```text
status = 200
title = X-HD: Fast Hausdorff Distance Computation with Ray Tracing
link_count = 1
dataset_or_artifact_link_found = false
```

GitHub:

```text
repo = pwrliang/X-HD
branches:
  main   = 7bf41c8442d059c94f4178355c6d5a10571d9658
  paper  = 8c3846866052e1e8755210021f23fac2cbe8c3d6
  hybrid = 4d9046a9e55d87f35daf81dd718444029fab56ce
release_count = 0
root_data_directory_found = false
dataset_archive_release_found = false
tree_likely_input_dataset_blob_found = false
```

The recursive tree still has many dataset-like names inside checked-in logs
(`.wkt`, `.nii`, etc.), but those are author log filenames, not the input
dataset bytes, HDDatasets bundle, release asset, or exact paper input hash
manifest.

Author/public pages:

```text
public PDF URL reachable
publication page URL reachable
no dataset artifact surfaced by the prefix probes
```

## Classification

```text
new_public_exact_input_artifact_found = false
external_artifacts_acquired = false
exact_input_blocker_removed = false
acm_supplement_inspected = false
```

Therefore the exact/full X-HD blocker is unchanged:

```text
Need author files/hashes, byte-identical regeneration, ACM-access supplement
inspection, or explicit external exact-equivalence acceptance.
```

## Claim Boundary

Authorized:

```text
public_artifact_refresh_claimed = true
```

Not authorized:

```text
new_public_exact_input_artifact_found = false
external_artifacts_acquired = false
exact_equivalence_accepted = false
exact_paper_dataset_reproduction_claimed = false
figure5_reproduction_claimed = false
full_xhd_paper_reproduction_claimed = false
performance_ratio_claimed = false
pod_execution_claimed = false
new_rtdl_route_code_added = false
explicit_lb_reopened = false
route_micro_optimization_goal_authorized = false
```

## Stop-Loss Gate G-1

This is provenance refresh, not app-artifact parity implementation.

```text
gate_generic_capability_produced: true
gate_non_app_consumer: public artifact availability refresh / external provenance decision
gate_requires_app_specific_logic: false
gate_downstream_consumer_reachable: true
```

Decision:

```text
PASS: provenance refresh, not app-artifact parity implementation.
```

## Validation

Commands:

```text
py Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5432_public_artifact_live_refresh.py
py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5432_public_artifact_live_refresh.py
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5432_public_artifact_live_refresh.json
py scripts/xhd_stop_loss_gate_check.py history/internal_docs/goal5432_xhd_public_artifact_live_refresh_2026-07-10.md history/internal_docs/call_for_review_goal5432_xhd_public_artifact_live_refresh_2026-07-10.md
py -m unittest tests.goal5432_public_artifact_live_refresh_test tests.goal5431_water_bg_outbox_refresh_test tests.goal5430_water_bg_exact_equivalence_packet_test tests.goal5329_xhd_external_response_intake_protocol_test
```

The known Windows Python prefix warning may appear and is not a failure if the
commands exit successfully.

## Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5432_public_artifact_live_refresh.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5432_public_artifact_live_refresh.json
tests/goal5432_public_artifact_live_refresh_test.py
history/internal_docs/goal5432_xhd_public_artifact_live_refresh_2026-07-10.md
history/internal_docs/call_for_review_goal5432_xhd_public_artifact_live_refresh_2026-07-10.md
```

## Next Recommended Action

```text
send_or_review_goal5431_outbox_or_wait_for_external_author_acm_response
```

No POD work is expected until a positive response supplies author files/hashes,
byte-identical regeneration instructions, inspectable ACM supplement contents,
or accepted exact-equivalence.

## Not Allowed Summary

Do not say:

```text
The ACM supplement was inspected.
The ACM supplement contains no useful artifacts.
All publication-adjacent artifacts are exhausted.
X-HD exact paper inputs were recovered.
Figure 5 or full X-HD paper reproduction is complete.
RTDL/author performance ratios are available.
```

Allowed summary:

```text
Goal5432 refreshed live public X-HD artifact surfaces. It found no new public
exact-input path: ACM supplement URLs remain forbidden from this environment,
Crossref exposes no dataset/artifact link, GitHub has no release/data directory
or likely input dataset blob, and author/public pages did not reveal exact input
artifacts. The exact-input blocker remains external.
```
