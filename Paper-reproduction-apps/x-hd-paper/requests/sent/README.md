# X-HD External Request Sent Receipts

Status: `no_request_sent`

Put one JSON receipt in this directory for each external request that the owner
actually sends. Start from:

```text
Paper-reproduction-apps/x-hd-paper/requests/external_request_send_receipt_template.json
```

Each receipt must copy the `request_id`, `request_path`, and
`request_sha256_at_send_time` from:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5438_external_request_send_manifest.json
```

A receipt proves only that a prepared request was sent. It does not prove that a
response arrived, artifacts were acquired, exact equivalence was accepted, or
any X-HD paper figure was reproduced.
