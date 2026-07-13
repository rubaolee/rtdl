# X-HD External Action Dispatch Bundle

Status: `prepared_not_sent`

This directory gathers the currently prepared external requests and one
receipt stub per sendable request. It is a handoff bundle only.
It does not claim that any request was sent.

## Sendable Requests

### general_author_input_provenance_request

```text
request_path = Paper-reproduction-apps/x-hd-paper/requests/author_input_provenance_request.md
audience = X-HD authors / artifact owner
purpose = Ask for exact paper input provenance across X-HD datasets.
sha256_at_prepare_time = f3d0af4d7157c06fa0abeb0a9a3d235a8d84e20a53a316a69e239b22f2736b38
receipt_stub = Paper-reproduction-apps/x-hd-paper/requests/send_bundle/receipts/general_author_input_provenance_request_receipt_stub.json
sent = false
```

### general_acm_supplement_inspection_request

```text
request_path = Paper-reproduction-apps/x-hd-paper/requests/acm_supplement_inspection_request.md
audience = ACM supplement access holder / owner
purpose = Ask for authorized inspection of ACM supplement contents.
sha256_at_prepare_time = 013f646400945f88c9ca1744dfd5973201102ffc7124c875c7a7cf9a12789423
receipt_stub = Paper-reproduction-apps/x-hd-paper/requests/send_bundle/receipts/general_acm_supplement_inspection_request_receipt_stub.json
sent = false
```

### water_bg_author_hash_request

```text
request_path = Paper-reproduction-apps/x-hd-paper/requests/author_water_bg_input_hash_request.md
audience = X-HD authors / artifact owner
purpose = Ask specifically for WaterBodies/BG paper-run WKT hashes, bytes, or regeneration provenance.
sha256_at_prepare_time = 8a48cb4ed38f7291b7e0677c5f71d88fbd8688f3604a60d5224b5448e6de3d12
receipt_stub = Paper-reproduction-apps/x-hd-paper/requests/send_bundle/receipts/water_bg_author_hash_request_receipt_stub.json
sent = false
```

### water_bg_exact_equivalence_review_request

```text
request_path = Paper-reproduction-apps/x-hd-paper/requests/water_bg_exact_equivalence_review_request.md
audience = owner or external reviewer
purpose = Ask whether the current Water/BG public reconstruction can be accepted under a bounded renamed claim.
sha256_at_prepare_time = 075f54412c7187aa003df85cf8eaf1f892b06fd0f895a0c2946d046bf5671875
receipt_stub = Paper-reproduction-apps/x-hd-paper/requests/send_bundle/receipts/water_bg_exact_equivalence_review_request_receipt_stub.json
sent = false
```

## How To Use

1. Review the selected request text.
2. If the owner sends it outside this repository, copy the matching
   receipt stub, fill the send fields, and place the real receipt in
   `Paper-reproduction-apps/x-hd-paper/requests/sent/`.
3. If a response arrives, normalize it into
   `Paper-reproduction-apps/x-hd-paper/requests/incoming/` before
   running the response inbox gate.

## Claim Boundary

```text
external_action_dispatch_bundle_claimed = true
request_sent_claimed = false
external_response_received = false
external_artifacts_acquired = false
exact_equivalence_accepted = false
exact_paper_dataset_reproduction_claimed = false
figure5_reproduction_claimed = false
full_xhd_paper_reproduction_claimed = false
performance_ratio_claimed = false
pod_execution_claimed = false
```

## Stop-Loss Rule

```text
gate_generic_capability_produced: true
gate_non_app_consumer: external action dispatch bundle / receipt workflow
gate_requires_app_specific_logic: false
gate_downstream_consumer_reachable: true
```
