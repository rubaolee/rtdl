# Goal 575: v0.9 Final Release Gate After Closest-Hit

Date: 2026-04-18

## Verdict

ACCEPT. The v0.9 candidate is release-ready after the post-Goal570 RTXRMQ and
closest-hit changes.

This report supersedes Goal 570, Goal 572, and Goal 574 as the final v0.9
release gate.

## Why This Gate Was Needed

Goal 570 closed the original v0.9 HIPRT candidate release gate. After that,
`/Users/rl2025/Downloads/2306.03282v1.pdf` was added as a release-blocking
paper workload. Goal 571 first included it as a bounded traversal-count analogue.
Goal 573 then solved the missing closest-hit feature for CPU reference,
`run_cpu`, and Embree, enabling an exact bounded RTXRMQ-style RMQ workload.

Therefore the final release gate had to be refreshed after the new primitive,
tests, performance evidence, docs, and release package updates.

## Final Feature State

v0.9 candidate includes:

- HIPRT `run_hiprt` parity coverage for the accepted 18-workload Linux matrix.
- Prepared HIPRT reuse evidence for 3D ray/triangle, 3D fixed-radius nearest
  neighbors, graph CSR, and bounded DB table data.
- Exact bounded RTXRMQ-style RMQ through `ray_triangle_closest_hit` on:
  - CPU Python reference
  - `run_cpu`
  - Embree

Explicit non-claims:

- no AMD GPU validation yet
- no HIPRT CPU fallback
- no RT-core speedup claim from the GTX 1070 validation path
- no OptiX, Vulkan, or HIPRT native support yet for `ray_triangle_closest_hit`

## Release-Facing Docs Refreshed

Updated:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/capability_boundaries.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/support_matrix.md`

The v0.9 package no longer names Goal 570 as the final gate. It now records the
post-Goal570 sequence through Goals 571-575 and includes the closest-hit
RTXRMQ support boundary.

## Final Test Evidence

Local macOS:

```text
python3 -m unittest discover -s tests
Ran 239 tests in 61.409s
OK
```

Fresh synced Linux checkout:

```text
cd /tmp/rtdl_goal575_final
make build-embree
python3 -m unittest discover -s tests
Ran 239 tests in 149.925s
OK
```

## Final Documentation Audit

The focused public-doc audit checked:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/capability_boundaries.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/support_matrix.md`

Checks:

- no stale Goal570-as-final wording
- no stale package title that frames v0.9 as HIPRT-only
- no stale status title that frames v0.9 as HIPRT-only
- no stale wording that denies the new public closest-hit support
- no broken internal Markdown links in the checked public docs

Result on macOS and Linux:

```json
{
  "valid": true,
  "stale_hits": [],
  "missing_links": []
}
```

## Exact RTXRMQ Evidence

Goal 573:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal573_rtxrmq_closest_hit_feature_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal573_rtxrmq_closest_hit_linux_2026-04-18.json`

Linux case:

- values: `4096`
- query rays: `2048`
- triangles: `8192`
- max query range: `128`

| Backend | Median seconds | Exact RMQ parity |
|---|---:|---|
| CPU Python reference | `11.408521` | yes |
| Embree | `0.027440` | yes |

## Consensus Already In Place

Goal 573:

- Claude review: `/Users/rl2025/rtdl_python_only/docs/reports/goal573_external_review_2026-04-18.md`
- Gemini Flash review: `/Users/rl2025/rtdl_python_only/docs/reports/goal573_gemini_flash_review_2026-04-18.md`

Both returned `ACCEPT`.

Goal 575 adds the final release-facing doc refresh and final release-gate
review after Goal 573.

## Goal 575 Final Consensus

- Codex final review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal575_codex_final_review_2026-04-18.md`
- Gemini Flash review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal575_gemini_flash_review_2026-04-18.md`

Both returned `ACCEPT`.

Claude was also contacted for Goal 575 but the CLI returned:

```text
You've hit your limit · resets 9pm (America/New_York)
```

No Claude verdict is claimed for Goal 575.

## Final Release Boundary

The release claim should be:

RTDL v0.9 is ready as a candidate/release line containing HIPRT parity coverage
for the accepted matrix plus exact bounded RTXRMQ-style closest-hit support on
CPU reference, `run_cpu`, and Embree.

The release claim must not say:

- HIPRT is AMD-GPU validated
- GTX 1070 numbers prove hardware RT-core speedup
- OptiX/Vulkan/HIPRT support `ray_triangle_closest_hit`
- RTDL is a full DBMS, full rendering engine, or arbitrary workload compiler
