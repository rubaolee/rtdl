# Goal5474: LibRTS Resume-Safe Exact Archive Acquisition Gate

Date: 2026-07-11

## Objective

Turn Goal5473's resource decision into an executable, fail-closed acquisition
protocol without downloading the 23.1 GB archive on an unsuitable host.

## Implementation

Added the app-owned runner:

```text
Paper-reproduction-apps/librts-paper/acquire_exact_ae_archive.py
```

It has three explicit modes:

```text
plan      detect host resources and emit the acquisition contract;
download  require every resource gate, resume with curl into a .part file,
          verify byte size and MD5, then atomically promote the file;
verify    verify an already-promoted archive without downloading it.
```

The archive contract is pinned to:

```text
Zenodo record: 14209767
file:          PPoPPAE-v2.tar.gz
size:          23,062,425,365 bytes
MD5:           89e589f086038f1cd3af9e3ed67da8c8
```

## Fail-Closed Properties

Download is authorized only when these detected acquisition conditions hold:

```text
Linux host;
at least 70 GiB free disk;
at least 64 GiB RAM.
```

GPU VRAM is tracked in a separate paper-execution suitability gate. A host may
legitimately acquire, verify, and inventory the archive without being able to
run every paper workload. This separation was added after the first suitable
POD exposed 20 GiB VRAM alongside ample RAM/disk.

The curl command uses `--continue-at -`, retries transient failures, and writes
only to `PPoPPAE-v2.tar.gz.part`. A failed transfer leaves the partial file for
resume. Promotion uses `os.replace` only after both exact byte length and MD5
match. A wrong length or checksum leaves the partial file in place and creates
no final archive.

Missing `nvidia-smi` is not treated as a crash or as permission to continue; it
becomes `gpu=unavailable`, `vram=0`, and a failed resource gate.

## Evidence

Committed machine-readable plan:

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5474_resume_safe_acquisition_plan.json
```

The plan was generated on the current Windows host and correctly records:

```text
status = resume_safe_acquisition_prepared__host_resource_gate_failed
download_authorized = false
download_executed = false
archive_verified = false
archive_extracted = false
exact_inputs_acquired = false
```

Focused validation:

```text
py -m unittest tests.goal5474_librts_resume_safe_dataset_acquisition_test -v

Ran 5 tests
OK
```

The tests cover combined resource authorization, resumable curl construction,
missing `nvidia-smi`, acquisition-vs-execution resource separation, verified
atomic promotion, and size/MD5 failure without promotion. They use a tiny
temporary file and perform no network transfer.

## Scope And Ownership

This runner is paper-app infrastructure. It does not add a public RTDL API or
change `src/rtdsl` / `src/native`. Its constants and Zenodo provenance are
specific to the LibRTS reproduction package and belong here.

## What This Proves

- the exact AE archive has a pinned, resume-safe acquisition protocol;
- unsuitable hosts fail closed before download;
- a completed transfer cannot become the official archive without size and
  MD5 verification;
- the next suitable POD can resume rather than restart a partial transfer.

## What This Does Not Prove

- the archive has been downloaded, verified, or extracted;
- the archive contains every expected exact input after extraction;
- any paper figure has been reproduced;
- any author/RTDL performance ratio is valid;
- Embree is in scope.

## Exit

```text
completed_resume_safe_exact_archive_acquisition_gate__download_not_executed__review_pending
```

Next: run `plan` on a suitable Linux RTX POD, execute `download`, then open a
separate safe-extraction and dataset-inventory gate before any figure run.
