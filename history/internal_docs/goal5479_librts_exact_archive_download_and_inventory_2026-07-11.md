# Goal5479: LibRTS Exact Archive Download And Inventory

Date: 2026-07-11

## Download And Verification

The official Zenodo v2 archive completed through the Goal5474 resumable gate:

```text
file = PPoPPAE-v2.tar.gz
size = 23,062,425,365 bytes
MD5 = 89e589f086038f1cd3af9e3ed67da8c8
verified = true
promoted_from_partial = true
```

Evidence:

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5479_pod_download_verified.json
```

## Safe Inventory

The Goal5475 gate reverified the archive and scanned every member without
extracting it:

```text
member_count = 1,694
file_count = 1,370
directory_count = 321
safe_relative_symlink_count = 3
unpacked_file_bytes = 88,229,246,574
top_level_entries = [PPoPPAE]
safe = true
```

The first strict inventory run correctly rejected all symlinks. Inspection
showed the official AE contains safe relative source-tree links. The gate was
amended to allow only relative links whose lexical target remains inside the
extraction root; they are created only after all regular files are written.
Escaping links, hardlinks, devices, special files, traversal, duplicates, and
destructive replacement remain rejected.

Evidence:

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5479_archive_inventory.json
```

## Boundary

This closes official archive acquisition and safe inventory. It does not close
extraction, identification of individual exact input files, any paper figure,
performance ratio, complete 24 GiB matrix capacity, or Embree evidence.

## Exit

```text
completed_exact_archive_download_md5_and_safe_inventory__extraction_pending__review_pending
```
