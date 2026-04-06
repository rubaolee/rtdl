# Goal 111 v0.2 Generate-Only MVP

Date: 2026-04-05
Author: Codex
Status: accepted

## Goal

Attempt one tightly constrained generate-only RTDL MVP and decide whether it is
promising enough to keep.

## Implemented package

The final package adds:

- generator module:
  - `src/rtdsl/generate_only.py`
- CLI entry point:
  - `scripts/rtdl_generate_only.py`
- generator tests:
  - `tests/goal111_generate_only_mvp_test.py`
- tracked worked example:
  - `examples/rtdl_generated_segment_polygon_hitcount_cpu.py`

## Accepted request contract

The MVP accepts one structured request with:

- workload
- dataset
- backend
- verify
- output mode

Current accepted values are intentionally narrow:

- workload:
  - `segment_polygon_hitcount`
- dataset:
  - `authored_segment_polygon_minimal`
  - `tests/fixtures/rayjoin/br_county_subset.cdb`
  - `derived/br_county_subset_segment_polygon_tiled_x4`
- backend:
  - `cpu_python_reference`
  - `cpu`
  - `embree`
  - `optix`
- output mode:
  - `rows`
  - `summary`

## What the generator emits

For one request, the generator emits one runnable Python RTDL program that
contains:

- an inline RTDL kernel
- a dataset/case builder
- the requested backend runner
- a verification block against `cpu_python_reference`
- JSON output

The generated program is specific to the request rather than a generic tutorial
shell. It freezes:

- requested dataset
- requested backend
- requested output shape
- whether verification should run

For the accepted dataset set, the generated program now owns the dataset
construction logic directly:

- authored minimal is emitted inline
- fixture-backed county subset is reconstructed from `rt.load_cdb(...)` plus
  explicit segment/polygon extraction logic
- derived `x4` case is reconstructed from the fixture builder plus explicit
  deterministic tiling helpers

## Worked example

Generation command:

```bash
cd /Users/rl2025/rtdl_python_only
python3 scripts/rtdl_generate_only.py \
  --workload segment_polygon_hitcount \
  --dataset authored_segment_polygon_minimal \
  --backend cpu \
  --output-mode summary \
  --output examples/rtdl_generated_segment_polygon_hitcount_cpu.py
```

The generated example file is:

- `examples/rtdl_generated_segment_polygon_hitcount_cpu.py`

Local smoke generation and generated-program execution were also validated on
the universally runnable reference backend:

```bash
cd /Users/rl2025/rtdl_python_only
python3 scripts/rtdl_generate_only.py \
  --workload segment_polygon_hitcount \
  --dataset authored_segment_polygon_minimal \
  --backend cpu_python_reference \
  --output-mode rows \
  --output build/goal111/rtdl_generated_segment_polygon_hitcount_cpu_python_reference.py

python3 build/goal111/rtdl_generated_segment_polygon_hitcount_cpu_python_reference.py
```

Observed payload:

```json
{
  "backend": "cpu_python_reference",
  "dataset": "authored_segment_polygon_minimal",
  "rows": [
    {"hit_count": 1, "segment_id": 1},
    {"hit_count": 1, "segment_id": 2}
  ],
  "verification_requested": true,
  "verified_against_cpu_python_reference": true,
  "workload": "segment_polygon_hitcount"
}
```

Capable-host `cpu` validation also succeeded on `lestat-lx1`:

```bash
ssh lestat-lx1 'cd /home/lestat/work/rtdl_python_only && \
  PYTHONPATH=src:. python3 /home/lestat/work/rtdl_python_only/build/goal111/rtdl_generated_segment_polygon_hitcount_cpu.py'
```

Observed payload:

```json
{
  "backend": "cpu",
  "dataset": "authored_segment_polygon_minimal",
  "row_count": 2,
  "verification_requested": true,
  "verified_against_cpu_python_reference": true,
  "workload": "segment_polygon_hitcount"
}
```

## Validation

Compile check:

```bash
python3 -m py_compile \
  src/rtdsl/generate_only.py \
  scripts/rtdl_generate_only.py \
  tests/goal111_generate_only_mvp_test.py
```

Test check:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest tests.goal111_generate_only_mvp_test
```

Result:

- `4 tests`
- `OK`
- `1 skipped`

The skipped test is the generated `cpu` execution path on this Mac because the
existing local native-oracle toolchain still lacks `geos_c`.

## Why this survives instead of being cut

The accepted concrete scenario is:

- the user already knows the workload family
- the user already knows the dataset and backend they want
- the user wants one runnable RTDL file immediately
- the user wants verification already wired in
- the user does not want to learn the example + baseline-runner helper stack
  just to get one reviewable starting program

For that scenario, the generator is more useful than:

- pointing the user at the generic workload example
- handing them a template and asking them to edit constants manually
- giving them a cookbook note

The generator produces the exact requested file in one step.

## Why this is still intentionally narrow

Goal 111 does **not** prove that RTDL should expand into broad code generation.

The accepted MVP remains:

- one-family only
- one-file only
- Python RTDL only
- verification-backed, but not multi-project scaffolding

So Goal 111 closes as:

- a kept generate-only MVP
- not a proof that code generation is now a co-equal v0.2 pillar

## Final judgment

Goal 111 is promising enough to keep as a narrow second bet.

It would become pause-worthy again if future work shows that expanded requests
produce little more than thin template emission.

## Review outcome

Final external reassessment after the strengthened package:

- Nash: keep
- Chandrasekhar: keep

Both reviewers explicitly kept the MVP only under the current narrow boundary:

- one family
- one file shape
- honest request contract
- no broad code-generation overclaim
