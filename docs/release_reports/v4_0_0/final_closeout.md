# RTDL V4.0.0 Final Closeout

Status: release closeout in progress for `v4.0.0`.

| Step | Status | Evidence |
| ---: | --- | --- |
| 1 | done | `VERSION` is `v4.0.0`; `pyproject.toml` is `4.0.0`. |
| 2 | done | Front page, docs index, tutorials, examples, and release doorway point to V4.0.0. |
| 3 | done | V4.0.0 release package exists under `docs/release_reports/v4_0_0/`. |
| 4 | done | M1 Linux GPU release gate exists and has a passing Linux artifact. |
| 5 | done | Public wording boundaries keep package, SDK, async, true-zero-copy, public speedup, and RT-core speedup claims blocked. |
| 6 | pending | Fresh post-promotion Linux GPU gate on the exact publication commit. |

The pending Linux rerun is a validation freshness item, not permission to widen
claims. Until it is attached to the exact publication commit, use the existing
V4.0 M1 Linux gate as route evidence and keep this closeout marked in progress.
