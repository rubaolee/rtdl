# Goal5255 - X-HD RTDL hd_exec-Compatible Entrypoint Result

Date: 2026-07-09

## Objective

Turn the X-HD paper reproduction line from a collection of review gates into a
user-facing RTDL paper-app entrypoint with the same key flags as the author's
`hd_exec` command.

This goal is about app usability and contract alignment. It is not a new
performance goal and does not claim that RTDL implements the author's fused
X-HD RT-core algorithm.

## Implemented

New app-owned runner:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
```

It accepts the author's key CLI flags:

```text
-input1 <path>
-input2 <path>
-n_dims <2|3>
-input_type <image|wkt|ply|off>
-variant <eb|nn|itk|clover|rt>
-execution <cpu|gpu>
-json <summary.json>
```

Supported subset:

```text
variant = rt
input_type = wkt | ply | off
n_dims = 2 | 3
```

Unsupported author options fail closed:

```text
variant != rt -> ValueError
input_type = image -> ValueError
```

RTDL-specific route selector:

```text
--rtdl-route auto | public-columnar | cell-mbr-fast-scalar | cell-mbr-exact-witness
```

Route behavior:

```text
public-columnar:
  Generic public RTDL columnar route.
  Runs directed input1 -> input2 only.
  Exact witness reference route.

cell-mbr-fast-scalar:
  3-D GPU route matching Goal5252's fast scalar family.
  HDResult route; per-source witness may be approximate.

cell-mbr-exact-witness:
  3-D GPU route matching Goal5253's exact-seed witness family.
  Per-source witness exact under the selected route contract.
```

## Output Contract

The runner writes author-shaped top-level fields:

```json
{
  "HDResult": 0.5,
  "Running": {
    "Algorithm": "RTDL-public-columnar",
    "AvgTime": 0.7627001032233238,
    "Repeats": [...]
  },
  "RTDL": {
    "schema": "rtdl.paper_reproduction.xhd.rtdl_hd_exec_compatible.v1",
    "route_label": "public-columnar",
    "hd_result_semantics": "directed_input1_to_input2",
    "claim_boundary": {...}
  }
}
```

Important semantic choice:

```text
HDResult = directed input1 -> input2
```

This follows the directed-asymmetric Goal5126 finding. It does not report the
symmetric max as `HDResult`.

## Validation

Local behavior tests:

```text
py -m unittest tests.goal5255_xhd_rtdl_hd_exec_entrypoint_test
```

Result:

```text
Ran 5 tests in 1.517s
OK
```

Compile check:

```text
py -m py_compile \
  Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py \
  tests/goal5255_xhd_rtdl_hd_exec_entrypoint_test.py
```

Result:

```text
OK
```

Manual directed-asymmetric smoke:

```text
py Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py \
  -input1 Paper-reproduction-apps/x-hd-paper/data/fixtures/directed2d_asymmetric_a.wkt \
  -input2 Paper-reproduction-apps/x-hd-paper/data/fixtures/directed2d_asymmetric_b.wkt \
  -n_dims 2 \
  -input_type wkt \
  -variant rt \
  -execution cpu \
  -json <temp>/xhd_rtdl_hd_exec_directed2d.json \
  --rtdl-route public-columnar
```

Observed:

```text
HDResult = 0.5
RTDL.hd_result_semantics = directed_input1_to_input2
RTDL.route_label = public-columnar
```

This is intentionally not the symmetric value 9.0 for that fixture.

## Files Changed

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
tests/goal5255_xhd_rtdl_hd_exec_entrypoint_test.py
Paper-reproduction-apps/x-hd-paper/README.md
```

## Claim Boundary

Allowed claim:

```text
The X-HD paper app now has an app-owned RTDL runner that accepts the author's
key hd_exec flags and writes HDResult/Running JSON while preserving explicit
RTDL route labels and claim boundaries.
```

Forbidden claims:

```text
full X-HD paper reproduction is complete
RTDL implements the author's fused RT-core X-HD algorithm
RTDL is performance-parity with author hd_exec
the route label may be omitted from performance summaries
exact paper dataset identity has been proven
```

## Status

```text
implemented_review_pending
```

## Next Recommended Work

1. Send Goal5255 for strict review.
2. If approved, use this runner as the user-facing RTDL app entrypoint in
   future X-HD documentation.
3. Keep internal gates for evidence production, but stop presenting them as
   the primary user experience.
