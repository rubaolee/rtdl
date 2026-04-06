# RTDL Generate-Only Handoff Bundle

This bundle was generated from RTDL Goal 113 generate-only maturation.

## Request

- workload: `segment_polygon_hitcount`
- dataset: `authored_segment_polygon_minimal`
- backend: `cpu_python_reference`
- verify: `true`
- output mode: `summary`
- artifact shape: `handoff_bundle`

## Files

- `generated_segment_polygon_hitcount_cpu_python_reference_authored_segment_polygon_minimal.py`: runnable generated RTDL program
- `request.json`: structured request manifest
- `README.md`: this handoff note

## Run

From the RTDL repo root:

```bash
PYTHONPATH=src:. python3 examples/rtdl_generated_segment_polygon_bundle/generated_segment_polygon_hitcount_cpu_python_reference_authored_segment_polygon_minimal.py
```

The generated program contains:

- the RTDL kernel
- accepted dataset construction logic
- the requested backend runner
- verification against `cpu_python_reference` when enabled
