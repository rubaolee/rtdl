# Local Linux Simulated User Clone Validation - 2026-06-28

Host: `192.168.1.20` (`lx1`)

Purpose: verify that a user on Linux can clone the public V4 surface, follow the README-style first path, and run the public validation gate without relying on the Windows working tree.

## Command Shape

```bash
rm -rf /tmp/rtdl_v4_user_clone
git clone --depth 1 --branch codex/v4-tier2-section8 https://github.com/rubaolee/rtdl /tmp/rtdl_v4_user_clone
cd /tmp/rtdl_v4_user_clone
export PYTHONPATH=src:.
python3 examples/tutorial_programs/hello_world.py
python3 examples/tutorial_programs/sorting_rows.py
python3 examples/tutorial_programs/fixed_radius_neighbors.py --mode both
python3 examples/tutorial_programs/nearest_neighbor.py --mode both
python3 examples/tutorial_programs/partner_choices.py --mode both
python3 examples/tutorial_programs/v4_frontdoor_quickstart.py
python3 examples/tutorial_programs/benchmark_app_recipes.py
python3 -m unittest \
  tests.v4_goal4803_public_markdown_link_integrity_test \
  tests.v4_goal4800_kernel_first_tutorial_classification_test \
  tests.v4_goal4640_public_docs_cleanup_test \
  tests.v4_goal4643_publication_decision_test \
  tests.v4_goal4774_release_packaging_audit_test \
  tests.v4_rayjoin_section57_public_entry_test
```

## Result

- Clone head: `bf92b7c5`
- Python: `Python 3.12.3`
- README-style tutorial commands: passed.
- Public validation gate: `Ran 35 tests in 35.325s` -> `OK`.
- Final marker: `LINUX_USER_CLONE_CLEAR`.

## Verdict

Clear. The current V4 public tutorial/documentation/example surface is usable from a fresh Linux clone for the checked learning path and public test gate.
