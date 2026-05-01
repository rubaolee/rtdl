# Goal873 Claude External Review

- reviewer: `Claude`
- date: `2026-04-24`
- verdict: `ACCEPT_WITH_CAVEATS`

## Verdict

Claude accepted the Goal873 gate design with caveats.

## Review Summary

Claude checked:

- The `ctypes` ABI for
  `rtdl_optix_run_segment_polygon_anyhit_rows_native_bounded` matches the
  caller-owned bounded buffer contract.
- Non-strict local behavior safely records missing `librtdl_optix` without
  failing local development.
- Strict RTX behavior requires the native symbol to run, row digest to match
  CPU reference, and `overflowed == 0`.
- Test coverage exercises digest ordering, non-strict missing backend, strict
  failure, strict success, and CLI JSON output.
- The boundary statement correctly avoids public path promotion.

## Caveats Raised

- No Linux/RTX strict artifact exists yet.
- Zero `output_capacity` could make strict mode compare an empty caller-owned
  buffer.
- Consumers must read `strict` together with `strict_pass` in JSON output.

## Follow-Up Applied

After the review, Goal873 was tightened to reject non-positive
`output_capacity`, and the markdown report now explicitly documents the
`strict` / `strict_pass` interpretation.

The Linux/RTX strict artifact remains pending and is the intended next cloud
gate for this path.
