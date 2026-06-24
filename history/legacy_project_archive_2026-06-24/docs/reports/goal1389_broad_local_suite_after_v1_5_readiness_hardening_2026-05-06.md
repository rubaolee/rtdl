# Goal1389: Broad Local Suite After v1.5 Readiness Hardening

Date: 2026-05-06

Source commit tested: `aa3d158`

## Scope

This report records a broad local regression run after the v1.5 internal
readiness decision hardening through Goal1388.

The run validates that the accumulated readiness API additions did not break
the wider test suite.

## Local Validation

Command:

```text
PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py'
```

Result:

```text
Ran 2656 tests in 380.982s
OK (skipped=197)
```

The test run generated the known transient archive:

```text
docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz
```

That generated tarball was removed and was not committed.
