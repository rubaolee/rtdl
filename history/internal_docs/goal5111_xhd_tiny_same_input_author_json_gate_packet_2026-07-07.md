# Goal5111 - X-HD Tiny Same-Input Author JSON Gate Packet

Date: 2026-07-07

## Status

```text
completed_packet_ready__author_hd_exec_execution_pending
```

This goal turns the Goal5110 scaffold into the first executable X-HD paper-app
gate packet. It does **not** claim author agreement yet. The author binary has
not been built or run in this local environment.

## What Was Added

Files:

```text
Paper-reproduction-apps/x-hd-paper/data/fixtures/tiny2d_a.wkt
Paper-reproduction-apps/x-hd-paper/data/fixtures/tiny2d_b.wkt
Paper-reproduction-apps/x-hd-paper/data/fixtures/tiny2d_expected.json
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_author_json_gate.py
Paper-reproduction-apps/x-hd-paper/results/tiny2d_local_reference_summary.json
tests/goal5111_xhd_author_json_gate_test.py
```

Updated:

```text
Paper-reproduction-apps/x-hd-paper/README.md
Paper-reproduction-apps/x-hd-paper/data/README.md
Paper-reproduction-apps/x-hd-paper/data/manifest.json
Paper-reproduction-apps/x-hd-paper/results/README.md
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
tests/goal5110_xhd_paper_app_scaffold_test.py
```

## Fixture

The tiny WKT fixture is intentionally small enough to audit by hand.

`tiny2d_a.wkt`:

```text
POINT(0 0)
POINT(2 0)
POINT(0 2)
```

`tiny2d_b.wkt`:

```text
POINT(0 0)
POINT(2 0)
POINT(0 3)
```

Expected exact values:

```text
directed_a_to_b = 1.0
directed_b_to_a = 1.0
hausdorff       = 1.0
tolerance       = 1e-9
```

The fixture is same-input in the paper-app sense: both the RTDL reference and
the author executable will consume the same two WKT files.

## Runner Contract

The runner is:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_author_json_gate.py
```

It supports two modes:

1. **Reference-only local mode**: parse the WKT fixtures and compute exact
   Hausdorff by brute force. This is runnable without CUDA or author code.
2. **Author JSON gate mode**: optionally run author `hd_exec`, read its JSON
   `HDResult`, and compare it with the exact reference under an explicit
   tolerance.

Author command shape:

```text
hd_exec
  -input1 <tiny2d_a.wkt>
  -input2 <tiny2d_b.wkt>
  -n_dims 2
  -input_type wkt
  -variant rt
  -execution gpu
  -json <author_summary.json>
  -overwrite=true
  -check=false
```

The runner fails closed when `--author-bin` is supplied without `--author-json`.

## Local Evidence

Generated local reference artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/tiny2d_local_reference_summary.json
```

Important fields:

```json
{
  "schema": "rtdl.paper_reproduction.xhd.author_json_gate.v1",
  "rtdl_reference": {
    "directed_a_to_b": 1.0,
    "directed_b_to_a": 1.0,
    "hausdorff": 1.0
  },
  "author_hd_result": null,
  "matched": null,
  "tolerance": 1e-9,
  "paper_reproduction_claim_authorized": false,
  "performance_claim_authorized": false
}
```

Interpretation: the local packet proves fixture parsing, exact reference
calculation, summary schema, and comparator plumbing. It does **not** prove
author agreement because `hd_exec` has not been run.

## Verification

Commands run:

```text
py -m unittest tests.goal5110_xhd_paper_app_scaffold_test tests.goal5111_xhd_author_json_gate_test
```

Result:

```text
Ran 7 tests in 0.087s
OK
```

JSON validation:

```text
manifest.json: json_ok
tiny2d_local_reference_summary.json: json_ok
```

The local Python runtime prints:

```text
Could not find platform independent libraries <prefix>
```

This warning is environmental noise in the local Python launcher; the tests and
JSON checks completed successfully.

## What This Proves

- The X-HD paper app now has a deterministic tiny same-input fixture.
- The explicit tolerance is selected for the first gate: `1e-9`.
- The app-owned runner can parse POINT WKT, compute an exact Hausdorff
  reference, load author `HDResult`, and report match/mismatch.
- Fake-author tests prove both pass and fail comparator paths.
- The gate is ready to run on a CUDA/POD environment once author `hd_exec` is
  built.

## What This Does Not Prove

- It does not prove X-HD paper reproduction.
- It does not prove exact paper dataset reproduction.
- It does not prove author agreement.
- It does not prove performance or speedup.
- It does not reclassify historical `examples/current/research_benchmarks/hausdorff_xhd/`
  evidence as paper-app evidence.
- It does not add any RTDL core primitive or app-specific language behavior.

## Core Boundary

All new execution logic is under the paper app directory or tests. The runner,
fixtures, author JSON parsing, tolerance, and paper-app status are app-owned.
No RTDL core API is promoted by this goal.

## Next Goal

Goal5112 should run the packet on a CUDA/POD environment:

1. Check out the pinned author repository commit
   `7bf41c8442d059c94f4178355c6d5a10571d9658`.
2. Build `hd_exec` or document the build blocker precisely.
3. Run the tiny WKT gate with `variant=rt`, `execution=gpu`.
4. Record author JSON, author `HDResult`, RTDL exact reference, tolerance, and
   `matched`.
5. Keep performance fields separate from correctness.

Expected exit labels:

```text
completed_tiny_same_input_author_json_gate_matched
blocked_author_hd_exec_build_or_runtime_with_exact_log
completed_tiny_same_input_author_json_gate_mismatch
```
