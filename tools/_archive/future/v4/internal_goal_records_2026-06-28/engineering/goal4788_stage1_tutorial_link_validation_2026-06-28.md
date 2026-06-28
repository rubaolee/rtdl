# Goal4788 Link Validation

Date: 2026-06-28

The public link gate is covered by:

```bash
PYTHONPATH=src:. python3 -m unittest tests.v4_goal4640_public_docs_cleanup_test
```

Final Linux result:

```text
Ran 14 tests in 28.821s
OK
```

The gate includes relative-link resolution for the public documentation set.
It passed after the current `tutorials/current/README.md` links were changed
from the removed stale pages to:

- `05_fixed_radius_neighbors.md`
- `06_nearest_witness.md`

No public link to `05_prepare_run_continue.md` or `06_measure_a_program.md`
remains in the current tutorial index.
