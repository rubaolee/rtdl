# Goal4788 Linux Validation

Date: 2026-06-28

Host:

`192.168.1.20`

Final validation directory:

`/tmp/rtdl_goal4788_full_check`

The initial `/tmp/rtdl_goal4788_check` directory was rejected as a validation
source because it was an incomplete temporary copy. The final run used a full
copy of `/home/lestat/work/rtdl_v4_release_final_20260627` with current public
docs, examples, tests, and `src/rtdsl` synchronized from the Windows workspace.

## Commands

```bash
cd /tmp/rtdl_goal4788_full_check
test ! -e tutorials/current/05_prepare_run_continue.md
test ! -e tutorials/current/06_measure_a_program.md
test -f tutorials/current/05_fixed_radius_neighbors.md
test -f tutorials/current/06_nearest_witness.md
PYTHONPATH=src:. python3 examples/tutorial_programs/operator_primitives.py
PYTHONPATH=src:. python3 examples/tutorial_programs/v4_frontdoor_quickstart.py
PYTHONPATH=src:. python3 examples/tutorial_programs/fixed_radius_neighbors.py
PYTHONPATH=src:. python3 examples/tutorial_programs/nearest_neighbor.py
PYTHONPATH=src:. python3 examples/tutorial_programs/ranked_summary_neighbors.py
PYTHONPATH=src:. python3 -m py_compile \
  examples/tutorial_programs/operator_primitives.py \
  examples/tutorial_programs/v4_frontdoor_quickstart.py \
  examples/tutorial_programs/fixed_radius_neighbors.py \
  examples/tutorial_programs/nearest_neighbor.py \
  examples/tutorial_programs/ranked_summary_neighbors.py
PYTHONPATH=src:. python3 -m unittest tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test
PYTHONPATH=src:. python3 -m unittest tests.v4_goal4640_public_docs_cleanup_test
```

## Results

| Check | Result |
| --- | --- |
| Old current pages absent | Passed. |
| New 05/06 current pages present | Passed. |
| Goal4788 tutorial scripts run | Passed. |
| Goal4788 tutorial scripts compile | Passed. |
| `tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test` | Passed: 7 tests. |
| `tests.v4_goal4640_public_docs_cleanup_test` | Passed: 14 tests. |
