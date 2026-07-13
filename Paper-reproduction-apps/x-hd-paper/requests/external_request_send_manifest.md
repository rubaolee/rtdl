# X-HD External Request Send Manifest

Status: `prepared_not_sent`

This manifest records prepared request files and their hashes. It does
not claim that any request was sent.

## Items

### general_author_input_provenance_request

```text
path = Paper-reproduction-apps/x-hd-paper/requests/author_input_provenance_request.md
audience = X-HD authors / artifact owner
sendable_external = true
status = prepared_not_sent
sha256 = f3d0af4d7157c06fa0abeb0a9a3d235a8d84e20a53a316a69e239b22f2736b38
ready_to_send_or_review = true
sent_claimed = false
```

### general_acm_supplement_inspection_request

```text
path = Paper-reproduction-apps/x-hd-paper/requests/acm_supplement_inspection_request.md
audience = ACM supplement access holder / owner
sendable_external = true
status = prepared_not_sent
sha256 = 013f646400945f88c9ca1744dfd5973201102ffc7124c875c7a7cf9a12789423
ready_to_send_or_review = true
sent_claimed = false
```

### water_bg_author_hash_request

```text
path = Paper-reproduction-apps/x-hd-paper/requests/author_water_bg_input_hash_request.md
audience = X-HD authors / artifact owner
sendable_external = true
status = prepared_not_sent
sha256 = 8a48cb4ed38f7291b7e0677c5f71d88fbd8688f3604a60d5224b5448e6de3d12
ready_to_send_or_review = true
sent_claimed = false
```

### water_bg_exact_equivalence_review_request

```text
path = Paper-reproduction-apps/x-hd-paper/requests/water_bg_exact_equivalence_review_request.md
audience = owner or external reviewer
sendable_external = true
status = prepared_not_sent
sha256 = 075f54412c7187aa003df85cf8eaf1f892b06fd0f895a0c2946d046bf5671875
ready_to_send_or_review = true
sent_claimed = false
```

### water_bg_external_action_packet

```text
path = Paper-reproduction-apps/x-hd-paper/requests/water_bg_external_action_packet.md
audience = owner/internal coordinator
sendable_external = false
status = prepared_not_sent
sha256 = ac038dbfb2114b77f215fe717eb26cd440bc1b5364ced563bf9cd3235126965c
ready_to_send_or_review = true
sent_claimed = false
```

## Receipt Template

If the owner sends a request, record a receipt using:

```text
Paper-reproduction-apps/x-hd-paper/requests/external_request_send_receipt_template.json
```

## Claim Boundary

```text
request_send_manifest_claimed = true
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
gate_non_app_consumer: external request send manifest / receipt workflow
gate_requires_app_specific_logic: false
gate_downstream_consumer_reachable: true
```
