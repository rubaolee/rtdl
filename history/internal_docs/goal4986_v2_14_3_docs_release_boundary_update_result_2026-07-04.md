# Goal4986 Result: v2.14.3 Docs And Release Boundary Update

Date: 2026-07-04

## Verdict

```text
completed_v2_14_3_docs_release_boundary_update
```

Goal4986 updated the RayJoin paper-reproduction app documentation and the v2.14 release packet so the public-facing wording matches the final v2.14.3 bounded performance matrix.

## Files Updated

```text
Paper-reproduction-apps/rayjoin-paper/README.md
docs/release_reports/v2_14/rayjoin_reproduction_packet.md
```

## What Changed

### RayJoin paper app README

Added a v2.14.3 writer-free binary route performance boundary:

- fresh/cold writer-free route: about `4.22s`;
- repeated full route in the same process: about `3.62-3.67s`;
- prepared/cached LSI replay: diagnostic only;
- no top4 author overlay-compute denominator is currently published;
- do not reuse the smaller public-sample author timing as a top4 denominator.

### v2.14 RayJoin reproduction packet

Updated the "Current Performance Boundary" section:

- paper text-output route remains a correctness anchor and is still text-writer expensive;
- writer-free binary route measures RTDL as a pipeline operator;
- top4 fresh/cold and repeated-route timings are stated with boundaries;
- remaining binary-route bottleneck is exact LSI producer setup/ensure work;
- no author ratio is claimed for top4.

## Validation

Public leak scan:

```text
rg "Goal[0-9]+|Claude|Gemini|Antigravity|Codex|verdict|call_for_review|internal_docs|0\\.0421s.*top4|2\\.04x|author.*parity" README.md docs Paper-reproduction-apps/rayjoin-paper/README.md -n
```

Result:

```text
0 matches
```

Compile gate:

```text
$env:PYTHONPATH='src'; py -m py_compile Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py src/rtdsl/embree_runtime.py src/rtdsl/optix_runtime.py
```

Result:

```text
passed
```

The Python launcher printed:

```text
Could not find platform independent libraries <prefix>
```

but exited `0`.

## Claim Boundary

Authorized:

- public docs may state the bounded writer-free binary route timings;
- public docs may explain that top4 author ratio is not measured;
- public docs may say exact LSI producer setup/ensure work is the remaining binary-route bottleneck.

Not authorized:

- no internal goal numbers in public docs;
- no reviewer names or process language in public docs;
- no author-parity claim;
- no warm-only claim;
- no reuse of `0.0421s` as a top4 denominator;
- no claim that prepared/cached replay is fresh overlay.

## Next Step

Proceed to Goal4987:

- final cleanup/status audit;
- final closeout/release packet;
- external review request;
- do not reset or discard project-state files without a separate explicit audit.
