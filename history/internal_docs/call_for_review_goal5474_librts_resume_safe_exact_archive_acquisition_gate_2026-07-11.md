# Call for Review: Goal5474 LibRTS Resume-Safe Exact Archive Acquisition Gate

Please strictly review:

```text
history/internal_docs/goal5474_librts_resume_safe_exact_archive_acquisition_gate_2026-07-11.md
Paper-reproduction-apps/librts-paper/acquire_exact_ae_archive.py
Paper-reproduction-apps/librts-paper/results/librts_goal5474_resume_safe_acquisition_plan.json
tests/goal5474_librts_resume_safe_dataset_acquisition_test.py
```

## Review Questions

1. Does the acquisition gate correctly require Linux, disk, and RAM while
   tracking 24 GiB GPU VRAM separately as paper-execution suitability?
2. Does the download command resume into a `.part` file and preserve it after
   transfer failure?
3. Are exact byte size and MD5 both required before atomic promotion?
4. Does a failed checksum leave the partial file visible and avoid a final
   archive?
5. Does missing `nvidia-smi` fail closed instead of crashing or authorizing?
6. Is extraction correctly kept as a separate future gate?
7. Is this correctly app-owned rather than a public RTDL system primitive?
8. Does the result avoid claiming download, exact inputs, figure reproduction,
   performance comparison, or Embree evidence?
9. Is a suitable Linux RTX POD now the correct next resource for this line?

Requested verdict label:

```text
approve_goal5474_librts_resume_safe_exact_archive_acquisition_gate
```
