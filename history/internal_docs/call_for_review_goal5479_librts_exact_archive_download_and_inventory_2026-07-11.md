# Call for Review: Goal5479 LibRTS Exact Archive Download And Inventory

Review:

```text
history/internal_docs/goal5479_librts_exact_archive_download_and_inventory_2026-07-11.md
Paper-reproduction-apps/librts-paper/results/librts_goal5479_pod_download_verified.json
Paper-reproduction-apps/librts-paper/results/librts_goal5479_archive_inventory.json
Paper-reproduction-apps/librts-paper/extract_verified_ae_archive.py
tests/goal5474_librts_resume_safe_dataset_acquisition_test.py
tests/goal5475_librts_safe_archive_extraction_test.py
```

Questions:

1. Do exact size and published MD5 establish the official archive identity?
2. Does inventory cover every member before extraction?
3. Is allowing only in-root relative symlinks necessary and still fail-closed?
4. Does delayed symlink creation prevent link-directed archive writes?
5. Are extraction, individual exact inputs, figures, ratios, and Embree still
   correctly unclaimed?

Requested verdict:

```text
approve_goal5479_librts_exact_archive_download_and_safe_inventory
```
