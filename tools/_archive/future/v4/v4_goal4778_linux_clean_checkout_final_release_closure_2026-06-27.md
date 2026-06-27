# V4 Goal4778 Linux Clean-Checkout Final Release Closure

Date: 2026-06-27

Status: `linux_clean_checkout_passed__release_tag_target_resolved_by_git_tag_object`

## Purpose

The RTX POD was not available. Local Linux `192.168.1.20` was used for
cross-platform correctness, clean-checkout reproducibility, strict release
surface checks, and installed-wheel smoke. It was not used for new RT-core
performance claims.

This closure follows the release-owner sequence:

1. confirm the current V4.0 release commit candidate;
2. run final clean-tree release gates and wheel smoke on Linux;
3. refresh the release record and `v4.0.0` tag target.

## Linux Environment

```text
host: lx1
os: Ubuntu 24.04 LTS
kernel: Linux 6.17.0-20-generic x86_64
python: Python 3.12.3
git: 2.43.0
checkout: /home/lestat/work/rtdl_v4_release_final_20260627
branch: codex/v4-tier2-section8
```

The machine does not have `python3.12-venv`, so the installed-wheel smoke now
falls back to `pip install --target` when venv creation fails. The fallback is
recorded explicitly as `install_method: pip_target_fallback`.

## Clean-Checkout Fixes Found By Linux

Linux clean checkout exposed release-provenance files that existed in the
Windows workspace but were hidden by `.gitignore`:

- `future/v4/evidence/v4_goal4759_full_v4_unittest_discover_with_review_manifest_2026-06-26.log`
- `future/v4/evidence/v4_goal4758_full_v4_unittest_discover_with_installed_wheel_script_gate_2026-06-26.log`
- `future/v4/evidence/v4_goal4758_package_wheel_build_2026-06-26.log`
- `future/v4/evidence/v4_goal4758_wheel_install_smoke_2026-06-26/wheel_install_with_deps.log`
- `future/v4/evidence/v4_goal4758_wheel_install_smoke_2026-06-26/import_claim_boundary_after_install.log`

These files are release evidence, not raw local debris. They are now tracked so
clean clones can validate Goal4757/4758/4759 without relying on local ghosts.

## Linux Verification Results

Strict release audit:

```bash
PYTHONPATH=src:.:scripts python3 scripts/v4_universe_audit.py --format json --strict-release
```

Result:

```text
status: pass
public_findings: []
tracked_file_count: 28354
unknown_untracked_count: 0
untracked_file_count: 0
```

Focused public/staging gate:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.v4_universe_audit_test \
  tests.v4_goal4640_public_docs_cleanup_test \
  tests.v4_frontdoor_test \
  tests.v4_goal4775_release_staging_manifest_test
```

Result:

```text
Ran 25 tests in 13.622s
OK
```

Full V4 discovery:

```bash
PYTHONPATH=src:. python3 -m unittest discover -s tests -p 'v4*_test.py'
```

Result:

```text
Ran 656 tests in 43.019s
OK (skipped=1)
```

Installed-wheel smoke:

```bash
PYTHONPATH=src:. python3 scripts/v4_goal4758_installed_wheel_smoke.py \
  --out-dir /tmp/rtdl_v4_linux_wheel_smoke_20260627
```

Result:

```text
status: passed
install_method: pip_target_fallback
install_status: passed
smoke_status: passed
matrix_apps: 10
matrix_rows: 30
measured_partners: cupy, numba, rtdl_native, torch
venv_create_status: failed
target_install_removed: true
```

The venv failure is expected on this host because `python3.12-venv` is not
installed. The fallback verifies the wheel from an installed package path
without CUDA and without importing from the source tree.

## Release Tag Policy

The public docs/API no longer hard-code a release commit SHA. The release target
is resolved by the `v4.0.0` Git tag object and this closure record. This avoids
stale commit strings in the user-facing tag when public-surface hardening occurs
after the first tag.

The tag annotation must record:

- target commit;
- Linux clean-checkout full V4 discovery result;
- strict release audit result;
- focused public/staging gate result;
- installed-wheel smoke result;
- forbidden claim boundaries.

## Non-Authorization

This closure does not authorize:

- broad V4-over-V2.14 or V4-over-V3 speedup wording;
- "all benchmark apps are faster" wording;
- Tier-3 arbitrary callback support;
- raw OptiX callback support;
- C ABI, embedding, or non-Python host claims;
- true external zero-copy claims;
- Barnes-Hut paper-reproduction expanded claims.

It only closes the Linux clean-checkout and release-target hygiene work needed
before refreshing the bounded V4.0 tag.
