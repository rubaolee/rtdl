# V3.0 Pod Evidence Probe

Date: 2026-06-15

Status: pass for V3 evidence substrate; not a benchmark.

## Result

The V3.0 pod evidence probe passed on the RTX pod at commit `4dcc3a45`.

| Check | Result |
| --- | --- |
| Pod hardware | NVIDIA RTX 4000 Ada Generation, driver 550.127.08, 20475 MiB |
| Native OptiX library | Loadable: `build/librtdl_optix.so` |
| Native Embree library | Loadable: `build/librtdl_embree.so` |
| Embree version | 4.3.0 |
| CUDA event probe | Passed |
| V3 same-stream readiness | Passed for the OptiX substrate packet |
| V3 device-resident readiness | Passed for the OptiX substrate packet |
| V3 true-zero-copy readiness | Passed for the OptiX substrate packet under the probe's explicit-transfer counter |
| Public speedup claim | Still forbidden |

The raw JSON evidence is stored in
`docs/reports/goal4401_v3_0_pod_evidence_probe_2026-06-15.json`.

## Timings Observed

| Measurement | Seconds | Meaning |
| --- | ---: | --- |
| CUDA event region | 0.246755524 | CuPy device operation between CUDA events on a non-default stream |
| Validation wrapper | 0.399113536 | Host-side validation wrapper, including the post-event scalar download |
| Embree native load | 0.001315765 | Native library load/version substrate check only |

The CUDA event timing does not represent RTDL V3 graph execution, OptiX traversal, or RT-core application speed. It proves that the pod can produce CUDA event evidence, pointer evidence, and explicit measured-region transfer accounting in the V3 instrumentation packet shape.

## What This Proves

1. The current pod can run the V3 M1-M7 contract tests: 49 tests passed.
2. The fresh V3 checkout can build/load the native OptiX and Embree libraries on the pod.
3. The V3 M3 instrumentation packet can carry real hardware evidence instead of metadata-only evidence.
4. The claim boundary remains locked: no public speedup, RT-core speedup, or benchmark claim is authorized by this probe.

## What This Does Not Prove

1. It does not prove V3 M4-M7 performance.
2. It does not prove RTDL V3 graph lowering into native OptiX or Embree execution.
3. It does not compare RT cores against Embree CPU cores.
4. It does not replace benchmark-app evidence.

## Next Gate

The next useful V3.0 step is a measured lowering pilot: take one V3 primitive/continuation graph, lower it into an actual native backend/partner execution path, and require the same evidence packet fields around that real workload. The first target should be the smallest graph that still exercises the V3 promise:

- prepared backend handle
- device-resident stream handoff
- same-stream partner continuation
- separated setup/traversal/continuation/materialization timing
- no public claim promotion until benchmark-scale rows pass
