# RTDL v2.14.1 Closeout Note

Status: current v2.14-line closeout note.

RTDL v2.14.1 closes the v2.14 source-tree release line. It keeps the v2.14
language/runtime boundary and adds a packaged RayJoin paper-reproduction app
with a Linux-validated public-sample workflow.

## What Changed

- Version marker updated to `v2.14.1`.
- The RayJoin paper-reproduction app is now a complete project under
  `Paper-reproduction-apps/rayjoin-paper/`.
- The RayJoin project includes:
  - public input manifest with SHA-256 checks;
  - patched author comparator build path (`AuthorOfficial`);
  - RTDL Section 5.2, 5.3, and 5.7 runners;
  - RTDL+Numba Section 5.7 runner;
  - one-command Linux public-sample runner.
- The Linux full runner was validated on the public County x Soil sample.

## Public-Sample Validation

The v2.14.1 Linux validation ran:

```bash
bash Paper-reproduction-apps/rayjoin-paper/scripts/run_full_public_sample.sh
```

The validated public sample contains:

| Role | SHA-256 |
| --- | --- |
| County input | `cee9f41da48c6f072b0692843cc23804517e8928f46c6c84675fc9a3b1e5a0e7` |
| Soil input | `525a6dda0e42c1ed63f30cd5ffe8e9283697f3c53076837a122ba098ad530d9f` |
| Section 5.7 answer | `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e` |

Observed checks:

| Check | Result |
| --- | --- |
| AuthorOfficial Section 5.7 output equals public answer | pass |
| RTDL Section 5.7 output equals public answer | pass |
| RTDL+Numba Section 5.7 output equals public answer | pass |

The three Section 5.7 outputs share SHA-256:

`464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`

## Claim Boundary

Safe statement:

```text
RTDL v2.14.1 packages a bounded RayJoin paper-reproduction app. On the public
County x Soil sample, the patched author comparator, RTDL route, and RTDL+Numba
route all produce byte-identical Section 5.7 output to the public answer.
```

Do not claim:

- all hidden Section 5.7 paper inputs are available;
- all eight original Section 5.7 pairs are reproduced from exact paper inputs;
- broad RTDL speedup over the RayJoin author program;
- Numba materially accelerates the full public-sample RayJoin app;
- RayJoin output formatting is a generic RTDL engine feature.

## Next Line

v2.14.2 is reserved for measured performance work. Its first step should be a
measurement-only phase decomposition of the RayJoin output path before any new
optimization implementation.
