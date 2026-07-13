# Call For Review - v2.14.3 Internal Release Packet

Date: 2026-07-05

Please review:

```text
history/internal_docs/v2_14_3_internal_release_packet_2026-07-05.md
history/internal_docs/v2_14_3_internal_release_manifest_2026-07-05.json
```

## Review Questions

1. Does the internal release packet correctly classify this as an internal
   release, not an external/public release?
2. Does it preserve the canonical v2.14.3 performance numbers:
   `~4.22s` warm-process fresh fast-pack, `~1.22s/query` prepared same-domain,
   and `~0.46-0.47s/query` locator prepare floor?
3. Does it correctly disclose the cold CLI one-shot evidence as noisy and
   separate from the warm-process product-facing number?
4. Does it correctly stop the device-resident carrier performance track for
   v2.14.3 while retaining the code path as experimental architecture work?
5. Does it correctly reject 10x, author parity, full zero-copy, full
   device-resident execution, replay-as-query-many, and unmeasured top4 author
   ratio claims?
6. Does it correctly classify the dirty working tree as retained project state
   rather than transient cache?
7. Is the public-surface scan result sufficient for internal release staging?
8. Is the final label appropriate:
   `internal_release_v2_14_3_staged_with_bounded_rayjoin_performance`?

Requested verdict label:

```text
approve_v2_14_3_internal_release_staging_packet
```
