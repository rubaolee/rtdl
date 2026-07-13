# Goal5475: LibRTS Safe Archive Extraction And Inventory Gate

Date: 2026-07-11

## Objective

Prepare the reviewed boundary between a verified 23.1 GB AE archive and usable
paper inputs. Do not extract or identify exact datasets before the archive is
present and verified.

## Implementation

Added the app-owned runner:

```text
Paper-reproduction-apps/librts-paper/extract_verified_ae_archive.py
```

Modes:

```text
plan       emit paths and safety contract without requiring the archive;
inventory  require Goal5474 size+MD5 verification, inspect every tar member;
extract    repeat verification/inventory, extract into staging, then atomically
           promote the complete directory.
```

The inventory rejects absolute paths, `..`, backslash/drive-prefix escapes,
duplicate paths, hardlinks, devices, and other special members. Safe relative
symlinks are allowed only when lexical resolution remains inside the extraction
root. It checks member count plus total expanded file bytes before extraction.

Extraction writes only under `.PPoPPAE-v2.extracting`, checks every extracted
file size and final aggregate file/byte counts, and promotes the directory with
`os.replace` only after the complete pass. Symlinks are created only after all
regular files are written, preventing link-directed archive writes. Existing staging or final paths fail
closed rather than being overwritten or deleted.

## Evidence

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5475_safe_extraction_plan.json
```

The committed plan truthfully records:

```text
status = safe_extraction_contract_ready__verified_archive_absent
archive_present = false
archive_verified = false
inventory_completed = false
archive_extracted = false
exact_input_files_identified = false
```

Validation:

```text
py -m unittest tests.goal5475_librts_safe_archive_extraction_test -v

Ran 4 tests
OK
```

The tests cover safe nested extraction, traversal/backslash rejection,
symlink/duplicate rejection, and the inherited exact size+MD5 verification
contract. They use tiny generated tar archives and do not access the network.

## Ownership And Claims

This is LibRTS app infrastructure, not an RTDL core API. It changes neither
`src/rtdsl` nor `src/native`. It proves a safe extraction protocol only. It
does not prove archive acquisition, inventory of the real archive, exact input
identity, figure reproduction, performance comparison, or Embree evidence.

## Exit

```text
completed_safe_extraction_inventory_contract__real_archive_absent__review_pending
```

Next: on a suitable POD, complete Goal5474 download/verification, run Goal5475
inventory, review the real top-level/data inventory, then authorize extraction.
