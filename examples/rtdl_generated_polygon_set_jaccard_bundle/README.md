# RTDL Generate-Only Handoff Bundle

This bundle was generated from the current RTDL generate-only workflow.

## Request

- workload: `polygon_set_jaccard`
- dataset: `authored_polygon_set_jaccard_minimal`
- backend: `cpu_python_reference`
- verify: `true`
- output mode: `rows`
- artifact shape: `handoff_bundle`

## Files

- `generated_polygon_set_jaccard_cpu_python_reference_authored_polygon_set_jaccard_minimal.py`: runnable generated RTDL program
- `request.json`: structured request manifest
- `README.md`: this handoff note

## Run

From the directory that contains this bundle:

```bash
python3 generated_polygon_set_jaccard_cpu_python_reference_authored_polygon_set_jaccard_minimal.py
```

The generated program contains:

- the RTDL kernel
- accepted dataset construction logic
- the requested backend runner
- verification against `cpu_python_reference` when enabled
