# Call for Review: Goal5475 LibRTS Safe Archive Extraction And Inventory Gate

Please strictly review:

```text
history/internal_docs/goal5475_librts_safe_archive_extraction_and_inventory_gate_2026-07-11.md
Paper-reproduction-apps/librts-paper/extract_verified_ae_archive.py
Paper-reproduction-apps/librts-paper/results/librts_goal5475_safe_extraction_plan.json
tests/goal5475_librts_safe_archive_extraction_test.py
```

Questions:

1. Must exact size+MD5 verification precede real inventory/extraction?
2. Are path traversal, Windows separator/drive escapes, duplicate paths,
   escaping symlinks, hardlinks, devices, and special files rejected while
   safe relative in-root symlinks remain usable?
3. Are expanded size and available disk checked before extraction?
4. Does extraction remain in staging until file/byte totals match inventory?
5. Do existing staging/final paths fail closed without destructive cleanup?
6. Is the committed artifact correctly classified as contract-only because the
   real archive is absent?
7. Is this correctly app-owned, with no RTDL core or Embree claim?

Requested verdict:

```text
approve_goal5475_librts_safe_archive_extraction_inventory_gate
```
