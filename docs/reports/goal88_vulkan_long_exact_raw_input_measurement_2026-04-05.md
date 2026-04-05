# Goal 88 Report: Vulkan Long Exact Raw-Input Measurement

Date: 2026-04-05
Status: complete

## Summary

Goal 88 asked a narrow follow-up question after Goal 87:

- now that Vulkan can execute the accepted long exact-source prepared surface,
  what does the repeated raw-input end-to-end story look like on the same
  surface?

The accepted answer is:

- Vulkan is parity-clean
- repeated runs are materially faster than the first raw-input call
- Vulkan still does not beat PostGIS on this surface

So Goal 88 closes the Vulkan raw-input measurement row honestly, even though it
is not a performance win.

## Surface

- host: `lestat-lx1`
- workload: long exact-source `county_zipcode`
- predicate: positive-hit `pip`
- boundary: repeated raw-input calls in one process
- source directories:
  - `/home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/uscounty_feature_layer`
  - `/home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/zipcode_feature_layer`

Artifact:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal88_vulkan_long_exact_raw_input_artifacts_2026-04-05/summary.json`

## Validation

Goal 88 reused the published Goal 77 runtime-cache measurement harness on a
clean Linux clone at the current published Vulkan head:

```bash
cd /home/lestat/work/rtdl_goal88
make build-vulkan
PYTHONPATH=src:. python3 scripts/goal77_runtime_cache_measurement.py \
  --backend vulkan \
  --county-dir /home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/uscounty_feature_layer \
  --zipcode-dir /home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/zipcode_feature_layer \
  --output-dir docs/reports/goal88_vulkan_long_exact_raw_input_artifacts_2026-04-05 \
  --host-label lestat-lx1-goal88
```

## Measured Result

PostGIS:

- run 1: `3.125241542 s`
- run 2: `3.088001120 s`
- run 3: `3.124289108 s`

Vulkan raw-input:

- first run: `16.140240988 s`
- repeated run 2: `6.709643080 s`
- repeated run 3: `6.827988418 s`

Parity:

- row count: `39073`
- SHA-256 digest matched on all reruns
- `parity_preserved_all_reruns`: `true`

## Outcome

Goal 88 establishes:

- Vulkan is now parity-clean on the accepted long exact-source raw-input row.
- Vulkan benefits from repeated-call reuse after the first raw-input call.
- Vulkan still does not beat PostGIS on that row.

Non-claims:

- Goal 88 does not claim any Vulkan performance win.
- Goal 88 does not claim Vulkan joins the mature OptiX/Embree long-workload
  performance closure.

## Interpretation

Goal 87 removed Vulkan's long prepared-execution blocker.
Goal 88 now shows the next honest status point:

- Vulkan has a complete long exact-source measurement story on both the
  prepared and raw-input boundaries
- but it is still materially slower than PostGIS, OptiX, and Embree

The repeated raw-input improvement is real:

- `16.140240988 s` down to `6.709643080 s`

but not enough to make Vulkan competitive on this surface.

## Conclusion

Goal 88 is still useful because it removes uncertainty.

We no longer have to say Vulkan is "not measured" on the accepted long
exact-source raw-input surface. We can now say exactly what it is:

- parity-clean
- improved by repeated-call reuse
- still not performance-competitive
